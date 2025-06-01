# Hierarchical Documentation Features

## Overview

The Wiki.js MCP server now supports **hierarchical documentation structures** perfect for enterprise-scale repository documentation. This allows you to create organized, nested documentation that scales from individual files to entire company codebases.

## New MCP Tools

### 1. `wikijs_create_repo_structure`
Creates a complete repository documentation structure with nested pages.

**Usage:**
```python
await wikijs_create_repo_structure(
    repo_name="Frontend App",
    description="A modern React frontend application", 
    sections=["Overview", "Components", "API", "Deployment", "Testing"]
)
```

**Creates:**
```
Frontend App/
├── Overview/
├── Components/
├── API/
├── Deployment/
└── Testing/
```

### 2. `wikijs_create_nested_page`
Creates pages with hierarchical paths, automatically creating parent pages if needed.

**Usage:**
```python
await wikijs_create_nested_page(
    title="Button Component",
    content="# Button Component\n\nA reusable button...",
    parent_path="frontend-app/components",
    create_parent_if_missing=True
)
```

**Creates:** `frontend-app/components/button-component`

### 3. `wikijs_get_page_children`
Retrieves all direct child pages of a parent page for navigation.

**Usage:**
```python
await wikijs_get_page_children(page_path="frontend-app/components")
```

**Returns:**
```json
{
  "parent": {"pageId": 18, "title": "Components", "path": "frontend-app/components"},
  "children": [
    {"pageId": 22, "title": "Button Component", "path": "frontend-app/components/button-component"},
    {"pageId": 23, "title": "Modal Component", "path": "frontend-app/components/modal-component"}
  ],
  "total_children": 2
}
```

### 4. `wikijs_create_documentation_hierarchy`
Creates a complete documentation hierarchy for a project based on file structure with auto-organization.

**Usage:**
```python
await wikijs_create_documentation_hierarchy(
    project_name="My App",
    file_mappings=[
        {"file_path": "src/components/Button.tsx", "doc_path": "components/button"},
        {"file_path": "src/api/users.ts", "doc_path": "api/users"},
        {"file_path": "src/utils/helpers.ts", "doc_path": "utils/helpers"}
    ],
    auto_organize=True
)
```

**Auto-organizes into sections:**
- **Components**: Files with "component" or "/components/" in path
- **API**: Files with "api", "/api/", or "endpoint" in path  
- **Utils**: Files with "util", "/utils/", or "/helpers/" in path
- **Services**: Files with "service" or "/services/" in path
- **Models**: Files with "model", "/models/", or "/types/" in path
- **Tests**: Files with "test", "/tests/", or ".test." in path
- **Config**: Files with "config", "/config/", or ".config." in path

## Enhanced Existing Tools

### `wikijs_create_page` (Enhanced)
Now supports `parent_id` parameter for creating hierarchical pages:

```python
await wikijs_create_page(
    title="API Endpoints", 
    content="# API Documentation...",
    parent_id="16"  # Creates as child of page 16
)
```

### `wikijs_search_pages` (Fixed)
Fixed GraphQL query issues - now works properly:

```python
await wikijs_search_pages("Button")
# Returns: {"results": [...], "total": 1}
```

## Enterprise Use Cases

### 1. Company-wide Repository Documentation
```
Company Docs/
├── frontend-web-app/
│   ├── Overview/
│   ├── Components/
│   │   ├── Button/
│   │   ├── Modal/
│   │   └── Form/
│   ├── API/
│   └── Deployment/
├── backend-api/
│   ├── Overview/
│   ├── Controllers/
│   ├── Models/
│   └── Database/
├── mobile-app/
│   ├── Overview/
│   ├── Screens/
│   └── Components/
└── shared-libraries/
    ├── UI Components/
    ├── Utilities/
    └── Types/
```

### 2. Automatic File-to-Documentation Mapping
The system automatically:
- Creates hierarchical page structures
- Links source files to documentation pages
- Organizes files by type (components, API, utils, etc.)
- Maintains parent-child relationships
- Enables easy navigation between related docs

### 3. Scalable Documentation Architecture
- **Root Level**: Repository names only
- **Section Level**: Logical groupings (Components, API, etc.)
- **Page Level**: Individual files/features
- **Sub-page Level**: Detailed documentation sections

## Benefits

✅ **Scalable**: Handles hundreds of repositories and thousands of files  
✅ **Organized**: Auto-categorizes files into logical sections  
✅ **Navigable**: Parent-child relationships enable easy browsing  
✅ **Searchable**: Full-text search across all hierarchical content  
✅ **Maintainable**: File-to-page mappings keep docs in sync with code  
✅ **Enterprise-ready**: Perfect for large organizations with many repos  

## Example: Complete Repository Setup

```python
# 1. Create repository structure
repo_result = await wikijs_create_repo_structure(
    "E-commerce Platform",
    "Full-stack e-commerce application",
    ["Overview", "Frontend", "Backend", "API", "Database", "Deployment"]
)

# 2. Create component documentation
button_result = await wikijs_create_nested_page(
    "Button Component",
    "# Button Component\n\nReusable button with variants...",
    "e-commerce-platform/frontend"
)

# 3. Get navigation structure
children = await wikijs_get_page_children(page_path="e-commerce-platform/frontend")

# 4. Search across all docs
search_results = await wikijs_search_pages("authentication")
```

This creates a professional, enterprise-grade documentation structure that scales with your organization's growth! 