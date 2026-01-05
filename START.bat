@echo off
chcp 65001 >nul
cd /d "%~dp0"

echo.
echo ══════════════════════════════════════════════════════════
echo   TG-Otvet: Telegram Bot Funnel System
echo ══════════════════════════════════════════════════════════
echo.

REM Check if venv exists
if not exist ".venv\Scripts\activate.bat" (
    echo [1/3] Creating virtual environment...
    python -m venv .venv
    if errorlevel 1 (
        echo ERROR: Failed to create virtual environment!
        echo Make sure Python 3.11+ is installed.
        pause
        exit /b 1
    )
) else (
    echo [1/3] Virtual environment found
)

echo [2/3] Activating environment...
call .venv\Scripts\activate.bat

REM Check if dependencies installed
python -c "import fastapi" 2>nul
if errorlevel 1 (
    echo [2/3] Installing dependencies...
    pip install -q fastapi uvicorn sqlalchemy aiosqlite aiogram apscheduler python-multipart aiofiles pydantic
    if errorlevel 1 (
        echo ERROR: Failed to install dependencies!
        pause
        exit /b 1
    )
)

echo [3/3] Starting Backend + Bot Manager...
echo.
echo   API:      http://localhost:8002
echo   Docs:     http://localhost:8002/docs
echo   Frontend: запустите START_FRONTEND.bat в другом окне
echo.
echo ══════════════════════════════════════════════════════════
echo.

python run.py

if errorlevel 1 (
    echo.
    echo ERROR: Application stopped with an error!
    pause
)
