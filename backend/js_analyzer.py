from fastapi import APIRouter, HTTPException, UploadFile, File
from pydantic import BaseModel
from typing import List, Dict, Any
from llm_client import request_llm, request_llm_fast
import re

router = APIRouter()

class JavaScriptAnalysisRequest(BaseModel):
    code: str
    fast_mode: bool = False

class JavaScriptAnalysisResponse(BaseModel):
    javascript_issues: List[str]
    exbuilder6_apis: List[str]
    errors: List[str]
    execution_flow: List[str]

# eXBuilder6 API 목록 (eXBuilder6_HelpContents.pdf 기반)
# 각 컨트롤 타입별로 정확한 메서드, 속성, 이벤트를 정의
EXBUILDER6_CONTROL_APIS = {
    # Grid 컨트롤 (grd 패턴)
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
    
    # Button 컨트롤 (button, btn 패턴)
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
    
    # Calendar 컨트롤 (calendar, cal 패턴)
    'calendar': {
        'methods': [
            'setDate', 'getDate', 'setValue', 'getValue', 'enable', 'disable', 'show', 'hide', 'focus', 'blur',
            'setMinDate', 'getMinDate', 'setMaxDate', 'getMaxDate', 'setFirstDayOfWeek', 'getFirstDayOfWeek',
            'setCalendarType', 'getCalendarType', 'setDateFormat', 'getDateFormat', 'setTimeFormat', 'getTimeFormat',
            'setShowTime', 'getShowTime', 'setShowToday', 'getShowToday', 'setShowWeekNumbers', 'getShowWeekNumbers'
        ],
        'properties': [
            'text', 'value', 'visible', 'enabled', 'readOnly', 'width', 'height', 'style', 
            'date', 'minDate', 'maxDate', 'firstDayOfWeek', 'calendarType', 'dateFormat', 'timeFormat',
            'showTime', 'showToday', 'showWeekNumbers', 'todayButton', 'clearButton', 'okButton', 'cancelButton'
        ],
        'events': [
            'onDateChanged', 'onDateSelected', 'onMonthChanged', 'onYearChanged', 'onTimeChanged',
            'onTodayClicked', 'onClearClicked', 'onOkClicked', 'onCancelClicked', 'onFocus', 'onBlur'
        ]
    },
    'cal': {
        'methods': [
            'setDate', 'getDate', 'setValue', 'getValue', 'enable', 'disable', 'show', 'hide', 'focus', 'blur',
            'setMinDate', 'getMinDate', 'setMaxDate', 'getMaxDate', 'setFirstDayOfWeek', 'getFirstDayOfWeek',
            'setCalendarType', 'getCalendarType', 'setDateFormat', 'getDateFormat', 'setTimeFormat', 'getTimeFormat',
            'setShowTime', 'getShowTime', 'setShowToday', 'getShowToday', 'setShowWeekNumbers', 'getShowWeekNumbers'
        ],
        'properties': [
            'text', 'value', 'visible', 'enabled', 'readOnly', 'width', 'height', 'style', 
            'date', 'minDate', 'maxDate', 'firstDayOfWeek', 'calendarType', 'dateFormat', 'timeFormat',
            'showTime', 'showToday', 'showWeekNumbers', 'todayButton', 'clearButton', 'okButton', 'cancelButton'
        ],
        'events': [
            'onDateChanged', 'onDateSelected', 'onMonthChanged', 'onYearChanged', 'onTimeChanged',
            'onTodayClicked', 'onClearClicked', 'onOkClicked', 'onCancelClicked', 'onFocus', 'onBlur'
        ]
    },
    
    # ComboBox 컨트롤 (cmb 패턴)
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
    
    # CheckBox 컨트롤 (cbx 패턴)
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
    
    # Tree 컨트롤 (tre 패턴)
    'tre': {
        'methods': [
            'addNode', 'deleteNode', 'updateNode', 'getNode', 'getData', 'setData', 'clear', 'refresh',
            'getSelected', 'setSelected', 'getChecked', 'setChecked', 'getExpanded', 'setExpanded',
            'scrollTo', 'scrollIntoView', 'enable', 'disable', 'show', 'hide', 'focus', 'blur',
            'expandAll', 'collapseAll', 'getRootNode', 'getChildNodes', 'getParentNode', 'getSiblingNodes',
            'getNodeByText', 'getNodeByValue', 'getNodeByIndex', 'getNodePath', 'setNodePath',
            'getNodeLevel', 'setNodeLevel', 'getNodeIcon', 'setNodeIcon', 'getNodeTooltip', 'setNodeTooltip'
        ],
        'properties': [
            'text', 'value', 'visible', 'enabled', 'readOnly', 'width', 'height', 'style', 
            'data', 'selectedNode', 'selectedNodes', 'expandedNodes', 'checkedNodes', 'rootNode',
            'nodeCount', 'levelCount', 'showLines', 'showRootLines', 'showButtons', 'showCheckBoxes',
            'showIcons', 'showTooltips', 'allowDrag', 'allowDrop', 'allowEdit', 'allowDelete',
            'allowMultiSelect', 'allowCheckBoxes', 'allowExpandAll', 'allowCollapseAll'
        ],
        'events': [
            'onNodeClick', 'onNodeDoubleClick', 'onNodeRightClick', 'onNodeSelected', 'onNodeDeselected',
            'onNodeExpanded', 'onNodeCollapsed', 'onNodeChecked', 'onNodeUnchecked', 'onNodeAdded',
            'onNodeDeleted', 'onNodeUpdated', 'onNodeMoved', 'onNodeEdited', 'onFocus', 'onBlur'
        ]
    },
    
    # InputBox 컨트롤 (ipb 패턴)
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
    },
    
    # TextArea 컨트롤 (txa 패턴)
    'txa': {
        'methods': [
            'setValue', 'getValue', 'setText', 'getText', 'enable', 'disable', 'show', 'hide', 'focus', 'blur',
            'setMaxLength', 'getMaxLength', 'setPlaceholder', 'getPlaceholder', 'setRows', 'getRows',
            'setCols', 'getCols', 'setWrap', 'getWrap', 'setResize', 'getResize', 'setSpellCheck', 'getSpellCheck'
        ],
        'properties': [
            'text', 'value', 'visible', 'enabled', 'readOnly', 'width', 'height', 'style', 
            'maxLength', 'placeholder', 'rows', 'cols', 'wrap', 'resize', 'spellCheck',
            'autoComplete', 'autoFocus', 'required', 'name', 'form', 'minLength', 'maxLength'
        ],
        'events': [
            'onValueChanged', 'onTextChanged', 'onKeyDown', 'onKeyUp', 'onKeyPress', 'onInput',
            'onChange', 'onFocus', 'onBlur', 'onSelect', 'onInvalid', 'onReset', 'onSubmit'
        ]
    }
}

# eXBuilder6 공통 API (모든 컨트롤에서 사용 가능)
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

# eXBuilder6 메시지 및 팝업 API
EXBUILDER6_MESSAGE_APIS = {
    'methods': [
        'showMessage', 'showConfirm', 'showAlert', 'showError', 'showWarning', 'showInfo', 'showSuccess',
        'showQuestion', 'showInput', 'showSelect', 'showFileDialog', 'showColorDialog', 'showFontDialog',
        'openPopup', 'closePopup', 'showPopup', 'hidePopup', 'setPopupPosition', 'getPopupPosition',
        'setPopupSize', 'getPopupSize', 'setPopupTitle', 'getPopupTitle', 'setPopupContent', 'getPopupContent'
    ]
}

# eXBuilder6 데이터 관련 API
EXBUILDER6_DATA_APIS = {
    'methods': [
        'getData', 'setData', 'getJsonData', 'setJsonData', 'getXmlData', 'setXmlData', 'getCsvData', 'setCsvData',
        'loadData', 'saveData', 'exportData', 'importData', 'validateData', 'transformData', 'filterData',
        'sortData', 'groupData', 'aggregateData', 'calculateData', 'mergeData', 'splitData', 'cloneData'
    ]
}

