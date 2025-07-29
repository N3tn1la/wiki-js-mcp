# Wiki.js MCP Server - Техническая спецификация

## 📋 Общая информация

| Параметр | Значение |
|----------|----------|
| **Название проекта** | Wiki.js MCP Server |
| **Версия** | 1.0.0 |
| **Автор** | Sahil Pethe |
| **Лицензия** | MIT |
| **Язык программирования** | Python 3.12+ |
| **Фреймворк** | FastMCP |
| **Статус** | Production Ready |

## 🏗️ Архитектурная спецификация

### Компонентная архитектура

```
┌─────────────────────────────────────────────────────────────┐
│                    Presentation Layer                       │
├─────────────────────────────────────────────────────────────┤
│  Cursor IDE  │  VS Code  │  Other IDEs  │  CLI Tools       │
│  (MCP Client)│(MCP Client)│(MCP Client)  │  (MCP Client)    │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                   MCP Protocol Layer                        │
├─────────────────────────────────────────────────────────────┤
│                    FastMCP Framework                        │
│              (Model Context Protocol)                       │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                   Business Logic Layer                      │
├─────────────────────────────────────────────────────────────┤
│  WikiJSClient  │  DatabaseManager  │  FileAnalyzer         │
│  (GraphQL API) │  (SQLAlchemy ORM) │  (AST Parser)         │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    Data Access Layer                        │
├─────────────────────────────────────────────────────────────┤
│  Wiki.js API  │  SQLite DB  │  File System  │  PostgreSQL   │
│  (GraphQL)    │ (Mappings)  │ (Code Files)  │ (Wiki.js Data)│
└─────────────────────────────────────────────────────────────┘
```

### Слои архитектуры

#### 1. Presentation Layer
- **MCP Clients**: Cursor IDE, VS Code, другие IDE
- **Protocol**: Model Context Protocol (MCP)
- **Communication**: JSON-RPC over stdio

#### 2. MCP Protocol Layer
- **Framework**: FastMCP
- **Tools**: 21 MCP инструментов
- **Error Handling**: Стандартизированная обработка ошибок

#### 3. Business Logic Layer
- **WikiJSClient**: GraphQL API клиент
- **DatabaseManager**: Управление SQLite базой данных
- **FileAnalyzer**: Анализ структуры кода

#### 4. Data Access Layer
- **Wiki.js GraphQL API**: Основной источник данных
- **SQLite**: Локальная база данных маппингов
- **PostgreSQL**: База данных Wiki.js

## ⚙️ Технические требования

### Системные требования

#### Минимальные требования
- **OS**: Windows 10+, macOS 10.15+, Ubuntu 18.04+
- **Python**: 3.12.0+
- **Docker**: 20.10.0+
- **Docker Compose**: 2.0.0+
- **RAM**: 2GB
- **Storage**: 1GB свободного места
- **Network**: Интернет для загрузки образов

#### Рекомендуемые требования
- **OS**: Windows 11+, macOS 12+, Ubuntu 20.04+
- **Python**: 3.12.5+
- **Docker**: 24.0.0+
- **Docker Compose**: 2.20.0+
- **RAM**: 4GB+
- **Storage**: 5GB+ свободного места
- **Network**: Стабильное интернет-соединение

### Зависимости

#### Основные зависимости (Python)
```toml
# Core Framework
fastmcp = "^0.1.0"              # MCP framework
httpx = "^0.27.0"               # Async HTTP client
pydantic = "^2.0"               # Data validation
pydantic-settings = "^2.0"      # Settings management

# Database
sqlalchemy = "^2.0"             # ORM
aiosqlite = "^0.19.0"           # Async SQLite

# Utilities
python-slugify = "^8.0"         # URL slug generation
markdown = "^3.5"               # Markdown processing
beautifulsoup4 = "^4.12"        # HTML parsing
python-dotenv = "^1.0.0"        # Environment variables
tenacity = "^8.0"               # Retry logic
```

