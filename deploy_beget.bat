@echo off
echo Starting deployment of TG-Otvet to Beget...

REM Set the project directory (usually in ~/domains/yourdomain.com or ~/apps/app_name)
set PROJECT_DIR="C:\path\to\your\project"
set VENV_DIR="%PROJECT_DIR%\.venv"

REM Navigate to project directory
cd %PROJECT_DIR%

REM Create virtual environment if it doesn't exist
if not exist %VENV_DIR% (
    echo Creating virtual environment...
    python -m venv %VENV_DIR%
)

REM Activate virtual environment
call %VENV_DIR%\Scripts\activate.bat

REM Upgrade pip
python -m pip install --upgrade pip

REM Install dependencies
echo Installing dependencies...
pip install -r requirements.txt

REM Create media directory if it doesn't exist
if not exist "media" mkdir media

REM Run database migrations (if any)
python init_db.py

echo Deployment completed!
echo Application setup finished.
pause