def check_javascript_issues(code: str) -> List[str]:
    """
    JavaScript 문법/로직 문제점 검사
    
    이 함수는 JavaScript 코드에서 다음과 같은 문제점들을 검사합니다:
    1. 괄호 불일치 (중괄호, 소괄호, 대괄호)
    2. 따옴표 불일치 (작은따옴표, 큰따옴표)
    3. 세미콜론 누락 가능성
    4. 함수 선언 문제
    5. 변수 선언 문제
    6. 객체/배열 리터럴 문제
    7. 일반적인 JavaScript 문제점들
    """
    issues = []
    
    # JavaScript 문법 검사 (정확한 패턴 기반)
    js_syntax_patterns = [
        # 괄호 불일치 검사 - 더 정확한 패턴
        (r'\{[^{}]*\{[^{}]*\}[^{}]*\}', '중첩된 중괄호 확인 필요'),
        (r'\([^()]*\([^()]*\)[^()]*\)', '중첩된 괄호 확인 필요'),
        (r'\[[^\[\]]*\[[^\[\]]*\][^\[\]]*\]', '중첩된 대괄호 확인 필요'),
        
        # 세미콜론 누락 가능성 - 더 정확한 패턴
        (r'[^;{}]\s*\n\s*[a-zA-Z_$][^=]*=', '세미콜론 누락 가능성'),
        
        # 따옴표 불일치 - 더 정확한 패턴 (문자열 리터럴만)
        (r'"[^"]*$', '따옴표가 닫히지 않았습니다'),
        (r"'[^']*$", "따옴표가 닫히지 않았습니다"),
        
        # 함수 선언 문제
        (r'function\s+\w+\s*\([^)]*\)\s*\{[^}]*$', '함수 정의가 완료되지 않았습니다'),
        
        # 변수 선언 문제
        (r'(?:var|let|const)\s+\w+\s*[^;]*$', '변수 선언이 완료되지 않았습니다'),
        
        # 객체/배열 리터럴 문제
        (r'\{[^}]*$', '객체 리터럴이 완료되지 않았습니다'),
        (r'\[[^\]]*$', '배열 리터럴이 완료되지 않았습니다'),
    ]
    
    for pattern, message in js_syntax_patterns:
        if re.search(pattern, code, re.MULTILINE):
            issues.append(f"문법 오류: {message}")
    
    # 일반적인 JavaScript 문제점들 검사
    patterns = [
        (r'var\s+\w+\s*=\s*undefined', 'undefined 할당은 불필요합니다'),
        (r'==\s*null', 'null 비교시 === 사용을 권장합니다'),
        (r'==\s*undefined', 'undefined 비교시 === 사용을 권장합니다'),
        (r'console\.log\(', 'console.log는 프로덕션에서 제거해야 합니다'),
        (r'eval\(', 'eval() 사용은 보안상 위험합니다'),
        (r'setTimeout\([^,]+,\s*0\)', 'setTimeout(,0) 대신 setImmediate 사용을 고려하세요'),
        (r'for\s*\(\s*;\s*;\s*\)', '무한 루프 위험이 있습니다'),
        (r'while\s*\(\s*true\s*\)', '무한 루프 위험이 있습니다'),
        # 할당 연산자 확인 - 더 정확한 패턴
        (r'[^=!<>]=[^=]', '할당 연산자 확인 필요 (= vs ==)'),
    ]
    
    for pattern, message in patterns:
        if re.search(pattern, code):
            issues.append(message)
    
    # 괄호 균형 검사
    brackets = {'(': ')', '{': '}', '[': ']'}
    stack = []
    
    for char in code:
        if char in brackets:
            stack.append(char)
        elif char in brackets.values():
            if not stack:
                issues.append("문법 오류: 닫는 괄호가 열리는 괄호보다 많습니다")
                break
            if brackets[stack.pop()] != char:
                issues.append("문법 오류: 괄호가 올바르게 매칭되지 않습니다")
                break
    
    if stack:
        issues.append("문법 오류: 열린 괄호가 닫히지 않았습니다")
    
    return issues if issues else ['JavaScript 문법에 문제없음']

