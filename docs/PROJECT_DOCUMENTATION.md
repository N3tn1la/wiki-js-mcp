# Wiki.js MCP Server - Детальная документация проекта

## 📋 Содержание

1. [Обзор проекта](#обзор-проекта)
2. [Архитектура системы](#архитектура-системы)
3. [Технические характеристики](#технические-характеристики)
4. [Функциональные возможности](#функциональные-возможности)
5. [Установка и настройка](#установка-и-настройка)
6. [Конфигурация](#конфигурация)
7. [API и инструменты](#api-и-инструменты)
8. [Примеры использования](#примеры-использования)
9. [Разработка и расширение](#разработка-и-расширение)
10. [Устранение неполадок](#устранение-неполадок)
11. [Безопасность](#безопасность)
12. [Производительность](#производительность)
13. [Лицензия и поддержка](#лицензия-и-поддержка)

---

## 🎯 Обзор проекта

### Описание
**Wiki.js MCP Server** - это комплексный сервер Model Context Protocol (MCP) для интеграции с Wiki.js, обеспечивающий иерархическую документацию и поддержку Docker-развертывания. Проект предназначен для организаций, управляющих множественными репозиториями и крупномасштабной документацией.

### Ключевые особенности
- ✅ **Иерархическая документация** - поддержка вложенных структур
- ✅ **GraphQL API интеграция** - полная совместимость с Wiki.js v2+
- ✅ **Docker-развертывание** - готовое к продакшену решение
- ✅ **21 MCP инструмент** - полный набор функций для управления документацией
- ✅ **Автоматическая генерация** - создание документации из структуры кода
- ✅ **Мультиязычность** - поддержка различных локалей
- ✅ **Безопасность** - встроенные механизмы защиты

### Целевая аудитория
- Разработчики и команды разработки
- Технические писатели
- DevOps инженеры
- Организации с множественными проектами
- Команды, использующие AI-ассистентов (Cursor, VS Code)

---

## 🏗️ Архитектура системы

### Общая архитектура
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Cursor IDE    │    │   VS Code       │    │   Другие IDE    │
│   (MCP Client)  │    │   (MCP Client)  │    │   (MCP Client)  │
└─────────┬───────┘    └─────────┬───────┘    └─────────┬───────┘
          │                      │                      │
          └──────────────────────┼──────────────────────┘
                                 │
                    ┌─────────────▼─────────────┐
                    │    Wiki.js MCP Server     │
                    │   (FastMCP Framework)     │
                    └─────────────┬─────────────┘
                                 │
          ┌──────────────────────┼──────────────────────┐
          │                      │                      │
┌─────────▼─────────┐  ┌─────────▼─────────┐  ┌─────────▼─────────┐
│   Wiki.js API     │  │   SQLite DB       │  │   File System     │
│   (GraphQL)       │  │   (Mappings)      │  │   (Code Analysis) │
└───────────────────┘  └───────────────────┘  └───────────────────┘
          │
┌─────────▼─────────┐
│   PostgreSQL      │
│   (Wiki.js Data)  │
└───────────────────┘
```

### Компоненты системы

#### 1. MCP Server (FastMCP)
- **Файл**: `src/wiki_mcp_server.py`
- **Фреймворк**: FastMCP
- **Функции**: Обработка MCP запросов, управление инструментами

#### 2. Wiki.js Client
- **Класс**: `WikiJSClient`
- **Протокол**: GraphQL API
- **Функции**: Аутентификация, запросы к Wiki.js

#### 3. Database Layer
- **ORM**: SQLAlchemy
- **База данных**: SQLite
- **Модели**: `FileMapping`, `RepositoryContext`

#### 4. Docker Infrastructure
- **Контейнеры**: Wiki.js, PostgreSQL, MCP Server
- **Оркестрация**: Docker Compose
- **Сеть**: Изолированная сеть `wikijs_network`

---

## ⚙️ Технические характеристики

### Системные требования
- **Python**: 3.12+
- **Docker**: 20.10+
- **Docker Compose**: 2.0+
- **RAM**: Минимум 2GB (рекомендуется 4GB+)
- **Дисковое пространство**: 1GB+ для баз данных

### Зависимости

#### Основные зависимости
```toml
python = "^3.12"
fastmcp = "^0.1.0"
httpx = "^0.27.0"
pydantic = "^2.0"
pydantic-settings = "^2.0"
python-slugify = "^8.0"
markdown = "^3.5"
beautifulsoup4 = "^4.12"
python-dotenv = "^1.0.0"
sqlalchemy = "^2.0"
tenacity = "^8.0"
aiosqlite = "^0.19.0"
```

#### Инструменты разработки
```toml
pytest = "^7.4.0"
pytest-asyncio = "^0.21.0"
black = "^23.0.0"
isort = "^5.12.0"
mypy = "^1.5.0"
```

### Производительность
- **Время отклика**: < 100ms для большинства операций
- **Параллельные запросы**: Поддержка асинхронных операций
- **Кэширование**: Умное кэширование метаданных страниц
- **Масштабируемость**: Поддержка сотен репозиториев

---

## 🚀 Функциональные возможности

### 1. Иерархическая документация

#### Создание структуры репозитория
```python
await wikijs_create_repo_structure(
    repo_name="Frontend App",
    description="Modern React application",
    sections=["Overview", "Components", "API", "Testing", "Deployment"]
)
```

#### Вложенные страницы
```python
await wikijs_create_nested_page(
    title="Button Component",
    content="# Button Component\n\nReusable button...",
    parent_path="frontend-app/components"
)
```

#### Навигация по иерархии
```python
await wikijs_get_page_children(page_path="frontend-app/components")
```

### 2. Управление страницами

#### Создание страниц
- Поддержка Markdown контента
- Автоматическая генерация slug
- Настройка тегов и метаданных
- Поддержка локализации

#### Обновление и синхронизация
- Отслеживание изменений файлов
- Автоматическая синхронизация документации
- Массовые операции обновления

### 3. Интеграция с кодом

#### Анализ структуры кода
- Извлечение классов и функций
- Анализ зависимостей
- Автоматическая генерация документации

#### Связывание файлов
- Маппинг файлов кода на страницы документации
- Отслеживание изменений
- Автоматическое обновление связей

### 4. Поиск и навигация

#### Полнотекстовый поиск
- Поиск по содержимому страниц
- Фильтрация по пространствам
- Поддержка сложных запросов

#### Иерархическая навигация
- Древовидная структура страниц
- Навигация по родительским/дочерним страницам
- Автоматическое создание навигации

---

## 📦 Установка и настройка

### Windows (Рекомендуется)

#### 1. Предварительные требования
```cmd
# Установите Docker Desktop
# Скачайте с https://www.docker.com/products/docker-desktop/
```

#### 2. Быстрая установка
```cmd
git clone https://github.com/your-repo/wiki-js-mcp.git
cd wiki-js-mcp
quick-start.bat
```

#### 3. Настройка Wiki.js
1. Откройте `http://localhost:3000`
2. Создайте администратора
3. Перейдите в **Admin → API Access → Create Token**
4. Скопируйте токен

#### 4. Настройка MCP
```cmd
# Отредактируйте .env файл
notepad .env

# Замените WIKIJS_TOKEN на ваш токен
WIKIJS_TOKEN=your_actual_token_here

# Запустите MCP сервер
start-mcp.bat
```

### Linux/macOS

#### 1. Установка зависимостей
```bash
# Ubuntu/Debian
sudo apt-get install docker.io docker-compose

# macOS
brew install docker docker-compose
```

#### 2. Настройка проекта
```bash
git clone https://github.com/your-repo/wiki-js-mcp.git
cd wiki-js-mcp
cp config/env.example .env
```

#### 3. Запуск сервисов
```bash
# Запуск Wiki.js и PostgreSQL
docker-compose up -d db wiki

# Установка Python зависимостей
./scripts/setup.sh

# Настройка токена в .env
# Запуск MCP сервера
./scripts/start-server.sh
```

### Docker Compose конфигурация

#### Основные сервисы
```yaml
services:
  db:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: wikijs
      POSTGRES_USER: wikijs
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    volumes:
      - db_data:/var/lib/postgresql/data

  wiki:
    image: ghcr.io/requarks/wiki:2
    depends_on:
      db:
        condition: service_healthy
    ports:
      - "3000:3000"
    environment:
      DB_TYPE: postgres
      DB_HOST: db
      DB_PORT: 5432
      DB_USER: ${POSTGRES_USER}
      DB_PASS: ${POSTGRES_PASSWORD}
      DB_NAME: ${POSTGRES_DB}
```

---

## ⚙️ Конфигурация

### Переменные окружения

#### База данных
```env
POSTGRES_DB=wikijs
POSTGRES_USER=wikijs
POSTGRES_PASSWORD=your_secure_password_here
```

#### Wiki.js подключение
```env
WIKIJS_API_URL=http://localhost:3000
WIKIJS_TOKEN=your_jwt_token_here
WIKIJS_USERNAME=your_username
WIKIJS_PASSWORD=your_password
```

#### MCP сервер
```env
WIKIJS_MCP_DB=./data/mcp/wikijs_mappings.db
LOG_LEVEL=INFO
LOG_FILE=./logs/wikijs_mcp.log
REPOSITORY_ROOT=./
DEFAULT_SPACE_NAME=Documentation
DEFAULT_LOCALE=en
```

### Аутентификация

#### JWT Token (Рекомендуется)
1. В Wiki.js: **Admin → API Access → Create Token**
2. Выберите права: **Full Access**
3. Скопируйте токен в `.env`

#### Username/Password (Альтернатива)
```env
WIKIJS_USERNAME=admin@example.com
WIKIJS_PASSWORD=your_password
```

### Локализация
```env
# Поддерживаемые локали
DEFAULT_LOCALE=en  # Английский
DEFAULT_LOCALE=ru  # Русский
DEFAULT_LOCALE=de  # Немецкий
DEFAULT_LOCALE=fr  # Французский
DEFAULT_LOCALE=es  # Испанский
```

---

## 🔧 API и инструменты

### MCP Инструменты (21 всего)

#### 1. Иерархическая документация (4 инструмента)
```python
# Создание структуры репозитория
await wikijs_create_repo_structure(repo_name, description, sections)

# Создание вложенных страниц
await wikijs_create_nested_page(title, content, parent_path)

# Навигация по иерархии
await wikijs_get_page_children(page_id, page_path)

# Автоматическая организация
await wikijs_create_documentation_hierarchy(project_name, file_mappings)
```

#### 2. Управление страницами (4 инструмента)
```python
# Создание страниц
await wikijs_create_page(title, content, description, path)

# Обновление страниц
await wikijs_update_page(page_id, title, content, description)

# Получение страниц
await wikijs_get_page(page_id, slug)

# Поиск страниц
await wikijs_search_pages(query, space_id)
```

#### 3. Удаление и очистка (4 инструмента)
```python
# Удаление отдельных страниц
await wikijs_delete_page(page_id, page_path)

# Массовое удаление
await wikijs_batch_delete_pages(page_ids, page_paths, path_pattern)

# Удаление иерархий
await wikijs_delete_hierarchy(root_path, delete_mode)

# Очистка маппингов
await wikijs_cleanup_orphaned_mappings()
```

#### 4. Организация (3 инструмента)
```python
# Управление пространствами
await wikijs_list_spaces()
await wikijs_create_space(name, description)

# Управление коллекциями
await wikijs_manage_collections(collection_name, description, space_ids)
```

#### 5. Интеграция с файлами (3 инструмента)
```python
# Связывание файлов
await wikijs_link_file_to_page(file_path, page_id, relationship)

# Синхронизация изменений
await wikijs_sync_file_docs(file_path, change_summary, snippet)

# Генерация документации
await wikijs_generate_file_overview(file_path, include_functions, include_classes)
```

#### 6. Массовые операции (1 инструмент)
```python
# Массовое обновление
await wikijs_bulk_update_project_docs(summary, affected_files, context)
```

#### 7. Системные инструменты (2 инструмента)
```python
# Проверка подключения
await wikijs_connection_status()

# Контекст репозитория
await wikijs_repository_context()
```

### GraphQL API интеграция

#### Основные операции
```graphql
# Создание страницы
mutation CreatePage($input: PageCreateInput!) {
  pages {
    create(input: $input) {
      responseResult {
        succeeded
        errorCode
        slug
        message
      }
      page {
        id
        title
        path
      }
    }
  }
}

# Поиск страниц
query SearchPages($query: String!) {
  pages {
    search(query: $query) {
      results {
        id
        title
        path
        description
      }
    }
  }
}
```

---

## 💡 Примеры использования

### Создание документации проекта

#### 1. Создание структуры репозитория
```python
# Создание полной структуры документации
result = await wikijs_create_repo_structure(
    repo_name="My Frontend App",
    description="Modern React application with TypeScript and Vite",
    sections=[
        "Overview",
        "Components", 
        "API Integration",
        "State Management",
        "Testing",
        "Deployment",
        "Troubleshooting"
    ]
)
```

#### 2. Создание документации компонентов
```python
# Создание документации для компонента
await wikijs_create_nested_page(
    title="Button Component",
    content="""
# Button Component

Reusable button component with multiple variants and states.

## Props
- `variant`: 'primary' | 'secondary' | 'danger'
- `size`: 'small' | 'medium' | 'large'
- `disabled`: boolean

## Examples
```jsx
<Button variant="primary" size="medium">
  Click me
</Button>
```
    """,
    parent_path="my-frontend-app/components"
)
```

#### 3. Автоматическая организация файлов
```python
# Создание иерархии на основе структуры файлов
await wikijs_create_documentation_hierarchy(
    project_name="My Project",
    file_mappings=[
        {"file_path": "src/components/Button.tsx", "doc_path": "components/button"},
        {"file_path": "src/components/Modal.tsx", "doc_path": "components/modal"},
        {"file_path": "src/api/users.ts", "doc_path": "api/users"},
        {"file_path": "src/utils/helpers.ts", "doc_path": "utils/helpers"},
        {"file_path": "src/hooks/useAuth.ts", "doc_path": "hooks/use-auth"}
    ],
    auto_organize=True
)
```

### Управление документацией

#### 1. Массовое обновление
```python
# Обновление документации после рефакторинга
await wikijs_bulk_update_project_docs(
    summary="Refactored authentication system",
    affected_files=[
        "src/auth/AuthProvider.tsx",
        "src/hooks/useAuth.ts", 
        "src/components/LoginForm.tsx"
    ],
    context="Updated authentication to use JWT tokens and refresh mechanism",
    auto_create_missing=True
)
```

#### 2. Очистка устаревшей документации
```python
# Предварительный просмотр удаления (безопасно)
preview = await wikijs_delete_hierarchy(
    "old-project",
    delete_mode="include_root",
    confirm_deletion=False
)

# Фактическое удаление
if preview["total_pages"] > 0:
    await wikijs_delete_hierarchy(
        "old-project",
        delete_mode="include_root",
        confirm_deletion=True
    )
```

#### 3. Синхронизация изменений
```python
# Синхронизация изменений в файле
await wikijs_sync_file_docs(
    file_path="src/components/Button.tsx",
    change_summary="Added new variant 'outline' and improved accessibility",
    snippet="""
// Added outline variant
variant: 'primary' | 'secondary' | 'danger' | 'outline'
    """
)
```

### Интеграция с Cursor IDE

#### Глобальные правила для Cursor
```
Before writing any code, always:
1. Search existing documentation using wikijs_search_pages
2. Check for related components or modules
3. Follow established patterns and naming conventions
4. Create documentation before implementing new features
5. Update documentation when making changes
6. Use wikijs_create_repo_structure for new projects
```

#### Примеры использования в Cursor
```
# Перед созданием нового компонента
"Search the documentation for authentication patterns before implementing login"

# При создании компонентов
"Create nested documentation under frontend-app/components before building the React component"

# Для API разработки
"Check existing API documentation and create endpoint docs using the established structure"

# При рефакторинге
"Update all related documentation pages for the files I'm about to modify"
```

---

## 🔨 Разработка и расширение

### Структура проекта
```
wiki-js-mcp/
├── src/
│   └── wiki_mcp_server.py      # Основной MCP сервер
├── config/
│   ├── env.example             # Шаблон конфигурации
│   └── example.env             # Пример конфигурации
├── data/
│   ├── docs/                   # Документация Wiki.js
│   ├── mcp/                    # База данных маппингов
│   └── sideload/               # Дополнительные файлы
├── logs/                       # Логи приложения
├── docker-compose.yml          # Docker Compose конфигурация
├── Dockerfile.mcp              # Dockerfile для MCP сервера
├── pyproject.toml              # Зависимости Poetry
├── requirements.txt            # Зависимости pip
├── scripts/setup.sh            # Скрипт настройки
├── scripts/start-server.sh     # Запуск MCP сервера
├── scripts/test-server.sh      # Тестирование сервера
├── scripts/quick-start.bat     # Быстрый старт для Windows
├── scripts/start-mcp.bat       # Запуск MCP для Windows
├── README.md                   # Основная документация
├── README-WINDOWS.md           # Документация для Windows
├── HIERARCHICAL_FEATURES.md    # Иерархические возможности
├── DELETION_TOOLS.md           # Инструменты удаления
├── MCP_TOOLS_TEST_REPORT.md    # Отчет о тестировании
├── DEEPLINK_INTEGRATION_REPORT.md # Отчет о Deeplink интеграции
├── GRAPHQL_SCHEMA_ANALYSIS.md  # Анализ GraphQL схемы
└── INSTALL.md                  # Руководство по установке
```

### Добавление новых инструментов

#### 1. Создание нового MCP инструмента
```python
@mcp.tool()
async def wikijs_custom_tool(param1: str, param2: int = 10) -> str:
    """
    Описание нового инструмента.
    
    Args:
        param1: Описание параметра 1
        param2: Описание параметра 2 (по умолчанию 10)
    
    Returns:
        JSON строка с результатом
    """
    try:
        # Логика инструмента
        result = await client.graphql_request(query, variables)
        
        return json.dumps({
            "success": True,
            "data": result,
            "message": "Operation completed successfully"
        }, indent=2)
        
    except Exception as e:
        logger.error(f"Error in custom tool: {e}")
        return json.dumps({
            "success": False,
            "error": str(e)
        }, indent=2)
```

#### 2. Тестирование нового инструмента
```python
# В scripts/test-server.sh
echo "Testing custom tool..."
result=$(python -c "
import asyncio
from src.wiki_mcp_server import wikijs_custom_tool

async def test():
    result = await wikijs_custom_tool('test', 5)
    print(result)

asyncio.run(test())
")
echo "Result: $result"
```

### Расширение GraphQL интеграции

#### 1. Добавление новых запросов
```python
async def custom_graphql_query(self, custom_params: Dict) -> Dict:
    """Выполнение кастомного GraphQL запроса."""
    query = """
    query CustomQuery($param: String!) {
        custom {
            data(param: $param) {
                id
                name
                value
            }
        }
    }
    """
    
    variables = {"param": custom_params.get("param")}
    return await self.graphql_request(query, variables)
```

#### 2. Обработка ошибок
```python
async def safe_graphql_request(self, query: str, variables: Dict = None) -> Dict:
    """Безопасный GraphQL запрос с обработкой ошибок."""
    try:
        result = await self.graphql_request(query, variables)
        
        if "errors" in result:
            error_messages = [error.get("message", "Unknown error") 
                            for error in result["errors"]]
            raise Exception(f"GraphQL errors: {', '.join(error_messages)}")
            
        return result
        
    except httpx.RequestError as e:
        logger.error(f"Network error: {e}")
        raise Exception(f"Network error: {e}")
        
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise
```

---

## 🛠️ Устранение неполадок

### Общие проблемы

#### 1. Docker не запускается
```bash
# Проверка статуса Docker
docker --version
docker-compose --version

# Перезапуск Docker Desktop
# Проверка доступности портов
netstat -an | findstr :3000
```

#### 2. Wiki.js недоступен
```bash
# Проверка контейнеров
docker-compose ps

# Просмотр логов
docker-compose logs wiki
docker-compose logs db

# Проверка подключения
curl http://localhost:3000/healthz
```

#### 3. MCP сервер не подключается
```bash
# Проверка токена
echo $WIKIJS_TOKEN

# Тестирование подключения
./scripts/test-server.sh

# Проверка логов
tail -f logs/wikijs_mcp.log
```

#### 4. Проблемы с аутентификацией
```bash
# Проверка GraphQL запроса
curl -X POST http://localhost:3000/graphql \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"query":"query { pages { list { id title } } }"}'
```

### Отладка

#### Включение отладочного режима
```env
LOG_LEVEL=DEBUG
```

#### Проверка GraphQL схемы
```python
# Получение схемы GraphQL
await wikijs_graphql_introspection()

# Получение деталей схемы страниц
await wikijs_get_page_schema_details()
```

#### Мониторинг производительности
```python
# Проверка статуса подключения
await wikijs_connection_status()

# Контекст репозитория
await wikijs_repository_context()
```

### Восстановление после сбоев

#### 1. Сброс базы данных
```bash
# Остановка сервисов
docker-compose down

# Удаление данных
rm -rf postgres_data/
rm -rf data/mcp/wikijs_mappings.db

# Перезапуск
docker-compose up -d
```

#### 2. Очистка кэша
```bash
# Очистка Docker кэша
docker system prune -a

# Пересборка образов
docker-compose build --no-cache
```

#### 3. Восстановление маппингов
```python
# Очистка сиротских маппингов
await wikijs_cleanup_orphaned_mappings()

# Пересоздание связей
await wikijs_link_file_to_page(file_path, page_id, relationship)
```

---

## 🔒 Безопасность

### Аутентификация и авторизация

#### JWT токены
- **Безопасное хранение**: Токены хранятся в переменных окружения
- **Ограниченные права**: Рекомендуется создавать токены с минимальными правами
- **Регулярная ротация**: Периодическое обновление токенов

#### Защита API
```python
# Проверка токена перед запросами
async def authenticate(self) -> bool:
    if not self.token:
        raise Exception("No authentication token provided")
    
    # Проверка валидности токена
    try:
        result = await self.graphql_request("query { pages { list { id } } }")
        return True
    except Exception as e:
        logger.error(f"Authentication failed: {e}")
        return False
```

### Защита данных

#### Шифрование
- **HTTPS**: Все API запросы через HTTPS
- **Переменные окружения**: Конфиденциальные данные в .env файлах
- **База данных**: Изолированная PostgreSQL база данных

#### Доступ к файлам
```python
# Безопасное чтение файлов
def safe_read_file(file_path: str) -> str:
    """Безопасное чтение файла с проверкой пути."""
    try:
        # Проверка, что файл находится в разрешенной директории
        abs_path = os.path.abspath(file_path)
        if not abs_path.startswith(os.path.abspath(settings.REPOSITORY_ROOT)):
            raise Exception("File path outside allowed directory")
            
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
            
    except Exception as e:
        logger.error(f"Error reading file {file_path}: {e}")
        raise
```

### Логирование и мониторинг

#### Структурированное логирование
```python
# Настройка логирования
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL.upper()),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(settings.LOG_FILE),
        logging.StreamHandler()
    ]
)
```

#### Аудит операций
```python
# Логирование операций
def log_operation(operation: str, user: str, details: Dict):
    """Логирование операций для аудита."""
    logger.info(f"Operation: {operation}, User: {user}, Details: {details}")
```

---

## 📈 Производительность

### Оптимизация запросов

#### Кэширование
```python
# Кэширование метаданных страниц
@lru_cache(maxsize=1000)
def get_page_metadata(page_id: int) -> Dict:
    """Кэширование метаданных страниц."""
    return fetch_page_metadata(page_id)
```

#### Пакетные операции
```python
# Массовые операции для улучшения производительности
async def bulk_create_pages(pages_data: List[Dict]) -> List[Dict]:
    """Массовое создание страниц."""
    results = []
    for page_data in pages_data:
        result = await wikijs_create_page(**page_data)
        results.append(result)
    return results
```

### Мониторинг производительности

#### Метрики
- **Время отклика**: Среднее время выполнения запросов
- **Пропускная способность**: Количество запросов в секунду
- **Использование памяти**: Потребление RAM приложением
- **Использование CPU**: Загрузка процессора

#### Профилирование
```python
import time
import functools

def performance_monitor(func):
    """Декоратор для мониторинга производительности."""
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = await func(*args, **kwargs)
            execution_time = time.time() - start_time
            logger.info(f"{func.__name__} executed in {execution_time:.2f}s")
            return result
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"{func.__name__} failed after {execution_time:.2f}s: {e}")
            raise
    return wrapper
```

### Масштабирование

#### Горизонтальное масштабирование
- **Множественные экземпляры**: Запуск нескольких MCP серверов
- **Балансировка нагрузки**: Использование reverse proxy
- **Кластеризация**: Оркестрация через Kubernetes

#### Вертикальное масштабирование
- **Увеличение ресурсов**: Больше RAM и CPU
- **Оптимизация базы данных**: Индексы и настройки PostgreSQL
- **Кэширование**: Redis для кэширования данных

---

## 📄 Лицензия и поддержка

### Лицензия
Проект распространяется под лицензией **MIT License**.

```
MIT License

Copyright (c) 2024 Wiki.js MCP Server

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

### Поддержка

#### Сообщество
- **GitHub Issues**: Сообщения об ошибках и запросы функций
- **Discussions**: Обсуждения и вопросы
- **Wiki**: Документация и руководства

#### Коммерческая поддержка
- **Консультации**: Помощь с настройкой и развертыванием
- **Кастомизация**: Разработка дополнительных функций
- **Обучение**: Тренинги по использованию системы

### Вклад в проект

#### Как внести вклад
1. **Fork** репозитория
2. Создайте **feature branch** (`git checkout -b feature/amazing-feature`)
3. **Commit** изменения (`git commit -m 'Add amazing feature'`)
4. **Push** в branch (`git push origin feature/amazing-feature`)
5. Откройте **Pull Request**

#### Стандарты кода
- **Python**: PEP 8, Black форматирование
- **Type hints**: Обязательное использование типов
- **Documentation**: Docstrings для всех функций
- **Testing**: Покрытие тестами новых функций

---

## 📚 Дополнительные ресурсы

### Документация
- **[README.md](README.md)** - Основная документация
- **[README-WINDOWS.md](README-WINDOWS.md)** - Руководство для Windows
- **[HIERARCHICAL_FEATURES.md](HIERARCHICAL_FEATURES.md)** - Иерархические возможности
- **[DELETION_TOOLS.md](DELETION_TOOLS.md)** - Инструменты удаления
- **[MCP_TOOLS_TEST_REPORT.md](MCP_TOOLS_TEST_REPORT.md)** - Отчет о тестировании
- **[DEEPLINK_INTEGRATION_REPORT.md](DEEPLINK_INTEGRATION_REPORT.md)** - Deeplink интеграция
- **[GRAPHQL_SCHEMA_ANALYSIS.md](GRAPHQL_SCHEMA_ANALYSIS.md)** - Анализ GraphQL схемы
- **[INSTALL.md](INSTALL.md)** - Руководство по установке

### Связанные проекты
- **[Wiki.js](https://wiki.js.org/)** - Платформа документации
- **[Model Context Protocol](https://modelcontextprotocol.io/)** - Протокол MCP
- **[FastMCP](https://github.com/jlowin/fastmcp)** - Python SDK для MCP
- **[Cursor](https://cursor.sh/)** - AI-ассистент для разработки

### Полезные ссылки
- **[Docker Documentation](https://docs.docker.com/)** - Документация Docker
- **[GraphQL Tutorial](https://graphql.org/learn/)** - Обучение GraphQL
- **[Python AsyncIO](https://docs.python.org/3/library/asyncio.html)** - Асинхронное программирование
- **[SQLAlchemy Documentation](https://docs.sqlalchemy.org/)** - ORM документация

---

## 🎯 Заключение

Wiki.js MCP Server представляет собой мощное решение для интеграции документации с современными IDE и AI-ассистентами. Проект обеспечивает:

- ✅ **Полную интеграцию** с Wiki.js через GraphQL API
- ✅ **Иерархическую документацию** для масштабируемых проектов
- ✅ **Автоматическую генерацию** документации из кода
- ✅ **Docker-развертывание** для простой установки
- ✅ **21 MCP инструмент** для полного управления документацией
- ✅ **Мультиязычность** и гибкую конфигурацию
- ✅ **Безопасность** и производительность

Проект готов к использованию в продакшене и активно развивается сообществом. Для начала работы используйте `scripts/quick-start.bat` (Windows) или следуйте инструкциям в основном [README.md](../README.md).

---

**Готовы начать?** 🚀 Запустите `wikijs_create_repo_structure` и создайте свою первую иерархическую документацию! 📚✨ 