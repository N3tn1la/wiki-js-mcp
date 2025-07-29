@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo 🚀 Wiki.js MCP Server - Быстрый запуск для Windows
echo ==================================================

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

docker-compose --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Ошибка: Docker Compose не установлен
    echo Установите Docker Compose с https://docs.docker.com/compose/install/
    pause
    exit /b 1
)

echo ✅ Docker и Docker Compose найдены

:: Создаем .env файл если его нет
if not exist ".env" (
    echo 📝 Создание файла .env...
    if exist "config\env.example" (
        copy "config\env.example" ".env" >nul
        echo ✅ Файл .env создан из примера
        echo ⚠️  ВАЖНО: Отредактируйте .env файл с вашими настройками!
    ) else (
        echo ❌ Файл config\env.example не найден
        pause
        exit /b 1
    )
) else (
    echo ✅ Файл .env уже существует
)

:: Создаем необходимые директории
echo 📁 Создание директорий...
if not exist "data\sideload" mkdir "data\sideload"
if not exist "data\docs" mkdir "data\docs"
if not exist "data\mcp" mkdir "data\mcp"
if not exist "logs" mkdir "logs"

:: Собираем образ MCP сервера
echo 🏗️ Сборка образа MCP сервера...
docker-compose --profile build build mcp-builder

if errorlevel 1 (
    echo ❌ Ошибка при сборке образа MCP
    echo Проверьте логи выше
    pause
    exit /b 1
)

echo ✅ Образ MCP сервера собран

:: Копируем сгенерированный deeplink из контейнера
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

:: Останавливаем существующие контейнеры
echo 🛑 Остановка существующих контейнеров...
docker-compose down >nul 2>&1

:: Запускаем Wiki.js и базу данных
echo 🐳 Запуск Wiki.js и PostgreSQL...
docker-compose up -d db wiki

echo ⏳ Ожидание запуска Wiki.js...
timeout /t 30 /nobreak >nul

:: Проверяем статус Wiki.js
echo 🔍 Проверка статуса Wiki.js...
curl -s http://localhost:3000 >nul 2>&1
if errorlevel 1 (
    echo ⚠️  Wiki.js еще не готов, проверьте логи:
    echo    docker-compose logs wiki
    echo    Подождите еще немного и попробуйте снова
) else (
    echo ✅ Wiki.js успешно запущен на http://localhost:3000
)

echo.
echo 🎉 Настройка завершена!
echo.
echo 📋 Следующие шаги:
echo 1. Откройте http://localhost:3000 в браузере
echo 2. Завершите первоначальную настройку Wiki.js
echo 3. Создайте API токен: Admin → API Access → Create Token
echo 4. Добавьте токен в файл .env (WIKIJS_TOKEN=your_token)
echo.
echo 5. Для подключения к Cursor:
echo    - Откройте файл cursor-mcp-deeplink.txt
echo    - Скопируйте deeplink и вставьте в браузер
echo    - Cursor автоматически добавит MCP сервер
echo    - Обновите переменную WIKIJS_TOKEN в настройках Cursor
echo.
echo 📖 Подробная документация: README-WINDOWS.md
pause