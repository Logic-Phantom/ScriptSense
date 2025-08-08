# JavaScript 코드 분석 도구 (eXBuilder6 통합)

이 도구는 JavaScript 코드를 분석하여 다음 4가지 항목으로 결과를 제공합니다:

1. **JavaScript 문법/로직 문제점** - 정확한 라인 위치와 함께 전통적인 JavaScript 관점에서의 문제점
2. **eXBuilder6 API 사용 여부** - eXBuilder6 프레임워크 API 사용 여부 및 잘못된 사용 검증
3. **오류 검사** - 잠재적 오류 및 보안 위험 요소
4. **실행 흐름** - 프로세스 중심의 코드 실행 과정 분석

## 🚀 주요 개선사항

### ✅ 정확한 오류 위치 표시
- JavaScript 문법 오류를 정확한 라인 번호와 문자 위치로 표시
- 괄호 불일치, 따옴표 불일치, 세미콜론 누락 등을 라인별로 검사
- 예: `라인 5 위치 12: 괄호 '('가 라인 3 위치 8의 '{'와 매칭되지 않습니다`

### ✅ eXBuilder6 API 검증 개선
- `app.lookup`은 올바른 사용이므로 오류로 보고하지 않음
- `addFileParameter` 등 FileInput 관련 특수 메서드 추가
- `length`, `files`, `control` 등 일반적인 JavaScript 속성 제외
- 잘못된 API 사용만 정확하게 보고

### ✅ 프로세스 중심 실행 흐름
- 이모티콘 제거하고 프로세스 중심 설명으로 변경
- 함수별로 목적과 작업을 명확하게 설명
- 예: `onFi1ValueChange 함수: 파일 처리 - 컨트롤 객체를 찾습니다, 파일 처리를 수행합니다`

### ✅ 대용량 파일 처리 성능
- 배치 처리 기능으로 1000줄 이상 파일도 빠르게 분석
- 코드 크기에 따른 자동 배치 크기 조정
- 메모리 효율적인 처리

## 📋 API 엔드포인트

### 1. 기본 분석
```http
POST /api/js/analyze
Content-Type: application/json

{
    "code": "JavaScript 코드",
    "fast_mode": false
}
```

### 2. 파일 분석
```http
POST /api/js/analyze/file
Content-Type: multipart/form-data

file: JavaScript 파일 (.js)
fast_mode: false (선택사항)
```

### 3. 상세 분석 (LLM 포함)
```http
POST /api/js/analyze/detailed
Content-Type: application/json

{
    "code": "JavaScript 코드",
    "fast_mode": false
}
```

### 4. 배치 분석 (대용량 파일)
```http
POST /api/js/analyze/batch
Content-Type: application/json

{
    "code": "대용량 JavaScript 코드",
    "fast_mode": true
}
```

## 🔧 사용 방법

### 1. 웹 브라우저에서 사용

1. `js-analyzer-demo.html` 파일을 브라우저에서 열기
2. 분석할 JavaScript 코드를 텍스트 영역에 입력
3. "코드 분석" 버튼 클릭
4. 결과 확인

### 2. Python 스크립트에서 사용

```python
import requests

url = "http://localhost:8000/api/js/analyze"
data = {
    "code": """
    function onFi1ValueChange() {
        const fileinput1 = app.lookup("fi1");
        const vaFiles = fileinput1.files;
        const submit = app.lookup("submission1");
        
        for (let i = 0; i < vaFiles.length; i++) {
            const voFile = vaFiles[i];
            submit.addFileParameter("file" + i, voFile);
        }
    }
    """,
    "fast_mode": False
}

response = requests.post(url, json=data)
result = response.json()
print(result)
```

### 3. 테스트 스크립트 실행

```bash
# 서버 실행
python -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000

# 테스트 실행
python test_improved_analyzer.py
```

## 📊 분석 항목 상세

