# 🚀 Быстрая установка Wiki.js MCP Server

## Windows (Рекомендуется)

### 1. Установите Docker Desktop
- Скачайте с [docker.com](https://www.docker.com/products/docker-desktop/)
- Установите и запустите Docker Desktop

### 2. Клонируйте репозиторий
```cmd
git clone https://github.com/your-repo/wiki-js-mcp.git
cd wiki-js-mcp
```

### 3. Запустите быстрый старт
```cmd
quick-start.bat
```

### 4. Настройте Wiki.js
1. Откройте http://localhost:3000
2. Создайте администратора
3. Перейдите в **Admin → API Access → Create Token**
4. Скопируйте токен

### 5. Настройте MCP
1. Откройте файл `.env`
2. Замените `WIKIJS_TOKEN=your_jwt_token_here` на ваш токен
3. Запустите: `start-mcp.bat`

### 6. Подключите к Cursor
1. Скопируйте содержимое `cursor-mcp.json` в `%USERPROFILE%\.cursor\mcp.json`
2. Перезапустите Cursor

## Linux/macOS

### 1. Установите Docker
```bash
# Ubuntu/Debian
sudo apt-get install docker.io docker-compose

# macOS
brew install docker docker-compose
```

### 2. Клонируйте и настройте
```bash
git clone https://github.com/your-repo/wiki-js-mcp.git
cd wiki-js-mcp
cp config/env.example .env
```

### 3. Запустите сервисы
```bash
docker-compose up -d db wiki
```

### 4. Настройте Wiki.js и MCP
1. Откройте http://localhost:3000
2. Создайте API токен
3. Обновите `.env` с токеном
4. Запустите MCP: `docker-compose --profile mcp up -d mcp-server`

### 5. Подключите к Cursor
Добавьте в `~/.cursor/mcp.json`:
```json
{
  "mcpServers": {
    "wikijs": {
      "command": "docker",
      "args": ["exec", "-i", "wikijs_mcp", "python", "src/wiki_mcp_server.py"]
    }
  }
}
```

## ✅ Проверка установки

1. **Wiki.js**: http://localhost:3000
2. **MCP сервер**: `docker-compose logs mcp-server`
3. **Cursor**: Проверьте подключение в настройках MCP

## 🆘 Проблемы?

- **Docker не запускается**: Убедитесь, что Docker Desktop запущен
- **Порт занят**: Измените порт в `docker-compose.yml`
- **MCP не подключается**: Проверьте токен в `.env`
- **Подробная документация**: [README-WINDOWS.md](README-WINDOWS.md)

---

**Готово!** 🎉 Теперь у вас есть полнофункциональный Wiki.js MCP Server!