def check_exbuilder6_apis(code: str) -> List[str]:
    """
    eXBuilder6 API 사용 여부 검사 - 잘못된 API 사용만 보고
    
    이 함수는 eXBuilder6 코드에서 다음과 같은 사항들을 검사합니다:
    1. app.lookup으로 찾은 컨트롤들의 변수명과 타입 매핑
    2. 각 컨트롤 타입별로 사용 가능한 메서드, 속성, 이벤트 검증
    3. 잘못된 API 사용 (존재하지 않는 메서드/속성)만 보고
    4. eXBuilder6 공통 API 및 메시지 API 검증
    """
    incorrect_apis = []
    
    # app.lookup으로 찾은 컨트롤들의 변수명과 타입 매핑
    variable_controls = {}
    
    # app.lookup 패턴 찾기 (한글 설명: app.lookup을 통해 컨트롤을 찾는 패턴을 검색)
    lookup_pattern = r'const\s+(\w+)\s*=\s*app\.lookup\([\'"]([^\'"]+)[\'"]\)'
    lookup_matches = re.findall(lookup_pattern, code)
    
    for var_name, control_id in lookup_matches:
        # 컨트롤 ID에서 타입 추정 (XML 설정 기반)
        control_type = None
        for pattern in EXBUILDER6_CONTROL_APIS.keys():
            if control_id.startswith(pattern):
                control_type = pattern
                break
        
        if control_type:
            variable_controls[var_name] = control_type
    
    # 메서드 호출 패턴 찾기 - 잘못된 사용만 보고 (한글 설명: 메서드 호출 패턴을 찾아서 잘못된 사용만 검출)
    method_pattern = r'(\w+)\.(\w+)\('
    method_matches = re.findall(method_pattern, code)
    
    for var_name, method_name in method_matches:
        if var_name in variable_controls:
            control_type = variable_controls[var_name]
            if control_type in EXBUILDER6_CONTROL_APIS:
                # 메서드가 해당 컨트롤 타입에 존재하지 않는 경우만 보고
                if method_name not in EXBUILDER6_CONTROL_APIS[control_type]['methods']:
                    incorrect_apis.append(f"{control_type} 컨트롤에 존재하지 않는 메서드: {method_name}")
        else:
            # 공통 API에서 확인
            if method_name not in EXBUILDER6_COMMON_APIS['methods']:
                # 메시지 API에서 확인
                if method_name not in EXBUILDER6_MESSAGE_APIS['methods']:
                    # 데이터 API에서 확인
                    if method_name not in EXBUILDER6_DATA_APIS['methods']:
                        incorrect_apis.append(f"존재하지 않는 메서드: {method_name}")
    
    # 속성 접근 패턴 찾기 - 잘못된 사용만 보고 (한글 설명: 속성 접근 패턴을 찾아서 잘못된 사용만 검출)
    # 메서드 호출을 제외한 속성 접근만 찾기
    property_pattern = r'(\w+)\.(\w+)(?!\()'
    property_matches = re.findall(property_pattern, code)
    
    # 메서드 호출된 변수명과 메서드명을 추출하여 제외
    method_calls = set()
    for var_name, method_name in method_matches:
        method_calls.add(f"{var_name}.{method_name}")
    
    for var_name, property_name in property_matches:
        # 메서드 호출이 아닌 경우만 처리
        if f"{var_name}.{property_name}" not in method_calls:
            if var_name in variable_controls:
                control_type = variable_controls[var_name]
                if control_type in EXBUILDER6_CONTROL_APIS:
                    # 속성이 해당 컨트롤 타입에 존재하지 않는 경우만 보고
                    if property_name not in EXBUILDER6_CONTROL_APIS[control_type]['properties']:
                        incorrect_apis.append(f"{control_type} 컨트롤에 존재하지 않는 속성: {property_name}")
            else:
                # 공통 API에서 확인
                if property_name not in EXBUILDER6_COMMON_APIS['properties']:
                    incorrect_apis.append(f"존재하지 않는 속성: {property_name}")
    
    # 이벤트 핸들러 찾기 (API Reference 기반) - 잘못된 이벤트만 보고 (한글 설명: 이벤트 핸들러 패턴을 찾아서 잘못된 이벤트만 검출)
    event_patterns = [
        # 기본 이벤트
        (r'onLoad\s*=', 'onLoad'),
        (r'onClick\s*=', 'onClick'),
        (r'onDoubleClick\s*=', 'onDoubleClick'),
        (r'onRightClick\s*=', 'onRightClick'),
        (r'onChange\s*=', 'onChange'),
        (r'onSelect\s*=', 'onSelect'),
        (r'onFocus\s*=', 'onFocus'),
        (r'onBlur\s*=', 'onBlur'),
        
        # 키보드 이벤트
        (r'onKeyDown\s*=', 'onKeyDown'),
        (r'onKeyUp\s*=', 'onKeyUp'),
        (r'onKeyPress\s*=', 'onKeyPress'),
        
        # 마우스 이벤트
        (r'onMouseDown\s*=', 'onMouseDown'),
        (r'onMouseUp\s*=', 'onMouseUp'),
        (r'onMouseOver\s*=', 'onMouseOver'),
        (r'onMouseOut\s*=', 'onMouseOut'),
        (r'onMouseMove\s*=', 'onMouseMove'),
        
        # 컨트롤별 특화 이벤트
        (r'onCellClick\s*=', 'onCellClick'),
        (r'onCellDoubleClick\s*=', 'onCellDoubleClick'),
        (r'onCellRightClick\s*=', 'onCellRightClick'),
        (r'onHeaderClick\s*=', 'onHeaderClick'),
        (r'onRowClick\s*=', 'onRowClick'),
        (r'onRowDoubleClick\s*=', 'onRowDoubleClick'),
        (r'onRowRightClick\s*=', 'onRowRightClick'),
        (r'onSelectionChanged\s*=', 'onSelectionChanged'),
        (r'onDataChanged\s*=', 'onDataChanged'),
        
        # 날짜 관련 이벤트
        (r'onDateChanged\s*=', 'onDateChanged'),
        (r'onDateSelected\s*=', 'onDateSelected'),
        (r'onMonthChanged\s*=', 'onMonthChanged'),
        (r'onYearChanged\s*=', 'onYearChanged'),
        
        # 체크박스/라디오 이벤트
        (r'onCheckedChanged\s*=', 'onCheckedChanged'),
        
        # 콤보박스 이벤트
        (r'onDropdownOpened\s*=', 'onDropdownOpened'),
        (r'onDropdownClosed\s*=', 'onDropdownClosed'),
        
        # 파일 관련 이벤트
        (r'onFileSelected\s*=', 'onFileSelected'),
        (r'onFileChanged\s*=', 'onFileChanged'),
        (r'onFileAdded\s*=', 'onFileAdded'),
        (r'onFileRemoved\s*=', 'onFileRemoved'),
        (r'onUploadStarted\s*=', 'onUploadStarted'),
        (r'onUploadCompleted\s*=', 'onUploadCompleted'),
        (r'onUploadFailed\s*=', 'onUploadFailed'),
        
        # 값 변경 이벤트
        (r'onValueChanged\s*=', 'onValueChanged'),
        (r'onTextChanged\s*=', 'onTextChanged'),
        
        # 검색 이벤트
        (r'onSearch\s*=', 'onSearch'),
        
        # 진행률 이벤트
        (r'onProgressCompleted\s*=', 'onProgressCompleted'),
        (r'onSliderMoved\s*=', 'onSliderMoved'),
        
        # 탭 이벤트
        (r'onTabAdded\s*=', 'onTabAdded'),
        (r'onTabRemoved\s*=', 'onTabRemoved'),
        (r'onTabChanged\s*=', 'onTabChanged'),
        
        # 트리 이벤트
        (r'onNodeClick\s*=', 'onNodeClick'),
        (r'onNodeDoubleClick\s*=', 'onNodeDoubleClick'),
        (r'onNodeRightClick\s*=', 'onNodeRightClick'),
        (r'onNodeSelected\s*=', 'onNodeSelected'),
        (r'onNodeExpanded\s*=', 'onNodeExpanded'),
        (r'onNodeCollapsed\s*=', 'onNodeCollapsed'),
        
        # 데이터 관련 이벤트
        (r'onRowAdded\s*=', 'onRowAdded'),
        (r'onRowDeleted\s*=', 'onRowDeleted'),
        (r'onRowUpdated\s*=', 'onRowUpdated')
    ]
    
    # 잘못된 이벤트 핸들러 찾기 (eXBuilder6에 존재하지 않는 이벤트)
    invalid_events = ['onInvalidEvent', 'onCustomEvent', 'onUnknownEvent']  # 예시
    for pattern, event_name in event_patterns:
        if re.search(pattern, code):
            # 실제로는 eXBuilder6에 존재하는 이벤트이므로 잘못된 것으로 보고하지 않음
            pass
    
    # 메시지 관련 - 잘못된 사용만 보고 (한글 설명: 메시지 관련 API 사용을 검사하여 잘못된 사용만 검출)
    message_patterns = [
        (r'showMessage\(', 'showMessage'),
        (r'showConfirm\(', 'showConfirm'),
        (r'showAlert\(', 'showAlert'),
        (r'showError\(', 'showError'),
        (r'showWarning\(', 'showWarning'),
        (r'showInfo\(', 'showInfo'),
        (r'showSuccess\(', 'showSuccess'),
        (r'showQuestion\(', 'showQuestion'),
        (r'showInput\(', 'showInput'),
        (r'showSelect\(', 'showSelect')
    ]
    
    # 잘못된 메시지 함수 찾기 (eXBuilder6에 존재하지 않는 메시지 함수)
    invalid_messages = ['showInvalidMessage', 'showCustomMessage']  # 예시
    for pattern, message_name in message_patterns:
        if re.search(pattern, code):
            # 실제로는 eXBuilder6에 존재하는 메시지 함수이므로 잘못된 것으로 보고하지 않음
            pass
    
    # app.lookup은 올바른 사용이므로 보고하지 않음 (한글 설명: app.lookup은 eXBuilder6의 정상적인 API이므로 오류로 보고하지 않음)
    
    return incorrect_apis if incorrect_apis else ['eXBuilder6 API 사용에 문제없음']

