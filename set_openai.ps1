# OpenAI API 모드로 전환하는 PowerShell 스크립트

Write-Host "🤖 ScriptSense - OpenAI 모드로 전환" -ForegroundColor Green
Write-Host "=" * 40

# OpenAI API Key 입력받기
$apiKey = Read-Host "OpenAI API Key를 입력하세요"

if ($apiKey) {
    # 환경변수 설정 (현재 세션)
    $env:LLM_MODE = "openai"
    $env:OPENAI_API_KEY = $apiKey
    
    Write-Host "✅ OpenAI 모드로 설정되었습니다!" -ForegroundColor Green
    Write-Host "현재 설정:" -ForegroundColor Yellow
    Write-Host "  LLM_MODE = $env:LLM_MODE"
    Write-Host "  OPENAI_API_KEY = 설정됨"
    Write-Host ""
    Write-Host "이제 백엔드 서버를 실행하세요:" -ForegroundColor Cyan
    Write-Host "  cd backend"
    Write-Host "  python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000"
} else {
    Write-Host "❌ API Key가 입력되지 않았습니다." -ForegroundColor Red
}
