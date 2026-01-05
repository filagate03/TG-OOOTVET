@echo off
echo ==========================================
echo TG-Otvet: Full System Start (Windows)
echo ==========================================

:: 1. Build Frontend
echo [1/3] Building Frontend...
cd frontend
if not exist "node_modules" (
    echo Installing npm packages...
    call npm install
)
echo Building production frontend...
call npm run build
cd ..

:: 2. Initialize Database
echo [2/3] Initializing Database...
python init_db.py

:: 3. Start Backend + Bot Manager
echo [3/3] Starting Backend + Bot Manager...
echo.
echo Open your browser at: http://localhost:8002
echo.
python run.py

pause