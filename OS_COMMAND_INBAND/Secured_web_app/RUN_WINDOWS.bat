@echo off
setlocal
cd /d "%~dp0"
echo [NetProbe Lab] Checking Python...
where py >nul 2>nul
if %errorlevel%==0 (set "PY=py -3") else (set "PY=python")
if not exist ".venv\Scripts\python.exe" (
  echo [NetProbe Lab] Creating virtual environment...
  %PY% -m venv .venv
  if errorlevel 1 (echo Could not create venv. Install Python 3.10+ and rerun.& pause & exit /b 1)
)
echo [NetProbe Lab] Installing requirements...
".venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 (echo Could not install Flask. Check your connection.& pause & exit /b 1)
echo.
echo ======================================================
echo   OPEN IN YOUR BROWSER: http://127.0.0.1:5000/
echo   Ctrl+C stops the demo.
echo ======================================================
echo.
".venv\Scripts\python.exe" app.py
pause
