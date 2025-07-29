@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo 🏗️ Сборка образа Wiki.js MCP Server
echo ===================================

:: Получаем директорию скрипта
set "SCRIPT_DIR=%~dp0"
cd /d "%SCRIPT_DIR%"

:: Проверяем наличие Docker
docker --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Ошибка: Docker не установлен
    echo Установите Docker Desktop с https://docker.com
    pause
    exit /b 1
)

echo ✅ Docker найден

:: Собираем образ MCP сервера
echo 🐳 Сборка образа wikijs-mcp:latest...
docker-compose --profile build build mcp-builder

if errorlevel 1 (
    echo ❌ Ошибка при сборке образа
    echo Проверьте логи выше
    pause
    exit /b 1
)

echo ✅ Образ wikijs-mcp:latest успешно собран

:: Копируем сгенерированный deeplink из контейнера
echo.
echo 🔗 Копирование deeplink из контейнера...
docker create --name temp-container wikijs-mcp:latest
docker cp temp-container:/app/data/cursor-mcp-deeplink.txt ./cursor-mcp-deeplink.txt
docker rm temp-container

if exist "cursor-mcp-deeplink.txt" (
    echo ✅ Deeplink успешно скопирован из контейнера
    echo 📄 Файл: cursor-mcp-deeplink.txt
    echo.
    echo 🔗 Deeplink для Cursor:
    type cursor-mcp-deeplink.txt
    echo.
) else (
    echo ⚠️  Deeplink не найден в контейнере, генерируем локально...
    python generate-deeplink.py
    if exist "cursor-mcp-deeplink.txt" (
        echo.
        echo 🔗 Deeplink для Cursor:
        type cursor-mcp-deeplink.txt
        echo.
    )
)

echo.
echo 📋 Теперь вы можете:
echo 1. Запустить Wiki.js: docker-compose up -d db wiki
echo 2. Настроить токен в файле .env
echo 3. Подключить MCP к Cursor используя deeplink из файла cursor-mcp-deeplink.txt
echo.
echo 📖 Подробная документация: README-WINDOWS.md
pause