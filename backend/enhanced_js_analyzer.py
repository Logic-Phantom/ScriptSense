from fastapi import APIRouter, HTTPException, UploadFile, File
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from enum import Enum
import re
import yaml
import logging
from pathlib import Path
from functools import lru_cache
from concurrent.futures import ThreadPoolExecutor
import asyncio
from contextlib import contextmanager
from llm_client import request_llm, request_llm_fast

# 로깅 설정
logger = logging.getLogger(__name__)

router = APIRouter()

# ============================================================================
# 데이터 모델 정의
# ============================================================================

class IssueSeverity(str, Enum):
    CRITICAL = "critical"
    HIGH = "high" 
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"

class AnalysisIssue(BaseModel):
    category: str  # 'syntax', 'api', 'security', 'performance'
    severity: IssueSeverity
    message: str
    line_number: Optional[int] = None
    column: Optional[int] = None
    suggestion: Optional[str] = None
    code_snippet: Optional[str] = None
    priority: Optional[str] = None  # 'LOW', 'MEDIUM', 'HIGH'

class JavaScriptAnalysisRequest(BaseModel):
    code: str
    fast_mode: bool = False

class EnhancedJavaScriptAnalysisResponse(BaseModel):
    issues: List[AnalysisIssue]
    statistics: Dict[str, int]
    execution_flow: List[str]
    recommendations: List[str]
    llm_analysis: Optional[str] = None

# ============================================================================
# 에러 패턴 정의 (카테고리별로 정리)
# ============================================================================

