@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo ℹ️  Информация о Wiki.js MCP Server
echo ===================================

echo.
echo 📋 MCP сервер теперь запускается автоматически через Cursor
echo.
echo 🔧 Для подключения к Cursor:
echo 1. Убедитесь, что Wiki.js запущен: http://localhost:3000
echo 2. Скопируйте содержимое cursor-mcp.json в %%USERPROFILE%%\.cursor\mcp.json
echo 3. Обновите переменную WIKIJS_TOKEN в конфигурации Cursor
echo 4. Перезапустите Cursor
echo.
echo 🐳 Управление сервисами:
echo - Запуск Wiki.js: docker-compose up -d db wiki
echo - Остановка: docker-compose down
echo - Логи: docker-compose logs wiki
echo.
echo 📖 Подробная документация: README-WINDOWS.md
pause