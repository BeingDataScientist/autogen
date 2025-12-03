#!/bin/bash
# Bash script to push to GitHub (for Linux/macOS)
# Usage: ./push_to_github.sh

echo "=== GitHub Push Script ==="
echo ""

# Check if config.json is ignored
if git check-ignore config.json > /dev/null; then
    echo "[OK] config.json is properly ignored"
else
    echo "[WARNING] config.json is NOT ignored! Aborting."
    exit 1
fi

echo ""
echo "Current status:"
git status --short

echo ""
read -p "Ready to push to GitHub? (y/n) " confirm
if [ "$confirm" != "y" ]; then
    echo "Aborted."
    exit 0
fi

echo ""
echo "Enter your GitHub repository URL:"
echo "Example: https://github.com/username/repo-name.git"
read -p "Repository URL: " repoUrl

if [ -z "$repoUrl" ]; then
    echo "No URL provided. Aborting."
    exit 1
fi

echo ""
echo "Setting up remote and pushing..."

# Remove existing remote if any
git remote remove origin 2>/dev/null

# Add remote
git remote add origin "$repoUrl"

# Rename branch to main if needed
currentBranch=$(git branch --show-current)
if [ "$currentBranch" != "main" ]; then
    git branch -M main
fi

# Push
echo ""
echo "Pushing to GitHub..."
git push -u origin main

if [ $? -eq 0 ]; then
    echo ""
    echo "[SUCCESS] Code pushed to GitHub!"
    echo "Your API key is safe - config.json was NOT uploaded."
else
    echo ""
    echo "[ERROR] Push failed. Check your repository URL and permissions."
fi

