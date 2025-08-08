from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from pydantic import BaseModel
from typing import Optional
from llm_client import request_llm, request_llm_fast

router = APIRouter()

PROMPT_TEMPLATE = """
eXBuilder6 코드 분석: 다음 코드를 분석하세요.

**분석:**
1. 오류 지점 (문법, 타입, API 오류)
2. 경고 지점 (성능, 스타일, 잠재적 문제)
3. 개선 제안 (구체적 수정 코드)
4. 실행 흐름 (단계별 동작 과정)

**중요**: 실제 발견된 문제만 언급, 라인 번호 명시

```javascript
{code}
```

**응답:**
## 1. 오류 지점
- **라인 X**: 구체적 오류

## 2. 경고 지점  
- **라인 X**: 구체적 경고

## 3. 개선 제안
- 구체적 수정 코드

## 4. 실행 흐름
- 단계별 상세 동작 과정
"""

class ReviewRequest(BaseModel):
    code: str
    fast_mode: bool = False  # 빠른 모드 (토큰 수 제한)
    ui_framework: str = "generic"  # UI 프레임워크 타입 (generic, nexacro, etc.)

@router.post("/text")
async def review_code(request: ReviewRequest):
    print(f"[LOG] /api/review/text called (ui_framework: {request.ui_framework})")
    
    # 코드 길이 확인 및 분할 처리
    code_length = len(request.code)
    estimated_tokens = code_length // 4
    
    if estimated_tokens > 3000:  # 3000 토큰 이상이면 분할 처리
        print(f"[LOG] Large code detected ({estimated_tokens} tokens), splitting...")
        return await review_large_code(request)
    
    # UI 프레임워크별 프롬프트 커스터마이징
    if request.ui_framework.lower() == "nexacro":
        prompt = PROMPT_TEMPLATE.replace("특정 UI 솔루션", "Nexacro Platform").format(code=request.code)
    elif request.ui_framework.lower() == "exbuilder":
        prompt = PROMPT_TEMPLATE.format(code=request.code)
    else:
        prompt = PROMPT_TEMPLATE.format(code=request.code)
    
    print(f"[LOG] Prompt generated. Calling LLM... (fast_mode: {request.fast_mode})")
    result = request_llm_fast(prompt) if request.fast_mode else request_llm(prompt)
    print("[LOG] LLM call finished. Returning result.")
    return {"result": result}

async def review_large_code(request: ReviewRequest):
    """대용량 코드를 함수별로 분할하여 분석"""
    code = request.code
    
    # 함수별로 분할
    functions = split_code_by_functions(code)
    
    if len(functions) <= 1:
        # 함수로 분할할 수 없으면 줄 단위로 분할
        chunks = split_code_by_lines(code, max_lines=100)
        results = []
        for i, chunk in enumerate(chunks):
            prompt = f"""eXBuilder6 코드 청크 분석: 청크 {i+1}/{len(chunks)}를 분석하세요.

**분석:** 오류, 경고, 개선안, 실행흐름

```javascript
{chunk}
```

**응답:**
## 오류 지점
- **라인 X**: 구체적 오류

## 경고 지점  
- **라인 X**: 구체적 경고

## 개선 제안
- 구체적 수정 코드

## 실행 흐름
- 단계별 상세 동작 과정"""
            result = request_llm_fast(prompt) if request.fast_mode else request_llm(prompt)
            results.append(f"## 청크 {i+1}\n{result}")
        
        return {"result": "\n\n".join(results)}
    else:
        # 함수별로 분석
        results = []
        for func_name, func_code in functions.items():
            prompt = f"""eXBuilder6 함수 분석: '{func_name}' 함수를 분석하세요.

**분석:** 오류, 경고, 개선안, 실행흐름

```javascript
{func_code}
```

**응답:**
## 오류 지점
- **라인 X**: 구체적 오류

## 경고 지점  
- **라인 X**: 구체적 경고

## 개선 제안
- 구체적 수정 코드

## 실행 흐름
- 단계별 상세 동작 과정"""
            result = request_llm_fast(prompt) if request.fast_mode else request_llm(prompt)
            results.append(f"## 함수: {func_name}\n{result}")
        
        return {"result": "\n\n".join(results)}

def split_code_by_functions(code: str):
    """코드를 함수별로 분할"""
    import re
    
    # 함수 정의 패턴 찾기
    function_pattern = r'function\s+(\w+)\s*\([^)]*\)\s*\{[^}]*\}'
    matches = re.finditer(function_pattern, code, re.DOTALL)
    
    functions = {}
    for match in matches:
        func_name = match.group(1)
        func_code = match.group(0)
        functions[func_name] = func_code
    
    return functions

def split_code_by_lines(code: str, max_lines: int = 100):
    """코드를 줄 단위로 분할"""
    lines = code.split('\n')
    chunks = []
    
    for i in range(0, len(lines), max_lines):
        chunk = '\n'.join(lines[i:i + max_lines])
        chunks.append(chunk)
    
    return chunks

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