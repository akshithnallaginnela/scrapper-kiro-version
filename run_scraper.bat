@echo off
REM Organic Products Web Scraper - Quick Run Script
REM Double-click this file to start scraping

echo ========================================
echo Organic Products Web Scraper
echo ========================================
echo.
echo Mode: TEST MODE (using cached data)
echo This is the RECOMMENDED way to run the scraper.
echo.
echo Starting scraper...
echo.

REM Run the scraper
python -m src.main --config config/config.test_mode.json

REM Check if successful
if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================
    echo SUCCESS! Scraping completed.
    echo ========================================
    echo.
    echo Results saved in the 'output' folder:
    echo   - JSON file: organic_products_*.json
    echo   - CSV file: organic_products_*.csv
    echo.
) else (
    echo.
    echo ========================================
    echo ERROR! Scraping failed.
    echo ========================================
    echo.
    echo Check scraper.log for details.
    echo.
)

echo Press any key to exit...
pause >nul