ERROR_PATTERNS = {
    'syntax_errors': [
        (r'\bar\s+\w+', '변수 선언 오류: "ar" → "var"로 수정하세요', IssueSeverity.HIGH),
        (r'\blet\s+\w+', '변수 선언 확인: "let" 사용을 권장합니다', IssueSeverity.LOW),
        (r'\bconst\s+\w+', '상수 선언 확인: "const" 사용을 권장합니다', IssueSeverity.LOW),
        (r'function\s+(\w+)\s*\([^)]*\)\s*\{[^}]*\1\s*\(', '재귀 함수 호출이 무한 루프를 일으킬 수 있습니다', IssueSeverity.HIGH),
        (r'var\s+(\w+)\s*=\s*\1', '변수가 자기 자신을 참조하고 있습니다', IssueSeverity.HIGH),
        (r'(\w+)\s*=\s*\1\s*[+\-*/]', '변수가 자기 자신과 연산하고 있습니다', IssueSeverity.MEDIUM),
    ],
    'variable_scope_issues': [
        (r'var\s+\w+\s*=\s*function\s*\([^)]*\)\s*\{[^}]*var\s+\w+', '함수 내부에서 var 재선언은 호이스팅 문제를 일으킬 수 있습니다', IssueSeverity.MEDIUM),
        (r'for\s*\(\s*var\s+\w+\s+in\s+', 'for...in 루프에서 var 사용시 스코프 문제가 발생할 수 있습니다', IssueSeverity.MEDIUM),
        (r'var\s+\w+\s*=\s*[^;]*\|\|[^;]*;', '논리 OR 연산자로 기본값 설정시 falsy 값 처리를 확인하세요', IssueSeverity.LOW),
    ],
    'null_reference': [
        (r'\.getElementById\([^)]*\)\.', 'getElementById 결과가 null일 수 있습니다', IssueSeverity.HIGH),
        (r'\.querySelector\([^)]*\)\.', 'querySelector 결과가 null일 수 있습니다', IssueSeverity.HIGH),
        (r'\.length\s*[<>=]', 'length 속성 접근시 null/undefined 오류 가능성', IssueSeverity.MEDIUM),
        (r'\.\w+\([^)]*\)\.', '메서드 체이닝시 중간 결과가 null일 수 있습니다', IssueSeverity.HIGH),
        (r'\[\d+\]\.', '배열 인덱스 접근시 해당 인덱스가 존재하지 않을 수 있습니다', IssueSeverity.MEDIUM),
    ],
    'xss_security': [
        (r'\.innerHTML\s*=', 'innerHTML 사용시 XSS 위험이 있습니다', IssueSeverity.CRITICAL),
        (r'eval\(', 'eval() 사용은 보안상 위험합니다', IssueSeverity.CRITICAL),
        (r'Function\s*\(', 'Function 생성자 사용은 보안상 위험합니다', IssueSeverity.CRITICAL),
        (r'\.outerHTML\s*=', 'outerHTML 사용시 XSS 위험이 있습니다', IssueSeverity.CRITICAL),
        (r'document\.write\s*\(', 'document.write 사용은 보안상 위험합니다', IssueSeverity.CRITICAL),
    ],
    'json_parsing': [
        (r'JSON\.parse\([^)]*\)', 'JSON.parse는 try-catch로 감싸야 합니다', IssueSeverity.HIGH),
        (r'\.parseInt\([^)]*\)', 'parseInt 호출시 잘못된 문자열일 수 있습니다', IssueSeverity.MEDIUM),
        (r'\.parseFloat\([^)]*\)', 'parseFloat 호출시 잘못된 문자열일 수 있습니다', IssueSeverity.MEDIUM),
        (r'Number\s*\([^)]*\)', 'Number() 변환시 NaN이 반환될 수 있습니다', IssueSeverity.MEDIUM),
    ],
    'array_operations': [
        (r'\.split\([^)]*\)\[', 'split 결과가 빈 배열일 수 있습니다', IssueSeverity.MEDIUM),
        (r'\.push\([^)]*\)', 'push 메서드 호출시 배열이 null일 수 있습니다', IssueSeverity.MEDIUM),
        (r'\.pop\(\)', 'pop 메서드 호출시 빈 배열일 수 있습니다', IssueSeverity.MEDIUM),
        (r'\.shift\(\)', 'shift 메서드 호출시 빈 배열일 수 있습니다', IssueSeverity.MEDIUM),
        (r'\.splice\([^)]*\)', 'splice 메서드 호출시 배열 범위를 벗어날 수 있습니다', IssueSeverity.MEDIUM),
        (r'\.slice\([^)]*\)', 'slice 메서드 호출시 잘못된 인덱스일 수 있습니다', IssueSeverity.LOW),
        (r'\.indexOf\([^)]*\)\s*[<>=]', 'indexOf 결과가 -1일 수 있습니다', IssueSeverity.MEDIUM),
    ],
    'string_operations': [
        (r'\.charAt\([^)]*\)', 'charAt 인덱스가 문자열 길이를 초과할 수 있습니다', IssueSeverity.MEDIUM),
        (r'\.substring\([^)]*\)', 'substring 인덱스가 잘못될 수 있습니다', IssueSeverity.MEDIUM),
        (r'\.substr\([^)]*\)', 'substr 인덱스가 잘못될 수 있습니다', IssueSeverity.MEDIUM),
        (r'\.replace\([^)]*\)', 'replace 메서드 호출시 정규식 오류가 발생할 수 있습니다', IssueSeverity.LOW),
        (r'\.match\([^)]*\)', 'match 메서드 호출시 정규식 오류가 발생할 수 있습니다', IssueSeverity.LOW),
    ],
    'comparison_issues': [
        (r'==\s*null', 'null 비교시 === 사용을 권장합니다', IssueSeverity.LOW),
        (r'==\s*undefined', 'undefined 비교시 === 사용을 권장합니다', IssueSeverity.LOW),
        (r'[^=!<>]=[^=]', '할당 연산자 확인 필요 (= vs ==)', IssueSeverity.MEDIUM),
        (r'[^=!<>]!=[^=]', '불일치 연산자 확인 필요 (!= vs !==)', IssueSeverity.LOW),
        (r'[^=!<>]=[^=]', '할당 연산자 확인 필요 (= vs ==)', IssueSeverity.MEDIUM),
        (r'typeof\s+\w+\s*==\s*["\']string["\']', 'typeof 비교시 === 사용을 권장합니다', IssueSeverity.LOW),
    ],
    'performance_issues': [
        (r'console\.log\(', 'console.log는 프로덕션에서 제거해야 합니다', IssueSeverity.LOW),
        (r'for\s*\(\s*;\s*;\s*\)', '무한 루프 위험이 있습니다', IssueSeverity.HIGH),
        (r'while\s*\(\s*true\s*\)', '무한 루프 위험이 있습니다', IssueSeverity.HIGH),
        (r'for\s*\(\s*var\s+\w+\s*=\s*0;\s*\w+\s*<\s*\w+\.length;\s*\w+\+\+\)', 'for 루프에서 length를 매번 계산하고 있습니다', IssueSeverity.MEDIUM),
        (r'\.innerHTML\s*\+=', 'innerHTML += 사용시 성능 저하가 발생할 수 있습니다', IssueSeverity.MEDIUM),
        (r'setInterval\s*\([^,]+,\s*[0-9]+\)', 'setInterval 사용시 메모리 누수가 발생할 수 있습니다', IssueSeverity.MEDIUM),
    ],
    'error_handling': [
        (r'try\s*\{[^}]*\}\s*catch\s*\([^)]*\)\s*\{[^}]*\}', 'catch 블록이 비어있거나 적절한 처리가 없습니다', IssueSeverity.MEDIUM),
        (r'throw\s+new\s+Error\s*\([^)]*\)', 'Error 객체 생성시 적절한 메시지를 포함하세요', IssueSeverity.LOW),
        (r'\.catch\s*\([^)]*\)\s*\{[^}]*\}', 'Promise catch 블록이 비어있거나 적절한 처리가 없습니다', IssueSeverity.MEDIUM),
    ],
    'unnecessary_code': [
        (r'var\s+\w+\s*=\s*undefined', 'undefined 할당은 불필요합니다', IssueSeverity.LOW),
        (r'var\s+\w+\s*=\s*null', 'null 할당이 필요한지 확인하세요', IssueSeverity.LOW),
        (r'return\s*;', 'return 문이 값을 반환하지 않습니다', IssueSeverity.LOW),
        (r'if\s*\([^)]*\)\s*\{[^}]*\}\s*else\s*\{[^}]*\}', 'if-else 블록이 비어있습니다', IssueSeverity.LOW),
    ],
    'async_issues': [
        (r'async\s+function\s+\w+\s*\([^)]*\)\s*\{[^}]*await\s+', 'async 함수에서 await 사용시 try-catch로 감싸세요', IssueSeverity.MEDIUM),
        (r'Promise\s*\.\s*resolve\s*\([^)]*\)', 'Promise.resolve 사용시 적절한 에러 처리가 필요합니다', IssueSeverity.LOW),
        (r'Promise\s*\.\s*reject\s*\([^)]*\)', 'Promise.reject 사용시 적절한 에러 처리가 필요합니다', IssueSeverity.LOW),
    ],
    'memory_leaks': [
        (r'addEventListener\s*\([^)]*\)', 'addEventListener 사용시 removeEventListener로 정리해야 합니다', IssueSeverity.MEDIUM),
        (r'setTimeout\s*\([^)]*\)', 'setTimeout 사용시 clearTimeout으로 정리해야 합니다', IssueSeverity.MEDIUM),
        (r'setInterval\s*\([^)]*\)', 'setInterval 사용시 clearInterval로 정리해야 합니다', IssueSeverity.MEDIUM),
        (r'new\s+Date\s*\([^)]*\)', 'Date 객체 생성이 반복적으로 발생하고 있습니다', IssueSeverity.LOW),
    ],
    'type_safety': [
        (r'typeof\s+\w+\s*!==\s*["\']string["\']', '타입 체크 후 적절한 처리가 필요합니다', IssueSeverity.LOW),
        (r'instanceof\s+\w+', 'instanceof 체크 후 적절한 처리가 필요합니다', IssueSeverity.LOW),
        (r'Array\.isArray\s*\([^)]*\)', 'Array.isArray 체크 후 적절한 처리가 필요합니다', IssueSeverity.LOW),
    ],
    'code_style': [
        (r'function\s+\w+\s*\([^)]*\)\s*\{[^}]{0,10}\}', '함수가 너무 짧습니다. 의미있는 로직이 있는지 확인하세요', IssueSeverity.LOW),
        (r'var\s+\w+\s*,\s*\w+', '여러 변수를 한 줄에 선언하는 것은 가독성을 떨어뜨립니다', IssueSeverity.LOW),
        (r'[^;]\s*$', '문장 끝에 세미콜론이 없습니다', IssueSeverity.LOW),
        (r'[^}]\s*else\s*\{', 'else 앞에 중괄호가 없습니다', IssueSeverity.LOW),
    ]
}

