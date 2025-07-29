# Быстрая установка Wiki.js MCP Server

## 🚀 Windows (Рекомендуется)

1. **Установите Docker Desktop** с [docker.com](https://www.docker.com/products/docker-desktop/)
2. **Клонируйте репозиторий** и запустите:
   ```cmd
   scripts/quick-start.bat
   ```
3. **Следуйте инструкциям** в основном [README.md](../README.md)

## 🐧 Linux/macOS

### 1. Подготовка окружения
```bash
# Копируйте шаблон конфигурации
cp config/env.example .env

# Отредактируйте .env с вашими данными:
# - Установите POSTGRES_PASSWORD на безопасный пароль
# - Обновите другие настройки при необходимости
```

### 2. Docker развертывание (Рекомендуется)
```bash
# Запустите Wiki.js с Docker
docker-compose up -d db wiki
```
Wiki.js будет доступен по адресу http://localhost:3000

Завершите начальную настройку в веб-интерфейсе

### 3. Настройка MCP сервера
```bash
# Установите Python зависимости
./scripts/setup.sh

# Обновите .env с учетными данными Wiki.js API:
# - Получите API ключ из панели администратора Wiki.js
# - Установите WIKIJS_TOKEN в файле .env

# Протестируйте подключение
./scripts/test-server.sh

# Запустите MCP сервер
./scripts/start-server.sh
```

### 4. Настройка Cursor MCP
Добавьте в ваш `~/.cursor/mcp.json`:
```json
{
  "mcpServers": {
    "wikijs": {
      "command": "/path/to/wiki-js-mcp/scripts/start-server.sh"
    }
  }
}
```

## 🔧 Устранение неполадок

### Проблемы с Docker
```bash
# Проверьте контейнеры
docker-compose ps

# Просмотрите логи
docker-compose logs wiki
docker-compose logs postgres

# Сбросьте все
docker-compose down -v
docker-compose up -d
```

### Проблемы с подключением
```bash
# Проверьте, что Wiki.js запущен
curl http://localhost:3000/graphql

# Проверьте аутентификацию
./scripts/test-server.sh

# Режим отладки
export LOG_LEVEL=DEBUG
./scripts/start-server.sh
```

### Частые проблемы
- **Конфликты портов**: Измените порт 3000 в `docker-compose.yml` при необходимости
- **Проблемы с базой данных**: Удалите `postgres_data/` и перезапустите
- **Права API**: Убедитесь, что API ключ имеет права администратора
- **Python зависимости**: Запустите `./scripts/setup.sh` для переустановки

## 📚 Дополнительная документация

- **[Полная документация](PROJECT_DOCUMENTATION.md)** - Подробное руководство
- **[Техническая спецификация](TECHNICAL_SPECIFICATION.md)** - Технические детали
- **[Руководство разработчика](DEVELOPMENT_GUIDE.md)** - Для разработчиков 