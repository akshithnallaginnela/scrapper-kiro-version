@echo off
REM View Latest Scraping Results

echo ========================================
echo Organic Products Web Scraper Results
echo ========================================
echo.

REM Find the latest JSON file
for /f "delims=" %%i in ('dir /b /o-d output\organic_products_*.json 2^>nul') do (
    set LATEST_JSON=%%i
    goto :found_json
)

:found_json
if defined LATEST_JSON (
    echo Latest results: %LATEST_JSON%
    echo.
    echo Opening in default JSON viewer...
    start "" "output\%LATEST_JSON%"
    
    REM Also show CSV if available
    set LATEST_CSV=%LATEST_JSON:.json=.csv%
    if exist "output\%LATEST_CSV%" (
        echo Opening CSV file...
        start "" "output\%LATEST_CSV%"
    )
) else (
    echo No results found in output folder.
    echo Run the scraper first using run_scraper.bat
)

echo.
echo Press any key to exit...
pause >nul