# ============================================================================
# eXBuilder6 API 설정 (YAML 파일로 분리 가능)
# ============================================================================

EXBUILDER6_CONTROL_APIS = {
    'grd': {
        'methods': [
            'addRow', 'deleteRow', 'updateRow', 'getRow', 'getData', 'setData', 'clear', 'refresh',
            'getSelected', 'setSelected', 'getChecked', 'setChecked', 'getExpanded', 'setExpanded',
            'scrollTo', 'scrollIntoView', 'enable', 'disable', 'show', 'hide', 'focus', 'blur',
            'getCellInfo', 'setCellInfo', 'getRowData', 'setRowData', 'getColumnData', 'setColumnData',
            'getHeaderData', 'setHeaderData', 'getFooterData', 'setFooterData', 'getSummaryData', 'setSummaryData',
            'insertRowData', 'removeRowData', 'getRowCount', 'getColumnCount', 'getSelectedRows', 'setSelectedRows',
            'getCellValue', 'setCellValue', 'getCellText', 'setCellText', 'getCellStyle', 'setCellStyle',
            'getColumnWidth', 'setColumnWidth', 'getRowHeight', 'setRowHeight', 'getVisibleRows', 'setVisibleRows',
            'getVisibleColumns', 'setVisibleColumns', 'getSortColumn', 'setSortColumn', 'getSortOrder', 'setSortOrder',
            'getFilterData', 'setFilterData', 'getGroupData', 'setGroupData', 'getSummaryData', 'setSummaryData',
            'getPagingData', 'setPagingData', 'getPageSize', 'setPageSize', 'getCurrentPage', 'setCurrentPage',
            'getTotalCount', 'setTotalCount', 'getPageCount', 'setPageCount', 'getPageInfo', 'setPageInfo'
        ],
        'properties': [
            'text', 'value', 'visible', 'enabled', 'readOnly', 'width', 'height', 'style', 'data', 
            'columns', 'rows', 'selectedIndex', 'selectedIndices', 'selectedRow', 'selectedRows',
            'currentRow', 'currentColumn', 'rowCount', 'columnCount', 'pageSize', 'currentPage',
            'totalCount', 'pageCount', 'sortColumn', 'sortOrder', 'filterData', 'groupData',
            'summaryData', 'pagingData', 'editable', 'selectable', 'multiSelect', 'checkable',
            'expandable', 'resizable', 'draggable', 'droppable', 'scrollable', 'paging', 'sorting',
            'filtering', 'grouping', 'summarizing', 'exporting', 'importing', 'printing'
        ],
        'events': [
            'onCellClick', 'onCellDoubleClick', 'onCellRightClick', 'onHeaderClick', 'onRowClick', 
            'onRowDoubleClick', 'onRowRightClick', 'onSelectionChanged', 'onDataChanged', 'onCellEdit',
            'onCellEditEnd', 'onCellEditCancel', 'onRowAdded', 'onRowDeleted', 'onRowUpdated',
            'onColumnResized', 'onColumnMoved', 'onColumnSorted', 'onColumnFiltered', 'onColumnGrouped',
            'onPageChanged', 'onPageSizeChanged', 'onScroll', 'onFocus', 'onBlur', 'onKeyDown', 'onKeyUp'
        ]
    },
    'button': {
        'methods': [
            'setText', 'getText', 'enable', 'disable', 'show', 'hide', 'focus', 'blur', 'click',
            'setIcon', 'getIcon', 'setIconAlign', 'getIconAlign', 'setButtonType', 'getButtonType',
            'setImage', 'getImage', 'setImageAlign', 'getImageAlign', 'setTooltip', 'getTooltip'
        ],
        'properties': [
            'text', 'value', 'visible', 'enabled', 'readOnly', 'width', 'height', 'style', 
            'icon', 'iconAlign', 'buttonType', 'image', 'imageAlign', 'tooltip', 'defaultButton',
            'cancelButton', 'flat', 'raised', 'outlined', 'textOnly', 'iconOnly', 'textAndIcon'
        ],
        'events': [
            'onClick', 'onDoubleClick', 'onRightClick', 'onMouseDown', 'onMouseUp', 
            'onMouseOver', 'onMouseOut', 'onFocus', 'onBlur', 'onKeyDown', 'onKeyUp'
        ]
    },
    'btn': {
        'methods': [
            'setText', 'getText', 'enable', 'disable', 'show', 'hide', 'focus', 'blur', 'click',
            'setIcon', 'getIcon', 'setIconAlign', 'getIconAlign', 'setButtonType', 'getButtonType',
            'setImage', 'getImage', 'setImageAlign', 'getImageAlign', 'setTooltip', 'getTooltip'
        ],
        'properties': [
            'text', 'value', 'visible', 'enabled', 'readOnly', 'width', 'height', 'style', 
            'icon', 'iconAlign', 'buttonType', 'image', 'imageAlign', 'tooltip', 'defaultButton',
            'cancelButton', 'flat', 'raised', 'outlined', 'textOnly', 'iconOnly', 'textAndIcon'
        ],
        'events': [
            'onClick', 'onDoubleClick', 'onRightClick', 'onMouseDown', 'onMouseUp', 
            'onMouseOver', 'onMouseOut', 'onFocus', 'onBlur', 'onKeyDown', 'onKeyUp'
        ]
    },
    'cmb': {
        'methods': [
            'addItem', 'deleteItem', 'updateItem', 'getItem', 'getData', 'setData', 'clear', 'refresh',
            'getSelected', 'setSelected', 'getChecked', 'setChecked', 'enable', 'disable', 'show', 'hide', 'focus', 'blur',
            'openDropdown', 'closeDropdown', 'getSelectedIndex', 'setSelectedIndex', 'getSelectedValue', 'setSelectedValue',
            'getSelectedText', 'setSelectedText', 'getItemCount', 'getItemText', 'setItemText', 'getItemValue', 'setItemValue',
            'getItemData', 'setItemData', 'getItemIndex', 'setItemIndex', 'getItemByValue', 'getItemByText', 'getItemByIndex'
        ],
        'properties': [
            'text', 'value', 'visible', 'enabled', 'readOnly', 'width', 'height', 'style', 
            'items', 'selectedIndex', 'selectedValue', 'selectedText', 'dropdownVisible', 'itemCount',
            'maxDropDownItems', 'dropDownWidth', 'dropDownHeight', 'autoComplete', 'caseSensitive',
            'filterMode', 'sortMode', 'editable', 'allowCustom', 'allowNull', 'placeholder'
        ],
        'events': [
            'onClick', 'onDoubleClick', 'onRightClick', 'onSelectionChanged', 'onDropdownOpened', 
            'onDropdownClosed', 'onItemSelected', 'onItemDeselected', 'onTextChanged', 'onFocus', 'onBlur'
        ]
    },
    'cbx': {
        'methods': [
            'setChecked', 'getChecked', 'setText', 'getText', 'enable', 'disable', 'show', 'hide', 'focus', 'blur',
            'setCheckType', 'getCheckType', 'setTextAlign', 'getTextAlign', 'setGroupName', 'getGroupName'
        ],
        'properties': [
            'text', 'value', 'visible', 'enabled', 'readOnly', 'width', 'height', 'style', 
            'checked', 'checkType', 'textAlign', 'groupName', 'threeState', 'indeterminate',
            'autoCheck', 'allowGrayed', 'flat', 'raised', 'outlined'
        ],
        'events': [
            'onClick', 'onDoubleClick', 'onRightClick', 'onCheckedChanged', 'onIndeterminateChanged',
            'onFocus', 'onBlur', 'onKeyDown', 'onKeyUp'
        ]
    },
    'ipb': {
        'methods': [
            'setValue', 'getValue', 'setText', 'getText', 'enable', 'disable', 'show', 'hide', 'focus', 'blur',
            'setMaxLength', 'getMaxLength', 'setPlaceholder', 'getPlaceholder', 'setInputType', 'getInputType',
            'setPattern', 'getPattern', 'setRequired', 'getRequired', 'setReadOnly', 'getReadOnly',
            'setAutoComplete', 'getAutoComplete', 'setAutoFocus', 'getAutoFocus', 'setSpellCheck', 'getSpellCheck'
        ],
        'properties': [
            'text', 'value', 'visible', 'enabled', 'readOnly', 'width', 'height', 'style', 
            'maxLength', 'placeholder', 'inputType', 'pattern', 'required', 'autoComplete',
            'autoFocus', 'spellCheck', 'min', 'max', 'step', 'size', 'multiple', 'accept'
        ],
        'events': [
            'onValueChanged', 'onTextChanged', 'onKeyDown', 'onKeyUp', 'onKeyPress', 'onInput',
            'onChange', 'onFocus', 'onBlur', 'onSelect', 'onInvalid', 'onReset', 'onSubmit'
        ]
    }
}

