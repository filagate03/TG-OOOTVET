@echo off
chcp 65001 >nul
cd /d "%~dp0frontend"

echo.
echo ══════════════════════════════════════════════
echo   TG-Otvet Frontend
echo ══════════════════════════════════════════════
echo.

REM Check if node_modules exists
if not exist "node_modules" (
    echo [1/2] Installing dependencies...
    call npm install
    if errorlevel 1 (
        echo ERROR: Failed to install npm packages!
        pause
        exit /b 1
    )
)

echo [2/2] Starting development server...
echo.
echo   URL: http://localhost:5173
echo.
echo ══════════════════════════════════════════════
echo.

call npm run dev -- --host

if errorlevel 1 (
    echo.
    echo ERROR: Frontend stopped with an error!
    pause
)