### 1. JavaScript 문법/로직 문제점
- **정확한 위치 표시**: 라인 번호와 문자 위치
- **괄호 불일치**: 중괄호, 소괄호, 대괄호 매칭 검사
- **따옴표 불일치**: 작은따옴표, 큰따옴표 검사
- **세미콜론 누락**: 정확한 패턴 기반 검사
- **함수/변수 선언 문제**: 완료되지 않은 선언 검사
- **객체/배열 리터럴 문제**: 완료되지 않은 리터럴 검사
- **일반적인 문제점**: undefined 할당, null 비교, console.log, eval() 등

### 2. eXBuilder6 API 사용 여부
다음 컨트롤 타입별로 정확한 API 검증:

#### Grid 컨트롤 (grd 패턴)
- **메서드**: addRow, deleteRow, updateRow, getRow, getData, setData, clear, refresh, insertRowData, removeRowData, getRowCount, getColumnCount, getSelectedRows, setSelectedRows, getCellValue, setCellValue, getCellText, setCellText, getCellStyle, setCellStyle, getColumnWidth, setColumnWidth, getRowHeight, setRowHeight, getVisibleRows, setVisibleRows, getVisibleColumns, setVisibleColumns, getSortColumn, setSortColumn, getSortOrder, setSortOrder, getFilterData, setFilterData, getGroupData, setGroupData, getSummaryData, setSummaryData, getPagingData, setPagingData, getPageSize, setPageSize, getCurrentPage, setCurrentPage, getTotalCount, setTotalCount, getPageCount, setPageCount, getPageInfo, setPageInfo
- **속성**: text, value, visible, enabled, readOnly, width, height, style, data, columns, rows, selectedIndex, selectedIndices, selectedRow, selectedRows, currentRow, currentColumn, rowCount, columnCount, pageSize, currentPage, totalCount, pageCount, sortColumn, sortOrder, filterData, groupData, summaryData, pagingData, editable, selectable, multiSelect, checkable, expandable, resizable, draggable, droppable, scrollable, paging, sorting, filtering, grouping, summarizing, exporting, importing, printing
- **이벤트**: onCellClick, onCellDoubleClick, onCellRightClick, onHeaderClick, onRowClick, onRowDoubleClick, onRowRightClick, onSelectionChanged, onDataChanged, onCellEdit, onCellEditEnd, onCellEditCancel, onRowAdded, onRowDeleted, onRowUpdated, onColumnResized, onColumnMoved, onColumnSorted, onColumnFiltered, onColumnGrouped, onPageChanged, onPageSizeChanged, onScroll, onFocus, onBlur, onKeyDown, onKeyUp

#### Button 컨트롤 (button, btn 패턴)
- **메서드**: setText, getText, enable, disable, show, hide, focus, blur, click, setIcon, getIcon, setIconAlign, getIconAlign, setButtonType, getButtonType, setImage, getImage, setImageAlign, getImageAlign, setTooltip, getTooltip
- **속성**: text, value, visible, enabled, readOnly, width, height, style, icon, iconAlign, buttonType, image, imageAlign, tooltip, defaultButton, cancelButton, flat, raised, outlined, textOnly, iconOnly, textAndIcon
- **이벤트**: onClick, onDoubleClick, onRightClick, onMouseDown, onMouseUp, onMouseOver, onMouseOut, onFocus, onBlur, onKeyDown, onKeyUp

#### Calendar 컨트롤 (calendar, cal 패턴)
- **메서드**: setDate, getDate, setValue, getValue, enable, disable, show, hide, focus, blur, setMinDate, getMinDate, setMaxDate, getMaxDate, setFirstDayOfWeek, getFirstDayOfWeek, setCalendarType, getCalendarType, setDateFormat, getDateFormat, setTimeFormat, getTimeFormat, setShowTime, getShowTime, setShowToday, getShowToday, setShowWeekNumbers, getShowWeekNumbers
- **속성**: text, value, visible, enabled, readOnly, width, height, style, date, minDate, maxDate, firstDayOfWeek, calendarType, dateFormat, timeFormat, showTime, showToday, showWeekNumbers, todayButton, clearButton, okButton, cancelButton
- **이벤트**: onDateChanged, onDateSelected, onMonthChanged, onYearChanged, onTimeChanged, onTodayClicked, onClearClicked, onOkClicked, onCancelClicked, onFocus, onBlur

