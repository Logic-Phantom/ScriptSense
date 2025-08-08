# LM Studio 모드로 전환하는 PowerShell 스크립트

Write-Host "🤖 ScriptSense - LM Studio 모드로 전환" -ForegroundColor Green
Write-Host "=" * 40

# LM Studio 모드로 설정
$env:LLM_MODE = "lmstudio"

Write-Host "✅ LM Studio 모드로 설정되었습니다!" -ForegroundColor Green
Write-Host "현재 설정:" -ForegroundColor Yellow
Write-Host "  LLM_MODE = $env:LLM_MODE"
Write-Host ""

Write-Host "⚠️  주의사항:" -ForegroundColor Yellow
Write-Host "1. LM Studio가 실행되어 있어야 합니다"
Write-Host "2. 모델이 로드되어 있어야 합니다"
Write-Host "3. 포트 1234에서 서버가 실행되어야 합니다"
Write-Host ""

Write-Host "LM Studio 설정 확인:" -ForegroundColor Cyan
Write-Host "1. LM Studio 실행"
Write-Host "2. 모델 다운로드 및 로드"
Write-Host "3. 'Local Server' 탭에서 서버 시작"
Write-Host "4. 포트가 1234인지 확인"
Write-Host ""

Write-Host "이제 백엔드 서버를 실행하세요:" -ForegroundColor Cyan
Write-Host "  cd backend"
Write-Host "  python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000"