#### Инструменты разработки
```toml
# Testing
pytest = "^7.4.0"
pytest-asyncio = "^0.21.0"

# Code Quality
black = "^23.0.0"               # Code formatting
isort = "^5.12.0"               # Import sorting
mypy = "^1.5.0"                 # Type checking
```

#### Docker зависимости
```yaml
# Wiki.js
ghcr.io/requarks/wiki:2         # Wiki.js application

# Database
postgres:15-alpine              # PostgreSQL database

# MCP Server
python:3.12-alpine              # Python runtime
```

## 🔧 Конфигурационная спецификация

### Переменные окружения

#### Обязательные переменные
```env
# Wiki.js Connection
WIKIJS_API_URL=http://localhost:3000
WIKIJS_TOKEN=your_jwt_token_here

# Database Configuration
WIKIJS_MCP_DB=./data/mcp/wikijs_mappings.db
```

#### Опциональные переменные
```env
# Authentication (Alternative)
WIKIJS_USERNAME=admin@example.com
WIKIJS_PASSWORD=your_password

# Logging
LOG_LEVEL=INFO
LOG_FILE=./logs/wikijs_mcp.log

# Repository Settings
REPOSITORY_ROOT=./
DEFAULT_SPACE_NAME=Documentation
DEFAULT_LOCALE=en
```

### Конфигурационные файлы