#### ComboBox 컨트롤 (cmb 패턴)
- **메서드**: addItem, deleteItem, updateItem, getItem, getData, setData, clear, refresh, getSelected, setSelected, getChecked, setChecked, enable, disable, show, hide, focus, blur, openDropdown, closeDropdown, getSelectedIndex, setSelectedIndex, getSelectedValue, setSelectedValue, getSelectedText, setSelectedText, getItemCount, getItemText, setItemText, getItemValue, setItemValue, getItemData, setItemData, getItemIndex, setItemIndex, getItemByValue, getItemByText, getItemByIndex
- **속성**: text, value, visible, enabled, readOnly, width, height, style, items, selectedIndex, selectedValue, selectedText, dropdownVisible, itemCount, maxDropDownItems, dropDownWidth, dropDownHeight, autoComplete, caseSensitive, filterMode, sortMode, editable, allowCustom, allowNull, placeholder
- **이벤트**: onClick, onDoubleClick, onRightClick, onSelectionChanged, onDropdownOpened, onDropdownClosed, onItemSelected, onItemDeselected, onTextChanged, onFocus, onBlur

#### CheckBox 컨트롤 (cbx 패턴)
- **메서드**: setChecked, getChecked, setText, getText, enable, disable, show, hide, focus, blur, setCheckType, getCheckType, setTextAlign, getTextAlign, setGroupName, getGroupName
- **속성**: text, value, visible, enabled, readOnly, width, height, style, checked, checkType, textAlign, groupName, threeState, indeterminate, autoCheck, allowGrayed, flat, raised, outlined
- **이벤트**: onClick, onDoubleClick, onRightClick, onCheckedChanged, onIndeterminateChanged, onFocus, onBlur, onKeyDown, onKeyUp

#### Tree 컨트롤 (tre 패턴)
- **메서드**: addNode, deleteNode, updateNode, getNode, getData, setData, clear, refresh, getSelected, setSelected, getChecked, setChecked, getExpanded, setExpanded, scrollTo, scrollIntoView, enable, disable, show, hide, focus, blur, expandAll, collapseAll, getRootNode, getChildNodes, getParentNode, getSiblingNodes, getNodeByText, getNodeByValue, getNodeByIndex, getNodePath, setNodePath, getNodeLevel, setNodeLevel, getNodeIcon, setNodeIcon, getNodeTooltip, setNodeTooltip
- **속성**: text, value, visible, enabled, readOnly, width, height, style, data, selectedNode, selectedNodes, expandedNodes, checkedNodes, rootNode, nodeCount, levelCount, showLines, showRootLines, showButtons, showCheckBoxes, showIcons, showTooltips, allowDrag, allowDrop, allowEdit, allowDelete, allowMultiSelect, allowCheckBoxes, allowExpandAll, allowCollapseAll
- **이벤트**: onNodeClick, onNodeDoubleClick, onNodeRightClick, onNodeSelected, onNodeDeselected, onNodeExpanded, onNodeCollapsed, onNodeChecked, onNodeUnchecked, onNodeAdded, onNodeDeleted, onNodeUpdated, onNodeMoved, onNodeEdited, onFocus, onBlur

