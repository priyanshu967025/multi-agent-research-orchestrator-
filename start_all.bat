@echo off
TITLE MARO - Multi-Agent Research Orchestrator Launcher
COLOR 0B

echo ======================================================================
echo    [MARO] MULTI-AGENT RESEARCH ORCHESTRATOR - 1-CLICK DEV LAUNCHER
echo ======================================================================
echo.
echo  Starting Django REST Framework Backend (Port 8000)...
start "MARO - Backend (Django)" cmd /k "cd backend && ..\.venv\Scripts\python.exe manage.py runserver 0.0.0.0:8000"

timeout /t 2 >nul

echo  Starting React + Vite Frontend (Port 5173)...
start "MARO - Frontend (React Vite)" cmd /k "cd frontend && npm run dev"

echo.
echo ======================================================================
echo   [OK] Services launched in separate windows!
echo   - Backend API:    http://127.0.0.1:8000/api/health/
echo   - React Web UI:   http://localhost:5173/
echo ======================================================================
echo.
echo Opening browser in 3 seconds...
timeout /t 3 >nul
start http://localhost:5173/

exit
