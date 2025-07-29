# Wiki.js MCP Server - Руководство по разработке

## 📋 Содержание

1. [Настройка среды разработки](#настройка-среды-разработки)
2. [Структура проекта](#структура-проекта)
3. [Стандарты кода](#стандарты-кода)
4. [Добавление новых функций](#добавление-новых-функций)
5. [Тестирование](#тестирование)
6. [Отладка](#отладка)
7. [Документирование](#документирование)
8. [Рабочий процесс](#рабочий-процесс)
9. [Публикация](#публикация)

---

## 🛠️ Настройка среды разработки

### Предварительные требования

#### Системные требования
- **Python**: 3.12.0+
- **Docker**: 20.10.0+
- **Docker Compose**: 2.0.0+
- **Git**: 2.30.0+
- **IDE**: VS Code, PyCharm, или Cursor (рекомендуется)

#### Установка зависимостей разработки

```bash
# Клонирование репозитория
git clone https://github.com/your-repo/wiki-js-mcp.git
cd wiki-js-mcp

# Создание виртуального окружения
python -m venv venv

# Активация виртуального окружения
# Windows
venv\Scripts\activate
# Linux/macOS
source venv/bin/activate

# Установка зависимостей
pip install -r requirements.txt

# Установка инструментов разработки
pip install -e .
```

### Настройка IDE

#### VS Code
```json
// .vscode/settings.json
{
    "python.defaultInterpreterPath": "./venv/bin/python",
    "python.linting.enabled": true,
    "python.linting.pylintEnabled": false,
    "python.linting.flake8Enabled": true,
    "python.formatting.provider": "black",
    "python.sortImports.args": ["--profile", "black"],
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": {
        "source.organizeImports": true
    }
}
```

#### PyCharm
1. Откройте проект в PyCharm
2. Настройте интерпретатор Python: `File → Settings → Project → Python Interpreter`
3. Выберите виртуальное окружение: `./venv/bin/python`
4. Установите инструменты: `Tools → External Tools`

### Настройка Git hooks

```bash
# Установка pre-commit hooks
pip install pre-commit
pre-commit install

# Создание .pre-commit-config.yaml
cat > .pre-commit-config.yaml << EOF
repos:
  - repo: https://github.com/psf/black
    rev: 23.0.0
    hooks:
      - id: black
        language_version: python3.12
  - repo: https://github.com/pycqa/isort
    rev: 5.12.0
    hooks:
      - id: isort
        args: ["--profile", "black"]
  - repo: https://github.com/pycqa/flake8
    rev: 6.0.0
    hooks:
      - id: flake8
EOF
```

---

## 📁 Структура проекта

### Общая структура
```
wiki-js-mcp/
├── src/                          # Исходный код
│   └── wiki_mcp_server.py       # Основной MCP сервер
├── config/                       # Конфигурационные файлы
│   ├── env.example              # Шаблон переменных окружения
│   └── example.env              # Пример конфигурации
├── data/                        # Данные приложения
│   ├── docs/                    # Документация Wiki.js
│   ├── mcp/                     # База данных маппингов
│   └── sideload/                # Дополнительные файлы
├── logs/                        # Логи приложения
├── tests/                       # Тесты
│   ├── unit/                    # Unit тесты
│   ├── integration/             # Integration тесты
│   └── fixtures/                # Тестовые данные
├── docs/                        # Документация разработки
├── scripts/                     # Скрипты разработки
├── docker-compose.yml           # Docker Compose конфигурация
├── Dockerfile.mcp               # Dockerfile для MCP сервера
├── pyproject.toml               # Poetry конфигурация
├── requirements.txt             # Зависимости pip
├── scripts/setup.sh             # Скрипт настройки
├── scripts/start-server.sh      # Запуск MCP сервера
├── scripts/test-server.sh       # Тестирование сервера
├── scripts/quick-start.bat      # Быстрый старт для Windows
├── scripts/start-mcp.bat        # Запуск MCP для Windows
└── README.md                    # Основная документация
```

### Структура исходного кода

#### Основной файл сервера
```python
# src/wiki_mcp_server.py
#!/usr/bin/env python3
"""Wiki.js MCP server using FastMCP - GraphQL version."""

# Импорты
import os
import sys
import json
import logging
from typing import Optional, List, Dict, Any
from fastmcp import FastMCP
from pydantic import Field
from pydantic_settings import BaseSettings

# Конфигурация
class Settings(BaseSettings):
    """Настройки приложения."""
    WIKIJS_API_URL: str = Field(default="http://localhost:3000")
    WIKIJS_TOKEN: Optional[str] = Field(default=None)
    # ... другие настройки

# Создание MCP сервера
mcp = FastMCP("Wiki.js Integration")

# Клиент Wiki.js
class WikiJSClient:
    """Wiki.js GraphQL API клиент."""
    # ... реализация

# MCP инструменты
@mcp.tool()
async def wikijs_create_page(title: str, content: str, description: str = None) -> str:
    """Создание новой страницы в Wiki.js."""
    # ... реализация

# Точка входа
def main():
    """Точка входа в приложение."""
    # ... реализация

if __name__ == "__main__":
    main()
```

---

## 📝 Стандарты кода

### Python стиль кода

#### PEP 8 соблюдение
```python
# ✅ Правильно
def create_page(title: str, content: str) -> Dict[str, Any]:
    """Создание страницы с указанным заголовком и содержимым."""
    return {"title": title, "content": content}

# ❌ Неправильно
def createPage(title,content):
    return {"title":title,"content":content}
```

#### Type hints
```python
# ✅ Обязательные type hints
from typing import Optional, List, Dict, Any

async def create_page(
    title: str,
    content: str,
    description: Optional[str] = None,
    tags: List[str] = None
) -> Dict[str, Any]:
    """Создание страницы с типизацией."""
    pass
```

#### Docstrings
```python
def process_file_content(content: str) -> str:
    """
    Обработка содержимого файла для создания документации.
    
    Args:
        content: Исходное содержимое файла
        
    Returns:
        Обработанное содержимое для документации
        
    Raises:
        ValueError: Если содержимое пустое
        
    Example:
        >>> process_file_content("# Hello World")
        "# Hello World\\n\\nДокументация..."
    """
    if not content:
        raise ValueError("Content cannot be empty")
    
    return f"{content}\n\nДокументация..."
```

### Форматирование кода

#### Black форматирование
```bash
# Форматирование всего проекта
black src/ tests/

# Форматирование конкретного файла
black src/wiki_mcp_server.py

# Проверка форматирования без изменений
black --check src/
```

#### isort сортировка импортов
```bash
# Сортировка импортов
isort src/ tests/

# Проверка сортировки
isort --check-only src/
```

#### mypy проверка типов
```bash
# Проверка типов
mypy src/

# Строгая проверка
mypy --strict src/
```

### Структура функций

#### Асинхронные функции
```python
async def wikijs_create_page(title: str, content: str) -> str:
    """
    Создание новой страницы в Wiki.js.
    
    Args:
        title: Заголовок страницы
        content: Содержимое страницы
        
    Returns:
        JSON строка с результатом операции
    """
    try:
        # Валидация входных данных
        if not title or not content:
            raise ValueError("Title and content are required")
        
        # Подготовка данных
        page_data = {
            "title": title.strip(),
            "content": content.strip(),
            "description": f"Page: {title}",
            "path": slugify(title),
            "locale": settings.DEFAULT_LOCALE,
            "tags": ["documentation"],
            "isPublished": True,
            "isPrivate": False,
            "editor": "markdown"
        }
        
        # Выполнение GraphQL запроса
        result = await client.create_page(page_data)
        
        # Обработка результата
        if result.get("success"):
            return json.dumps({
                "success": True,
                "pageId": result["page"]["id"],
                "title": result["page"]["title"],
                "path": result["page"]["path"],
                "message": "Page created successfully"
            }, indent=2)
        else:
            return json.dumps({
                "success": False,
                "error": result.get("error", "Unknown error")
            }, indent=2)
            
    except Exception as e:
        logger.error(f"Error creating page: {e}")
        return json.dumps({
            "success": False,
            "error": str(e)
        }, indent=2)
```

---

## 🚀 Добавление новых функций

### Процесс добавления новой функции

#### 1. Планирование
```python
# Определение требований
"""
Новая функция: wikijs_export_pages
- Экспорт страниц в различных форматах (Markdown, PDF, HTML)
- Поддержка массового экспорта
- Настройка формата и опций экспорта
"""
```

#### 2. Создание функции
```python
@mcp.tool()
async def wikijs_export_pages(
    page_ids: List[int] = None,
    page_paths: List[str] = None,
    format: str = "markdown",
    include_metadata: bool = True,
    output_dir: str = "./exports"
) -> str:
    """
    Экспорт страниц в различных форматах.
    
    Args:
        page_ids: Список ID страниц для экспорта
        page_paths: Список путей страниц для экспорта
        format: Формат экспорта (markdown, pdf, html)
        include_metadata: Включить метаданные
        output_dir: Директория для сохранения
        
    Returns:
        JSON строка с результатом экспорта
    """
    try:
        # Валидация параметров
        if not page_ids and not page_paths:
            raise ValueError("Either page_ids or page_paths must be provided")
        
        if format not in ["markdown", "pdf", "html"]:
            raise ValueError("Format must be markdown, pdf, or html")
        
        # Получение страниц
        pages = []
        if page_ids:
            for page_id in page_ids:
                page = await client.get_page(page_id)
                pages.append(page)
        
        if page_paths:
            for page_path in page_paths:
                page = await client.get_page_by_path(page_path)
                pages.append(page)
        
        # Экспорт страниц
        exported_files = []
        for page in pages:
            exported_file = await export_page(page, format, include_metadata, output_dir)
            exported_files.append(exported_file)
        
        return json.dumps({
            "success": True,
            "exported_files": exported_files,
            "total_exported": len(exported_files),
            "format": format,
            "output_dir": output_dir
        }, indent=2)
        
    except Exception as e:
        logger.error(f"Error exporting pages: {e}")
        return json.dumps({
            "success": False,
            "error": str(e)
        }, indent=2)

async def export_page(page: Dict, format: str, include_metadata: bool, output_dir: str) -> str:
    """Экспорт отдельной страницы."""
    # Реализация экспорта
    pass
```

#### 3. Добавление тестов
```python
# tests/unit/test_export.py
import pytest
from unittest.mock import AsyncMock, patch
from src.wiki_mcp_server import wikijs_export_pages

@pytest.mark.asyncio
async def test_export_pages_success():
    """Тест успешного экспорта страниц."""
    with patch('src.wiki_mcp_server.client') as mock_client:
        mock_client.get_page.return_value = {
            "id": 1,
            "title": "Test Page",
            "content": "# Test Content"
        }
        
        result = await wikijs_export_pages(
            page_ids=[1],
            format="markdown",
            output_dir="./test_exports"
        )
        
        result_data = json.loads(result)
        assert result_data["success"] is True
        assert result_data["total_exported"] == 1
        assert result_data["format"] == "markdown"

@pytest.mark.asyncio
async def test_export_pages_invalid_format():
    """Тест экспорта с неверным форматом."""
    result = await wikijs_export_pages(
        page_ids=[1],
        format="invalid_format"
    )
    
    result_data = json.loads(result)
    assert result_data["success"] is False
    assert "Format must be" in result_data["error"]
```

#### 4. Обновление документации
```markdown
## Экспорт страниц

### wikijs_export_pages
Экспорт страниц в различных форматах (Markdown, PDF, HTML).

**Параметры:**
- `page_ids`: Список ID страниц для экспорта
- `page_paths`: Список путей страниц для экспорта
- `format`: Формат экспорта (markdown, pdf, html)
- `include_metadata`: Включить метаданные
- `output_dir`: Директория для сохранения

**Пример использования:**
```python
await wikijs_export_pages(
    page_ids=[1, 2, 3],
    format="markdown",
    output_dir="./exports"
)
```
```

### Добавление новых GraphQL запросов

#### 1. Расширение WikiJSClient
```python
class WikiJSClient:
    """Wiki.js GraphQL API клиент."""
    
    async def export_pages(self, page_ids: List[int], format: str) -> Dict:
        """Экспорт страниц через GraphQL API."""
        query = """
        query ExportPages($pageIds: [Int!]!, $format: String!) {
            pages {
                export(pageIds: $pageIds, format: $format) {
                    files {
                        filename
                        content
                        size
                    }
                    totalSize
                    format
                }
            }
        }
        """
        
        variables = {
            "pageIds": page_ids,
            "format": format
        }
        
        return await self.graphql_request(query, variables)
```

#### 2. Обработка ошибок
```python
async def safe_export_pages(self, page_ids: List[int], format: str) -> Dict:
    """Безопасный экспорт страниц с обработкой ошибок."""
    try:
        result = await self.export_pages(page_ids, format)
        
        if "errors" in result:
            error_messages = [error.get("message", "Unknown error") 
                            for error in result["errors"]]
            raise Exception(f"GraphQL errors: {', '.join(error_messages)}")
            
        return result
        
    except httpx.RequestError as e:
        logger.error(f"Network error during export: {e}")
        raise Exception(f"Network error: {e}")
        
    except Exception as e:
        logger.error(f"Unexpected error during export: {e}")
        raise
```

---

## 🧪 Тестирование

### Типы тестов

#### Unit тесты
```python
# tests/unit/test_wiki_mcp_server.py
import pytest
from unittest.mock import AsyncMock, patch
from src.wiki_mcp_server import wikijs_create_page, WikiJSClient

@pytest.mark.asyncio
async def test_create_page_success():
    """Тест успешного создания страницы."""
    with patch('src.wiki_mcp_server.client') as mock_client:
        mock_client.create_page.return_value = {
            "success": True,
            "page": {
                "id": 123,
                "title": "Test Page",
                "path": "test-page"
            }
        }
        
        result = await wikijs_create_page(
            title="Test Page",
            content="# Test Content"
        )
        
        result_data = json.loads(result)
        assert result_data["success"] is True
        assert result_data["pageId"] == 123
        assert result_data["title"] == "Test Page"

@pytest.mark.asyncio
async def test_create_page_validation_error():
    """Тест валидации входных данных."""
    result = await wikijs_create_page(
        title="",  # Пустой заголовок
        content="# Test Content"
    )
    
    result_data = json.loads(result)
    assert result_data["success"] is False
    assert "Title is required" in result_data["error"]
```

#### Integration тесты
```python
# tests/integration/test_wiki_js_integration.py
import pytest
import httpx
from src.wiki_mcp_server import WikiJSClient

@pytest.mark.asyncio
async def test_wiki_js_connection():
    """Тест подключения к Wiki.js."""
    client = WikiJSClient()
    
    # Проверка подключения
    is_connected = await client.authenticate()
    assert is_connected is True
    
    # Проверка создания страницы
    page_data = {
        "title": "Integration Test Page",
        "content": "# Integration Test",
        "description": "Test page for integration tests",
        "path": "integration-test",
        "locale": "en",
        "tags": ["test"],
        "isPublished": True,
        "isPrivate": False,
        "editor": "markdown"
    }
    
    result = await client.create_page(page_data)
    assert result["success"] is True
    assert "page" in result
    
    # Очистка - удаление тестовой страницы
    page_id = result["page"]["id"]
    await client.delete_page(page_id)
```

#### End-to-End тесты
```python
# tests/e2e/test_full_workflow.py
import pytest
import asyncio
from src.wiki_mcp_server import wikijs_create_repo_structure, wikijs_create_nested_page

@pytest.mark.asyncio
async def test_full_documentation_workflow():
    """Тест полного рабочего процесса создания документации."""
    
    # 1. Создание структуры репозитория
    repo_result = await wikijs_create_repo_structure(
        repo_name="Test Project",
        description="Test project for E2E testing",
        sections=["Overview", "Components", "API"]
    )
    
    repo_data = json.loads(repo_result)
    assert repo_data["success"] is True
    
    # 2. Создание вложенных страниц
    page_result = await wikijs_create_nested_page(
        title="Test Component",
        content="# Test Component\n\nThis is a test component.",
        parent_path="test-project/components"
    )
    
    page_data = json.loads(page_result)
    assert page_data["success"] is True
    
    # 3. Проверка иерархии
    children_result = await wikijs_get_page_children(
        page_path="test-project/components"
    )
    
    children_data = json.loads(children_result)
    assert children_data["total_children"] >= 1
```

### Запуск тестов

#### Команды тестирования
```bash
# Запуск всех тестов
pytest

# Запуск с подробным выводом
pytest -v

# Запуск с покрытием кода
pytest --cov=src --cov-report=html

# Запуск конкретного теста
pytest tests/unit/test_wiki_mcp_server.py::test_create_page_success

# Запуск тестов по маркеру
pytest -m "integration"

# Запуск тестов в параллельном режиме
pytest -n auto
```

#### Конфигурация pytest
```ini
# pytest.ini
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = 
    -v
    --tb=short
    --strict-markers
    --disable-warnings
markers =
    unit: Unit tests
    integration: Integration tests
    e2e: End-to-end tests
    slow: Slow running tests
```

### Mock и фикстуры

#### Создание фикстур
```python
# tests/fixtures/wiki_js_data.py
import pytest
import json

@pytest.fixture
def sample_page_data():
    """Фикстура с данными тестовой страницы."""
    return {
        "id": 123,
        "title": "Test Page",
        "content": "# Test Content\n\nThis is a test page.",
        "description": "A test page for unit testing",
        "path": "test-page",
        "tags": ["test", "documentation"],
        "locale": "en",
        "isPublished": True,
        "isPrivate": False,
        "createdAt": "2024-01-01T00:00:00Z",
        "updatedAt": "2024-01-01T00:00:00Z"
    }

@pytest.fixture
def sample_graphql_response():
    """Фикстура с GraphQL ответом."""
    return {
        "data": {
            "pages": {
                "create": {
                    "responseResult": {
                        "succeeded": True,
                        "errorCode": None,
                        "slug": "test-page",
                        "message": "Page created successfully"
                    },
                    "page": {
                        "id": 123,
                        "title": "Test Page",
                        "path": "test-page"
                    }
                }
            }
        }
    }
```

#### Использование mock
```python
@pytest.mark.asyncio
async def test_with_mock(sample_graphql_response):
    """Тест с использованием mock."""
    with patch('src.wiki_mcp_server.client.graphql_request') as mock_request:
        mock_request.return_value = sample_graphql_response
        
        result = await wikijs_create_page(
            title="Test Page",
            content="# Test Content"
        )
        
        result_data = json.loads(result)
        assert result_data["success"] is True
        
        # Проверка вызова mock
        mock_request.assert_called_once()
        call_args = mock_request.call_args
        assert "create" in call_args[0][0]  # GraphQL query
```

---

## 🐛 Отладка

### Логирование

#### Настройка логирования
```python
import logging

# Настройка логирования для разработки
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/development.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Использование в коде
def debug_function():
    logger.debug("Debug message")
    logger.info("Info message")
    logger.warning("Warning message")
    logger.error("Error message")
```

#### Структурированное логирование
```python
import logging
import json
from datetime import datetime

class StructuredLogger:
    """Структурированный логгер для отладки."""
    
    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
    
    def log_operation(self, operation: str, data: Dict, result: Dict):
        """Логирование операции с контекстом."""
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "operation": operation,
            "input_data": data,
            "result": result,
            "success": result.get("success", False)
        }
        
        self.logger.info(json.dumps(log_entry, indent=2))

# Использование
logger = StructuredLogger("wiki_mcp_server")

async def create_page_with_logging(title: str, content: str):
    """Создание страницы с логированием."""
    input_data = {"title": title, "content": content}
    
    try:
        result = await wikijs_create_page(title, content)
        logger.log_operation("create_page", input_data, json.loads(result))
        return result
    except Exception as e:
        error_result = {"success": False, "error": str(e)}
        logger.log_operation("create_page", input_data, error_result)
        raise
```

### Отладка MCP сервера

#### Запуск в режиме отладки
```bash
# Запуск с отладочным выводом
python -u src/wiki_mcp_server.py

# Запуск с переменными окружения
DEBUG=1 LOG_LEVEL=DEBUG python src/wiki_mcp_server.py

# Запуск с профилированием
python -m cProfile -o profile.stats src/wiki_mcp_server.py
```

#### Отладка GraphQL запросов
```python
async def debug_graphql_request(query: str, variables: Dict = None):
    """Отладочная функция для GraphQL запросов."""
    logger.debug(f"GraphQL Query: {query}")
    logger.debug(f"GraphQL Variables: {json.dumps(variables, indent=2)}")
    
    try:
        result = await client.graphql_request(query, variables)
        logger.debug(f"GraphQL Response: {json.dumps(result, indent=2)}")
        return result
    except Exception as e:
        logger.error(f"GraphQL Error: {e}")
        raise
```

### Инструменты отладки

#### pdb отладчик
```python
import pdb

async def debug_function():
    """Функция с отладочными точками."""
    # Установка точки останова
    pdb.set_trace()
    
    result = await wikijs_create_page("Test", "Content")
    
    # Инспекция результата
    pdb.set_trace()
    
    return result
```

#### ipdb (улучшенный отладчик)
```python
import ipdb

async def debug_with_ipdb():
    """Отладка с ipdb."""
    ipdb.set_trace()
    
    # Интерактивная отладка
    # Доступные команды: n (next), s (step), c (continue), p (print)
    
    result = await wikijs_create_page("Test", "Content")
    return result
```

---

## 📚 Документирование

### Docstrings

#### Google Style Docstrings
```python
def process_markdown_content(content: str, options: Dict[str, Any] = None) -> str:
    """
    Обработка Markdown контента для Wiki.js.
    
    Преобразует Markdown в HTML и применяет дополнительные опции форматирования.
    
    Args:
        content: Исходный Markdown контент
        options: Дополнительные опции обработки
        
            * include_toc: Включить оглавление (default: True)
            * highlight_code: Подсветка синтаксиса кода (default: True)
            * math_support: Поддержка математических формул (default: False)
        
    Returns:
        Обработанный HTML контент
        
    Raises:
        ValueError: Если контент пустой или некорректный
        MarkdownError: При ошибках обработки Markdown
        
    Example:
        >>> content = "# Title\\n\\nThis is **bold** text."
        >>> result = process_markdown_content(content)
        >>> print(result)
        '<h1>Title</h1>\\n<p>This is <strong>bold</strong> text.</p>'
        
    Note:
        Функция автоматически экранирует HTML теги в контенте для безопасности.
    """
    if not content:
        raise ValueError("Content cannot be empty")
    
    # Реализация обработки
    pass
```

#### Type hints с документацией
```python
from typing import TypedDict, Optional, List

class PageOptions(TypedDict, total=False):
    """Опции для создания страницы."""
    
    description: Optional[str]
    """Описание страницы (опционально)"""
    
    tags: List[str]
    """Список тегов для страницы"""
    
    is_private: bool
    """Приватная ли страница (по умолчанию False)"""
    
    locale: str
    """Локаль страницы (по умолчанию 'en')"""

async def create_page_with_options(
    title: str,
    content: str,
    options: PageOptions = None
) -> Dict[str, Any]:
    """
    Создание страницы с расширенными опциями.
    
    Args:
        title: Заголовок страницы
        content: Содержимое страницы
        options: Дополнительные опции создания
        
    Returns:
        Словарь с результатом создания страницы
    """
    pass
```

### README файлы

#### Структура README
```markdown
# Название модуля

Краткое описание функциональности модуля.

## Установка

```bash
pip install module-name
```

## Быстрый старт

```python
from module import function

result = function("example")
print(result)
```

## API Reference

### function(param: str) -> str

Описание функции.

**Параметры:**
- `param`: Описание параметра

**Возвращает:**
Описание возвращаемого значения

**Примеры:**
```python
result = function("test")
assert result == "processed_test"
```

## Примеры использования

### Базовый пример
```python
# Код примера
```

### Продвинутый пример
```python
# Сложный код примера
```

## Тестирование

```bash
pytest tests/
```

## Лицензия

MIT License
```

### Автоматическая генерация документации

#### Sphinx документация
```python
# docs/conf.py
project = 'Wiki.js MCP Server'
copyright = '2024, Sahil Pethe'
author = 'Sahil Pethe'

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx.ext.viewcode',
    'sphinx.ext.intersphinx',
]

# Настройки autodoc
autodoc_default_options = {
    'members': True,
    'member-order': 'bysource',
    'special-members': '__init__',
    'undoc-members': True,
    'exclude-members': '__weakref__'
}
```

#### Генерация документации
```bash
# Установка Sphinx
pip install sphinx sphinx-rtd-theme

# Создание документации
sphinx-quickstart docs

# Генерация HTML
cd docs && make html

# Генерация PDF
make latexpdf
```

---

## 🔄 Рабочий процесс

### Git workflow

#### Создание feature branch
```bash
# Создание новой ветки
git checkout -b feature/new-function

# Разработка
# ... внесение изменений ...

# Коммиты
git add .
git commit -m "feat: add new export function

- Add wikijs_export_pages function
- Support multiple export formats
- Add comprehensive tests
- Update documentation"

# Push в репозиторий
git push origin feature/new-function
```

#### Conventional Commits
```bash
# Типы коммитов
feat: новая функция
fix: исправление ошибки
docs: изменения в документации
style: форматирование кода
refactor: рефакторинг
test: добавление тестов
chore: обновление зависимостей

# Примеры
git commit -m "feat: add page export functionality"
git commit -m "fix: resolve GraphQL authentication issue"
git commit -m "docs: update API documentation"
git commit -m "test: add integration tests for export"
```

### Code Review

#### Checklist для review
- [ ] Код соответствует стандартам PEP 8
- [ ] Все функции имеют type hints
- [ ] Добавлены docstrings для новых функций
- [ ] Покрытие тестами > 80%
- [ ] Обновлена документация
- [ ] Нет критических ошибок безопасности
- [ ] Производительность не ухудшена

#### Pull Request template
```markdown
## Описание изменений

Краткое описание того, что было добавлено/изменено.

## Тип изменений

- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Тестирование

- [ ] Unit тесты пройдены
- [ ] Integration тесты пройдены
- [ ] E2E тесты пройдены
- [ ] Ручное тестирование выполнено

## Документация

- [ ] Обновлена API документация
- [ ] Обновлены примеры использования
- [ ] Обновлен README если необходимо

## Checklist

- [ ] Код отформатирован (black, isort)
- [ ] Проверка типов пройдена (mypy)
- [ ] Линтер не выдает ошибок (flake8)
- [ ] Все тесты проходят
- [ ] Документация актуальна
```

### CI/CD Pipeline

#### GitHub Actions
```yaml
# .github/workflows/ci.yml
name: CI

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.12'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install pytest pytest-cov black isort mypy flake8
    
    - name: Lint with flake8
      run: flake8 src/ tests/
    
    - name: Check formatting with black
      run: black --check src/ tests/
    
    - name: Check imports with isort
      run: isort --check-only src/ tests/
    
    - name: Type check with mypy
      run: mypy src/
    
    - name: Test with pytest
      run: |
        pytest --cov=src --cov-report=xml
    
    - name: Upload coverage
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
```

---

## 📦 Публикация

### Подготовка к релизу

#### Обновление версии
```python
# src/__init__.py
__version__ = "1.1.0"
```

```toml
# pyproject.toml
[tool.poetry]
version = "1.1.0"
```

#### Создание changelog
```markdown
# CHANGELOG.md
# Changelog

All notable changes to this project will be documented in this file.

## [1.1.0] - 2024-01-15

### Added
- New `wikijs_export_pages` function for exporting pages in multiple formats
- Support for PDF and HTML export formats
- Batch export functionality
- Export metadata options

### Changed
- Improved error handling in GraphQL requests
- Enhanced logging for better debugging
- Updated documentation with new examples

### Fixed
- Resolved authentication token refresh issue
- Fixed memory leak in bulk operations
- Corrected type hints for better IDE support

## [1.0.0] - 2024-01-01

### Added
- Initial release with 21 MCP tools
- Wiki.js GraphQL API integration
- Hierarchical documentation support
- Docker deployment support
```

### Создание релиза

#### GitHub Release
```bash
# Создание тега
git tag -a v1.1.0 -m "Release version 1.1.0"
git push origin v1.1.0

# Создание release на GitHub
# - Загрузить собранные файлы
# - Добавить changelog
# - Указать совместимость
```

#### PyPI публикация
```bash
# Сборка пакета
python setup.py sdist bdist_wheel

# Проверка пакета
twine check dist/*

# Загрузка в PyPI
twine upload dist/*
```

### Документирование релиза

#### Release Notes
```markdown
# Release Notes - v1.1.0

## 🎉 Новые возможности

### Экспорт страниц
Добавлена возможность экспорта страниц в различных форматах:
- **Markdown**: Чистый Markdown без HTML
- **PDF**: Готовые к печати документы
- **HTML**: Веб-страницы с полным форматированием

### Массовый экспорт
Поддержка экспорта множественных страниц одной командой:
```python
await wikijs_export_pages(
    page_ids=[1, 2, 3, 4, 5],
    format="pdf",
    output_dir="./exports"
)
```

## 🔧 Улучшения

### Производительность
- Оптимизированы GraphQL запросы
- Улучшено кэширование метаданных
- Сокращено время отклика на 30%

### Надежность
- Улучшена обработка сетевых ошибок
- Добавлены автоматические повторы для неудачных запросов
- Улучшено логирование для отладки

## 🐛 Исправления

- Исправлена проблема с обновлением токенов аутентификации
- Устранена утечка памяти при массовых операциях
- Исправлены type hints для лучшей поддержки IDE

## 📚 Документация

- Добавлены примеры использования новых функций
- Обновлена API документация
- Добавлены руководства по миграции

## 🔄 Миграция

Для обновления с версии 1.0.0:
1. Обновите зависимости: `pip install --upgrade wiki-js-mcp`
2. Проверьте совместимость API
3. Обновите конфигурацию если необходимо

## 📦 Загрузка

- **PyPI**: `pip install wiki-js-mcp==1.1.0`
- **GitHub**: [Releases](https://github.com/your-repo/wiki-js-mcp/releases/tag/v1.1.0)
- **Docker**: `docker pull wikijs-mcp:1.1.0`
```

---

## 🎯 Заключение

Данное руководство по разработке обеспечивает:

- ✅ **Стандартизированный процесс** разработки
- ✅ **Качественный код** с тестированием
- ✅ **Подробную документацию** для всех функций
- ✅ **Эффективную отладку** и мониторинг
- ✅ **Автоматизированный CI/CD** процесс
- ✅ **Профессиональную публикацию** релизов

Следуйте этим рекомендациям для обеспечения высокого качества кода и эффективной разработки проекта Wiki.js MCP Server. 🚀 