EXBUILDER6_COMMON_APIS = {
    'methods': [
        'setValue', 'getValue', 'setText', 'getText', 'enable', 'disable', 'show', 'hide', 'focus', 'blur',
        'setVisible', 'getVisible', 'setEnabled', 'getEnabled', 'setReadOnly', 'getReadOnly',
        'setWidth', 'getWidth', 'setHeight', 'getHeight', 'setStyle', 'getStyle', 'setData', 'getData',
        'refresh', 'clear', 'reset', 'validate', 'isValid', 'getParent', 'getChild', 'getChildren',
        'getSibling', 'getSiblings', 'getRoot', 'getAncestor', 'getDescendant', 'getFirstChild',
        'getLastChild', 'getNextSibling', 'getPreviousSibling', 'addChild', 'removeChild', 'insertChild'
    ],
    'properties': [
        'text', 'value', 'visible', 'enabled', 'readOnly', 'width', 'height', 'style', 'data',
        'name', 'id', 'className', 'tagName', 'parentNode', 'childNodes', 'firstChild', 'lastChild',
        'nextSibling', 'previousSibling', 'nodeType', 'nodeValue', 'nodeName', 'attributes'
    ],
    'events': [
        'onLoad', 'onUnload', 'onClick', 'onDoubleClick', 'onRightClick', 'onMouseDown', 'onMouseUp',
        'onMouseOver', 'onMouseOut', 'onMouseMove', 'onMouseEnter', 'onMouseLeave', 'onFocus', 'onBlur',
        'onKeyDown', 'onKeyUp', 'onKeyPress', 'onChange', 'onSelect', 'onInput', 'onInvalid', 'onReset',
        'onSubmit', 'onError', 'onAbort', 'onLoad', 'onUnload', 'onResize', 'onScroll', 'onContextMenu'
    ]
}

# ============================================================================
# 설정 관리 클래스
# ============================================================================

class ConfigManager:
    def __init__(self, config_path: str = "config/exbuilder6.yaml"):
        self.config_path = Path(config_path)
        self.config = self._load_config()
    
    def _load_config(self) -> Dict:
        """YAML 설정 파일 로드"""
        try:
            if self.config_path.exists():
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    return yaml.safe_load(f)
            else:
                # 기본 설정 반환
                return {
                    'versions': {
                        '6.0': EXBUILDER6_CONTROL_APIS
                    },
                    'current_apis': EXBUILDER6_CONTROL_APIS
                }
        except Exception as e:
            logger.warning(f"설정 파일 로드 실패: {e}, 기본 설정 사용")
            return {
                'versions': {
                    '6.0': EXBUILDER6_CONTROL_APIS
                },
                'current_apis': EXBUILDER6_CONTROL_APIS
            }
    
    def get_api_info(self, version: str = "6.0") -> Dict:
        """버전별 API 정보 반환"""
        return self.config.get('versions', {}).get(version, {})
    
    def update_api_info(self, new_apis: Dict):
        """API 정보 업데이트"""
        self.config['current_apis'] = new_apis

# ============================================================================
# JavaScript 파서 클래스
# ============================================================================