#### Docker Compose
```yaml
version: '3.8'
services:
  db:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: ${POSTGRES_DB:-wikijs}
      POSTGRES_USER: ${POSTGRES_USER:-wikijs}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:-wikijsrocks1}
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

#### MCP Configuration
```json
{
  "mcpServers": {
    "wikijs": {
      "command": "python",
      "args": ["src/wiki_mcp_server.py"],
      "env": {
        "WIKIJS_API_URL": "http://localhost:3000",
        "WIKIJS_TOKEN": "your_token_here"
      }
    }
  }
}
```

## 📊 Спецификация API

### MCP Инструменты (21 инструмент)

#### 1. Иерархическая документация (4 инструмента)

##### `wikijs_create_repo_structure`
```python
async def wikijs_create_repo_structure(
    repo_name: str,
    description: str = None,
    sections: list = None
) -> str
```
**Назначение**: Создание полной структуры документации репозитория
**Возвращает**: JSON с информацией о созданных страницах

##### `wikijs_create_nested_page`
```python
async def wikijs_create_nested_page(
    title: str,
    content: str,
    parent_path: str,
    create_parent_if_missing: bool = True
) -> str
```
**Назначение**: Создание вложенных страниц с иерархической структурой
**Возвращает**: JSON с информацией о созданной странице

##### `wikijs_get_page_children`
```python
async def wikijs_get_page_children(
    page_id: int = None,
    page_path: str = None
) -> str
```
**Назначение**: Получение дочерних страниц для навигации
**Возвращает**: JSON с списком дочерних страниц

##### `wikijs_create_documentation_hierarchy`
```python
async def wikijs_create_documentation_hierarchy(
    project_name: str,
    file_mappings: list,
    auto_organize: bool = True
) -> str
```
**Назначение**: Создание документационной иерархии на основе структуры файлов
**Возвращает**: JSON с информацией о созданной иерархии

#### 2. Управление страницами (4 инструмента)

##### `wikijs_create_page`
```python
async def wikijs_create_page(
    title: str,
    content: str,
    description: str = None,
    path: str = None
) -> str
```
**Назначение**: Создание новых страниц
**Возвращает**: JSON с информацией о созданной странице

##### `wikijs_update_page`
```python
async def wikijs_update_page(
    page_id: int,
    title: str = None,
    content: str = None,
    description: str = None
) -> str
```
**Назначение**: Обновление существующих страниц
**Возвращает**: JSON с информацией об обновленной странице

##### `wikijs_get_page`
```python
async def wikijs_get_page(
    page_id: int = None,
    slug: str = None
) -> str
```
**Назначение**: Получение страницы по ID или slug
**Возвращает**: JSON с данными страницы

##### `wikijs_search_pages`
```python
async def wikijs_search_pages(
    query: str,
    space_id: str = None
) -> str
```
**Назначение**: Поиск страниц по тексту
**Возвращает**: JSON с результатами поиска

#### 3. Удаление и очистка (4 инструмента)

##### `wikijs_delete_page`
```python
async def wikijs_delete_page(
    page_id: int = None,
    page_path: str = None,
    remove_file_mapping: bool = True
) -> str
```
**Назначение**: Удаление отдельных страниц
**Возвращает**: JSON с информацией об удалении

##### `wikijs_batch_delete_pages`
```python
async def wikijs_batch_delete_pages(
    page_ids: List[int] = None,
    page_paths: List[str] = None,
    path_pattern: str = None,
    confirm_deletion: bool = False,
    remove_file_mappings: bool = True
) -> str
```
**Назначение**: Массовое удаление страниц
**Возвращает**: JSON с результатами массового удаления

##### `wikijs_delete_hierarchy`
```python
async def wikijs_delete_hierarchy(
    root_path: str,
    delete_mode: str = "children_only",
    confirm_deletion: bool = False,
    remove_file_mappings: bool = True
) -> str
```
**Назначение**: Удаление иерархий страниц
**Возвращает**: JSON с результатами удаления иерархии

##### `wikijs_cleanup_orphaned_mappings`
```python
async def wikijs_cleanup_orphaned_mappings() -> str
```
**Назначение**: Очистка сиротских маппингов
**Возвращает**: JSON с результатами очистки

#### 4. Организация (3 инструмента)

##### `wikijs_list_spaces`
```python
async def wikijs_list_spaces() -> str
```
**Назначение**: Список пространств документации
**Возвращает**: JSON со списком пространств

##### `wikijs_create_space`
```python
async def wikijs_create_space(
    name: str,
    description: str = None
) -> str
```
**Назначение**: Создание новых пространств
**Возвращает**: JSON с информацией о созданном пространстве

##### `wikijs_manage_collections`
```python
async def wikijs_manage_collections(
    collection_name: str,
    description: str = None,
    space_ids: List[int] = None
) -> str
```
**Назначение**: Управление коллекциями страниц
**Возвращает**: JSON с информацией о коллекции

#### 5. Интеграция с файлами (3 инструмента)

##### `wikijs_link_file_to_page`
```python
async def wikijs_link_file_to_page(
    file_path: str,
    page_id: int,
    relationship: str = "documents"
) -> str
```
**Назначение**: Связывание файлов кода со страницами документации
**Возвращает**: JSON с информацией о созданной связи

##### `wikijs_sync_file_docs`
```python
async def wikijs_sync_file_docs(
    file_path: str,
    change_summary: str,
    snippet: str = None
) -> str
```
**Назначение**: Синхронизация изменений в файлах с документацией
**Возвращает**: JSON с информацией о синхронизации

##### `wikijs_generate_file_overview`
```python
async def wikijs_generate_file_overview(
    file_path: str,
    include_functions: bool = True,
    include_classes: bool = True,
    include_dependencies: bool = True,
    include_examples: bool = False,
    target_page_id: int = None
) -> str
```
**Назначение**: Автоматическая генерация документации файла
**Возвращает**: JSON с информацией о созданной документации

#### 6. Массовые операции (1 инструмент)

##### `wikijs_bulk_update_project_docs`
```python
async def wikijs_bulk_update_project_docs(
    summary: str,
    affected_files: list,
    context: str,
    auto_create_missing: bool = True
) -> str
```
**Назначение**: Массовое обновление документации проекта
**Возвращает**: JSON с результатами массового обновления

#### 7. Системные инструменты (2 инструмента)

##### `wikijs_connection_status`
```python
async def wikijs_connection_status() -> str
```
**Назначение**: Проверка статуса подключения к Wiki.js
**Возвращает**: JSON со статусом подключения

##### `wikijs_repository_context`
```python
async def wikijs_repository_context() -> str
```
**Назначение**: Получение контекста репозитория
**Возвращает**: JSON с контекстом репозитория

### GraphQL API спецификация

#### Основные операции

##### Создание страницы
```graphql
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
        description
        content
        tags
        locale
        createdAt
        updatedAt
      }
    }
  }
}
```

##### Поиск страниц
```graphql
query SearchPages($query: String!, $path: String, $locale: String) {
  pages {
    search(query: $query, path: $path, locale: $locale) {
      results {
        id
        title
        path
        description
        tags
        locale
        createdAt
        updatedAt
      }
      totalHits
      suggestions
    }
  }
}
```

##### Получение страницы
```graphql
query GetPage($id: Int!) {
  pages {
    single(id: $id) {
      id
      title
      path
      description
      content
      tags
      locale
      isPrivate
      isPublished
      createdAt
      updatedAt
      authorId
      authorName
      creatorId
      creatorName
    }
  }
}
```

## 🗄️ Спецификация базы данных

### SQLite схема (маппинги)

#### Таблица `file_mappings`
```sql
CREATE TABLE file_mappings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    file_path VARCHAR NOT NULL UNIQUE,
    page_id INTEGER NOT NULL,
    relationship_type VARCHAR NOT NULL,
    last_updated DATETIME DEFAULT CURRENT_TIMESTAMP,
    file_hash VARCHAR,
    repository_root VARCHAR DEFAULT '',
    space_name VARCHAR DEFAULT ''
);
```

#### Таблица `repository_contexts`
```sql
CREATE TABLE repository_contexts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    root_path VARCHAR NOT NULL UNIQUE,
    space_name VARCHAR NOT NULL,
    space_id INTEGER,
    last_updated DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### PostgreSQL схема (Wiki.js)

