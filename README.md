# ScriptSense - eXBuilder6 JavaScript 분석기

ScriptSense는 eXBuilder6 환경에서 작성된 JavaScript 코드를 분석하고 개선점을 제안하는 도구입니다.

## 🚀 주요 기능

### 기본 분석기 (`/api/js`)
- JavaScript 문법/로직 문제점 검사
- eXBuilder6 API 사용 여부 검사
- 잠재적 오류 검사
- 실행 흐름 분석

### 🆕 향상된 분석기 (`/api/enhanced-js`)
- **구조화된 분석 결과**: 심각도별 이슈 분류 및 통계
- **성능 최적화**: 비동기 처리 및 정규표현식 캐싱
- **정확한 위치 추적**: 라인 번호 및 컬럼 위치 제공
- **스마트 제안**: 카테고리별 개선 제안사항
- **설정 관리**: YAML 기반 API 정보 관리
- **향상된 파싱**: 주석 및 문자열을 고려한 정확한 분석

## 📁 프로젝트 구조

```
ScriptSense/
├── backend/
│   ├── enhanced_js_analyzer.py    # 🆕 향상된 분석기
│   ├── js_analyzer.py             # 기본 분석기
│   ├── config/
│   │   └── exbuilder6.yaml        # 🆕 API 설정 파일
│   ├── main.py
│   └── requirements.txt
├── frontend/
│   └── src/
│       └── components/
│           └── ReviewResult.tsx
├── test_enhanced_analyzer.py      # 🆕 향상된 분석기 테스트
└── README.md
```

## 🔧 설치 및 실행

### 1. 의존성 설치
```bash
cd backend
pip install -r requirements.txt
```

### 2. 서버 실행
```bash
cd backend
uvicorn main:app --reload
```

### 3. 테스트 실행
```bash
python test_enhanced_analyzer.py
```

## 📊 API 엔드포인트

### 기본 분석기
- `POST /api/js/analyze` - JavaScript 코드 분석
- `POST /api/js/analyze/file` - JavaScript 파일 분석
- `POST /api/js/analyze/detailed` - 상세 분석 (LLM 포함)

### 🆕 향상된 분석기
- `POST /api/enhanced-js/analyze` - 향상된 JavaScript 코드 분석
- `POST /api/enhanced-js/analyze/file` - 향상된 JavaScript 파일 분석
- `POST /api/enhanced-js/analyze/detailed` - 향상된 상세 분석 (LLM 포함)

## 🎯 향상된 분석기 주요 개선사항

### 1. **중복 코드 제거 및 최적화**
- 에러 패턴을 카테고리별로 정리하여 중복 제거
- 정규표현식 패턴 사전 컴파일로 성능 향상
- `@lru_cache` 데코레이터를 통한 메모이제이션

### 2. **eXBuilder6 API 검증 로직 개선**
- 동적 컨트롤 ID 처리 지원
- 정확한 prefix 매칭 및 추가 검증
- YAML 설정 파일을 통한 API 정보 관리

### 3. **JavaScript 문법 검사 정확도 향상**
- 주석과 문자열을 고려한 정확한 파싱
- 이스케이프 문자 처리
- 라인별 정확한 위치 추적

### 4. **분석 결과 구조화 개선**
- `AnalysisIssue` 모델을 통한 구조화된 결과
- 심각도별 분류 (Critical, High, Medium, Low, Info)
- 라인 번호, 컬럼 위치, 제안사항 포함

### 5. **성능 최적화**
- 비동기 처리로 병렬 분석 수행
- ThreadPoolExecutor를 통한 멀티스레딩
- 대용량 코드 처리 최적화

### 6. **설정 관리 개선**
- YAML 파일을 통한 API 정보 외부화
- 버전별 API 정보 관리
- 런타임 API 정보 업데이트 지원

### 7. **에러 처리 및 로깅 강화**
- 컨텍스트 매니저를 통한 에러 처리
- 구조화된 로깅
- 상세한 에러 메시지 제공

## 📈 분석 결과 예시

### 향상된 분석기 응답 형식
```json
{
  "issues": [
    {
      "category": "xss_security",
      "severity": "critical",
      "message": "innerHTML 사용시 XSS 위험이 있습니다",
      "line_number": 15,
      "column": 25,
      "suggestion": "innerText나 textContent를 사용하거나 입력값을 sanitize하세요."
    }
  ],
  "statistics": {
    "total_issues": 5,
    "critical_issues": 1,
    "high_issues": 2,
    "medium_issues": 1,
    "low_issues": 1
  },
  "execution_flow": [
    "onLoad 함수: 초기화 - 컨트롤 객체를 찾습니다, 데이터를 처리합니다",
    "이벤트 핸들러: onClick"
  ],
  "recommendations": [
    "보안 위험이 있는 코드를 즉시 수정하세요.",
    "높은 우선순위 이슈들을 우선적으로 해결하세요."
  ]
}
```

## 🔍 지원하는 eXBuilder6 컨트롤

- **Grid (grd)**: 데이터 그리드 컨트롤
- **Button (btn)**: 버튼 컨트롤
- **ComboBox (cmb)**: 콤보박스 컨트롤
- **CheckBox (cbx)**: 체크박스 컨트롤
- **InputBox (ipb)**: 입력박스 컨트롤
- **TextArea (txa)**: 텍스트 영역 컨트롤
- **Tree (tre)**: 트리 컨트롤
- **Calendar (cal)**: 캘린더 컨트롤

## 🛠️ 개발 및 테스트

### 테스트 실행
```bash
# 향상된 분석기 테스트
python test_enhanced_analyzer.py

# 개별 컴포넌트 테스트
python -c "
from backend.enhanced_js_analyzer import ConfigManager
config = ConfigManager()
print('설정 로드 성공:', bool(config.config))
"
```

### 설정 파일 수정
`backend/config/exbuilder6.yaml` 파일을 수정하여 새로운 API 정보를 추가하거나 기존 정보를 업데이트할 수 있습니다.

## 📝 사용 예시

### JavaScript 코드 분석
```python
import requests

# 향상된 분석기 사용
response = requests.post("http://localhost:8000/api/enhanced-js/analyze", 
    json={
        "code": """
        function onLoad() {
            var grid = app.lookup("grdMain");
            grid.addRow();
        }
        """,
        "fast_mode": False
    }
)

result = response.json()
print(f"발견된 이슈: {result['statistics']['total_issues']}개")
```

## 🤝 기여하기

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다.

## 🆕 업데이트 로그

### v2.0.0 - 향상된 분석기 출시
- 구조화된 분석 결과 제공
- 성능 최적화 및 비동기 처리
- 정확한 위치 추적 및 제안사항
- YAML 기반 설정 관리
- 향상된 에러 처리 및 로깅

### v1.0.0 - 기본 분석기
- JavaScript 문법 검사
- eXBuilder6 API 검증
- 기본 오류 검사
- 실행 흐름 분석