# Wiki.js MCP Server - Краткий обзор проекта

## 🎯 Что это?

**Wiki.js MCP Server** - это сервер Model Context Protocol (MCP) для интеграции Wiki.js с современными IDE и AI-ассистентами. Позволяет управлять документацией прямо из редакторов кода через 21 специализированный инструмент.

## 🚀 Ключевые возможности

### ✅ Иерархическая документация
- Создание вложенных структур документации
- Автоматическая организация по типам файлов
- Навигация по родительским/дочерним страницам

### ✅ Интеграция с кодом
- Автоматическая генерация документации из структуры кода
- Связывание файлов кода со страницами документации
- Отслеживание изменений и синхронизация

### ✅ Docker-развертывание
- Готовое к продакшену решение
- Простая установка одной командой
- Изолированная среда выполнения

### ✅ 21 MCP инструмент
- Полный набор функций для управления документацией
- Поддержка массовых операций
- Безопасные механизмы удаления

## 📊 Статистика проекта

| Параметр | Значение |
|----------|----------|
| **Версия** | 1.0.0 |
| **Python** | 3.12+ |
| **MCP инструментов** | 21 |
| **Поддерживаемые IDE** | Cursor, VS Code, другие |
| **Лицензия** | MIT |
| **Статус** | Готов к продакшену |

## 🏗️ Архитектура

```
IDE (Cursor/VS Code) → MCP Server → Wiki.js GraphQL API → PostgreSQL
                              ↓
                        SQLite (маппинги)
```

## 🛠️ Быстрый старт

### Windows (Рекомендуется)
```cmd
git clone https://github.com/your-repo/wiki-js-mcp.git
cd wiki-js-mcp
quick-start.bat
```

### Linux/macOS
```bash
git clone https://github.com/your-repo/wiki-js-mcp.git
cd wiki-js-mcp
cp config/env.example .env
docker-compose up -d db wiki
./scripts/setup.sh
```

## 📋 Основные инструменты

### Иерархическая документация
- `wikijs_create_repo_structure` - Создание структуры репозитория
- `wikijs_create_nested_page` - Создание вложенных страниц
- `wikijs_get_page_children` - Навигация по иерархии

### Управление страницами
- `wikijs_create_page` - Создание страниц
- `wikijs_update_page` - Обновление страниц
- `wikijs_search_pages` - Поиск по содержимому

### Интеграция с кодом
- `wikijs_generate_file_overview` - Автоматическая генерация документации
- `wikijs_link_file_to_page` - Связывание файлов
- `wikijs_sync_file_docs` - Синхронизация изменений

### Удаление и очистка
- `wikijs_delete_page` - Удаление отдельных страниц
- `wikijs_batch_delete_pages` - Массовое удаление
- `wikijs_delete_hierarchy` - Удаление иерархий

## 💡 Примеры использования

### Создание документации проекта
```python
# Создание структуры репозитория
await wikijs_create_repo_structure(
    repo_name="My App",
    description="Modern web application",
    sections=["Overview", "Components", "API", "Deployment"]
)

# Создание документации компонента
await wikijs_create_nested_page(
    title="Button Component",
    content="# Button Component\n\nReusable button...",
    parent_path="my-app/components"
)
```

### Интеграция с Cursor IDE
```
Before writing any code, always:
1. Search existing documentation using wikijs_search_pages
2. Create documentation before implementing new features
3. Update documentation when making changes
```

## 🔧 Конфигурация

### Основные переменные окружения
```env
WIKIJS_API_URL=http://localhost:3000
WIKIJS_TOKEN=your_jwt_token_here
WIKIJS_MCP_DB=./data/mcp/wikijs_mappings.db
DEFAULT_LOCALE=en
```

### Поддерживаемые локали
- `en` - Английский
- `ru` - Русский
- `de` - Немецкий
- `fr` - Французский
- `es` - Испанский

## 📈 Производительность

- **Время отклика**: < 100ms
- **Параллельные запросы**: Асинхронные операции
- **Масштабируемость**: Сотни репозиториев
- **Кэширование**: Умное кэширование метаданных

## 🔒 Безопасность

- **JWT токены** для аутентификации
- **HTTPS** для всех API запросов
- **Изолированная база данных** PostgreSQL
- **Безопасное чтение файлов** с проверкой путей

## 📚 Документация

- **[PROJECT_DOCUMENTATION.md](PROJECT_DOCUMENTATION.md)** - Детальная документация
- **[README.md](README.md)** - Основная документация
- **[README-WINDOWS.md](README-WINDOWS.md)** - Руководство для Windows
- **[INSTALL.md](INSTALL.md)** - Быстрая установка

## 🆘 Поддержка

### Сообщество
- GitHub Issues для сообщений об ошибках
- Discussions для вопросов и обсуждений
- Wiki для дополнительной документации

### Коммерческая поддержка
- Консультации по настройке
- Кастомизация функций
- Обучение использованию

## 🎯 Целевая аудитория

- **Разработчики** и команды разработки
- **Технические писатели**
- **DevOps инженеры**
- **Организации** с множественными проектами
- **Команды**, использующие AI-ассистентов

## 🚀 Готово к использованию

Проект полностью готов к использованию в продакшене и активно развивается сообществом. Начните с `scripts/quick-start.bat` (Windows) или следуйте инструкциям в основном [README.md](../README.md).

---

**Начните прямо сейчас!** 🚀 Создайте свою первую иерархическую документацию с помощью `wikijs_create_repo_structure`! 📚✨ 