class JavaScriptParser:
    def __init__(self):
        self.in_single_comment = False
        self.in_multi_comment = False
        self.in_string = False
        self.string_delimiter = None
        self.escape_next = False
    
    def clean_code(self, code: str) -> str:
        """주석과 문자열을 고려한 코드 정리"""
        cleaned_lines = []
        
        for line in code.split('\n'):
            cleaned_line = self._clean_line(line)
            if cleaned_line.strip():
                cleaned_lines.append(cleaned_line)
        
        return '\n'.join(cleaned_lines)
    
    def _clean_line(self, line: str) -> str:
        """라인별 정리 (주석 제거, 문자열 보호)"""
        result = []
        i = 0
        
        while i < len(line):
            char = line[i]
            
            # 주석 처리
            if not self.in_string:
                if char == '/' and i + 1 < len(line):
                    if line[i + 1] == '/':
                        break  # 단일 라인 주석
                    elif line[i + 1] == '*':
                        self.in_multi_comment = True
                        i += 2
                        continue
                
                if self.in_multi_comment:
                    if char == '*' and i + 1 < len(line) and line[i + 1] == '/':
                        self.in_multi_comment = False
                        i += 2
                        continue
                    i += 1
                    continue
            
            # 문자열 처리
            if char in ['"', "'", '`']:
                if not self.in_string:
                    self.in_string = True
                    self.string_delimiter = char
                elif char == self.string_delimiter and not self.escape_next:
                    self.in_string = False
                    self.string_delimiter = None
            
            # 이스케이프 처리
            self.escape_next = (char == '\\' and not self.escape_next)
            
            result.append(char)
            i += 1
        
        return ''.join(result)

# ============================================================================
# eXBuilder6 API 검증 클래스
# ============================================================================

class EXBuilder6APIValidator:
    def __init__(self, config_manager: ConfigManager):
        self.config_manager = config_manager
        self.control_patterns = self._load_control_patterns()
        self.dynamic_controls: Dict[str, str] = {}
    
    def _load_control_patterns(self) -> Dict[str, Dict]:
        """설정 파일에서 컨트롤 패턴 로드"""
        return self.config_manager.get_api_info()
    
    def identify_control_type(self, control_id: str) -> str:
        """향상된 컨트롤 타입 식별"""
        # 1. 정확한 prefix 매칭
        for pattern_name in self.control_patterns.keys():
            if control_id.startswith(pattern_name):
                # 추가 검증: 숫자나 특수문자로 이어지는지 확인
                if len(control_id) > len(pattern_name):
                    next_char = control_id[len(pattern_name)]
                    if next_char.isdigit() or next_char == '_':
                        return pattern_name
                else:
                    return pattern_name
        
        # 2. 동적 컨트롤 검사
        return self._check_dynamic_control(control_id)
    
    def _check_dynamic_control(self, control_id: str) -> str:
        """동적 컨트롤 검사"""
        # 동적으로 생성된 컨트롤 ID 패턴 검사
        dynamic_patterns = [
            (r'^grd\d+$', 'grd'),
            (r'^btn\d+$', 'btn'),
            (r'^cmb\d+$', 'cmb'),
            (r'^cbx\d+$', 'cbx'),
            (r'^ipb\d+$', 'ipb'),
        ]
        
        for pattern, control_type in dynamic_patterns:
            if re.match(pattern, control_id):
                return control_type
        
        return 'unknown'
    
    def validate_api_usage(self, var_name: str, method_name: str, 
                          control_type: str) -> List[AnalysisIssue]:
        """API 사용 검증"""
        issues = []
        
        if control_type in self.control_patterns:
            apis = self.control_patterns[control_type]
            
            # 메서드 검증
            if method_name not in apis.get('methods', []):
                # 공통 API 확인
                if method_name not in EXBUILDER6_COMMON_APIS['methods']:
                    issues.append(AnalysisIssue(
                        category='api',
                        severity=IssueSeverity.HIGH,
                        message=f"{control_type} 컨트롤에 '{method_name}' 메서드가 없습니다. "
                                f"사용 가능한 메서드: {', '.join(apis.get('methods', [])[:5])}...",
                        suggestion=f"올바른 메서드를 사용하거나 공통 API를 확인하세요."
                    ))
        
        return issues

# ============================================================================
# 성능 최적화된 분석기 클래스
# ============================================================================

