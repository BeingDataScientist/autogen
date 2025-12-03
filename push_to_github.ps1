# PowerShell script to push to GitHub
# Usage: .\push_to_github.ps1

Write-Host "=== GitHub Push Script ===" -ForegroundColor Cyan
Write-Host ""

# Check if config.json is ignored
$ignored = git check-ignore config.json
if ($ignored) {
    Write-Host "[OK] config.json is properly ignored" -ForegroundColor Green
} else {
    Write-Host "[WARNING] config.json is NOT ignored! Aborting." -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "Current status:" -ForegroundColor Yellow
git status --short

Write-Host ""
$confirm = Read-Host "Ready to push to GitHub? (y/n)"
if ($confirm -ne "y") {
    Write-Host "Aborted." -ForegroundColor Yellow
    exit 0
}

Write-Host ""
Write-Host "Enter your GitHub repository URL:" -ForegroundColor Yellow
Write-Host "Example: https://github.com/username/repo-name.git" -ForegroundColor Gray
$repoUrl = Read-Host "Repository URL"

if (-not $repoUrl) {
    Write-Host "No URL provided. Aborting." -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "Setting up remote and pushing..." -ForegroundColor Yellow

# Remove existing remote if any
git remote remove origin 2>$null

# Add remote
git remote add origin $repoUrl

# Rename branch to main if needed
$currentBranch = git branch --show-current
if ($currentBranch -ne "main") {
    git branch -M main
}

# Push
Write-Host ""
Write-Host "Pushing to GitHub..." -ForegroundColor Yellow
git push -u origin main

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "[SUCCESS] Code pushed to GitHub!" -ForegroundColor Green
    Write-Host "Your API key is safe - config.json was NOT uploaded." -ForegroundColor Green
} else {
    Write-Host ""
    Write-Host "[ERROR] Push failed. Check your repository URL and permissions." -ForegroundColor Red
}