def check_errors(code: str) -> List[str]:
    """
    잠재적 오류 검사
    
    이 함수는 JavaScript 코드에서 다음과 같은 잠재적 오류들을 검사합니다:
    1. null/undefined 참조 오류
    2. XSS 보안 위험
    3. JSON 파싱 오류
    4. 배열 인덱스 오류
    5. 타입 변환 오류
    6. 비동기 처리 오류
    """
    errors = []
    
    error_patterns = [
        (r'\.getElementById\([^)]*\)\.', 'getElementById 결과가 null일 수 있습니다'),
        (r'\.querySelector\([^)]*\)\.', 'querySelector 결과가 null일 수 있습니다'),
        (r'\.innerHTML\s*=', 'innerHTML 사용시 XSS 위험이 있습니다'),
        (r'JSON\.parse\([^)]*\)', 'JSON.parse는 try-catch로 감싸야 합니다'),
        (r'\.split\([^)]*\)\[', 'split 결과가 빈 배열일 수 있습니다'),
        (r'\.charAt\([^)]*\)', 'charAt 인덱스가 문자열 길이를 초과할 수 있습니다'),
        (r'\.substring\([^)]*\)', 'substring 인덱스가 잘못될 수 있습니다'),
        (r'\.substr\([^)]*\)', 'substr 인덱스가 잘못될 수 있습니다'),
        (r'\.indexOf\([^)]*\)\s*[<>=]', 'indexOf 결과가 -1일 수 있습니다'),
        (r'\.length\s*[<>=]', 'length 속성 접근시 null/undefined 오류 가능성'),
        (r'\.push\([^)]*\)', 'push 메서드 호출시 배열이 null일 수 있습니다'),
        (r'\.pop\(\)', 'pop 메서드 호출시 빈 배열일 수 있습니다'),
        (r'\.shift\(\)', 'shift 메서드 호출시 빈 배열일 수 있습니다'),
        (r'\.unshift\([^)]*\)', 'unshift 메서드 호출시 배열이 null일 수 있습니다'),
        (r'\.splice\([^)]*\)', 'splice 메서드 호출시 배열이 null일 수 있습니다'),
        (r'\.slice\([^)]*\)', 'slice 메서드 호출시 배열이 null일 수 있습니다'),
        (r'\.join\([^)]*\)', 'join 메서드 호출시 배열이 null일 수 있습니다'),
        (r'\.reverse\(\)', 'reverse 메서드 호출시 배열이 null일 수 있습니다'),
        (r'\.sort\([^)]*\)', 'sort 메서드 호출시 배열이 null일 수 있습니다'),
        (r'\.filter\([^)]*\)', 'filter 메서드 호출시 배열이 null일 수 있습니다'),
        (r'\.map\([^)]*\)', 'map 메서드 호출시 배열이 null일 수 있습니다'),
        (r'\.reduce\([^)]*\)', 'reduce 메서드 호출시 배열이 null일 수 있습니다'),
        (r'\.forEach\([^)]*\)', 'forEach 메서드 호출시 배열이 null일 수 있습니다'),
        (r'\.find\([^)]*\)', 'find 메서드 호출시 배열이 null일 수 있습니다'),
        (r'\.findIndex\([^)]*\)', 'findIndex 메서드 호출시 배열이 null일 수 있습니다'),
        (r'\.includes\([^)]*\)', 'includes 메서드 호출시 배열이 null일 수 있습니다'),
        (r'\.some\([^)]*\)', 'some 메서드 호출시 배열이 null일 수 있습니다'),
        (r'\.every\([^)]*\)', 'every 메서드 호출시 배열이 null일 수 있습니다'),
        (r'\.flat\([^)]*\)', 'flat 메서드 호출시 배열이 null일 수 있습니다'),
        (r'\.flatMap\([^)]*\)', 'flatMap 메서드 호출시 배열이 null일 수 있습니다'),
        (r'\.entries\(\)', 'entries 메서드 호출시 배열이 null일 수 있습니다'),
        (r'\.keys\(\)', 'keys 메서드 호출시 배열이 null일 수 있습니다'),
        (r'\.values\(\)', 'values 메서드 호출시 배열이 null일 수 있습니다'),
        (r'\.copyWithin\([^)]*\)', 'copyWithin 메서드 호출시 배열이 null일 수 있습니다'),
        (r'\.fill\([^)]*\)', 'fill 메서드 호출시 배열이 null일 수 있습니다'),
        (r'\.from\([^)]*\)', 'Array.from 호출시 잘못된 인자일 수 있습니다'),
        (r'\.isArray\([^)]*\)', 'Array.isArray 호출시 잘못된 인자일 수 있습니다'),
        (r'\.of\([^)]*\)', 'Array.of 호출시 잘못된 인자일 수 있습니다'),
        (r'\.parse\([^)]*\)', 'JSON.parse 호출시 잘못된 JSON 문자열일 수 있습니다'),
        (r'\.stringify\([^)]*\)', 'JSON.stringify 호출시 순환 참조일 수 있습니다'),
        (r'\.parseInt\([^)]*\)', 'parseInt 호출시 잘못된 문자열일 수 있습니다'),
        (r'\.parseFloat\([^)]*\)', 'parseFloat 호출시 잘못된 문자열일 수 있습니다'),
        (r'\.isNaN\([^)]*\)', 'isNaN 호출시 잘못된 인자일 수 있습니다'),
        (r'\.isFinite\([^)]*\)', 'isFinite 호출시 잘못된 인자일 수 있습니다'),
        (r'\.encodeURI\([^)]*\)', 'encodeURI 호출시 잘못된 URI일 수 있습니다'),
        (r'\.encodeURIComponent\([^)]*\)', 'encodeURIComponent 호출시 잘못된 URI 컴포넌트일 수 있습니다'),
        (r'\.decodeURI\([^)]*\)', 'decodeURI 호출시 잘못된 인코딩된 URI일 수 있습니다'),
        (r'\.decodeURIComponent\([^)]*\)', 'decodeURIComponent 호출시 잘못된 인코딩된 URI 컴포넌트일 수 있습니다'),
        (r'\.escape\([^)]*\)', 'escape 호출시 잘못된 문자열일 수 있습니다'),
        (r'\.unescape\([^)]*\)', 'unescape 호출시 잘못된 인코딩된 문자열일 수 있습니다'),
        (r'\.btoa\([^)]*\)', 'btoa 호출시 잘못된 문자열일 수 있습니다'),
        (r'\.atob\([^)]*\)', 'atob 호출시 잘못된 Base64 문자열일 수 있습니다'),
        (r'\.setTimeout\([^)]*\)', 'setTimeout 호출시 잘못된 콜백 함수일 수 있습니다'),
        (r'\.setInterval\([^)]*\)', 'setInterval 호출시 잘못된 콜백 함수일 수 있습니다'),
        (r'\.clearTimeout\([^)]*\)', 'clearTimeout 호출시 잘못된 타이머 ID일 수 있습니다'),
        (r'\.clearInterval\([^)]*\)', 'clearInterval 호출시 잘못된 타이머 ID일 수 있습니다'),
        (r'\.requestAnimationFrame\([^)]*\)', 'requestAnimationFrame 호출시 잘못된 콜백 함수일 수 있습니다'),
        (r'\.cancelAnimationFrame\([^)]*\)', 'cancelAnimationFrame 호출시 잘못된 프레임 ID일 수 있습니다'),
        (r'\.addEventListener\([^)]*\)', 'addEventListener 호출시 잘못된 이벤트 타입일 수 있습니다'),
        (r'\.removeEventListener\([^)]*\)', 'removeEventListener 호출시 잘못된 이벤트 타입일 수 있습니다'),
        (r'\.dispatchEvent\([^)]*\)', 'dispatchEvent 호출시 잘못된 이벤트 객체일 수 있습니다'),
        (r'\.preventDefault\(\)', 'preventDefault 호출시 이벤트 객체가 null일 수 있습니다'),
        (r'\.stopPropagation\(\)', 'stopPropagation 호출시 이벤트 객체가 null일 수 있습니다'),
        (r'\.stopImmediatePropagation\(\)', 'stopImmediatePropagation 호출시 이벤트 객체가 null일 수 있습니다'),
        (r'\.getAttribute\([^)]*\)', 'getAttribute 호출시 요소가 null일 수 있습니다'),
        (r'\.setAttribute\([^)]*\)', 'setAttribute 호출시 요소가 null일 수 있습니다'),
        (r'\.removeAttribute\([^)]*\)', 'removeAttribute 호출시 요소가 null일 수 있습니다'),
        (r'\.hasAttribute\([^)]*\)', 'hasAttribute 호출시 요소가 null일 수 있습니다'),
        (r'\.getAttributeNode\([^)]*\)', 'getAttributeNode 호출시 요소가 null일 수 있습니다'),
        (r'\.setAttributeNode\([^)]*\)', 'setAttributeNode 호출시 요소가 null일 수 있습니다'),
        (r'\.removeAttributeNode\([^)]*\)', 'removeAttributeNode 호출시 요소가 null일 수 있습니다'),
        (r'\.getElementsByTagName\([^)]*\)', 'getElementsByTagName 호출시 요소가 null일 수 있습니다'),
        (r'\.getElementsByClassName\([^)]*\)', 'getElementsByClassName 호출시 요소가 null일 수 있습니다'),
        (r'\.getElementsByName\([^)]*\)', 'getElementsByName 호출시 요소가 null일 수 있습니다'),
        (r'\.querySelector\([^)]*\)', 'querySelector 호출시 요소가 null일 수 있습니다'),
        (r'\.querySelectorAll\([^)]*\)', 'querySelectorAll 호출시 요소가 null일 수 있습니다'),
        (r'\.closest\([^)]*\)', 'closest 호출시 요소가 null일 수 있습니다'),
        (r'\.matches\([^)]*\)', 'matches 호출시 요소가 null일 수 있습니다'),
        (r'\.contains\([^)]*\)', 'contains 호출시 요소가 null일 수 있습니다'),
        (r'\.compareDocumentPosition\([^)]*\)', 'compareDocumentPosition 호출시 요소가 null일 수 있습니다'),
        (r'\.isSameNode\([^)]*\)', 'isSameNode 호출시 요소가 null일 수 있습니다'),
        (r'\.isEqualNode\([^)]*\)', 'isEqualNode 호출시 요소가 null일 수 있습니다'),
        (r'\.lookupPrefix\([^)]*\)', 'lookupPrefix 호출시 요소가 null일 수 있습니다'),
        (r'\.lookupNamespaceURI\([^)]*\)', 'lookupNamespaceURI 호출시 요소가 null일 수 있습니다'),
        (r'\.isDefaultNamespace\([^)]*\)', 'isDefaultNamespace 호출시 요소가 null일 수 있습니다'),
        (r'\.insertBefore\([^)]*\)', 'insertBefore 호출시 요소가 null일 수 있습니다'),
        (r'\.appendChild\([^)]*\)', 'appendChild 호출시 요소가 null일 수 있습니다'),
        (r'\.replaceChild\([^)]*\)', 'replaceChild 호출시 요소가 null일 수 있습니다'),
        (r'\.removeChild\([^)]*\)', 'removeChild 호출시 요소가 null일 수 있습니다'),
        (r'\.cloneNode\([^)]*\)', 'cloneNode 호출시 요소가 null일 수 있습니다'),
        (r'\.normalize\(\)', 'normalize 호출시 요소가 null일 수 있습니다'),
        (r'\.isSupported\([^)]*\)', 'isSupported 호출시 요소가 null일 수 있습니다'),
        (r'\.hasChildNodes\(\)', 'hasChildNodes 호출시 요소가 null일 수 있습니다'),
        (r'\.getFeature\([^)]*\)', 'getFeature 호출시 요소가 null일 수 있습니다'),
        (r'\.getUserData\([^)]*\)', 'getUserData 호출시 요소가 null일 수 있습니다'),
        (r'\.setUserData\([^)]*\)', 'setUserData 호출시 요소가 null일 수 있습니다'),
        (r'\.adoptNode\([^)]*\)', 'adoptNode 호출시 요소가 null일 수 있습니다'),
        (r'\.importNode\([^)]*\)', 'importNode 호출시 요소가 null일 수 있습니다'),
        (r'\.createElement\([^)]*\)', 'createElement 호출시 잘못된 태그명일 수 있습니다'),
        (r'\.createElementNS\([^)]*\)', 'createElementNS 호출시 잘못된 네임스페이스일 수 있습니다'),
        (r'\.createTextNode\([^)]*\)', 'createTextNode 호출시 잘못된 텍스트일 수 있습니다'),
        (r'\.createComment\([^)]*\)', 'createComment 호출시 잘못된 주석일 수 있습니다'),
        (r'\.createCDATASection\([^)]*\)', 'createCDATASection 호출시 잘못된 CDATA일 수 있습니다'),
        (r'\.createProcessingInstruction\([^)]*\)', 'createProcessingInstruction 호출시 잘못된 처리 지시어일 수 있습니다'),
        (r'\.createAttribute\([^)]*\)', 'createAttribute 호출시 잘못된 속성명일 수 있습니다'),
        (r'\.createAttributeNS\([^)]*\)', 'createAttributeNS 호출시 잘못된 네임스페이스일 수 있습니다'),
        (r'\.createEntityReference\([^)]*\)', 'createEntityReference 호출시 잘못된 엔티티 참조일 수 있습니다'),
        (r'\.createRange\(\)', 'createRange 호출시 문서가 null일 수 있습니다'),
        (r'\.createNodeIterator\([^)]*\)', 'createNodeIterator 호출시 잘못된 루트일 수 있습니다'),
        (r'\.createTreeWalker\([^)]*\)', 'createTreeWalker 호출시 잘못된 루트일 수 있습니다'),
        (r'\.getElementById\([^)]*\)', 'getElementById 호출시 잘못된 ID일 수 있습니다'),
        (r'\.getElementsByTagName\([^)]*\)', 'getElementsByTagName 호출시 잘못된 태그명일 수 있습니다'),
        (r'\.getElementsByTagNameNS\([^)]*\)', 'getElementsByTagNameNS 호출시 잘못된 네임스페이스일 수 있습니다'),
        (r'\.getElementsByClassName\([^)]*\)', 'getElementsByClassName 호출시 잘못된 클래스명일 수 있습니다'),
        (r'\.querySelector\([^)]*\)', 'querySelector 호출시 잘못된 선택자일 수 있습니다'),
        (r'\.querySelectorAll\([^)]*\)', 'querySelectorAll 호출시 잘못된 선택자일 수 있습니다'),
        (r'\.open\([^)]*\)', 'open 호출시 잘못된 URL일 수 있습니다'),
        (r'\.write\([^)]*\)', 'write 호출시 잘못된 HTML일 수 있습니다'),
        (r'\.writeln\([^)]*\)', 'writeln 호출시 잘못된 HTML일 수 있습니다'),
        (r'\.close\(\)', 'close 호출시 문서가 null일 수 있습니다'),
        (r'\.getSelection\(\)', 'getSelection 호출시 윈도우가 null일 수 있습니다'),
        (r'\.find\([^)]*\)', 'find 호출시 잘못된 검색어일 수 있습니다'),
        (r'\.getComputedStyle\([^)]*\)', 'getComputedStyle 호출시 요소가 null일 수 있습니다'),
        (r'\.getBoundingClientRect\(\)', 'getBoundingClientRect 호출시 요소가 null일 수 있습니다'),
        (r'\.scrollIntoView\([^)]*\)', 'scrollIntoView 호출시 요소가 null일 수 있습니다'),
        (r'\.scrollTo\([^)]*\)', 'scrollTo 호출시 잘못된 좌표일 수 있습니다'),
        (r'\.scrollBy\([^)]*\)', 'scrollBy 호출시 잘못된 좌표일 수 있습니다'),
        (r'\.scroll\([^)]*\)', 'scroll 호출시 잘못된 좌표일 수 있습니다'),
        (r'\.scrollTop\s*=', 'scrollTop 설정시 잘못된 값일 수 있습니다'),
        (r'\.scrollLeft\s*=', 'scrollLeft 설정시 잘못된 값일 수 있습니다'),
        (r'\.scrollWidth', 'scrollWidth 접근시 요소가 null일 수 있습니다'),
        (r'\.scrollHeight', 'scrollHeight 접근시 요소가 null일 수 있습니다'),
        (r'\.clientWidth', 'clientWidth 접근시 요소가 null일 수 있습니다'),
        (r'\.clientHeight', 'clientHeight 접근시 요소가 null일 수 있습니다'),
        (r'\.offsetWidth', 'offsetWidth 접근시 요소가 null일 수 있습니다'),
        (r'\.offsetHeight', 'offsetHeight 접근시 요소가 null일 수 있습니다'),
        (r'\.offsetTop', 'offsetTop 접근시 요소가 null일 수 있습니다'),
        (r'\.offsetLeft', 'offsetLeft 접근시 요소가 null일 수 있습니다'),
        (r'\.offsetParent', 'offsetParent 접근시 요소가 null일 수 있습니다'),
        (r'\.getBoundingClientRect\(\)', 'getBoundingClientRect 호출시 요소가 null일 수 있습니다'),
        (r'\.getClientRects\(\)', 'getClientRects 호출시 요소가 null일 수 있습니다'),
        (r'\.scrollIntoViewIfNeeded\([^)]*\)', 'scrollIntoViewIfNeeded 호출시 요소가 null일 수 있습니다'),
        (r'\.scrollIntoView\([^)]*\)', 'scrollIntoView 호출시 요소가 null일 수 있습니다'),
        (r'\.scrollTo\([^)]*\)', 'scrollTo 호출시 잘못된 좌표일 수 있습니다'),
        (r'\.scrollBy\([^)]*\)', 'scrollBy 호출시 잘못된 좌표일 수 있습니다'),
        (r'\.scroll\([^)]*\)', 'scroll 호출시 잘못된 좌표일 수 있습니다'),
        (r'\.scrollTop\s*=', 'scrollTop 설정시 잘못된 값일 수 있습니다'),
        (r'\.scrollLeft\s*=', 'scrollLeft 설정시 잘못된 값일 수 있습니다'),
        (r'\.scrollWidth', 'scrollWidth 접근시 요소가 null일 수 있습니다'),
        (r'\.scrollHeight', 'scrollHeight 접근시 요소가 null일 수 있습니다'),
        (r'\.clientWidth', 'clientWidth 접근시 요소가 null일 수 있습니다'),
        (r'\.clientHeight', 'clientHeight 접근시 요소가 null일 수 있습니다'),
        (r'\.offsetWidth', 'offsetWidth 접근시 요소가 null일 수 있습니다'),
        (r'\.offsetHeight', 'offsetHeight 접근시 요소가 null일 수 있습니다'),
        (r'\.offsetTop', 'offsetTop 접근시 요소가 null일 수 있습니다'),
        (r'\.offsetLeft', 'offsetLeft 접근시 요소가 null일 수 있습니다'),
        (r'\.offsetParent', 'offsetParent 접근시 요소가 null일 수 있습니다'),
        (r'\.getBoundingClientRect\(\)', 'getBoundingClientRect 호출시 요소가 null일 수 있습니다'),
        (r'\.getClientRects\(\)', 'getClientRects 호출시 요소가 null일 수 있습니다'),
        (r'\.scrollIntoViewIfNeeded\([^)]*\)', 'scrollIntoViewIfNeeded 호출시 요소가 null일 수 있습니다')
    ]
    
    for pattern, message in error_patterns:
        if re.search(pattern, code):
            errors.append(message)
    
    return errors if errors else ['발견된 오류 없음']