class PerformanceOptimizedAnalyzer:
    def __init__(self):
        self.compiled_patterns = self._compile_patterns()
        self.config_manager = ConfigManager()
        self.api_validator = EXBuilder6APIValidator(self.config_manager)
        self.js_parser = JavaScriptParser()
    
    @lru_cache(maxsize=1000)
    def _compile_patterns(self):
        """정규표현식 패턴 사전 컴파일"""
        compiled = {}
        for category, patterns in ERROR_PATTERNS.items():
            compiled[category] = [
                (re.compile(pattern), message, severity) 
                for pattern, message, severity in patterns
            ]
        return compiled
    
    def create_issue(self, category: str, severity: IssueSeverity, message: str,
                    line_number: int = None, suggestion: str = None) -> AnalysisIssue:
        """이슈 객체 생성 헬퍼"""
        # 심각도에 따른 우선순위 설정
        priority_map = {
            IssueSeverity.CRITICAL: 'HIGH',
            IssueSeverity.HIGH: 'HIGH',
            IssueSeverity.MEDIUM: 'MEDIUM',
            IssueSeverity.LOW: 'LOW',
            IssueSeverity.INFO: 'LOW'
        }
        
        return AnalysisIssue(
            category=category,
            severity=severity,
            message=message,
            line_number=line_number,
            suggestion=suggestion,
            priority=priority_map.get(severity, 'MEDIUM')
        )
    
    def check_errors_optimized(self, code: str) -> List[AnalysisIssue]:
        """최적화된 오류 검사"""
        issues = []
        
        for category, patterns in self.compiled_patterns.items():
            for pattern, message, severity in patterns:
                matches = pattern.finditer(code)
                for match in matches:
                    # 라인 번호 계산
                    line_number = code[:match.start()].count('\n') + 1
                    column = match.start() - code.rfind('\n', 0, match.start()) - 1
                    
                    issues.append(self.create_issue(
                        category=category,
                        severity=severity,
                        message=message,
                        line_number=line_number,
                        suggestion=self._get_suggestion(category, message)
                    ))
        
        return issues
    
    def _get_suggestion(self, category: str, message: str) -> str:
        """카테고리별 제안사항"""
        suggestions = {
            'syntax_errors': '변수 선언 키워드를 올바르게 사용하고, 재귀 함수나 자기 참조를 피하세요.',
            'variable_scope_issues': 'let/const를 사용하고, 스코프 문제를 방지하세요.',
            'null_reference': 'null 체크를 추가하거나 옵셔널 체이닝(?.)을 사용하세요.',
            'xss_security': 'innerText나 textContent를 사용하거나 입력값을 sanitize하세요.',
            'json_parsing': 'try-catch 블록으로 감싸서 예외 처리를 하세요.',
            'array_operations': '배열이 null이 아닌지 확인하거나 기본값을 설정하세요.',
            'string_operations': '인덱스 범위를 확인하거나 안전한 메서드를 사용하세요.',
            'comparison_issues': '엄격한 비교 연산자(===, !==)를 사용하세요.',
            'performance_issues': '프로덕션에서는 console.log를 제거하고 무한 루프를 방지하세요.',
            'error_handling': '적절한 에러 처리 로직을 추가하세요.',
            'unnecessary_code': '불필요한 코드를 제거하세요.',
            'async_issues': 'async/await 사용시 try-catch로 감싸고 적절한 에러 처리를 하세요.',
            'memory_leaks': '이벤트 리스너나 타이머를 적절히 정리하세요.',
            'type_safety': '타입 체크 후 적절한 처리를 추가하세요.',
            'code_style': '코드 스타일 가이드를 따르고 가독성을 높이세요.',
            'api': 'eXBuilder6 API 문서를 확인하고 올바른 메서드명을 사용하세요.'
        }
        return suggestions.get(category, '코드를 검토하고 개선하세요.')
    
    def check_javascript_syntax(self, code: str) -> List[AnalysisIssue]:
        """JavaScript 문법 검사"""
        issues = []
        lines = code.split('\n')
        
        # 괄호 균형 검사
        brackets = {'(': ')', '{': '}', '[': ']'}
        stack = []
        
        for line_num, line in enumerate(lines, 1):
            for char_pos, char in enumerate(line):
                if char in brackets:
                    stack.append((char, line_num, char_pos + 1))
                elif char in brackets.values():
                    if not stack:
                        issues.append(self.create_issue(
                            category='syntax',
                            severity=IssueSeverity.HIGH,
                            message=f"닫는 괄호 '{char}'가 열리는 괄호보다 많습니다",
                            line_number=line_num
                        ))
                        break
                    open_bracket, open_line, open_pos = stack.pop()
                    if brackets[open_bracket] != char:
                        issues.append(self.create_issue(
                            category='syntax',
                            severity=IssueSeverity.HIGH,
                            message=f"괄호 '{char}'가 라인 {open_line}의 '{open_bracket}'와 매칭되지 않습니다",
                            line_number=line_num
                        ))
                        break
        
        if stack:
            for bracket, line_num, char_pos in stack:
                issues.append(self.create_issue(
                    category='syntax',
                    severity=IssueSeverity.HIGH,
                    message=f"열린 괄호 '{bracket}'가 닫히지 않았습니다",
                    line_number=line_num
                ))
        
        # 추가 문법 검사
        issues.extend(self._check_additional_syntax(code))
        
        return issues
    
    def _check_additional_syntax(self, code: str) -> List[AnalysisIssue]:
        """추가 문법 검사"""
        issues = []
        
        # 세미콜론 누락 검사
        semicolon_pattern = r'([^;{}])\s*\n\s*([a-zA-Z_$])'
        for match in re.finditer(semicolon_pattern, code):
            line_num = code[:match.start()].count('\n') + 1
            issues.append(self.create_issue(
                category='code_style',
                severity=IssueSeverity.LOW,
                message="세미콜론이 누락되었습니다",
                line_number=line_num
            ))
        
        # 중복 변수 선언 검사
        var_pattern = r'var\s+(\w+)'
        declared_vars = {}
        for match in re.finditer(var_pattern, code):
            var_name = match.group(1)
            line_num = code[:match.start()].count('\n') + 1
            if var_name in declared_vars:
                issues.append(self.create_issue(
                    category='variable_scope_issues',
                    severity=IssueSeverity.MEDIUM,
                    message=f"변수 '{var_name}'가 중복 선언되었습니다",
                    line_number=line_num
                ))
            else:
                declared_vars[var_name] = line_num
        
        # 미사용 변수 검사
        for var_name, line_num in declared_vars.items():
            usage_pattern = rf'\b{var_name}\b(?!\s*=)'
            if not re.search(usage_pattern, code[code.find('\n', code.find(var_name)):]):
                issues.append(self.create_issue(
                    category='unnecessary_code',
                    severity=IssueSeverity.LOW,
                    message=f"선언된 변수 '{var_name}'가 사용되지 않습니다",
                    line_number=line_num
                ))
        
        return issues
    
    def check_exbuilder6_apis(self, code: str) -> List[AnalysisIssue]:
        """eXBuilder6 API 검사"""
        issues = []
        
        # app.lookup으로 찾은 컨트롤들의 변수명과 타입 매핑
        variable_controls = {}
        
        # app.lookup 패턴 찾기 (ar, var, let, const 모두 포함)
        lookup_patterns = [
            r'(?:ar|var|let|const)\s+(\w+)\s*=\s*app\.lookup\([\'"]([^\'"]+)[\'"]\)',
            r'(\w+)\s*=\s*app\.lookup\([\'"]([^\'"]+)[\'"]\)'
        ]
        
        for pattern in lookup_patterns:
            lookup_matches = re.findall(pattern, code)
            for var_name, control_id in lookup_matches:
                control_type = self.api_validator.identify_control_type(control_id)
                if control_type != 'unknown':
                    variable_controls[var_name] = control_type
        
        # 메서드 호출 패턴 찾기 (오타 감지 포함)
        method_pattern = r'(\w+)\.(\w+)\('
        method_matches = re.findall(method_pattern, code)
        
        for var_name, method_name in method_matches:
            if method_name == 'lookup':
                continue
                
            if var_name in variable_controls:
                control_type = variable_controls[var_name]
                api_issues = self.api_validator.validate_api_usage(var_name, method_name, control_type)
                issues.extend(api_issues)
            else:
                # app.lookup으로 찾지 못한 변수에 대한 메서드 호출도 검사
                # 일반적인 eXBuilder6 API 패턴과 비교
                common_apis = EXBUILDER6_COMMON_APIS['methods']
                if method_name not in common_apis:
                    # 오타 가능성이 있는 API 이름 찾기
                    similar_apis = self._find_similar_api(method_name, common_apis)
                    if similar_apis:
                        issues.append(self.create_issue(
                            category='api',
                            severity=IssueSeverity.HIGH,
                            message=f"잘못된 API 호출: '{method_name}' 메서드가 존재하지 않습니다. "
                                    f"유사한 API: {', '.join(similar_apis[:3])}",
                            suggestion=f"올바른 API 이름을 확인하세요. 제안: {similar_apis[0] if similar_apis else 'API 문서 확인'}"
                        ))
        
        return issues
    
    def _find_similar_api(self, method_name: str, api_list: List[str]) -> List[str]:
        """유사한 API 이름 찾기 (오타 감지용)"""
        similar_apis = []
        
        for api in api_list:
            # 정확한 매칭
            if api == method_name:
                return []
            
            # 유사도 계산 (간단한 방법)
            if len(api) >= len(method_name) - 2 and len(api) <= len(method_name) + 2:
                # 공통 문자 수 계산
                common_chars = sum(1 for c in method_name if c in api)
                similarity = common_chars / max(len(method_name), len(api))
                
                if similarity >= 0.7:  # 70% 이상 유사
                    similar_apis.append(api)
        
        # 유사도 순으로 정렬
        similar_apis.sort(key=lambda x: sum(1 for c in method_name if c in x), reverse=True)
        return similar_apis
    
    async def analyze_async(self, code: str) -> Dict:
        """비동기 분석"""
        tasks = []
        
        # 병렬로 각 분석 수행
        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor(max_workers=4) as executor:
            tasks.extend([
                loop.run_in_executor(executor, self.check_javascript_syntax, code),
                loop.run_in_executor(executor, self.check_exbuilder6_apis, code),
                loop.run_in_executor(executor, self.check_errors_optimized, code),
                loop.run_in_executor(executor, self.analyze_execution_flow, code)
            ])
        
        results = await asyncio.gather(*tasks)
        
        return {
            'syntax': results[0],
            'apis': results[1], 
            'errors': results[2],
            'flow': results[3]
        }
    
    def analyze_execution_flow(self, code: str) -> List[str]:
        """실행 흐름 분석"""
        flow = []
        
        # 함수별로 분석
        functions = re.findall(r'function\s+(\w+)\s*\([^)]*\)\s*\{([^}]+)\}', code, re.DOTALL)
        if functions:
            for func_name, func_body in functions:
                process_description = self._analyze_function_process(func_name, func_body)
                flow.append(process_description)
        
        # 이벤트 핸들러 찾기
        event_handlers = re.findall(r'this\.(on\w+)\s*=', code)
        if event_handlers:
            flow.append(f"이벤트 핸들러: {', '.join(event_handlers)}")
        
        # 비동기 작업 찾기
        async_matches = re.findall(r'(setTimeout|setInterval|fetch|Promise|async|await)', code)
        if async_matches:
            unique_async = list(set(async_matches))
            flow.append(f"비동기 작업: {', '.join(unique_async)}")
        
        return flow if flow else ['간단한 순차적 실행 프로세스']
    
    def _analyze_function_process(self, func_name: str, func_body: str) -> str:
        """함수의 프로세스를 분석하여 설명 생성"""
        purpose = self._analyze_function_purpose(func_name)
        operations = []
        
        # 주요 작업 분석
        if 'app.lookup' in func_body:
            operations.append("컨트롤 객체를 찾습니다")
        if any(keyword in func_body for keyword in ['file', 'files', 'addFileParameter']):
            operations.append("파일 처리를 수행합니다")
        if any(keyword in func_body for keyword in ['data', 'setData', 'getData']):
            operations.append("데이터를 처리합니다")
        if 'if' in func_body:
            operations.append("조건에 따라 분기합니다")
        if any(keyword in func_body for keyword in ['for', 'while', 'do']):
            operations.append("반복 작업을 수행합니다")
        
        if operations:
            return f"{func_name} 함수: {purpose} - {', '.join(operations)}"
        else:
            return f"{func_name} 함수: {purpose} - 기본 작업을 수행합니다"
    
    def _analyze_function_purpose(self, func_name: str) -> str:
        """함수명을 분석하여 목적 추정"""
        func_name_lower = func_name.lower()
        
        if 'onload' in func_name_lower or 'init' in func_name_lower:
            return "초기화"
        elif 'click' in func_name_lower:
            return "클릭 이벤트 처리"
        elif 'change' in func_name_lower:
            return "값 변경 이벤트 처리"
        elif 'file' in func_name_lower:
            return "파일 처리"
        elif 'data' in func_name_lower:
            return "데이터 처리"
        elif 'submit' in func_name_lower:
            return "제출 처리"
        elif 'validate' in func_name_lower:
            return "유효성 검사"
        elif 'save' in func_name_lower:
            return "저장 처리"
        elif 'delete' in func_name_lower:
            return "삭제 처리"
        elif 'update' in func_name_lower:
            return "업데이트 처리"
        elif 'add' in func_name_lower:
            return "추가 처리"
        elif 'remove' in func_name_lower:
            return "제거 처리"
        else:
            return "일반 처리"

