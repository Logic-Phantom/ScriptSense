from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from pydantic import BaseModel
from typing import Optional
from llm_client import request_llm, request_llm_fast

router = APIRouter()

PROMPT_TEMPLATE = """
당신은 JavaScript 코드 리뷰 전문가입니다. 다음 코드를 정확히 분석하여 마크다운 형식으로 답변해주세요.

**코드 유형**: 이 코드는 특정 UI 솔루션의 API를 사용하는 JavaScript 코드입니다. `app.lookup()`, `addFileParameter()` 등의 메서드는 해당 UI 솔루션의 전용 API입니다.

**eXBuilder6 API 참고사항** (해당하는 경우):
- `cpr.controls`: UI 컨트롤 관련 API
- `cpr.core`: 핵심 기능 API  
- `cpr.events`: 이벤트 처리 API
- `cpr.data`: 데이터 처리 API
- `app.lookup()`: 컴포넌트 조회
- `addFileParameter()`: 파일 파라미터 추가

**분석 요구사항:**
1. **코드 스타일 및 오류 분석**: 
   - JavaScript 문법 오류
   - 변수명 오타 (예: `subFIle` → `submit`)
   - 코드 스타일 문제
   - UI 솔루션 API 사용법 오류
   - eXBuilder6 API 사용법 검증

2. **구체적인 리팩토링 제안**: 
   - 실제 개선 가능한 부분만 제시
   - UI 솔루션 API의 올바른 사용법 제안
   - eXBuilder6 모범 사례 적용

3. **실행 흐름 설명**: 
   - 코드가 실제로 어떻게 동작하는지 단계별로 설명
   - UI 솔루션 API 호출 흐름 포함
   - eXBuilder6 이벤트 처리 흐름

**중요**: 
- 코드에 실제로 존재하는 내용만 분석
- 존재하지 않는 속성이나 메서드는 언급하지 마세요
- UI 솔루션의 전용 API임을 고려하여 분석
- eXBuilder6 API 문서 참조: http://edu.tomatosystem.co.kr:8081/help/nav/0_10

```javascript
{code}
```

**응답 형식:**
## 1. 코드 스타일 및 오류 분석
- JavaScript 문법 및 스타일 문제
- UI 솔루션 API 사용법 문제
- eXBuilder6 API 사용법 검증

## 2. 리팩토링 제안  
- 구체적인 개선 방안
- UI 솔루션 API 최적화 제안
- eXBuilder6 모범 사례 적용

## 3. 실행 흐름
1단계: ...
2단계: ...
"""

class ReviewRequest(BaseModel):
    code: str
    fast_mode: bool = False  # 빠른 모드 (토큰 수 제한)
    ui_framework: str = "generic"  # UI 프레임워크 타입 (generic, nexacro, etc.)

@router.post("/text")
async def review_code(request: ReviewRequest):
    print(f"[LOG] /api/review/text called (ui_framework: {request.ui_framework})")
    
    # UI 프레임워크별 프롬프트 커스터마이징
    if request.ui_framework.lower() == "nexacro":
        prompt = PROMPT_TEMPLATE.replace("특정 UI 솔루션", "Nexacro Platform").format(code=request.code)
    elif request.ui_framework.lower() == "exbuilder":
        prompt = PROMPT_TEMPLATE.replace("특정 UI 솔루션", "eXBuilder6").replace("`app.lookup()`, `addFileParameter()` 등의 메서드는 해당 UI 솔루션의 전용 API입니다.", "`app.lookup()`, `addFileParameter()` 등의 메서드는 eXBuilder6의 전용 API입니다. eXBuilder6는 cpr.controls, cpr.core, cpr.events 등의 네임스페이스를 사용합니다.").format(code=request.code)
    else:
        prompt = PROMPT_TEMPLATE.format(code=request.code)
    
    print(f"[LOG] Prompt generated. Calling LLM... (fast_mode: {request.fast_mode})")
    result = request_llm_fast(prompt) if request.fast_mode else request_llm(prompt)
    print("[LOG] LLM call finished. Returning result.")
    return {"result": result}

@router.post("/file")
async def review_file(file: UploadFile = File(...), fast_mode: bool = False):
    print(f"[LOG] /api/review/file called (fast_mode: {fast_mode})")
    if not file.filename.endswith('.js'):
        print("[LOG] File extension not allowed.")
        raise HTTPException(status_code=400, detail=".js 파일만 업로드 가능합니다.")
    code = (await file.read()).decode("utf-8")
    prompt = PROMPT_TEMPLATE.format(code=code)
    print(f"[LOG] Prompt generated from file. Calling LLM... (fast_mode: {fast_mode})")
    result = request_llm_fast(prompt) if fast_mode else request_llm(prompt)
    print("[LOG] LLM call finished. Returning result.")
    return {"result": result}

@router.post("/file/fast")
async def review_file_fast(file: UploadFile = File(...)):
    """빠른 파일 리뷰 (토큰 수 제한)"""
    return await review_file(file, fast_mode=True)