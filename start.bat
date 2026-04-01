@echo off
echo Starting Product Price Monitoring System...

:: Ensure we are in the correct directory
cd /d "%~dp0"

:: Start Backend on strictly 127.0.0.1
echo Starting FastAPI Backend...
start "Backend API" cmd /c ".\venv\Scripts\python src\main.py"

:: Delay momentarily to ensure backend binds
timeout /t 3 /nobreak >nul

:: Start Frontend on strictly 127.0.0.1
echo Starting Frontend UI...
cd frontend
start "Frontend Dev Server" cmd /c "..\venv\Scripts\python -m http.server 3000 --bind 127.0.0.1"

echo ==============================================
echo [SUCCESS] System is booting up!
echo.
echo    Backend API: http://127.0.0.1:8000
echo    Frontend UI: http://127.0.0.1:3000
echo.
echo You can now navigate to http://127.0.0.1:3000 in your browser.
echo ==============================================
pause
