#!/bin/bash

# Wiki.js MCP Server - Быстрый запуск
# Этот скрипт настраивает и запускает весь проект

set -e  # Выход при ошибке

echo "🚀 Wiki.js MCP Server - Быстрый запуск"
echo "======================================"

# Получаем директорию скрипта
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Проверяем наличие Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Ошибка: Docker не установлен"
    echo "Установите Docker с https://docker.com"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Ошибка: Docker Compose не установлен"
    echo "Установите Docker Compose с https://docs.docker.com/compose/install/"
    exit 1
fi

echo "✅ Docker и Docker Compose найдены"

# Создаем .env файл если его нет
if [ ! -f ".env" ]; then
    echo "📝 Создание файла .env..."
    if [ -f "config/env.example" ]; then
        cp config/env.example .env
        echo "✅ Файл .env создан из примера"
        echo "⚠️  ВАЖНО: Отредактируйте .env файл с вашими настройками!"
    else
        echo "❌ Файл config/env.example не найден"
        exit 1
    fi
else
    echo "✅ Файл .env уже существует"
fi

# Создаем необходимые директории
echo "📁 Создание директорий..."
mkdir -p data/sideload data/docs data/mcp logs

# Останавливаем существующие контейнеры
echo "🛑 Остановка существующих контейнеров..."
docker-compose down 2>/dev/null || true

# Запускаем Wiki.js и базу данных
echo "🐳 Запуск Wiki.js и PostgreSQL..."
docker-compose up -d db wiki

echo "⏳ Ожидание запуска Wiki.js..."
sleep 30

# Проверяем статус Wiki.js
echo "🔍 Проверка статуса Wiki.js..."
if curl -s http://localhost:3000 > /dev/null; then
    echo "✅ Wiki.js успешно запущен на http://localhost:3000"
else
    echo "⚠️  Wiki.js еще не готов, проверьте логи:"
    echo "   docker-compose logs wiki"
    echo "   Подождите еще немного и попробуйте снова"
fi

echo ""
echo "🎉 Настройка завершена!"
echo ""
echo "📋 Следующие шаги:"
echo "1. Откройте http://localhost:3000 в браузере"
echo "2. Завершите первоначальную настройку Wiki.js"
echo "3. Создайте API токен: Admin → API Access → Create Token"
echo "4. Добавьте токен в файл .env (WIKIJS_TOKEN=your_token)"
echo ""
echo "5. Для запуска MCP сервера:"
echo "   docker-compose --profile mcp up -d mcp-server"
echo ""
echo "6. Для подключения к Cursor:"
echo "   - Скопируйте содержимое cursor-mcp.json в ~/.cursor/mcp.json"
echo "   - Обновите пути в конфигурации"
echo ""
echo "📖 Подробная документация: README.md"