# 자동 실행 스크립트 (Windows PowerShell)
# 백엔드(FastAPI)와 프론트엔드(React) 서버를 각각 새 창에서 실행
# 종료: run_stop.ps1 실행

Write-Host "[1/2] 백엔드(FastAPI) 서버 실행..."
$backend = Start-Process powershell -PassThru -ArgumentList "-NoExit", "-Command", "cd backend; uvicorn main:app --reload"

Start-Sleep -Seconds 2

Write-Host "[2/2] 프론트엔드(React) 개발 서버 실행..."
$frontend = Start-Process powershell -PassThru -ArgumentList "-NoExit", "-Command", "cd frontend; npm install; npm start"

# PID 파일 저장
Set-Content -Path ".server_pids" -Value ("$($backend.Id)`n$($frontend.Id)")

Write-Host "---"
Write-Host "서버가 실행 중입니다."
Write-Host "백엔드: http://localhost:8000"
Write-Host "프론트엔드: http://localhost:3000"
Write-Host "종료하려면 run_stop.ps1 실행!"
Write-Host "---"