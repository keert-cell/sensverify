# SensVerify Auto Deploy Script
# Run this after Git install is complete

$env:PATH = $env:PATH + ";C:\Program Files\Git\cmd;C:\Program Files\Git\bin"
$repoUrl = "https://github.com/keert-cell/sensverify.git"
$projectDir = "c:\Users\venkat designs tools\Desktop\news detector\fake-news-detector"

Set-Location $projectDir

Write-Host "=== SensVerify Auto Deploy ===" -ForegroundColor Cyan

# Check git
$gitVersion = git --version 2>&1
Write-Host "Git: $gitVersion" -ForegroundColor Green

# Configure git
git config --global user.email "keert-cell@github.com"
git config --global user.name "Keerthi SensVerify"

# Init if needed
if (-not (Test-Path ".git")) {
    Write-Host "Initializing git repo..." -ForegroundColor Yellow
    git init
    git remote add origin $repoUrl
} else {
    Write-Host "Git repo exists." -ForegroundColor Green
    # Make sure remote is set
    git remote set-url origin $repoUrl 2>$null
    if ($LASTEXITCODE -ne 0) {
        git remote add origin $repoUrl
    }
}

# Stage all files
Write-Host "Staging files..." -ForegroundColor Yellow
git add app.py
git add requirements.txt
git add train.py
git add data_generator.py
git add README.md
git add .streamlit/config.toml
git add models/ 2>$null
git add data/ 2>$null

# Commit
Write-Host "Committing..." -ForegroundColor Yellow
git commit -m "Added Real SIM Connect API for multi-user v2.0"

# Push
Write-Host "Pushing to GitHub..." -ForegroundColor Yellow
git branch -M main
git push -u origin main --force

Write-Host ""
Write-Host "=== DONE! ===" -ForegroundColor Green
Write-Host "Code pushed to: $repoUrl" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next: Go to https://share.streamlit.io and deploy!" -ForegroundColor Magenta
