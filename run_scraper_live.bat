@echo off
REM Organic Products Web Scraper - Live Scraping
REM This version scrapes real websites (not cached data)

echo ========================================
echo Organic Products Web Scraper (LIVE)
echo ========================================
echo.
echo WARNING: This will scrape real websites.
echo This may take 1-5 minutes depending on network speed.
echo.
echo Starting scraper...
echo.

REM Run the scraper with live configuration
python -m src.main --config config/config.json

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
