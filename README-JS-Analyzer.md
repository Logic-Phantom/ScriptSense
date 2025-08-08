# JavaScript 코드 분석 도구

이 도구는 JavaScript 코드를 분석하여 다음 4가지 항목으로 결과를 제공합니다:

1. **JavaScript 문법/로직 문제점** - 전통적인 JavaScript 관점에서의 문제점
2. **eXBuilder6 API 사용 여부** - eXBuilder6 프레임워크 API 사용 여부
3. **오류 검사** - 잠재적 오류 및 보안 위험 요소
4. **실행 흐름** - 코드의 실행 과정 분석

## 사용 방법

### 1. 웹 브라우저에서 사용

1. `js-analyzer-demo.html` 파일을 브라우저에서 열기
2. 분석할 JavaScript 코드를 텍스트 영역에 입력
3. "코드 분석" 버튼 클릭
4. 결과 확인

### 2. Node.js에서 사용

```javascript
const { analyzeJavaScriptCode } = require('./js-analyzer.js');

const code = `
function example() {
    console.log("Hello World");
    this.form.setValue('field1', 'test');
}
`;

const result = analyzeJavaScriptCode(code);
console.log(result);
```

### 3. 파일에서 직접 분석

```javascript
const { analyzeJavaScriptFile } = require('./js-analyzer.js');

const result = analyzeJavaScriptFile('./your-script.js');
console.log(result);
```

## 분석 항목 상세

### 1. JavaScript 문법/로직 문제점
- 문법 오류 검사
- undefined 불필요한 할당
- null/undefined 비교시 === 사용 권장
- console.log 프로덕션 제거 필요
- eval() 보안 위험
- setTimeout(,0) 대신 setImmediate 권장

### 2. eXBuilder6 API 사용 여부
다음 API들의 사용 여부를 검사합니다:
- `this.form`, `this.grid`, `this.tree`, `this.combo`
- `this.onLoad`, `this.onClick`, `this.onChange`
- `this.getValue`, `this.setValue`, `this.getData`, `this.setData`
- `this.addRow`, `this.deleteRow`, `this.updateRow`
- `this.showMessage`, `this.showConfirm`, `this.showAlert`
- 기타 eXBuilder6 관련 API들

### 3. 오류 검사
- getElementById/querySelector null 참조 가능성
- innerHTML XSS 위험
- JSON.parse try-catch 없음
- split 결과 빈 배열 가능성

### 4. 실행 흐름
- 함수 정의
- 이벤트 리스너
- 비동기 작업 (setTimeout, fetch, Promise 등)
- 조건부 실행 (if, switch 등)
- 반복 실행 (for, while 등)

## 예제

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
- JavaScript 문제점: null 비교시 === 사용 권장, console.log 프로덕션 제거 필요
- eXBuilder6 API: 사용 안함
- 오류: 발견된 오류 없음
- 실행 흐름: 함수 정의, 조건부 실행

### eXBuilder6 예제
```javascript
this.onLoad = function() {
    this.form.setValue('field1', 'Hello');
    this.grid.addRow({id: 1, name: 'Test'});
    this.showMessage('데이터가 로드되었습니다.');
};
```

**분석 결과:**
- JavaScript 문제점: 발견된 문제점 없음
- eXBuilder6 API: this.form.setValue, this.grid.addRow, this.showMessage
- 오류: 발견된 오류 없음
- 실행 흐름: 함수 정의

## 파일 구조

- `js-analyzer.js` - 메인 분석 도구
- `js-analyzer-demo.html` - 웹 인터페이스
- `README-JS-Analyzer.md` - 사용법 설명서

## 라이선스

이 도구는 MIT 라이선스 하에 제공됩니다.
