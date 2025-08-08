# ScriptSense: JavaScript 코드 자동 리뷰 & 분석

LM Studio를 활용한 JavaScript 코드 자동 분석 도구입니다. 코드의 문제점을 찾고, eXBuilder6 API 사용 여부를 확인하며, 실행 흐름을 분석합니다.

## 주요 기능

### 1. 일반 리뷰 모드
- eXBuilder6 코드 분석
- 오류 지점, 경고 지점, 개선 제안, 실행 흐름 분석
- LM Studio를 활용한 고급 분석

### 2. JavaScript 분석 모드 (신규)
- **JavaScript 문법/로직 문제점**: 전통적인 JavaScript 관점에서의 문제점
- **eXBuilder6 API 사용 여부**: eXBuilder6 프레임워크 API 사용 여부
- **오류 검사**: 잠재적 오류 및 보안 위험 요소
- **실행 흐름**: 코드의 실행 과정 분석

## 설치 및 실행

### 1. LM Studio 설정
```bash
# LM Studio 설정 스크립트 실행
./set_lmstudio.ps1
```

### 2. 서버 실행
```bash
# 전체 서버 실행 (백엔드 + 프론트엔드)
./run_all.ps1
```

### 3. 서버 종료
```bash
# 서버 종료
./run_stop.ps1
```

## 사용 방법

### 웹 인터페이스
1. 브라우저에서 `http://localhost:3000` 접속
2. 분석 모드 선택:
   - **일반 리뷰**: eXBuilder6 코드 분석
   - **JavaScript 분석**: JavaScript 코드 분석
3. 코드 입력 또는 파일 업로드
4. 분석 실행

### API 사용

#### JavaScript 분석 API
```bash
# 코드 분석
curl -X POST "http://localhost:8000/api/js/analyze" \
  -H "Content-Type: application/json" \
  -d '{"code": "function test() { console.log(\"Hello\"); }", "fast_mode": false}'

# 파일 분석
curl -X POST "http://localhost:8000/api/js/analyze/file" \
  -F "file=@your-script.js"
```

#### 일반 리뷰 API
```bash
# 코드 리뷰
curl -X POST "http://localhost:8000/api/review/text" \
  -H "Content-Type: application/json" \
  -d '{"code": "your code here"}'
```

## JavaScript 분석 항목 상세

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

### JavaScript 분석 예제
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

## 프로젝트 구조

```
ScriptSense/
├── backend/
│   ├── main.py              # FastAPI 메인 앱
│   ├── review.py            # 일반 리뷰 API
│   ├── js_analyzer.py       # JavaScript 분석 API (신규)
│   ├── llm_client.py        # LM Studio 클라이언트
│   └── config_llm.py        # LLM 설정
├── frontend/
│   └── src/
│       └── App.tsx          # React 앱 (JavaScript 분석 기능 포함)
├── run_all.ps1              # 서버 실행 스크립트
├── run_stop.ps1             # 서버 종료 스크립트
└── set_lmstudio.ps1         # LM Studio 설정 스크립트
```

## 라이선스

이 프로젝트는 MIT 라이선스 하에 제공됩니다.