#### Основные таблицы Wiki.js
- `pages` - Страницы документации
- `spaces` - Пространства документации
- `users` - Пользователи системы
- `groups` - Группы пользователей
- `permissions` - Права доступа
- `tags` - Теги страниц
- `comments` - Комментарии
- `history` - История изменений

## 🔒 Спецификация безопасности

### Аутентификация

#### JWT токены
- **Алгоритм**: RS256 (RSA + SHA256)
- **Время жизни**: Настраивается в Wiki.js
- **Хранение**: Переменные окружения
- **Передача**: HTTP заголовок Authorization

#### Username/Password (альтернатива)
- **Протокол**: HTTP Basic Auth
- **Шифрование**: HTTPS/TLS
- **Хранение**: Переменные окружения

### Авторизация

#### Права доступа
- **Full Access**: Полный доступ к API
- **Read Only**: Только чтение
- **Custom**: Настраиваемые права

#### Проверка прав
```python
async def check_permissions(operation: str, user_id: int) -> bool:
    """Проверка прав пользователя на операцию."""
    # Реализация проверки прав
    pass
```

### Защита данных

#### Шифрование
- **Транспорт**: HTTPS/TLS 1.2+
- **Хранение**: Переменные окружения
- **База данных**: Изолированная PostgreSQL

#### Валидация входных данных
```python
from pydantic import BaseModel, Field

class PageCreateInput(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    content: str = Field(..., min_length=1)
    description: str = Field(None, max_length=500)
    path: str = Field(None, regex=r'^[a-z0-9\-/]+$')
```

## 📈 Спецификация производительности

### Метрики производительности

#### Время отклика
- **Создание страницы**: < 200ms
- **Обновление страницы**: < 150ms
- **Поиск страниц**: < 100ms
- **Получение страницы**: < 50ms

#### Пропускная способность
- **Запросов в секунду**: 100+ RPS
- **Параллельных соединений**: 50+
- **Размер ответа**: < 1MB

#### Использование ресурсов
- **RAM**: < 512MB
- **CPU**: < 10% при нагрузке
- **Дисковое пространство**: < 100MB

### Оптимизация

