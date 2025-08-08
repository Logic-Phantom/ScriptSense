// eXBuilder6 API 사용 예제 (API Reference 기반)
this.onLoad = function() {
    // app.lookup으로 컨트롤 찾기 (XML 설정 기반 네이밍 패턴)
    const grdData = app.lookup('grdData');
    const buttonSave = app.lookup('buttonSave');
    const calendarDate = app.lookup('calendarDate');
    
    grdData.addRow({id: 1, name: 'Test'});
    buttonSave.setText('저장');
    calendarDate.setMinDate('2024-01-01');
    calendarDate.setMaxDate('2024-12-31');
    showMessage('데이터가 로드되었습니다.');
};

this.onClick = function() {
    const grdData = app.lookup('grdData');
    const cmbCategory = app.lookup('cmbCategory');
    
    const selectedItem = cmbCategory.getSelected();
    if (selectedItem) {
        grdData.refresh();
        cmbCategory.openDropdown();
    }
};

// 일반 JavaScript 함수 (eXBuilder6 API 아님)
function insertRowData() {
    // 일반 JavaScript 함수
    console.log('데이터 삽입 중...');
    
    const element = document.getElementById('output');
    element.innerHTML = '데이터가 삽입되었습니다.';
    
    try {
        const jsonData = JSON.parse('{"test": "data"}');
        console.log(jsonData);
    } catch (e) {
        console.error('JSON 파싱 오류:', e);
    }
}

// eXBuilder6 Tree API 사용
this.onTreeSelect = function() {
    const treMenu = app.lookup('treMenu');
    const ipbSearch = app.lookup('ipbSearch');
    
    const selectedNode = treMenu.getSelected();
    if (selectedNode) {
        ipbSearch.setValue(selectedNode.text);
        ipbSearch.setMaxLength(100);
        ipbSearch.setPlaceholder('검색어를 입력하세요');
        showInfo('노드가 선택되었습니다.');
    }
};

// eXBuilder6 Combo API 사용
this.onComboChange = function() {
    const cmbCategory = app.lookup('cmbCategory');
    const grdData = app.lookup('grdData');
    
    const selectedItem = cmbCategory.getSelected();
    grdData.setData(selectedItem.data);
    cmbCategory.closeDropdown();
};

// Button 컨트롤 사용
this.onButtonClick = function() {
    const buttonSave = app.lookup('buttonSave');
    const ipbName = app.lookup('ipbName');
    
    buttonSave.setText('저장 중...');
    buttonSave.disable();
    buttonSave.click();
    
    const name = ipbName.getValue();
    if (name) {
        showMessage('저장되었습니다.');
    }
    
    buttonSave.setText('저장');
    buttonSave.enable();
};

// CheckBox 컨트롤 사용
this.onCheckBoxChange = function() {
    const cbxAgree = app.lookup('cbxAgree');
    const buttonSubmit = app.lookup('buttonSubmit');
    
    if (cbxAgree.getChecked()) {
        buttonSubmit.enable();
    } else {
        buttonSubmit.disable();
    }
};

// Calendar 컨트롤 사용
this.onCalendarSelect = function() {
    const calendarDate = app.lookup('calendarDate');
    const ipbDate = app.lookup('ipbDate');
    
    const selectedDate = calendarDate.getDate();
    ipbDate.setValue(selectedDate);
    calendarDate.setFirstDayOfWeek(1); // 월요일부터 시작
};

// FileUpload 컨트롤 사용
this.onFileUpload = function() {
    const fudFiles = app.lookup('fudFiles');
    const pgrUpload = app.lookup('pgrUpload');
    
    fudFiles.addFile('test.txt', fileObject);
    pgrUpload.setValue(50);
    pgrUpload.setMinValue(0);
    pgrUpload.setMaxValue(100);
};

// NumberEditor 컨트롤 사용
this.onNumberChange = function() {
    const nbeAmount = app.lookup('nbeAmount');
    
    nbeAmount.setMinValue(0);
    nbeAmount.setMaxValue(1000000);
    nbeAmount.setDecimalPlaces(2);
    const value = nbeAmount.getValue();
};

// SearchInput 컨트롤 사용
this.onSearch = function() {
    const sipSearch = app.lookup('sipSearch');
    
    sipSearch.setSearchDelay(500);
    sipSearch.search();
    const searchText = sipSearch.getValue();
};

// Slider 컨트롤 사용
this.onSliderMove = function() {
    const sldVolume = app.lookup('sldVolume');
    
    sldVolume.setMinValue(0);
    sldVolume.setMaxValue(100);
    sldVolume.setStep(5);
    const volume = sldVolume.getValue();
};

// TabFolder 컨트롤 사용
this.onTabChange = function() {
    const tabMain = app.lookup('tabMain');
    
    tabMain.addTab('새 탭', 'newTab');
    const activeTab = tabMain.getActiveTab();
    tabMain.setActiveTab('newTab');
};

// TextArea 컨트롤 사용
this.onTextAreaChange = function() {
    const txaDescription = app.lookup('txaDescription');
    
    txaDescription.setMaxLength(1000);
    txaDescription.setPlaceholder('설명을 입력하세요');
    txaDescription.setRows(5);
    const text = txaDescription.getValue();
};

// MaskEditor 컨트롤 사용
this.onMaskEditorChange = function() {
    const msePhone = app.lookup('msePhone');
    
    msePhone.setMask('000-0000-0000');
    msePhone.setPromptChar('_');
    const phone = msePhone.getValue();
};

// 이벤트 핸들러들
this.onCellClick = function(e) {
    const grdData = app.lookup('grdData');
    const cellInfo = grdData.getCellInfo(e.rowIndex, e.colIndex);
    showMessage(`셀 클릭: ${cellInfo.text}`);
};

this.onDateChanged = function(e) {
    const calendarDate = app.lookup('calendarDate');
    const selectedDate = calendarDate.getDate();
    showInfo(`날짜 변경: ${selectedDate}`);
};

this.onFileSelected = function(e) {
    const fiFile = app.lookup('fiFile');
    const files = fiFile.getFiles();
    showMessage(`${files.length}개 파일이 선택되었습니다.`);
};

this.onValueChanged = function(e) {
    const ipbName = app.lookup('ipbName');
    const newValue = ipbName.getValue();
    showInfo(`값 변경: ${newValue}`);
};

this.onSearch = function(e) {
    const sipSearch = app.lookup('sipSearch');
    const searchText = sipSearch.getValue();
    showMessage(`검색: ${searchText}`);
};

this.onNodeSelected = function(e) {
    const treMenu = app.lookup('treMenu');
    const selectedNode = treMenu.getSelected();
    showInfo(`노드 선택: ${selectedNode.text}`);
};
