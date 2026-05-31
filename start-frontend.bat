@echo off
title AgentsChat Frontend
cd /d "C:\Users\27218\Desktop\AgentsChat\frontend"

echo Killing any process on port 5173...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":5173.*LISTENING"') do (
    taskkill /F /PID %%a 2>nul
)

echo Starting frontend...
npm run dev
pause
