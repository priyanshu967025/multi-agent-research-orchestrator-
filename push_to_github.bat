@echo off
setlocal enabledelayedexpansion
title Multi-Agent Research Orchestrator - 1-Click GitHub Push Tool
color 0B

echo =====================================================================
echo       MULTI-AGENT RESEARCH ORCHESTRATOR - 1-CLICK GITHUB PUSH
echo =====================================================================
echo.

:: 1. Check if Git is installed
git --version >nul 2>&1
if %errorlevel% neq 0 (
    color 0C
    echo [ERROR] Git is not installed or not in PATH.
    echo Please install Git from https://git-scm.com/ and try again.
    pause
    exit /b 1
)

:: 2. Show current remote
echo [1/4] Checking Current Git Remote...
for /f "tokens=*" %%a in ('git remote get-url origin 2^>nul') do set CURRENT_REMOTE=%%a

if defined CURRENT_REMOTE (
    echo Current GitHub Remote URL is:
    echo "!CURRENT_REMOTE!"
    echo.
    set /p CHANGE_REMOTE="Do you want to push to this URL? (Y/N, default=Y): "
    if /i "!CHANGE_REMOTE!"=="N" (
        set /p NEW_URL="Enter your new GitHub Repository URL (e.g., https://github.com/username/repo.git): "
        git remote set-url origin "!NEW_URL!"
        echo Updated remote origin to: !NEW_URL!
    )
) else (
    set /p NEW_URL="Enter your GitHub Repository URL (e.g., https://github.com/username/repo.git): "
    git remote add origin "!NEW_URL!"
)

echo.
echo [2/4] Staging all code files, notes, and configs...
git add .

echo.
echo [3/4] Creating Commit...
git commit -m "feat: complete multi-agent research orchestrator project with React UI, Django backend, LangGraph, and full placement notes" 2>nul
if %errorlevel% neq 0 (
    echo Working tree already up to date with commit.
)

echo.
echo [4/4] Pushing to GitHub (main branch)...
git branch -M main
git push -u origin main --force

if %errorlevel% equ 0 (
    color 0A
    echo.
    echo =====================================================================
    echo [SUCCESS] Your project has been successfully pushed to GitHub!
    echo Check your repository on github.com.
    echo =====================================================================
) else (
    color 0C
    echo.
    echo =====================================================================
    echo [FAILED] Push failed. Please check your GitHub credentials or repository URL.
    echo You may need to run: git push -u origin main --force
    echo =====================================================================
)

echo.
pause
