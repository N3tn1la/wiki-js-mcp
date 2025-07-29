@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo 🔗 Ручная генерация deeplink для Cursor
echo ========================================

:: Получаем директорию скрипта
set "SCRIPT_DIR=%~dp0"
cd /d "%SCRIPT_DIR%"

:: Проверяем наличие Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Ошибка: Python не установлен
    echo Установите Python с https://python.org
    pause
    exit /b 1
)

echo ✅ Python найден

:: Проверяем наличие файла конфигурации
if not exist "cursor-mcp.json" (
    echo ❌ Файл cursor-mcp.json не найден
    pause
    exit /b 1
)

echo ✅ Файл конфигурации найден

:: Генерируем deeplink
echo 🔗 Генерация deeplink...
python generate-deeplink.py

if errorlevel 1 (
    echo ❌ Ошибка при генерации deeplink
    pause
    exit /b 1
)

echo.
echo ✅ Deeplink успешно сгенерирован!
echo 📄 Файл: cursor-mcp-deeplink.txt
echo.
echo 🔗 Deeplink для Cursor:
type cursor-mcp-deeplink.txt
echo.
pause 