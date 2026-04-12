@echo off
REM Check if everything is set up correctly

echo ========================================
echo Organic Products Web Scraper
echo Setup Verification
echo ========================================
echo.

echo Checking Python installation...
python --version
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Python not found!
    echo Please install Python 3.8 or higher.
    goto :end
)
echo.

echo Checking dependencies...
python check_dependencies.py
echo.

echo ========================================
echo Setup check complete!
echo ========================================
echo.
echo If all checks passed, you can run:
echo   - run_scraper.bat (quick test with cached data)
echo   - run_scraper_live.bat (scrape real websites)
echo.

:end
echo Press any key to exit...
pause >nul
