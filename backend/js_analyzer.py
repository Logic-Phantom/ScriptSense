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

# eXBuilder6 API 목록
EXBUILDER6_APIS = [
    'this.form', 'this.grid', 'this.tree', 'this.combo', 'this.button',
    'this.onLoad', 'this.onClick', 'this.onChange', 'this.onSelect',
    'this.getValue', 'this.setValue', 'this.getData', 'this.setData',
    'this.addRow', 'this.deleteRow', 'this.updateRow',
    'this.showMessage', 'this.showConfirm', 'this.showAlert',
    'this.openPopup', 'this.closePopup', 'this.getParent',
    'this.getChild', 'this.getSibling', 'this.getRoot',
    'this.getSelected', 'this.getChecked', 'this.getExpanded',
    'this.setSelected', 'this.setChecked', 'this.setExpanded',
    'this.refresh', 'this.reload', 'this.clear',
    'this.enable', 'this.disable', 'this.show', 'this.hide',
    'this.focus', 'this.blur', 'this.scrollTo', 'this.scrollIntoView'
]

def check_javascript_issues(code: str) -> List[str]:
    """JavaScript 문법/로직 문제점 검사"""
    issues = []
    
    # 기본적인 JavaScript 문법 검사
    try:
        compile(code, '<string>', 'exec')
    except SyntaxError as e:
        issues.append(f"문법 오류: {e.msg}")
    
    # 일반적인 문제점들 검사
    patterns = [
        (r'var\s+\w+\s*=\s*undefined', 'undefined 할당은 불필요합니다'),
        (r'==\s*null', 'null 비교시 === 사용을 권장합니다'),
        (r'==\s*undefined', 'undefined 비교시 === 사용을 권장합니다'),
        (r'console\.log\(', 'console.log는 프로덕션에서 제거해야 합니다'),
        (r'eval\(', 'eval() 사용은 보안상 위험합니다'),
        (r'setTimeout\([^,]+,\s*0\)', 'setTimeout(,0) 대신 setImmediate 사용을 고려하세요')
    ]
    
    for pattern, message in patterns:
        if re.search(pattern, code):
            issues.append(message)
    
    return issues

def check_exbuilder6_apis(code: str) -> List[str]:
    """eXBuilder6 API 사용 여부 검사"""
    found_apis = []
    
    for api in EXBUILDER6_APIS:
        if api in code:
            found_apis.append(api)
    
    return found_apis

def check_errors(code: str) -> List[str]:
    """잠재적 오류 검사"""
    errors = []
    
    error_patterns = [
        (r'\.getElementById\([^)]*\)\.', 'getElementById 결과가 null일 수 있습니다'),
        (r'\.querySelector\([^)]*\)\.', 'querySelector 결과가 null일 수 있습니다'),
        (r'\.innerHTML\s*=', 'innerHTML 사용시 XSS 위험이 있습니다'),
        (r'JSON\.parse\([^)]*\)', 'JSON.parse는 try-catch로 감싸야 합니다'),
        (r'\.split\([^)]*\)\[', 'split 결과가 빈 배열일 수 있습니다')
    ]
    
    for pattern, message in error_patterns:
        if re.search(pattern, code):
            errors.append(message)
    
    return errors

def analyze_execution_flow(code: str) -> List[str]:
    """실행 흐름 분석"""
    flow = []
    
    # 함수 정의 찾기
    function_matches = re.findall(r'function\s+(\w+)\s*\(', code)
    if function_matches:
        flow.append(f"함수 정의: {', '.join(function_matches)}")
    
    # 이벤트 리스너 찾기
    event_matches = re.findall(r'\.addEventListener\([^)]+\)', code)
    if event_matches:
        flow.append(f"이벤트 리스너: {', '.join(event_matches)}")
    
    # 비동기 작업 찾기
    async_matches = re.findall(r'(setTimeout|setInterval|fetch|Promise|async|await)', code)
    if async_matches:
        unique_async = list(set(async_matches))
        flow.append(f"비동기 작업: {', '.join(unique_async)}")
    
    # 조건문 찾기
    conditional_matches = re.findall(r'(if|else|switch|case)', code)
    if conditional_matches:
        unique_conditionals = list(set(conditional_matches))
        flow.append(f"조건부 실행: {', '.join(unique_conditionals)}")
    
    # 반복문 찾기
    loop_matches = re.findall(r'(for|while|do)', code)
    if loop_matches:
        unique_loops = list(set(loop_matches))
        flow.append(f"반복 실행: {', '.join(unique_loops)}")
    
    return flow if flow else ['순차적 실행']

def analyze_with_llm(code: str, fast_mode: bool = False) -> Dict[str, Any]:
    """LM Studio를 사용한 고급 분석"""
    prompt = f"""JavaScript 코드를 다음 4가지 항목으로 분석해주세요:

**분석할 코드:**
```javascript
{code}
```

**분석 요청:**
1. JavaScript 문법/로직 문제점 (구체적인 라인 번호와 함께)
2. eXBuilder6 API 사용 여부 (사용된 API 목록)
3. 잠재적 오류 및 보안 위험 요소
4. 실행 흐름 (단계별 상세 과정)

**응답 형식:**
## 1. JavaScript 문법/로직 문제점
- **라인 X**: 구체적 문제점

## 2. eXBuilder6 API 사용 여부
- 사용된 API: this.form.setValue, this.grid.addRow 등

## 3. 오류 검사
- **라인 X**: 구체적 오류

## 4. 실행 흐름
- 단계별 상세 동작 과정

발견된 문제가 없으면 "발견된 문제점 없음"으로 표시하세요."""

    try:
        result = request_llm_fast(prompt) if fast_mode else request_llm(prompt)
        return {"llm_analysis": result}
    except Exception as e:
        return {"llm_analysis": f"LLM 분석 중 오류 발생: {str(e)}"}

@router.post("/analyze", response_model=JavaScriptAnalysisResponse)
async def analyze_javascript(request: JavaScriptAnalysisRequest):
    """JavaScript 코드 분석"""
    try:
        # 기본 분석
        javascript_issues = check_javascript_issues(request.code)
        exbuilder6_apis = check_exbuilder6_apis(request.code)
        errors = check_errors(request.code)
        execution_flow = analyze_execution_flow(request.code)
        
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
    """JavaScript 파일 분석"""
    try:
        if not file.filename.endswith('.js'):
            raise HTTPException(status_code=400, detail="JavaScript 파일(.js)만 업로드 가능합니다.")
        
        content = await file.read()
        code = content.decode('utf-8')
        
        # 기본 분석
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
    """상세한 JavaScript 코드 분석 (LLM 포함)"""
    try:
        # 기본 분석
        basic_analysis = {
            "javascript_issues": check_javascript_issues(request.code),
            "exbuilder6_apis": check_exbuilder6_apis(request.code),
            "errors": check_errors(request.code),
            "execution_flow": analyze_execution_flow(request.code)
        }
        
        # LM Studio를 사용한 고급 분석
        llm_analysis = analyze_with_llm(request.code, request.fast_mode)
        
        return {
            "basic_analysis": basic_analysis,
            "llm_analysis": llm_analysis
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"분석 중 오류 발생: {str(e)}")
