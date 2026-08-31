#!/usr/bin/env bash
# Multi-Agent Research Orchestrator — Automated Linux/macOS Setup Script
set -e

echo "=========================================================="
echo " Multi-Agent Research Orchestrator (MARO) Setup"
echo "=========================================================="

# 1. Virtual environment setup
if [ ! -d ".venv" ]; then
    echo "[1/4] Creating Python virtual environment (.venv)..."
    python3 -m venv .venv
fi

echo "[2/4] Installing Python dependencies..."
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# 2. Database migrations
echo "[3/4] Running Django database migrations..."
cd backend
python manage.py migrate
cd ..

# 3. Frontend dependencies
echo "[4/4] Installing Frontend npm packages..."
cd frontend
npm install
cd ..

echo "=========================================================="
echo " Setup Complete! To start the project:"
echo " 1. Backend:  cd backend && source ../.venv/bin/activate && python manage.py runserver"
echo " 2. Frontend: cd frontend && npm run dev"
echo "=========================================================="
