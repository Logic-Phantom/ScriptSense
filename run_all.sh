#!/bin/bash

# LM Studio가 실행 중이어야 합니다 (http://localhost:1234/v1/chat)

echo "[1/2] 백엔드(FastAPI) 서버 실행..."
cd backend
uvicorn main:app --reload &
BACKEND_PID=$!
cd ..

sleep 2

echo "[2/2] 프론트엔드(React) 개발 서버 실행..."
cd frontend
npm install
npm start &
FRONTEND_PID=$!
cd ..

echo "---\n서버가 실행 중입니다.\n백엔드: http://localhost:8000\n프론트엔드: http://localhost:3000\nLM Studio: http://localhost:1234/v1/chat (별도 실행 필요)\n---"

wait $BACKEND_PID $FRONTEND_PID