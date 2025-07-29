# Wiki.js MCP Server

A comprehensive **Model Context Protocol (MCP) server** for Wiki.js integration with **hierarchical documentation** support and Docker deployment. Perfect for organizations managing multiple repositories and large-scale documentation.

## 🚀 Quick Start

### Windows/Docker Users (Recommended)
For Windows users, we provide a simplified setup with Docker:

1. **Install Docker Desktop** from [docker.com](https://www.docker.com/products/docker-desktop/)
2. **Clone the repository** and run:
   ```cmd
   # Start Wiki.js and database
   docker-compose up -d
   
   # Build MCP server image
   scripts\build-mcp.bat
   ```
3. **Follow the setup wizard** and see [docs/QUICK_INSTALL.md](docs/QUICK_INSTALL.md) for detailed instructions

### Linux/macOS Users

#### 1. Environment Setup

First, clone this repository and set up environment variables:
```bash
# Copy environment template
cp config/env.example .env

# Edit .env with your credentials:
# - Set POSTGRES_PASSWORD to a secure password
# - Update other settings as needed
```

#### 2. Docker Deployment (Recommended)

```bash
# Start Wiki.js and database
docker-compose up -d db wiki
```
Wiki.js will be available at http://localhost:3000

Complete the initial setup in the web interface

#### 3. Build MCP Server
```bash
# Build MCP server Docker image
docker-compose --profile build build mcp-builder

# Or use the build script (Windows)
scripts\build-mcp.bat
```

#### 4. Setup MCP Server (Alternative - Direct Python)
```bash
# Install Python dependencies
./scripts/setup.sh

# Update .env with Wiki.js API credentials:
# - Get API key from Wiki.js admin panel  
# - Set WIKIJS_TOKEN in .env file

# Test the connection
./scripts/test-server.sh

# Start MCP server
# (not needed for AI IDEs like Cursor, simply click on the refresh icon after editing mcp.json
# and you should see a green dot with all tools listed. In existing open Cursor windows,
# this refresh is necessary in order to use this MCP)
./scripts/start-server.sh
```

#### 5. Configure Cursor MCP
Add to your `~/.cursor/mcp.json`:
```json
{
  "mcpServers": {
    "wikijs": {
      "command": "/path/to/wiki-js-mcp/scripts/start-server.sh"
    }
  }
}
```

**Alternative: Use Deeplink (Recommended)**
After running `scripts\build-mcp.bat`, a `cursor-mcp-deeplink.txt` file will be generated. Copy the deeplink from this file and paste it into your browser to automatically configure Cursor MCP.
```

## 🎯 Enhanced Cursor Integration

### Global Rules for Documentation-First Development
Add these **Global Rules** in Cursor to automatically leverage documentation before coding:

```
Before writing any code, always:
1. Search existing documentation using wikijs_search_pages to understand current patterns and architecture
2. Check for related components, functions, or modules that might already exist
3. If documentation exists for similar functionality, follow the established patterns and naming conventions
4. If no documentation exists, create it using wikijs_create_page or wikijs_create_nested_page before implementing
5. Always update documentation when making changes using wikijs_sync_file_docs
6. For new features, use wikijs_create_repo_structure to plan the documentation hierarchy first
```

These rules ensure that your AI assistant will:
- ✅ Check documentation before suggesting implementations
- ✅ Follow existing patterns and conventions
- ✅ Maintain up-to-date documentation automatically
- ✅ Create structured documentation for new features
- ✅ Avoid duplicating existing functionality

### Usage Tips for Cursor
```
# Before starting a new feature
"Search the documentation for authentication patterns before implementing login"

# When creating components
"Create nested documentation under frontend-app/components before building the React component"

# For API development
"Check existing API documentation and create endpoint docs using the established structure"

# During refactoring
"Update all related documentation pages for the files I'm about to modify"
```

## 🚀 Key Features

### 📁 **Hierarchical Documentation**
- **Repository-level organization**: Create structured docs for multiple repos
- **Nested page creation**: Automatic parent-child relationships
- **Auto-organization**: Smart categorization by file type (components, API, utils, etc.)
- **Enterprise scalability**: Handle hundreds of repos and thousands of files

### 🔧 **Core Functionality**
- **GraphQL API integration**: Full Wiki.js v2+ compatibility
- **File-to-page mapping**: Automatic linking between source code and documentation
- **Code structure analysis**: Extract classes, functions, and dependencies
- **Bulk operations**: Update multiple pages simultaneously
- **Change tracking**: Monitor file modifications and sync docs

### 🐳 **Docker Setup**
- **One-command deployment**: Complete Wiki.js setup with PostgreSQL
- **Persistent storage**: Data survives container restarts
- **Health checks**: Automatic service monitoring
- **Production-ready**: Optimized for development and deployment
- **Windows support**: Full Docker Desktop integration

### 🔍 **Smart Features**
- **Repository context detection**: Auto-detect Git repositories
- **Content generation**: Auto-create documentation from code structure
- **Search integration**: Full-text search across hierarchical content
- **Health monitoring**: Connection status and error handling

## 📊 MCP Tools (21 Total)

### 🏗️ **Hierarchical Documentation Tools**
1. **`wikijs_create_repo_structure`** - Create complete repository documentation structure
2. **`wikijs_create_nested_page`** - Create pages with hierarchical paths
3. **`wikijs_get_page_children`** - Navigate parent-child page relationships
4. **`wikijs_create_documentation_hierarchy`** - Auto-organize project files into docs

### 📝 **Core Page Management**
5. **`wikijs_create_page`** - Create new pages (now with parent support)
6. **`wikijs_update_page`** - Update existing pages
7. **`wikijs_get_page`** - Retrieve page content and metadata
8. **`wikijs_search_pages`** - Search pages by text (fixed GraphQL issues)

### 🗑️ **Deletion & Cleanup Tools**
9. **`wikijs_delete_page`** - Delete specific pages by ID or path
10. **`wikijs_batch_delete_pages`** - Batch delete with pattern matching and safety checks
11. **`wikijs_delete_hierarchy`** - Delete entire page hierarchies with multiple modes
12. **`wikijs_cleanup_orphaned_mappings`** - Clean up orphaned file-to-page mappings

### 🗂️ **Organization & Structure**
13. **`wikijs_list_spaces`** - List top-level documentation spaces
14. **`wikijs_create_space`** - Create new documentation spaces
15. **`wikijs_manage_collections`** - Manage page collections

### 🔗 **File Integration**
16. **`wikijs_link_file_to_page`** - Link source files to documentation pages
17. **`wikijs_sync_file_docs`** - Sync code changes to documentation
18. **`wikijs_generate_file_overview`** - Auto-generate file documentation

### 🚀 **Bulk Operations**
19. **`wikijs_bulk_update_project_docs`** - Batch update multiple pages

### 🔧 **System Tools**
20. **`wikijs_connection_status`** - Check API connection health
21. **`wikijs_repository_context`** - Show repository mappings and context

## 🏢 Enterprise Use Cases

### Multi-Repository Documentation
```
Company Documentation/
├── frontend-web-app/
│   ├── Overview/
│   ├── Components/
│   │   ├── Button/
│   │   ├── Modal/
│   │   └── Form/
│   ├── API Integration/
│   └── Deployment/
├── backend-api/
│   ├── Overview/
│   ├── Controllers/
│   ├── Models/
│   └── Database Schema/
├── mobile-app/
│   ├── Overview/
│   ├── Screens/
│   └── Native Components/
└── shared-libraries/
    ├── UI Components/
    ├── Utilities/
    └── Type Definitions/
```

### Automatic Organization
The system intelligently categorizes files:
- **Components**: React/Vue components, UI elements
- **API**: Endpoints, controllers, routes
- **Utils**: Helper functions, utilities
- **Services**: Business logic, external integrations
- **Models**: Data models, types, schemas
- **Tests**: Unit tests, integration tests
- **Config**: Configuration files, environment setup

## 📚 Usage Examples

### Create Repository Documentation
```python
# Create complete repository structure
await wikijs_create_repo_structure(
    "My Frontend App",
    "Modern React application with TypeScript",
    ["Overview", "Components", "API", "Testing", "Deployment"]
)

# Create nested component documentation
await wikijs_create_nested_page(
    "Button Component",
    "# Button Component\n\nReusable button with multiple variants...",
    "my-frontend-app/components"
)

# Auto-organize entire project
await wikijs_create_documentation_hierarchy(
    "My Project",
    [
        {"file_path": "src/components/Button.tsx"},
        {"file_path": "src/api/users.ts"},
        {"file_path": "src/utils/helpers.ts"}
    ],
    auto_organize=True
)
```

### Documentation Management
```python
# Clean up and manage documentation
# Preview what would be deleted (safe)
preview = await wikijs_delete_hierarchy(
    "old-project",
    delete_mode="include_root",
    confirm_deletion=False
)

# Delete entire deprecated project
await wikijs_delete_hierarchy(
    "old-project",
    delete_mode="include_root", 
    confirm_deletion=True
)

# Batch delete test pages
await wikijs_batch_delete_pages(
    path_pattern="*test*",
    confirm_deletion=True
)

# Clean up orphaned file mappings
await wikijs_cleanup_orphaned_mappings()
```

## ⚙️ Configuration

### Environment Variables
```bash
# Docker Database Configuration
POSTGRES_DB=wikijs
POSTGRES_USER=wikijs
POSTGRES_PASSWORD=your_secure_password_here

# Wiki.js Connection
WIKIJS_API_URL=http://localhost:3000
WIKIJS_API_KEY=your_jwt_token_here

# Alternative: Username/Password
WIKIJS_USERNAME=your_username
WIKIJS_PASSWORD=your_password

# Database & Logging
WIKIJS_MCP_DB=./data/mcp/wikijs_mappings.db
LOG_LEVEL=INFO
LOG_FILE=./logs/wikijs_mcp.log

# Repository Settings
REPOSITORY_ROOT=./
DEFAULT_SPACE_NAME=Documentation
```

### Authentication Options
1. **JWT Token** (Recommended): Use API key from Wiki.js admin panel
2. **Username/Password**: Traditional login credentials

## 🔧 Technical Architecture

### GraphQL Integration
- **Full GraphQL API support**: Native Wiki.js v2+ compatibility
- **Optimized queries**: Efficient data fetching and mutations
- **Error handling**: Comprehensive GraphQL error management
- **Retry logic**: Automatic retry with exponential backoff

### Database Layer
- **SQLite storage**: Local file-to-page mappings
- **Repository context**: Git repository detection and tracking
- **Change tracking**: File hash monitoring for sync detection
- **Relationship management**: Parent-child page hierarchies

### Code Analysis
- **AST parsing**: Extract Python classes, functions, imports
- **Structure detection**: Identify code patterns and organization
- **Documentation generation**: Auto-create comprehensive overviews
- **Dependency mapping**: Track imports and relationships

## 📈 Performance & Scalability

- **Async operations**: Non-blocking I/O for all API calls
- **Bulk processing**: Efficient batch operations for large projects
- **Caching**: Smart caching of page relationships and metadata
- **Connection pooling**: Optimized HTTP client management

## 🛠️ Development

### Project Structure
```
wiki-js-mcp/
├── src/
│   └── wiki_mcp_server.py      # Main MCP server implementation
├── config/
│   ├── cursor-mcp.json # MCP configuration for Windows/VS Code
│   └── env.example             # Configuration template
├── docs/                       # Project documentation
│   ├── README.md               # Documentation index
│   ├── PROJECT_DOCUMENTATION.md # Complete project documentation
│   ├── PROJECT_OVERVIEW.md     # Project overview
│   ├── DOCUMENTATION_INDEX.md  # Documentation index
│   ├── DEVELOPMENT_GUIDE.md    # Development guide
│   ├── TECHNICAL_SPECIFICATION.md # Technical specification
│   └── QUICK_INSTALL.md        # Quick installation guide
├── scripts/                    # Scripts and utilities
│   ├── build-mcp.bat           # Build MCP Docker image (Windows)
│   ├── quick-start.bat         # Complete setup (Windows)
│   ├── *.sh                    # Linux/macOS scripts
│   └── generate-deeplink.py    # DeepLink generator
├── docker-compose.yml          # Docker Compose setup
├── Dockerfile.mcp              # MCP server Dockerfile
├── pyproject.toml              # Poetry dependencies
├── requirements.txt            # Pip dependencies
├── LICENSE                     # MIT License
└── README.md                   # This file
```

### Dependencies
- **FastMCP**: Official Python MCP SDK
- **httpx**: Async HTTP client for GraphQL
- **SQLAlchemy**: Database ORM for mappings
- **Pydantic**: Configuration and validation
- **tenacity**: Retry logic for reliability

## 🔍 Troubleshooting

### Docker Issues
```bash
# Check containers
docker-compose ps

# View logs
docker-compose logs wiki
docker-compose logs postgres

# Reset everything
docker-compose down -v
docker-compose up -d

# Rebuild MCP image if needed
scripts\build-mcp.bat
```

### Connection Issues
```bash
# Check Wiki.js is running
curl http://localhost:3000/graphql

# Verify authentication
./scripts/test-server.sh

# Debug mode
export LOG_LEVEL=DEBUG
./scripts/start-server.sh
```

### Common Problems
- **Port conflicts**: Change port 3000 in `docker-compose.yml` if needed
- **Database issues**: Remove `postgres_data/` and restart
- **API permissions**: Ensure API key has admin privileges
- **Python dependencies**: Run `./scripts/setup.sh` to reinstall
- **MCP connection issues**: Use deeplink from `cursor-mcp-deeplink.txt` after running `scripts\build-mcp.bat`

## 📚 Documentation

- **[Quick Installation Guide](docs/QUICK_INSTALL.md)** - Complete setup guide for all platforms
- **[Project Documentation](docs/)** - Complete project documentation and guides
- **[Configuration Examples](config/env.example)** - Environment setup

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **Wiki.js Team**: For the excellent documentation platform
- **MCP Protocol**: For the standardized AI integration framework
- **FastMCP**: For the Python MCP SDK

---

**Ready to scale your documentation?** 🚀 Start with `wikijs_create_repo_structure` and build enterprise-grade documentation hierarchies! Use the Cursor global rules to ensure documentation-first development! 📚✨ 