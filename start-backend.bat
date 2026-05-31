@echo off
cd /d "C:\Users\27218\Desktop\AgentsChat\backend"
uvicorn main:app --reload --host 127.0.0.1 --port 8000
pause