# ============================================================================
# 에러 처리 및 로깅
# ============================================================================

@contextmanager
def error_context(operation: str):
    """에러 컨텍스트 관리"""
    try:
        logger.info(f"Starting {operation}")
        yield
        logger.info(f"Completed {operation}")
    except Exception as e:
        logger.error(f"Error in {operation}: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"{operation} 중 오류 발생: {str(e)}"
        )

# ============================================================================
# API 엔드포인트
# ============================================================================

@router.post("/analyze", response_model=EnhancedJavaScriptAnalysisResponse)
async def analyze_javascript_enhanced(request: JavaScriptAnalysisRequest):
    """향상된 JavaScript 분석"""
    with error_context("JavaScript 분석"):
        analyzer = PerformanceOptimizedAnalyzer()
        results = await analyzer.analyze_async(request.code)
        
        # 모든 이슈 통합
        all_issues = []
        all_issues.extend(results['syntax'])
        all_issues.extend(results['apis'])
        all_issues.extend(results['errors'])
        
        # 통계 계산
        statistics = {
            'total_issues': len(all_issues),
            'syntax_issues': len(results['syntax']),
            'api_issues': len(results['apis']),
            'error_issues': len(results['errors']),
            'critical_issues': len([i for i in all_issues if i.severity == IssueSeverity.CRITICAL]),
            'high_issues': len([i for i in all_issues if i.severity == IssueSeverity.HIGH]),
            'medium_issues': len([i for i in all_issues if i.severity == IssueSeverity.MEDIUM]),
            'low_issues': len([i for i in all_issues if i.severity == IssueSeverity.LOW])
        }
        
        # 권장사항 생성
        recommendations = []
        if statistics['critical_issues'] > 0:
            recommendations.append("보안 위험이 있는 코드를 즉시 수정하세요.")
        if statistics['high_issues'] > 0:
            recommendations.append("높은 우선순위 이슈들을 우선적으로 해결하세요.")
        if statistics['syntax_issues'] > 0:
            recommendations.append("문법 오류를 수정하여 코드 실행을 보장하세요.")
        if statistics['api_issues'] > 0:
            recommendations.append("eXBuilder6 API 사용법을 확인하고 올바른 메서드를 사용하세요.")
        
        if not recommendations:
            recommendations.append("코드 품질이 양호합니다. 계속해서 좋은 코딩 관례를 유지하세요.")
        
        return EnhancedJavaScriptAnalysisResponse(
            issues=all_issues,
            statistics=statistics,
            execution_flow=results['flow'],
            recommendations=recommendations
        )

