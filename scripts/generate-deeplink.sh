#!/bin/bash

echo "🔗 Копирование deeplink из Docker контейнера"
echo "============================================="

# Проверяем наличие Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Ошибка: Docker не установлен"
    exit 1
fi

# Проверяем наличие образа
if ! docker images | grep -q "wikijs-mcp"; then
    echo "❌ Образ wikijs-mcp:latest не найден"
    echo "Сначала соберите образ: docker-compose --profile build build mcp-builder"
    exit 1
fi

# Копируем deeplink из контейнера
echo "🔗 Копирование deeplink из контейнера..."
docker create --name temp-container wikijs-mcp:latest
docker cp temp-container:/app/data/cursor-mcp-deeplink.txt ./cursor-mcp-deeplink.txt
docker rm temp-container

if [ -f "cursor-mcp-deeplink.txt" ]; then
    echo ""
    echo "✅ Deeplink успешно скопирован из контейнера!"
    echo "📄 Файл сохранен: cursor-mcp-deeplink.txt"
    echo ""
    echo "🔗 Deeplink для Cursor:"
    cat cursor-mcp-deeplink.txt
    echo ""
else
    echo "⚠️  Deeplink не найден в контейнере, генерируем локально..."
    if command -v python3 &> /dev/null; then
        python3 generate-deeplink.py
        if [ -f "cursor-mcp-deeplink.txt" ]; then
            echo ""
            echo "🔗 Deeplink для Cursor:"
            cat cursor-mcp-deeplink.txt
            echo ""
        fi
    else
        echo "❌ Python3 не установлен для локальной генерации"
        exit 1
    fi
fi 