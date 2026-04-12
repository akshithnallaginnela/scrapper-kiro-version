@echo off
REM Final push to GitHub - Ready to execute!

echo ========================================
echo Push to GitHub: scrapper-kiro-version
echo ========================================
echo.
echo Git user: akshithnallaginnela
echo Git email: akshithdeekshith@gmail.com
echo.
echo Repository will be created at:
echo https://github.com/akshithnallaginnela/scrapper-kiro-version
echo.
echo ========================================
echo STEP 1: Create GitHub Repository First!
echo ========================================
echo.
echo Before running this script, you MUST:
echo.
echo 1. Go to: https://github.com/new
echo 2. Repository name: scrapper-kiro-version
echo 3. Make it PUBLIC
echo 4. DO NOT initialize with README, .gitignore, or license
echo 5. Click "Create repository"
echo.
echo ========================================
echo.
pause
echo.
echo ========================================
echo STEP 2: Adding Remote and Pushing
echo ========================================
echo.

REM Add remote
echo Adding remote repository...
git remote add origin https://github.com/akshithnallaginnela/scrapper-kiro-version.git
if %ERRORLEVEL% NEQ 0 (
    echo Remote already exists, removing and re-adding...
    git remote remove origin
    git remote add origin https://github.com/akshithnallaginnela/scrapper-kiro-version.git
)
echo.

REM Push to GitHub
echo Pushing to GitHub...
git push -u origin main
echo.

if %ERRORLEVEL% EQU 0 (
    echo ========================================
    echo SUCCESS! Repository pushed to GitHub!
    echo ========================================
    echo.
    echo Your repository is now live at:
    echo https://github.com/akshithnallaginnela/scrapper-kiro-version
    echo.
) else (
    echo ========================================
    echo ERROR! Push failed.
    echo ========================================
    echo.
    echo Common issues:
    echo 1. Repository not created on GitHub yet
    echo 2. Authentication required - you may need to:
    echo    - Use GitHub Desktop
    echo    - Set up SSH keys
    echo    - Use Personal Access Token
    echo.
    echo See GITHUB_SETUP_GUIDE.txt for help
    echo.
)

pause
