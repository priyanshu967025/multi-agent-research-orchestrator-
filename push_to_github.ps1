# Multi-Agent Research Orchestrator — 1-Click PowerShell GitHub Push Tool
Write-Host "=====================================================================" -ForegroundColor Cyan
Write-Host "      MULTI-AGENT RESEARCH ORCHESTRATOR - GITHUB PUSH TOOL" -ForegroundColor Green
Write-Host "=====================================================================" -ForegroundColor Cyan
Write-Host ""

# 1. Check Git
try {
    $gitVersion = git --version
    Write-Host "[1/4] Git detected: $gitVersion" -ForegroundColor Yellow
} catch {
    Write-Host "[ERROR] Git is not installed or not in PATH." -ForegroundColor Red
    exit 1
}

# 2. Check Remote
$currentRemote = git remote get-url origin 2>$null
if ($currentRemote) {
    Write-Host "Current Remote URL: $currentRemote" -ForegroundColor White
    $change = Read-Host "Do you want to use this remote URL? (Y/N, default=Y)"
    if ($change -eq "N" -or $change -eq "n") {
        $newUrl = Read-Host "Enter your new GitHub Repository URL (e.g. https://github.com/user/repo.git)"
        if ($newUrl) {
            git remote set-url origin $newUrl
            Write-Host "Remote origin updated to: $newUrl" -ForegroundColor Green
        }
    }
} else {
    $newUrl = Read-Host "Enter your GitHub Repository URL (e.g. https://github.com/user/repo.git)"
    if ($newUrl) {
        git remote add origin $newUrl
    }
}

# 3. Stage & Commit
Write-Host ""
Write-Host "[2/4] Staging all files..." -ForegroundColor Yellow
git add .

Write-Host "[3/4] Committing changes..." -ForegroundColor Yellow
git commit -m "feat: complete multi-agent research orchestrator project with React UI, Django backend, LangGraph, and full placement notes" 2>$null

# 4. Push
Write-Host ""
Write-Host "[4/4] Pushing to GitHub (main branch)..." -ForegroundColor Yellow
git branch -M main
git push -u origin main --force

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "=====================================================================" -ForegroundColor Green
    Write-Host "[SUCCESS] Project successfully pushed to GitHub!" -ForegroundColor Green
    Write-Host "=====================================================================" -ForegroundColor Green
} else {
    Write-Host ""
    Write-Host "=====================================================================" -ForegroundColor Red
    Write-Host "[ERROR] Git push encountered an issue. Check your URL / credentials." -ForegroundColor Red
    Write-Host "=====================================================================" -ForegroundColor Red
}