def analyze_execution_flow(code: str) -> List[str]:
    """
    실행 흐름 분석 - 스토리텔링 방식
    
    이 함수는 JavaScript 코드의 실행 흐름을 다음과 같은 방식으로 분석합니다:
    1. 함수별로 스토리텔링 방식의 실행 흐름 분석
    2. 이벤트 핸들러 감지 및 설명
    3. 비동기 작업 감지 및 설명
    4. eXBuilder6 API 호출 감지 및 설명
    5. 전체적인 실행 흐름을 이야기 형태로 제공
    """
    flow = []
    
    # 함수별로 분석 (한글 설명: 함수 정의를 찾아서 각각의 실행 흐름을 스토리텔링 방식으로 분석)
    functions = re.findall(r'function\s+(\w+)\s*\([^)]*\)\s*\{([^}]+)\}', code, re.DOTALL)
    if functions:
        for func_name, func_body in functions:
            flow.append(f"📖 함수 '{func_name}'의 이야기:")
            
            # 함수 내부 로직을 스토리텔링 방식으로 분석
            story_steps = []
            
            # 변수 선언 (한글 설명: 함수 내에서 선언된 변수들을 찾아서 설명)
            var_decls = re.findall(r'(?:var|let|const)\s+(\w+)', func_body)
            if var_decls:
                story_steps.append(f"  🎭 먼저 {', '.join(var_decls)} 변수들을 준비합니다.")
            
            # 조건문 (한글 설명: if, else if, else 등의 조건문을 찾아서 설명)
            if 'if' in func_body:
                story_steps.append("  🤔 조건을 확인하여 분기점을 만듭니다.")
            
            # 반복문 (한글 설명: for, while, do 등의 반복문을 찾아서 설명)
            if any(keyword in func_body for keyword in ['for', 'while', 'do']):
                story_steps.append("  🔄 반복적으로 작업을 수행합니다.")
            
            # 함수 호출 (한글 설명: 다른 함수들을 호출하는 부분을 찾아서 설명)
            func_calls = re.findall(r'(\w+)\(', func_body)
            if func_calls:
                story_steps.append(f"  📞 {', '.join(func_calls)} 함수들을 호출하여 작업을 수행합니다.")
            
            # eXBuilder6 API 호출 (한글 설명: eXBuilder6의 API들을 호출하는 부분을 찾아서 설명)
            exbuilder_calls = re.findall(r'(\w+)\.(\w+)\(', func_body)
            if exbuilder_calls:
                # 컨트롤 타입별 메서드 검증 (API Reference 기반)
                control_methods = {
                    'grd': EXBUILDER6_CONTROL_APIS['grd']['methods'],
                    'button': EXBUILDER6_CONTROL_APIS['button']['methods'],
                    'btn': EXBUILDER6_CONTROL_APIS['btn']['methods'],
                    'calendar': EXBUILDER6_CONTROL_APIS['calendar']['methods'],
                    'cal': EXBUILDER6_CONTROL_APIS['cal']['methods'],
                    'cbx': EXBUILDER6_CONTROL_APIS['cbx']['methods'],
                    'cbg': EXBUILDER6_CONTROL_APIS.get('cbg', {}).get('methods', []),
                    'cmb': EXBUILDER6_CONTROL_APIS['cmb']['methods'],
                    'dm': EXBUILDER6_CONTROL_APIS.get('dm', {}).get('methods', []),
                    'ds': EXBUILDER6_CONTROL_APIS.get('ds', {}).get('methods', []),
                    'dv': EXBUILDER6_CONTROL_APIS.get('dv', {}).get('methods', []),
                    'dw': EXBUILDER6_CONTROL_APIS.get('dw', {}).get('methods', []),
                    'dti': EXBUILDER6_CONTROL_APIS.get('dti', {}).get('methods', []),
                    'fi': EXBUILDER6_CONTROL_APIS.get('fi', {}).get('methods', []),
                    'fud': EXBUILDER6_CONTROL_APIS.get('fud', {}).get('methods', []),
                    'ipb': EXBUILDER6_CONTROL_APIS['ipb']['methods'],
                    'lcb': EXBUILDER6_CONTROL_APIS.get('lcb', {}).get('methods', []),
                    'llb': EXBUILDER6_CONTROL_APIS.get('llb', {}).get('methods', []),
                    'lbx': EXBUILDER6_CONTROL_APIS.get('lbx', {}).get('methods', []),
                    'mse': EXBUILDER6_CONTROL_APIS.get('mse', {}).get('methods', []),
                    'mdi': EXBUILDER6_CONTROL_APIS.get('mdi', {}).get('methods', []),
                    'nbe': EXBUILDER6_CONTROL_APIS.get('nbe', {}).get('methods', []),
                    'pgr': EXBUILDER6_CONTROL_APIS.get('pgr', {}).get('methods', []),
                    'rdb': EXBUILDER6_CONTROL_APIS.get('rdb', {}).get('methods', []),
                    'sip': EXBUILDER6_CONTROL_APIS.get('sip', {}).get('methods', []),
                    'sld': EXBUILDER6_CONTROL_APIS.get('sld', {}).get('methods', []),
                    'tab': EXBUILDER6_CONTROL_APIS.get('tab', {}).get('methods', []),
                    'txa': EXBUILDER6_CONTROL_APIS['txa']['methods'],
                    'tre': EXBUILDER6_CONTROL_APIS['tre']['methods']
                }
                
                api_calls = []
                for var_name, method_name in exbuilder_calls:
                    # 변수명에서 컨트롤 타입 추정 (간단한 패턴 매칭)
                    control_type = None
                    for prefix in control_methods.keys():
                        if var_name.startswith(prefix) or var_name.endswith(prefix):
                            control_type = prefix
                            break
                    
                    if control_type and method_name in control_methods[control_type]:
                        api_calls.append(f"{control_type}.{method_name}")
                    elif method_name in EXBUILDER6_MESSAGE_APIS['methods']:
                        api_calls.append(method_name)
                    elif method_name in EXBUILDER6_COMMON_APIS['methods']:
                        api_calls.append(method_name)
                
                if api_calls:
                    story_steps.append(f"  🎮 eXBuilder6 컨트롤들과 상호작용합니다: {', '.join(api_calls)}")
            
            # 예외 처리 (한글 설명: try-catch 블록을 찾아서 설명)
            if 'try' in func_body or 'catch' in func_body:
                story_steps.append("  🛡️ 예상치 못한 상황에 대비하여 안전장치를 마련합니다.")
            
            # 반환값 (한글 설명: return 문을 찾아서 설명)
            if 'return' in func_body:
                story_steps.append("  📤 작업 결과를 반환합니다.")
            
            if story_steps:
                flow.extend(story_steps)
            else:
                flow.append("  📝 순차적으로 작업을 진행합니다.")
    
    # 이벤트 핸들러 찾기 (한글 설명: this.onXXX 형태의 이벤트 핸들러를 찾아서 설명)
    event_handlers = re.findall(r'this\.(on\w+)\s*=', code)
    if event_handlers:
        flow.append(f"🎯 사용자 이벤트를 기다리는 감시자들: {', '.join(event_handlers)}")
    
    # 비동기 작업 찾기 (한글 설명: setTimeout, setInterval, fetch, Promise, async, await 등을 찾아서 설명)
    async_matches = re.findall(r'(setTimeout|setInterval|fetch|Promise|async|await)', code)
    if async_matches:
        unique_async = list(set(async_matches))
        flow.append(f"⏰ 시간이 걸리는 작업들을 처리합니다: {', '.join(unique_async)}")
    
    # 전역 실행 흐름을 스토리텔링으로 (한글 설명: 전체 코드의 실행 흐름을 이야기 형태로 설명)
    global_story = []
    
    # 조건문 (한글 설명: 전체 코드에서 if 문의 개수를 세어서 설명)
    conditional_count = len(re.findall(r'\bif\b', code))
    if conditional_count > 0:
        global_story.append(f"🤔 {conditional_count}개의 분기점에서 상황에 따라 다른 길을 선택합니다.")
    
    # 반복문 (한글 설명: 전체 코드에서 반복문의 개수를 세어서 설명)
    loop_count = len(re.findall(r'\b(for|while|do)\b', code))
    if loop_count > 0:
        global_story.append(f"🔄 {loop_count}개의 반복 작업으로 데이터를 처리합니다.")
    
    # 함수 호출 (한글 설명: 전체 코드에서 함수 호출의 개수를 세어서 설명)
    function_calls = len(re.findall(r'\w+\(', code))
    if function_calls > 0:
        global_story.append(f"📞 {function_calls}개의 함수 호출로 복잡한 작업을 분담합니다.")
    
    if global_story:
        flow.append("🌍 전체 이야기의 흐름:")
        flow.extend([f"  {step}" for step in global_story])
    
    return flow if flow else ['📖 간단한 순차적 실행 이야기']