#### InputBox 컨트롤 (ipb 패턴)
- **메서드**: setValue, getValue, setText, getText, enable, disable, show, hide, focus, blur, setMaxLength, getMaxLength, setPlaceholder, getPlaceholder, setInputType, getInputType, setPattern, getPattern, setRequired, getRequired, setReadOnly, getReadOnly, setAutoComplete, getAutoComplete, setAutoFocus, getAutoFocus, setSpellCheck, getSpellCheck
- **속성**: text, value, visible, enabled, readOnly, width, height, style, maxLength, placeholder, inputType, pattern, required, autoComplete, autoFocus, spellCheck, min, max, step, size, multiple, accept
- **이벤트**: onValueChanged, onTextChanged, onKeyDown, onKeyUp, onKeyPress, onInput, onChange, onFocus, onBlur, onSelect, onInvalid, onReset, onSubmit

#### TextArea 컨트롤 (txa 패턴)
- **메서드**: setValue, getValue, setText, getText, enable, disable, show, hide, focus, blur, setMaxLength, getMaxLength, setPlaceholder, getPlaceholder, setRows, getRows, setCols, getCols, setWrap, getWrap, setResize, getResize, setSpellCheck, getSpellCheck
- **속성**: text, value, visible, enabled, readOnly, width, height, style, maxLength, placeholder, rows, cols, wrap, resize, spellCheck, autoComplete, autoFocus, required, name, form, minLength, maxLength
- **이벤트**: onValueChanged, onTextChanged, onKeyDown, onKeyUp, onKeyPress, onInput, onChange, onFocus, onBlur, onSelect, onInvalid, onReset, onSubmit

#### 공통 API (모든 컨트롤에서 사용 가능)
- **메서드**: setValue, getValue, setText, getText, enable, disable, show, hide, focus, blur, setVisible, getVisible, setEnabled, getEnabled, setReadOnly, getReadOnly, setWidth, getWidth, setHeight, getHeight, setStyle, getStyle, setData, getData, refresh, clear, reset, validate, isValid, getParent, getChild, getChildren, getSibling, getSiblings, getRoot, getAncestor, getDescendant, getFirstChild, getLastChild, getNextSibling, getPreviousSibling, addChild, removeChild, insertChild
- **속성**: text, value, visible, enabled, readOnly, width, height, style, data, name, id, className, tagName, parentNode, childNodes, firstChild, lastChild, nextSibling, previousSibling, nodeType, nodeValue, nodeName, attributes
- **이벤트**: onLoad, onUnload, onClick, onDoubleClick, onRightClick, onMouseDown, onMouseUp, onMouseOver, onMouseOut, onMouseMove, onMouseEnter, onMouseLeave, onFocus, onBlur, onKeyDown, onKeyUp, onKeyPress, onChange, onSelect, onInput, onInvalid, onReset, onSubmit, onError, onAbort, onLoad, onUnload, onResize, onScroll, onContextMenu

#### 메시지 API
- **메서드**: showMessage, showConfirm, showAlert, showError, showWarning, showInfo, showSuccess, showQuestion, showInput, showSelect, showFileDialog, showColorDialog, showFontDialog, openPopup, closePopup, showPopup, hidePopup, setPopupPosition, getPopupPosition, setPopupSize, getPopupSize, setPopupTitle, getPopupTitle, setPopupContent, getPopupContent

#### 데이터 API
- **메서드**: getData, setData, getJsonData, setJsonData, getXmlData, setXmlData, getCsvData, setCsvData, loadData, saveData, exportData, importData, validateData, transformData, filterData, sortData, groupData, aggregateData, calculateData, mergeData, splitData, cloneData

### 3. 오류 검사
- **null/undefined 참조 오류**: getElementById, querySelector 결과가 null일 수 있는 경우
- **XSS 보안 위험**: innerHTML 사용시 XSS 위험
- **JSON 파싱 오류**: JSON.parse try-catch 없음
- **배열 인덱스 오류**: split, charAt, substring 등 인덱스 오류 가능성
- **타입 변환 오류**: parseInt, parseFloat 등 잘못된 문자열 처리
- **비동기 처리 오류**: setTimeout, setInterval 등 콜백 함수 오류
- **DOM 조작 오류**: getAttribute, setAttribute 등 요소 null 오류
- **스크롤 관련 오류**: scrollTo, scrollBy 등 좌표 오류