#### Кэширование
```python
from functools import lru_cache

@lru_cache(maxsize=1000)
def get_page_metadata(page_id: int) -> Dict:
    """Кэширование метаданных страниц."""
    return fetch_page_metadata(page_id)
```

#### Асинхронные операции
```python
async def bulk_operations(pages_data: List[Dict]) -> List[Dict]:
    """Массовые асинхронные операции."""
    tasks = [process_page(page_data) for page_data in pages_data]
    return await asyncio.gather(*tasks)
```

#### Пакетные запросы
```python
async def batch_graphql_requests(queries: List[str]) -> List[Dict]:
    """Пакетные GraphQL запросы."""
    # Реализация пакетных запросов
    pass
```

## 🧪 Спецификация тестирования

### Типы тестов

#### Unit тесты
- **Покрытие**: 80%+
- **Фреймворк**: pytest
- **Асинхронность**: pytest-asyncio

#### Integration тесты
- **API тесты**: httpx
- **База данных**: SQLite in-memory
- **Mock сервисы**: unittest.mock

#### End-to-End тесты
- **Docker окружение**: docker-compose
- **Wiki.js**: Реальный экземпляр
- **MCP клиент**: Тестовый клиент

### Примеры тестов

#### Unit тест
```python
import pytest
from src.wiki_mcp_server import wikijs_create_page

@pytest.mark.asyncio
async def test_create_page_success():
    """Тест успешного создания страницы."""
    result = await wikijs_create_page(
        title="Test Page",
        content="# Test Content"
    )
    
    assert result["success"] is True
    assert "pageId" in result
    assert result["title"] == "Test Page"
```

#### Integration тест
```python
@pytest.mark.asyncio
async def test_wiki_js_connection():
    """Тест подключения к Wiki.js."""
    client = WikiJSClient()
    is_connected = await client.authenticate()
    
    assert is_connected is True
```

## 📦 Спецификация развертывания

### Docker развертывание

#### Dockerfile
```dockerfile
FROM python:3.12-alpine

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY src/ ./src/
COPY config/ ./config/

CMD ["python", "src/wiki_mcp_server.py"]
```

#### Docker Compose
```yaml
version: '3.8'
services:
  mcp-server:
    build: .
    environment:
      - WIKIJS_API_URL=http://wiki:3000
      - WIKIJS_TOKEN=${WIKIJS_TOKEN}
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
    depends_on:
      - wiki
```

### Локальное развертывание

#### Установка зависимостей
```bash
pip install -r requirements.txt
```

#### Запуск сервера
```bash
python src/wiki_mcp_server.py
```

### Продакшен развертывание

#### Kubernetes
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: wikijs-mcp-server
spec:
  replicas: 3
  selector:
    matchLabels:
      app: wikijs-mcp-server
  template:
    metadata:
      labels:
        app: wikijs-mcp-server
    spec:
      containers:
      - name: mcp-server
        image: wikijs-mcp:latest
        env:
        - name: WIKIJS_API_URL
          value: "http://wiki-service:3000"
        - name: WIKIJS_TOKEN
          valueFrom:
            secretKeyRef:
              name: wikijs-secrets
              key: token
```

## 🔄 Спецификация версионирования

### Семантическое версионирование
- **Major**: Несовместимые изменения API
- **Minor**: Новая функциональность, обратная совместимость
- **Patch**: Исправления ошибок, обратная совместимость

### История версий

#### v1.0.0 (Текущая)
- ✅ Полная интеграция с Wiki.js GraphQL API
- ✅ 21 MCP инструмент
- ✅ Иерархическая документация
- ✅ Docker развертывание
- ✅ Мультиязычность

#### Планируемые версии
- **v1.1.0**: Расширенные возможности поиска
- **v1.2.0**: Интеграция с Git hooks
- **v2.0.0**: Поддержка других платформ документации

---

**Техническая спецификация завершена.** 📋 Проект готов к разработке и развертыванию согласно указанным техническим требованиям. 🚀 