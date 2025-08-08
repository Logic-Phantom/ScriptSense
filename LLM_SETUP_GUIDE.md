# 🤖 ScriptSense LLM 설정 가이드

## 🚨 현재 오류 해결 방법

현재 다음과 같은 오류가 발생하고 있습니다:
```
[ERROR] LLM 요청 실패 (LM Studio): HTTPConnectionPool(host='localhost', port=1234): Max retries exceeded with url: /v1/chat/completions
```

이는 LM Studio에 연결할 수 없어서 발생하는 문제입니다.

## 🔧 해결 방법

### 방법 1: OpenAI API 사용 (권장 - 즉시 해결)

1. **PowerShell에서 환경변수 설정:**
   ```powershell
   .\set_openai.ps1
   ```

2. **수동으로 환경변수 설정:**
   ```powershell
   $env:LLM_MODE = "openai"
   $env:OPENAI_API_KEY = "your_openai_api_key_here"
   ```

3. **백엔드 서버 실행:**
   ```powershell
   cd backend
   python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

### 방법 2: LM Studio 설정

1. **LM Studio 설치 및 실행:**
   - [LM Studio 다운로드](https://lmstudio.ai/)
   - 설치 후 실행

2. **모델 다운로드:**
   - LM Studio에서 적당한 모델 선택 (예: Llama 2 7B, CodeLlama 등)
   - 모델 다운로드

3. **로컬 서버 시작:**
   - LM Studio에서 "Local Server" 탭으로 이동
   - 포트가 1234인지 확인
   - "Start Server" 클릭

4. **환경변수 설정:**
   ```powershell
   .\set_lmstudio.ps1
   ```

5. **백엔드 서버 실행:**
   ```powershell
   cd backend
   python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

## 🛠 설정 도구

### 대화형 설정 도구
```bash
cd backend
python config_llm.py
```

### PowerShell 스크립트
- `set_openai.ps1` - OpenAI API 모드로 전환
- `set_lmstudio.ps1` - LM Studio 모드로 전환

## 📋 현재 설정 확인

현재 어떤 LLM이 설정되어 있는지 확인하려면:

```powershell
echo "LLM_MODE: $env:LLM_MODE"
echo "OPENAI_API_KEY: $(if ($env:OPENAI_API_KEY) { '설정됨' } else { '설정되지 않음' })"
```

## 🔍 문제 해결

### LM Studio 연결 문제
- LM Studio가 실행 중인지 확인
- 모델이 로드되어 있는지 확인
- 포트 1234에서 서버가 실행 중인지 확인
- 방화벽이 차단하고 있지 않은지 확인

### OpenAI API 문제
- API 키가 올바른지 확인
- API 키에 크레딧이 있는지 확인
- 인터넷 연결 상태 확인

## 📊 성능 비교

| 방법 | 장점 | 단점 |
|------|------|------|
| **OpenAI API** | ✅ 빠른 응답<br>✅ 안정적<br>✅ 설정 간단 | ❌ 사용료 발생<br>❌ 인터넷 필요 |
| **LM Studio** | ✅ 무료<br>✅ 오프라인 가능<br>✅ 프라이버시 | ❌ 느린 응답<br>❌ 높은 시스템 요구사항<br>❌ 복잡한 설정 |

## 🚀 권장 설정

**개발/테스트 환경:** OpenAI API (빠르고 안정적)
**프로덕션 환경:** 요구사항에 따라 선택
