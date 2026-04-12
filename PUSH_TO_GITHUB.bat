@echo off
REM Script to push the project to GitHub
REM Repository name: scrapper-kiro-version

echo ========================================
echo Push to GitHub: scrapper-kiro-version
echo ========================================
echo.

echo Step 1: Initializing Git repository...
git init
echo.

echo Step 2: Adding all files...
git add .
echo.

echo Step 3: Creating initial commit...
git commit -m "Initial commit: Organic Products Web Scraper built with Kiro AI"
echo.

echo Step 4: Renaming branch to main...
git branch -M main
echo.

echo ========================================
echo IMPORTANT: Next Steps
echo ========================================
echo.
echo 1. Go to GitHub.com and create a new repository:
echo    - Repository name: scrapper-kiro-version
echo    - Description: Organic Products Web Scraper built with Kiro AI
echo    - Visibility: PUBLIC
echo    - DO NOT initialize with README, .gitignore, or license
echo.
echo 2. Copy your repository URL (it will look like):
echo    https://github.com/YOUR_USERNAME/scrapper-kiro-version.git
echo.
echo 3. Run these commands (replace YOUR_USERNAME):
echo.
echo    git remote add origin https://github.com/YOUR_USERNAME/scrapper-kiro-version.git
echo    git push -u origin main
echo.
echo ========================================
echo.

pause
