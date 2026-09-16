@echo off
setlocal
echo ======================================================================
echo    Multi-Agent Research Orchestrator (MARO) - Verification Runner
echo ======================================================================
echo.

if exist .venv\Scripts\python.exe (
    set PYTHON_CMD=.venv\Scripts\python.exe
) else (
    set PYTHON_CMD=python
)

%PYTHON_CMD% verify_all.py
pause
