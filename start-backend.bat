@echo off
title AgentsChat Backend
cd /d "C:\Users\27218\Desktop\AgentsChat\backend"

echo Killing any process on port 8000...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":8000.*LISTENING"') do (
    taskkill /F /PID %%a 2>nul
)

echo Starting backend...
uvicorn main:app --reload --host 127.0.0.1 --port 8000
pause