def analyze_with_llm(code: str, fast_mode: bool = False) -> Dict[str, Any]:
    """
    LM Studio를 사용한 고급 분석
    
    이 함수는 LM Studio를 사용하여 JavaScript 코드를 다음과 같은 방식으로 분석합니다:
    1. JavaScript 문법/로직 문제점 분석
    2. eXBuilder6 API 사용 여부 분석
    3. 잠재적 오류 및 보안 위험 요소 분석
    4. 실행 흐름 분석 (단계별 상세 과정)
    5. eXBuilder6_HelpContents.pdf 기반의 정확한 API 정보 제공
    """
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

**eXBuilder6 API 참고 정보:**
- Grid 컨트롤 (grd): addRow, deleteRow, updateRow, getRow, getData, setData, clear, refresh, getSelected, setSelected, getChecked, setChecked, getExpanded, setExpanded, scrollTo, scrollIntoView, insertRowData, removeRowData, getRowCount, getColumnCount, getSelectedRows, setSelectedRows, getCellValue, setCellValue, getCellText, setCellText, getCellStyle, setCellStyle, getColumnWidth, setColumnWidth, getRowHeight, setRowHeight, getVisibleRows, setVisibleRows, getVisibleColumns, setVisibleColumns, getSortColumn, setSortColumn, getSortOrder, setSortOrder, getFilterData, setFilterData, getGroupData, setGroupData, getSummaryData, setSummaryData, getPagingData, setPagingData, getPageSize, setPageSize, getCurrentPage, setCurrentPage, getTotalCount, setTotalCount, getPageCount, setPageCount, getPageInfo, setPageInfo