@router.post("/analyze/file")
async def analyze_javascript_file_enhanced(file: UploadFile = File(...), fast_mode: bool = False):
    """향상된 JavaScript 파일 분석"""
    with error_context("파일 분석"):
        if not file.filename.endswith('.js'):
            raise HTTPException(status_code=400, detail="JavaScript 파일(.js)만 업로드 가능합니다.")
        
        content = await file.read()
        code = content.decode('utf-8')
        
        analyzer = PerformanceOptimizedAnalyzer()
        results = await analyzer.analyze_async(code)
        
        # 결과 통합
        all_issues = []
        all_issues.extend(results['syntax'])
        all_issues.extend(results['apis'])
        all_issues.extend(results['errors'])
        
        return {
            "file_name": file.filename,
            "file_size": len(content),
            "issues": all_issues,
            "execution_flow": results['flow']
        }

@router.post("/analyze/detailed")
async def analyze_javascript_detailed_enhanced(request: JavaScriptAnalysisRequest):
    """상세한 JavaScript 코드 분석 (LLM 포함)"""
    with error_context("상세 분석"):
        # 기본 분석
        analyzer = PerformanceOptimizedAnalyzer()
        basic_results = await analyzer.analyze_async(request.code)
        
        # 결과 통합
        all_issues = []
        all_issues.extend(basic_results['syntax'])
        all_issues.extend(basic_results['apis'])
        all_issues.extend(basic_results['errors'])
        
        # 통계 생성
        statistics = {
            'total_issues': len(all_issues),
            'syntax_issues': len(basic_results['syntax']),
            'api_issues': len(basic_results['apis']),
            'error_issues': len(basic_results['errors']),
            'critical_issues': len([i for i in all_issues if i.severity == IssueSeverity.CRITICAL]),
            'high_priority_issues': len([i for i in all_issues if i.severity == IssueSeverity.HIGH]),
            'medium_priority_issues': len([i for i in all_issues if i.severity == IssueSeverity.MEDIUM]),
            'low_priority_issues': len([i for i in all_issues if i.severity == IssueSeverity.LOW])
        }
        
        # 권장사항 생성
        recommendations = []
        if statistics['critical_issues'] > 0:
            recommendations.append("보안 위험이 있는 코드를 즉시 수정하세요.")
        if statistics['high_priority_issues'] > 0:
            recommendations.append("높은 우선순위 이슈들을 우선적으로 해결하세요.")
        if statistics['syntax_issues'] > 0:
            recommendations.append("문법 오류를 수정하여 코드 실행을 보장하세요.")
        if statistics['api_issues'] > 0:
            recommendations.append("eXBuilder6 API 사용법을 확인하고 올바른 메서드를 사용하세요.")
        
        if not recommendations:
            recommendations.append("코드 품질이 양호합니다. 계속해서 좋은 코딩 관례를 유지하세요.")
        
        # LLM 분석
        try:
            llm_result = analyze_with_llm(request.code, request.fast_mode)
            llm_analysis = llm_result.get("llm_analysis", "LLM 분석 결과를 가져올 수 없습니다.")
        except Exception as e:
            llm_analysis = f"LLM 분석 실패: {str(e)}"
        
        return EnhancedJavaScriptAnalysisResponse(
            issues=all_issues,
            statistics=statistics,
            execution_flow=basic_results['flow'],
            recommendations=recommendations,
            llm_analysis=llm_analysis
        )

def analyze_with_llm(code: str, fast_mode: bool = False) -> Dict[str, Any]:
    """LM Studio를 사용한 고급 분석"""
    prompt = f"""JavaScript 코드를 다음 4가지 항목으로 분석해주세요:

**분석할 코드:**
```javascript
{code}
```

**분석 요청:**
1. JavaScript 문법/로직 문제점 (구체적인 라인 번호와 함께)
2. eXBuilder6 API 사용 여부 (사용된 API 목록 및 잘못된 사용 여부)
3. 잠재적 오류 및 보안 위험 요소
4. 실행 흐름 (단계별 상세 과정 - 스토리텔링 방식)

발견된 문제가 없으면 "발견된 문제점 없음"으로 표시하세요."""

    try:
        result = request_llm_fast(prompt) if fast_mode else request_llm(prompt)
        return {"llm_analysis": result}
    except Exception as e:
        return {"llm_analysis": f"LLM 분석 중 오류 발생: {str(e)}"}