### 4. 실행 흐름 (프로세스 중심)
- **함수별 프로세스 분석**: 각 함수의 목적과 작업을 명확하게 설명
- **이벤트 핸들러 감지**: this.onXXX 형태의 이벤트 핸들러
- **비동기 작업 감지**: setTimeout, setInterval, fetch, Promise, async, await
- **전체 프로세스 요약**: 함수 개수, 이벤트 핸들러 개수, 비동기 작업 개수

## ⚡ 성능 최적화

### 배치 처리 성능
- **작은 파일 (≤1000줄)**: 일반 분석 사용
- **중간 파일 (1000-10000줄)**: 1000줄 배치
- **큰 파일 (10000-50000줄)**: 2000줄 배치  
- **매우 큰 파일 (>50000줄)**: 5000줄 배치

### 분석 모드
- **일반 모드**: 상세한 분석 (기본값)
- **빠른 모드**: 기본 분석만 수행 (fast_mode: true)

## 📝 예제

### 기본 JavaScript 예제
```javascript
function calculateSum(a, b) {
    if (a == null || b == undefined) {
        return 0;
    }
    return a + b;
}

const result = calculateSum(5, 3);
console.log(result);
```

**분석 결과:**
- **JavaScript 문제점**: 
  - 라인 2: null 비교시 === 사용 권장
  - 라인 6: console.log는 프로덕션에서 제거해야 합니다
- **eXBuilder6 API**: eXBuilder6 API 사용에 문제없음
- **오류**: 발견된 오류 없음
- **실행 흐름**: calculateSum 함수: 일반 처리 - 조건에 따라 분기합니다

### eXBuilder6 예제
```javascript
function onFi1ValueChange() {
    const fileinput1 = app.lookup("fi1");
    const vaFiles = fileinput1.files;
    const submit = app.lookup("submission1");
    
    for (let i = 0; i < vaFiles.length; i++) {
        const voFile = vaFiles[i];
        submit.addFileParameter("file" + i, voFile);
    }
}

function onBtnInitClick() {
    const grid = app.lookup("grd1");
    grid.addRow();
    grid.setValue("column1", "test");
    
    const button = app.lookup("btn1");
    button.setText("Click me");
}
```

**분석 결과:**
- **JavaScript 문제점**: JavaScript 문법에 문제없음
- **eXBuilder6 API**: eXBuilder6 API 사용에 문제없음
- **오류**: 발견된 오류 없음
- **실행 흐름**: 
  - onFi1ValueChange 함수: 파일 처리 - 컨트롤 객체를 찾습니다, 파일 처리를 수행합니다, 반복 작업을 수행합니다
  - onBtnInitClick 함수: 초기화 - 컨트롤 객체를 찾습니다, 컨트롤 값을 설정/가져옵니다, 데이터 행을 관리합니다

## 🔧 설치 및 실행

### 1. 의존성 설치
```bash
pip install fastapi uvicorn requests
```

### 2. 서버 실행
```bash
python -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

### 3. 테스트 실행
```bash
python test_improved_analyzer.py
```

## 📚 참고 자료

- **eXBuilder6 API Reference**: http://edu.tomatosystem.co.kr:8081/help/nav/0_10
- **eXBuilder6 Properties**: http://edu.tomatosystem.co.kr:8081/help/nav/0_7_4_0
- **eXBuilder6 Help Contents**: frontend/ref/eXBuilder6_HelpContents.pdf

## 🆕 최신 업데이트

### v2.0.0 (2024-01-XX)
- ✅ 정확한 라인 위치 표시 기능 추가
- ✅ eXBuilder6 API 검증 로직 개선
- ✅ 프로세스 중심 실행 흐름 분석
- ✅ 대용량 파일 배치 처리 기능
- ✅ 성능 최적화 및 메모리 효율성 개선
- ✅ 상세한 한글 설명 및 문서화
