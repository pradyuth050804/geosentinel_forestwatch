@echo off
echo ============================================================
echo Starting GeoSentinel Backend Server
echo ============================================================
echo.

REM Initialize conda
call %USERPROFILE%\miniconda3\Scripts\activate.bat
call conda activate geosentinel

if errorlevel 1 (
    echo ERROR: Could not activate conda environment
    pause
    exit /b 1
)

echo Starting Flask API server...
echo.

REM Run the launcher script from project root
python "%~dp0run_backend.py"

pause