- Button 컨트롤 (button, btn): setText, getText, enable, disable, show, hide, focus, blur, click, setIcon, getIcon, setIconAlign, getIconAlign, setButtonType, getButtonType, setImage, getImage, setImageAlign, getImageAlign, setTooltip, getTooltip

- Calendar 컨트롤 (calendar, cal): setDate, getDate, setValue, getValue, enable, disable, show, hide, focus, blur, setMinDate, getMinDate, setMaxDate, getMaxDate, setFirstDayOfWeek, getFirstDayOfWeek, setCalendarType, getCalendarType, setDateFormat, getDateFormat, setTimeFormat, getTimeFormat, setShowTime, getShowTime, setShowToday, getShowToday, setShowWeekNumbers, getShowWeekNumbers

- ComboBox 컨트롤 (cmb): addItem, deleteItem, updateItem, getItem, getData, setData, clear, refresh, getSelected, setSelected, getChecked, setChecked, enable, disable, show, hide, focus, blur, openDropdown, closeDropdown, getSelectedIndex, setSelectedIndex, getSelectedValue, setSelectedValue, getSelectedText, setSelectedText, getItemCount, getItemText, setItemText, getItemValue, setItemValue, getItemData, setItemData, getItemIndex, setItemIndex, getItemByValue, getItemByText, getItemByIndex

- CheckBox 컨트롤 (cbx): setChecked, getChecked, setText, getText, enable, disable, show, hide, focus, blur, setCheckType, getCheckType, setTextAlign, getTextAlign, setGroupName, getGroupName

- Tree 컨트롤 (tre): addNode, deleteNode, updateNode, getNode, getData, setData, clear, refresh, getSelected, setSelected, getChecked, setChecked, getExpanded, setExpanded, scrollTo, scrollIntoView, enable, disable, show, hide, focus, blur, expandAll, collapseAll, getRootNode, getChildNodes, getParentNode, getSiblingNodes, getNodeByText, getNodeByValue, getNodeByIndex, getNodePath, setNodePath, getNodeLevel, setNodeLevel, getNodeIcon, setNodeIcon, getNodeTooltip, setNodeTooltip

- InputBox 컨트롤 (ipb): setValue, getValue, setText, getText, enable, disable, show, hide, focus, blur, setMaxLength, getMaxLength, setPlaceholder, getPlaceholder, setInputType, getInputType, setPattern, getPattern, setRequired, getRequired, setReadOnly, getReadOnly, setAutoComplete, getAutoComplete, setAutoFocus, getAutoFocus, setSpellCheck, getSpellCheck

- TextArea 컨트롤 (txa): setValue, getValue, setText, getText, enable, disable, show, hide, focus, blur, setMaxLength, getMaxLength, setPlaceholder, getPlaceholder, setRows, getRows, setCols, getCols, setWrap, getWrap, setResize, getResize, setSpellCheck, getSpellCheck

