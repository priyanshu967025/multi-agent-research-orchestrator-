# MARO - Multi-Agent Research Orchestrator PowerShell Launcher
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host "   [MARO] MULTI-AGENT RESEARCH ORCHESTRATOR - 1-CLICK DEV LAUNCHER" -ForegroundColor Cyan
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host ""

$rootDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$pythonExe = Join-Path $rootDir ".venv\Scripts\python.exe"

Write-Host "-> Launching Django REST Backend (Port 8000)..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$rootDir\backend'; & '$pythonExe' manage.py runserver 0.0.0.0:8000"

Start-Sleep -Seconds 2

Write-Host "-> Launching React + Vite Frontend (Port 5173)..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$rootDir\frontend'; npm run dev"

Write-Host ""
Write-Host "======================================================================" -ForegroundColor Green
Write-Host "  [OK] Both services launched successfully!" -ForegroundColor Green
Write-Host "  - Backend:   http://127.0.0.1:8000/api/health/" -ForegroundColor White
Write-Host "  - Frontend:  http://localhost:5173/" -ForegroundColor White
Write-Host "======================================================================" -ForegroundColor Green
Write-Host ""

Start-Sleep -Seconds 2
Start-Process "http://localhost:5173/"
