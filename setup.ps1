# Multi-Agent Research Orchestrator — Automated Windows Setup Script
Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host " Multi-Agent Research Orchestrator (MARO) Setup" -ForegroundColor Green
Write-Host "==========================================================" -ForegroundColor Cyan

# 1. Virtual environment setup
if (-Not (Test-Path ".venv")) {
    Write-Host "[1/4] Creating Python virtual environment (.venv)..." -ForegroundColor Yellow
    python -m venv .venv
}

Write-Host "[2/4] Installing Python dependencies..." -ForegroundColor Yellow
& ".\.venv\Scripts\python.exe" -m pip install --upgrade pip
& ".\.venv\Scripts\python.exe" -m pip install -r requirements.txt

# 2. Database migrations
Write-Host "[3/4] Running Django database migrations..." -ForegroundColor Yellow
& ".\.venv\Scripts\python.exe" backend\manage.py migrate

# 3. Frontend dependencies
Write-Host "[4/4] Installing Frontend npm packages..." -ForegroundColor Yellow
cd frontend
npm install
cd ..

Write-Host "==========================================================" -ForegroundColor Green
Write-Host " Setup Complete! To start the project:" -ForegroundColor Green
Write-Host " 1. Backend:  cd backend; ..\.venv\Scripts\python.exe manage.py runserver" -ForegroundColor White
Write-Host " 2. Frontend: cd frontend; npm run dev" -ForegroundColor White
Write-Host "==========================================================" -ForegroundColor Green
