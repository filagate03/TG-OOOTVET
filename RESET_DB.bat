@echo off
chcp 65001 >nul
cd /d "%~dp0"

echo.
echo ══════════════════════════════════════════════════════════
echo   СБРОС БАЗЫ ДАННЫХ TG-Otvet
echo ══════════════════════════════════════════════════════════
echo.
echo   ВНИМАНИЕ: Все данные будут удалены!
echo.
pause

echo.
echo [1/2] Удаление старой базы данных...
if exist "bot.db" del /f "bot.db"
echo Done!

echo [2/2] Удаление медиа файлов...
if exist "media" rmdir /s /q "media"
mkdir media
echo Done!

echo.
echo ══════════════════════════════════════════════════════════
echo   База данных сброшена!
echo   Теперь запустите START.bat
echo ══════════════════════════════════════════════════════════
echo.
pause
