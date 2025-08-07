from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from pydantic import BaseModel
from typing import Optional
from llm_client import request_llm

router = APIRouter()

PROMPT_TEMPLATE = """
너는 자바스크립트 코드 리뷰어이자 흐름 요약 전문가야.
다음 코드를 분석해서 다음을 마크다운으로 작성해줘:

1. 코드 스타일 및 오류 가능성 리뷰
2. 리팩토링 제안
3. 이 코드가 어떤 흐름으로 동작하는지 설명 (1단계 → 2단계 ... 형식)

```javascript
{code}
```
"""

class ReviewRequest(BaseModel):
    code: str

@router.post("/text")
async def review_code(request: ReviewRequest):
    print("[LOG] /api/review/text called")
    prompt = PROMPT_TEMPLATE.format(code=request.code)
    print("[LOG] Prompt generated. Calling LLM...")
    result = request_llm(prompt)
    print("[LOG] LLM call finished. Returning result.")
    return {"result": result}

@router.post("/file")
async def review_file(file: UploadFile = File(...)):
    print("[LOG] /api/review/file called")
    if not file.filename.endswith('.js'):
        print("[LOG] File extension not allowed.")
        raise HTTPException(status_code=400, detail=".js 파일만 업로드 가능합니다.")
    code = (await file.read()).decode("utf-8")
    prompt = PROMPT_TEMPLATE.format(code=code)
    print("[LOG] Prompt generated from file. Calling LLM...")
    result = request_llm(prompt)
    print("[LOG] LLM call finished. Returning result.")
    return {"result": result}