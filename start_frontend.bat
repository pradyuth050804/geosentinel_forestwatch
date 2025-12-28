@echo off
echo ============================================================
echo Starting GeoSentinel Frontend
echo ============================================================
echo.

cd /d %~dp0frontend

echo Installing frontend dependencies (first time only)...
call npm install

echo.
echo Starting Vite development server...
echo Frontend will run on http://localhost:5173
echo.
echo Press Ctrl+C to stop the server
echo.
call npm run dev

pause
