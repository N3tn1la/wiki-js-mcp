#!/usr/bin/env python3
"""
Генератор deeplink для автоматического добавления MCP сервера в Cursor
"""

import json
import os
import sys
import base64
from pathlib import Path

def generate_cursor_deeplink():
    """Генерирует deeplink для добавления MCP сервера в Cursor"""
    
    # Читаем конфигурацию MCP
    config_path = Path("cursor-mcp.json")
    if not config_path.exists():
        print("❌ Файл cursor-mcp.json не найден")
        return None
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
    except Exception as e:
        print(f"❌ Ошибка чтения конфигурации: {e}")
        return None
    
    # Создаем deeplink
    deeplink_data = {
        "mcpServers": config["mcpServers"]
    }
    
    # Кодируем в base64
    json_str = json.dumps(deeplink_data, separators=(',', ':'))
    encoded_data = base64.urlsafe_b64encode(json_str.encode('utf-8')).decode('utf-8')
    
    # Создаем deeplink
    deeplink = f"cursor://mcp/add?config={encoded_data}"
    
    return deeplink

def save_deeplink_file(deeplink):
    """Сохраняет deeplink в файл"""
    # В Docker контейнере сохраняем в /app/data, иначе в текущую директорию
    if Path("/app").exists():
        deeplink_file = Path("/app/data/cursor-mcp-deeplink.txt")
    else:
        deeplink_file = Path("cursor-mcp-deeplink.txt")
    
    content = f"""🔗 Deeplink для добавления Wiki.js MCP в Cursor

Скопируйте и вставьте эту ссылку в браузер для автоматического добавления MCP сервера:

{deeplink}

📋 Инструкция:
1. Скопируйте ссылку выше
2. Вставьте в адресную строку браузера
3. Нажмите Enter
4. Cursor автоматически добавит MCP сервер

⚠️ Важно: Убедитесь, что:
- Wiki.js сервер запущен
- Токен настроен в файле .env
- Docker контейнер wikijs-mcp:latest собран

📖 Подробная документация: README-WINDOWS.md
"""
    
    try:
        with open(deeplink_file, 'w', encoding='utf-8') as f:
            f.write(content)
        return deeplink_file
    except Exception as e:
        print(f"❌ Ошибка сохранения файла: {e}")
        return None

def main():
    print("🔗 Генерация deeplink для Cursor")
    print("=" * 40)
    
    # Генерируем deeplink
    deeplink = generate_cursor_deeplink()
    if not deeplink:
        sys.exit(1)
    
    # Сохраняем в файл
    deeplink_file = save_deeplink_file(deeplink)
    if not deeplink_file:
        sys.exit(1)
    
    print("✅ Deeplink успешно сгенерирован!")
    print(f"📄 Файл сохранен: {deeplink_file}")
    print()
    print("🔗 Deeplink для Cursor:")
    print(deeplink)
    print()
    print("📋 Скопируйте ссылку выше и вставьте в браузер для добавления MCP в Cursor")

if __name__ == "__main__":
    main() 