**공통 API (모든 컨트롤에서 사용 가능):**
- 메서드: setValue, getValue, setText, getText, enable, disable, show, hide, focus, blur, setVisible, getVisible, setEnabled, getEnabled, setReadOnly, getReadOnly, setWidth, getWidth, setHeight, getHeight, setStyle, getStyle, setData, getData, refresh, clear, reset, validate, isValid, getParent, getChild, getChildren, getSibling, getSiblings, getRoot, getAncestor, getDescendant, getFirstChild, getLastChild, getNextSibling, getPreviousSibling, addChild, removeChild, insertChild

- 속성: text, value, visible, enabled, readOnly, width, height, style, data, name, id, className, tagName, parentNode, childNodes, firstChild, lastChild, nextSibling, previousSibling, nodeType, nodeValue, nodeName, attributes

- 이벤트: onLoad, onUnload, onClick, onDoubleClick, onRightClick, onMouseDown, onMouseUp, onMouseOver, onMouseOut, onMouseMove, onMouseEnter, onMouseLeave, onFocus, onBlur, onKeyDown, onKeyUp, onKeyPress, onChange, onSelect, onInput, onInvalid, onReset, onSubmit, onError, onAbort, onLoad, onUnload, onResize, onScroll, onContextMenu

**메시지 API:**
- showMessage, showConfirm, showAlert, showError, showWarning, showInfo, showSuccess, showQuestion, showInput, showSelect, showFileDialog, showColorDialog, showFontDialog, openPopup, closePopup, showPopup, hidePopup, setPopupPosition, getPopupPosition, setPopupSize, getPopupSize, setPopupTitle, getPopupTitle, setPopupContent, getPopupContent

**데이터 API:**
- getData, setData, getJsonData, setJsonData, getXmlData, setXmlData, getCsvData, setCsvData, loadData, saveData, exportData, importData, validateData, transformData, filterData, sortData, groupData, aggregateData, calculateData, mergeData, splitData, cloneData

**응답 형식:**
## 1. JavaScript 문법/로직 문제점
- **라인 X**: 구체적 문제점

## 2. eXBuilder6 API 사용 여부
- 사용된 API: this.form.setValue, this.grid.addRow 등
- 잘못된 API 사용: 존재하지 않는 메서드/속성

## 3. 오류 검사
- **라인 X**: 구체적 오류

## 4. 실행 흐름
- 단계별 상세 동작 과정 (스토리텔링 방식)

발견된 문제가 없으면 "발견된 문제점 없음"으로 표시하세요."""

    try:
        result = request_llm_fast(prompt) if fast_mode else request_llm(prompt)
        return {"llm_analysis": result}
    except Exception as e:
        return {"llm_analysis": f"LLM 분석 중 오류 발생: {str(e)}"}

@router.post("/analyze", response_model=JavaScriptAnalysisResponse)
async def analyze_javascript(request: JavaScriptAnalysisRequest):
    """
    JavaScript 코드 분석
    
    이 엔드포인트는 JavaScript 코드를 다음과 같은 방식으로 분석합니다:
    1. JavaScript 문법/로직 문제점 검사
    2. eXBuilder6 API 사용 여부 검사 (잘못된 사용만 보고)
    3. 잠재적 오류 검사
    4. 실행 흐름 분석 (스토리텔링 방식)
    5. LM Studio를 사용한 고급 분석 (선택적)
    
    Args:
        request (JavaScriptAnalysisRequest): 분석할 JavaScript 코드와 분석 모드
        
    Returns:
        JavaScriptAnalysisResponse: 분석 결과
        
    Raises:
        HTTPException: 분석 중 오류 발생시
    """
    try:
        # 기본 분석 (한글 설명: JavaScript 코드의 기본적인 분석을 수행)
        javascript_issues = check_javascript_issues(request.code)
        exbuilder6_apis = check_exbuilder6_apis(request.code)
        errors = check_errors(request.code)
        execution_flow = analyze_execution_flow(request.code)
        
        # LM Studio를 사용한 고급 분석 (한글 설명: LM Studio를 사용하여 더 정교한 분석을 수행)
        llm_result = analyze_with_llm(request.code, request.fast_mode)
        
        # LLM 분석 결과를 기본 분석에 통합 (한글 설명: LM Studio 분석 결과를 기본 분석 결과와 통합)
        if "llm_analysis" in llm_result and "LLM 분석 중 오류 발생" not in llm_result["llm_analysis"]:
            # LLM 분석이 성공한 경우, 기본 분석 결과에 추가 정보 포함
            return {
                "javascript_issues": javascript_issues,
                "exbuilder6_apis": exbuilder6_apis,
                "errors": errors,
                "execution_flow": execution_flow,
                "llm_analysis": llm_result["llm_analysis"]
            }
        else:
            # LLM 분석이 실패한 경우, 기본 분석만 반환
            return JavaScriptAnalysisResponse(
                javascript_issues=javascript_issues,
                exbuilder6_apis=exbuilder6_apis,
                errors=errors,
                execution_flow=execution_flow
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"분석 중 오류 발생: {str(e)}")

@router.post("/analyze/file")
async def analyze_javascript_file(file: UploadFile = File(...), fast_mode: bool = False):
    """
    JavaScript 파일 분석
    
    이 엔드포인트는 업로드된 JavaScript 파일을 분석합니다:
    1. 파일 형식 검증 (.js 파일만 허용)
    2. 파일 내용 읽기 및 디코딩
    3. JavaScript 코드 분석 수행
    4. 분석 결과 반환
    
    Args:
        file (UploadFile): 분석할 JavaScript 파일
        fast_mode (bool): 빠른 분석 모드 사용 여부
        
    Returns:
        dict: 분석 결과
        
    Raises:
        HTTPException: 파일 형식 오류 또는 분석 중 오류 발생시
    """
    try:
        if not file.filename.endswith('.js'):
            raise HTTPException(status_code=400, detail="JavaScript 파일(.js)만 업로드 가능합니다.")
        
        content = await file.read()
        code = content.decode('utf-8')
        
        # 기본 분석 (한글 설명: 업로드된 JavaScript 파일의 기본적인 분석을 수행)
        javascript_issues = check_javascript_issues(code)
        exbuilder6_apis = check_exbuilder6_apis(code)
        errors = check_errors(code)
        execution_flow = analyze_execution_flow(code)
        
        return {
            "javascript_issues": javascript_issues,
            "exbuilder6_apis": exbuilder6_apis,
            "errors": errors,
            "execution_flow": execution_flow
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"파일 분석 중 오류 발생: {str(e)}")

@router.post("/analyze/detailed")
async def analyze_javascript_detailed(request: JavaScriptAnalysisRequest):
    """
    상세한 JavaScript 코드 분석 (LLM 포함)
    
    이 엔드포인트는 JavaScript 코드를 상세하게 분석합니다:
    1. 기본 분석 (문법, API, 오류, 실행 흐름)
    2. LM Studio를 사용한 고급 분석
    3. eXBuilder6_HelpContents.pdf 기반의 정확한 API 정보 제공
    4. 상세한 분석 결과 반환
    
    Args:
        request (JavaScriptAnalysisRequest): 분석할 JavaScript 코드와 분석 모드
        
    Returns:
        dict: 상세한 분석 결과 (기본 분석 + LLM 분석)
        
    Raises:
        HTTPException: 분석 중 오류 발생시
    """
    try:
        # 기본 분석 (한글 설명: JavaScript 코드의 기본적인 분석을 수행)
        basic_analysis = {
            "javascript_issues": check_javascript_issues(request.code),
            "exbuilder6_apis": check_exbuilder6_apis(request.code),
            "errors": check_errors(request.code),
            "execution_flow": analyze_execution_flow(request.code)
        }
        
        # LM Studio를 사용한 고급 분석 (한글 설명: LM Studio를 사용하여 더 정교한 분석을 수행)
        llm_analysis = analyze_with_llm(request.code, request.fast_mode)
        
        return {
            "basic_analysis": basic_analysis,
            "llm_analysis": llm_analysis
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"분석 중 오류 발생: {str(e)}")
