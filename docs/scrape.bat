@echo off
chcp 65001 >nul
echo ========================================
echo   Joybuy Product Scraper
echo ========================================
echo.

echo [1/3] Starting Chrome debug mode...
start "" "C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222 --user-data-dir="C:\temp\chrome-debug"
echo Waiting for Chrome...
timeout /t 5 /nobreak >nul

echo [2/3] Running scraper...
python %~dp0scrape_joybuy.py

echo.
echo [3/3] Done. Open http://192.168.0.154/
pause
