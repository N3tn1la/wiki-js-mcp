#!/usr/bin/env python3
"""Wiki.js MCP server using FastMCP - GraphQL version."""

import os
from dotenv import load_dotenv
load_dotenv()

import sys
import datetime
import json
import hashlib
import logging
import ast
import re
from pathlib import Path
from typing import Optional, List, Dict, Any, Union
from dataclasses import dataclass

import httpx
from fastmcp import FastMCP
from slugify import slugify
import markdown
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from tenacity import retry, stop_after_attempt, wait_exponential
from pydantic import Field
from pydantic_settings import BaseSettings

# Create FastMCP server
mcp = FastMCP("Wiki.js Integration")

# Configuration
class Settings(BaseSettings):
    WIKIJS_API_URL: str = Field(default="http://localhost:3000")
    WIKIJS_TOKEN: Optional[str] = Field(default=None)
    WIKIJS_API_KEY: Optional[str] = Field(default=None)  # Alternative name for token
    WIKIJS_USERNAME: Optional[str] = Field(default=None)
    WIKIJS_PASSWORD: Optional[str] = Field(default=None)
    WIKIJS_MCP_DB: str = Field(default="./wikijs_mappings.db")
    LOG_LEVEL: str = Field(default="INFO")
    LOG_FILE: str = Field(default="wikijs_mcp.log")
    REPOSITORY_ROOT: str = Field(default="./")
    DEFAULT_SPACE_NAME: str = Field(default="Documentation")
    DEFAULT_LOCALE: str = Field(default="en")  # Default locale for pages
    
    class Config:
        env_file = ".env"
        extra = "ignore"  # Allow extra fields without validation errors
    
    @property
    def token(self) -> Optional[str]:
        """Get the token from either WIKIJS_TOKEN or WIKIJS_API_KEY."""
        return self.WIKIJS_TOKEN or self.WIKIJS_API_KEY

settings = Settings()

# Setup logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL.upper()),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(settings.LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Database models
Base = declarative_base()

class FileMapping(Base):
    __tablename__ = 'file_mappings'
    
    id = Column(Integer, primary_key=True)
    file_path = Column(String, unique=True, nullable=False)
    page_id = Column(Integer, nullable=False)
    relationship_type = Column(String, nullable=False)
    last_updated = Column(DateTime, default=datetime.datetime.utcnow)
    file_hash = Column(String)
    repository_root = Column(String, default='')
    space_name = Column(String, default='')

class RepositoryContext(Base):
    __tablename__ = 'repository_contexts'
    
    id = Column(Integer, primary_key=True)
    root_path = Column(String, unique=True, nullable=False)
    space_name = Column(String, nullable=False)
    space_id = Column(Integer)
    last_updated = Column(DateTime, default=datetime.datetime.utcnow)

# Database setup
engine = create_engine(f"sqlite:///{settings.WIKIJS_MCP_DB}")
Base.metadata.create_all(engine)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class WikiJSClient:
    """Wiki.js GraphQL API client for handling requests."""
    
    def __init__(self):
        self.base_url = settings.WIKIJS_API_URL.rstrip('/')
        self.client = httpx.AsyncClient(timeout=30.0)
        self.authenticated = False
        
    async def authenticate(self) -> bool:
        """Set up authentication headers for GraphQL requests."""
        if settings.token:
            self.client.headers.update({
                "Authorization": f"Bearer {settings.token}",
                "Content-Type": "application/json"
            })
            self.authenticated = True
            return True
        elif settings.WIKIJS_USERNAME and settings.WIKIJS_PASSWORD:
            # For username/password, we need to login via GraphQL mutation
            try:
                login_mutation = """
                mutation($username: String!, $password: String!) {
                    authentication {
                        login(username: $username, password: $password) {
                            succeeded
                            jwt
                            message
                        }
                    }
                }
                """
                
                response = await self.graphql_request(login_mutation, {
                    "username": settings.WIKIJS_USERNAME,
                    "password": settings.WIKIJS_PASSWORD
                })
                
                if response.get("data", {}).get("authentication", {}).get("login", {}).get("succeeded"):
                    jwt_token = response["data"]["authentication"]["login"]["jwt"]
                    self.client.headers.update({
                        "Authorization": f"Bearer {jwt_token}",
                        "Content-Type": "application/json"
                    })
                    self.authenticated = True
                    return True
                else:
                    logger.error(f"Login failed: {response}")
                    return False
            except Exception as e:
                logger.error(f"Authentication failed: {e}")
                return False
        return False
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def graphql_request(self, query: str, variables: Dict = None) -> Dict:
        """Make GraphQL request to Wiki.js with retry for queries."""
        return await self._graphql_request_internal(query, variables)
    
    async def graphql_request_without_retry(self, query: str, variables: Dict = None) -> Dict:
        """Make GraphQL request to Wiki.js without retry for mutations."""
        return await self._graphql_request_internal(query, variables)
    
    async def _graphql_request_internal(self, query: str, variables: Dict = None) -> Dict:
        """Internal GraphQL request implementation."""
        url = f"{self.base_url}/graphql"
        
        payload = {"query": query}
        if variables:
            payload["variables"] = variables
        
        try:
            response = await self.client.post(url, json=payload)
            response.raise_for_status()
            
            data = response.json()
            
            # Check for GraphQL errors
            if "errors" in data:
                error_msg = "; ".join([err.get("message", str(err)) for err in data["errors"]])
                raise Exception(f"GraphQL error: {error_msg}")
            
            return data
        except httpx.HTTPStatusError as e:
            logger.error(f"Wiki.js GraphQL HTTP error {e.response.status_code}: {e.response.text}")
            raise Exception(f"Wiki.js GraphQL HTTP error {e.response.status_code}: {e.response.text}")
        except httpx.RequestError as e:
            logger.error(f"Wiki.js connection error: {str(e)}")
            raise Exception(f"Wiki.js connection error: {str(e)}")

# Initialize client
wikijs = WikiJSClient()

def get_db():
    """Get database session."""
    db = SessionLocal()
    try:
        return db
    finally:
        db.close()

def get_file_hash(file_path: str) -> str:
    """Calculate SHA256 hash of file content."""
    try:
        with open(file_path, 'rb') as f:
            return hashlib.sha256(f.read()).hexdigest()
    except FileNotFoundError:
        return ""

def markdown_to_html(content: str) -> str:
    """Convert markdown content to HTML."""
    md = markdown.Markdown(extensions=['codehilite', 'fenced_code', 'tables'])
    return md.convert(content)

def find_repository_root(start_path: str = None) -> Optional[str]:
    """Find the repository root by looking for .git directory or .wikijs_mcp file."""
    if start_path is None:
        start_path = os.getcwd()
    
    current_path = Path(start_path).resolve()
    
    # Walk up the directory tree
    for path in [current_path] + list(current_path.parents):
        # Check for .git directory (Git repository)
        if (path / '.git').exists():
            return str(path)
        # Check for .wikijs_mcp file (explicit Wiki.js repository marker)
        if (path / '.wikijs_mcp').exists():
            return str(path)
    
    # If no repository markers found, use current directory
    return str(current_path)

def extract_code_structure(file_path: str) -> Dict[str, Any]:
    """Extract classes and functions from Python files using AST."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        tree = ast.parse(content)
        structure = {
            'classes': [],
            'functions': [],
            'imports': []
        }
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                structure['classes'].append({
                    'name': node.name,
                    'line': node.lineno,
                    'docstring': ast.get_docstring(node)
                })
            elif isinstance(node, ast.FunctionDef):
                structure['functions'].append({
                    'name': node.name,
                    'line': node.lineno,
                    'docstring': ast.get_docstring(node)
                })
            elif isinstance(node, (ast.Import, ast.ImportFrom)):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        structure['imports'].append(alias.name)
                else:
                    module = node.module or ''
                    for alias in node.names:
                        structure['imports'].append(f"{module}.{alias.name}")
        
        return structure
    except Exception as e:
        logger.error(f"Error parsing {file_path}: {e}")
        return {'classes': [], 'functions': [], 'imports': []}

# MCP Tools Implementation

@mcp.tool()
async def wikijs_create_page(title: str, content: str, description: str = None, path: str = None) -> str:
    """
    Create a new page in Wiki.js.
    
    Args:
        title: Page title
        content: Page content
        description: Page description (optional)
        path: Page path (optional, will be auto-generated if not provided)
    
    Returns:
        JSON string with page details
    """
    try:
        await wikijs.authenticate()
        
        # Generate path if not provided
        if not path:
            path = title.lower().replace(" ", "-").replace("_", "-")
        
        # Use proper create mutation with all required parameters
        create_mutation = """
        mutation($title: String!, $content: String!, $description: String!, $path: String!, $locale: String!, $editor: String!, $isPublished: Boolean!, $isPrivate: Boolean!, $tags: [String]!) {
            pages {
                create(
                    title: $title,
                    content: $content,
                    description: $description,
                    path: $path,
                    locale: $locale,
                    editor: $editor,
                    isPublished: $isPublished,
                    isPrivate: $isPrivate,
                    tags: $tags
                ) {
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
                        isPublished
                        createdAt
                        updatedAt
                    }
                }
            }
        }
        """
        
        variables = {
            "title": title,
            "content": content,
            "description": description or title,
            "path": path,
            "locale": settings.DEFAULT_LOCALE,
            "editor": "markdown",
            "isPublished": True,
            "isPrivate": False,
            "tags": []
        }
        
        response = await wikijs.graphql_request_without_retry(create_mutation, variables)
        logger.info(f"Wiki.js create_page raw response: {response}")
        
        if not response or "data" not in response:
            return json.dumps({"error": "Invalid response from Wiki.js API", "raw_response": str(response)})
        
        create_result = response.get("data", {}).get("pages", {}).get("create", {})
        response_result = create_result.get("responseResult", {})
        
        if response_result.get("succeeded"):
            page_data = create_result.get("page", {})
            if not page_data:
                return json.dumps({
                    "error": "Page created but no page data returned.",
                    "raw_response": str(response)
                })
            return json.dumps({
                "pageId": page_data.get("id"),
                "title": page_data.get("title"),
                "path": page_data.get("path"),
                "description": page_data.get("description"),
                "content": page_data.get("content"),
                "isPublished": page_data.get("isPublished"),
                "createdAt": page_data.get("createdAt"),
                "updatedAt": page_data.get("updatedAt"),
                "url": f"/{page_data.get('path')}",
                "raw_response": str(response)
            })
        else:
            error_msg = response_result.get("message", "Unknown error")
            return json.dumps({
                "error": f"Failed to create page: {error_msg}",
                "raw_response": str(response)
            })
        
    except Exception as e:
        error_msg = f"Failed to create page: {str(e)}"
        logger.error(error_msg)
        return json.dumps({"error": error_msg})

@mcp.tool()
async def wikijs_update_page(page_id: int, title: str = None, content: str = None, description: str = None) -> str:
    """
    Update an existing page in Wiki.js.
    
    Args:
        page_id: Page ID to update
        title: New title (optional)
        content: New content (optional)
        description: New description (optional)
    
    Returns:
        JSON string with update status
    """
    try:
        await wikijs.authenticate()
        
        # Use proper update mutation with tags handling
        update_mutation = """
        mutation($id: Int!, $title: String, $content: String, $description: String, $tags: [String]) {
            pages {
                update(
                    id: $id,
                    title: $title,
                    content: $content,
                    description: $description,
                    tags: $tags
                ) {
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
                        isPublished
                        updatedAt
                        tags {
                            id
                            title
                            tag
                        }
                    }
                }
            }
        }
        """
        
        # Get current page data first
        get_page_query = """
        query($id: Int!) {
            pages {
                single(id: $id) {
                    id
                    title
                    content
                    description
                    editor
                    isPrivate
                    locale
                    tags {
                        id
                        title
                        tag
                    }
                }
            }
        }
        """
        
        page_response = await wikijs.graphql_request_without_retry(get_page_query, {"id": page_id})
        
        if not page_response or "data" not in page_response:
            return json.dumps({"error": "Failed to get current page data"})
        
        current_page = page_response.get("data", {}).get("pages", {}).get("single")
        if not current_page:
            return json.dumps({"error": "Page not found"})
        
        # Extract tag names from current page tags
        current_tags = []
        if current_page.get("tags"):
            current_tags = [tag.get("tag", "") for tag in current_page.get("tags", []) if tag.get("tag")]
        
        # Ensure we have at least one tag to avoid GraphQL validation errors
        if not current_tags:
            current_tags = ["default"]
        
        # Use current values as defaults, override with provided values
        variables = {
            "id": page_id,
            "title": title if title is not None else current_page.get("title"),
            "content": content if content is not None else current_page.get("content"),
            "description": description if description is not None else current_page.get("description"),
            "editor": current_page.get("editor", "markdown"),
            "isPrivate": current_page.get("isPrivate", False),
            "locale": current_page.get("locale", settings.DEFAULT_LOCALE),
            "tags": current_tags
        }
        
        response = await wikijs.graphql_request_without_retry(update_mutation, variables)
        
        if not response or "data" not in response:
            return json.dumps({"error": "Invalid response from Wiki.js API"})
        
        update_result = response.get("data", {}).get("pages", {}).get("update", {})
        response_result = update_result.get("responseResult", {})
        
        if response_result.get("succeeded"):
            page_data = update_result.get("page", {})
            if not page_data:
                return json.dumps({
                    "error": "Page updated but no page data returned.",
                    "raw_response": str(response)
                })
            
            # Extract tags from response
            page_tags = []
            if page_data.get("tags"):
                page_tags = [tag.get("tag", "") for tag in page_data.get("tags", []) if tag.get("tag")]
            
            return json.dumps({
                "pageId": page_data.get("id"),
                "title": page_data.get("title"),
                "path": page_data.get("path"),
                "description": page_data.get("description"),
                "content": page_data.get("content"),
                "isPublished": page_data.get("isPublished"),
                "updatedAt": page_data.get("updatedAt"),
                "tags": page_tags,
                "status": "updated",
                "raw_response": str(response)
            })
        else:
            error_msg = response_result.get("message", "Unknown error")
            return json.dumps({
                "error": f"Failed to update page: {error_msg}",
                "raw_response": str(response)
            })
        
    except Exception as e:
        error_msg = f"Failed to update page: {str(e)}"
        logger.error(error_msg)
        return json.dumps({"error": error_msg})

@mcp.tool()
async def wikijs_get_page(page_id: int = None, slug: str = None) -> str:
    """
    Retrieve page metadata and content from Wiki.js.
    
    Args:
        page_id: Page ID (optional)
        slug: Page slug/path (optional)
    
    Returns:
        JSON string with page data
    """
    try:
        await wikijs.authenticate()
        
        if page_id:
            # Get page by ID using correct API
            query = """
            query($id: Int!) {
                pages {
                    single(id: $id) {
                        id
                        title
                        path
                        content
                        description
                        isPublished
                        locale
                        createdAt
                        updatedAt
                    }
                }
            }
            """
            variables = {"id": page_id}
            response = await wikijs.graphql_request(query, variables)
            
            if not response or "data" not in response:
                return json.dumps({"error": "Invalid response from Wiki.js API"})
            
            page_data = response.get("data", {}).get("pages", {}).get("single")
            
        elif slug:
            # Get page by path using list query and filter - same approach as search
            query = """
            query {
                pages {
                    list {
                        id
                        title
                        path
                        content
                        description
                        isPublished
                        locale
                        createdAt
                        updatedAt
                    }
                }
            }
            """
            response = await wikijs.graphql_request(query)
            
            if not response or "data" not in response:
                return json.dumps({"error": "Invalid response from Wiki.js API"})
            
            pages_list = response.get("data", {}).get("pages", {}).get("list", [])
            page_data = None
            for page in pages_list:
                if page.get("path") == slug:
                    page_data = page
                    break
        else:
            return json.dumps({"error": "Either page_id or slug must be provided"})
        
        if not page_data:
            return json.dumps({"error": "Page not found"})
        
        result = {
            "pageId": page_data["id"],
            "title": page_data["title"],
            "path": page_data["path"],
            "content": page_data.get("content", ""),
            "description": page_data.get("description", ""),
            "isPublished": page_data.get("isPublished", True),
            "locale": page_data.get("locale", "en"),
            "createdAt": page_data.get("createdAt"),
            "updatedAt": page_data.get("updatedAt")
        }
        
        return json.dumps(result)
        
    except Exception as e:
        error_msg = f"Failed to get page: {str(e)}"
        logger.error(error_msg)
        return json.dumps({"error": error_msg})

@mcp.tool()
async def wikijs_search_pages(query: str, space_id: str = None) -> str:
    """
    Search pages by text in Wiki.js.
    
    Args:
        query: Search query
        space_id: Space ID to limit search (optional)
    
    Returns:
        JSON string with search results
    """
    try:
        await wikijs.authenticate()
        
        # Simplified GraphQL query - just get all pages
        search_query = """
        query {
            pages {
                list {
                    id
                    title
                    path
                    description
                    isPublished
                    locale
                    updatedAt
                }
            }
        }
        """
        
        response = await wikijs.graphql_request(search_query)
        
        if not response or "data" not in response:
            return json.dumps({"error": "Invalid response from Wiki.js API"})
        
        pages_data = response.get("data", {}).get("pages", {}).get("list", [])
        
        # Filter pages based on search query
        results = []
        for page in pages_data:
            title = page.get("title", "").lower()
            description = page.get("description", "").lower()
            path = page.get("path", "").lower()
            search_term = query.lower()
            
            # Simple text search in title, description, and path
            if (search_term in title or 
                search_term in description or 
                search_term in path or
                query == "*"):  # Show all pages if query is "*"
                
                results.append({
                    "pageId": page.get("id"),
                    "title": page.get("title"),
                    "snippet": page.get("description", ""),
                    "score": 1.0,
                    "path": page.get("path"),
                    "isPublished": page.get("isPublished", True),
                    "lastModified": page.get("updatedAt")
                })
        
        return json.dumps({
            "results": results, 
            "total": len(results)
        })
        
    except Exception as e:
        error_msg = f"Search failed: {str(e)}"
        logger.error(error_msg)
        return json.dumps({"error": error_msg})

@mcp.tool()
async def wikijs_list_spaces() -> str:
    """
    List all spaces (top-level Wiki.js containers).
    Note: Wiki.js doesn't have "spaces" like BookStack, but we can list pages at root level.
    
    Returns:
        JSON string with spaces list
    """
    try:
        await wikijs.authenticate()
        
        # Get all pages and group by top-level paths
        query = """
        query {
            pages {
                list {
                    id
                    title
                    path
                    description
                    isPublished
                    locale
                }
            }
        }
        """
        
        response = await wikijs.graphql_request(query)
        
        pages = response.get("data", {}).get("pages", {}).get("list", [])
        
        # Group pages by top-level path (simulate spaces)
        spaces = {}
        for page in pages:
            path_parts = page["path"].split("/")
            if len(path_parts) > 0:
                top_level = path_parts[0] if path_parts[0] else "root"
                if top_level not in spaces:
                    spaces[top_level] = {
                        "spaceId": hash(top_level) % 10000,  # Generate pseudo ID
                        "name": top_level.replace("-", " ").title(),
                        "slug": top_level,
                        "description": f"Pages under /{top_level}",
                        "pageCount": 0
                    }
                spaces[top_level]["pageCount"] += 1
        
        return json.dumps({"spaces": list(spaces.values())})
        
    except Exception as e:
        error_msg = f"Failed to list spaces: {str(e)}"
        logger.error(error_msg)
        return json.dumps({"error": error_msg})

@mcp.tool()
async def wikijs_create_space(name: str, description: str = None) -> str:
    """
    Create a new space in Wiki.js.
    Note: Wiki.js doesn't have spaces, so this creates a root-level page as a space placeholder.
    
    Args:
        name: Space name
        description: Space description (optional)
    
    Returns:
        JSON string with space details
    """
    try:
        await wikijs.authenticate()
        
        # Create a root-level page as a space placeholder
        content = f"# {name}\n\n"
        if description:
            content += f"{description}\n\n"
        content += "This is a space placeholder created via MCP."
        
        # Use proper create mutation with all required parameters
        create_mutation = """
        mutation($title: String!, $content: String!, $description: String!, $path: String!, $locale: String!, $editor: String!, $isPublished: Boolean!, $isPrivate: Boolean!, $tags: [String]!) {
            pages {
                create(
                    title: $title,
                    content: $content,
                    description: $description,
                    path: $path,
                    locale: $locale,
                    editor: $editor,
                    isPublished: $isPublished,
                    isPrivate: $isPrivate,
                    tags: $tags
                ) {
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
                        isPublished
                        createdAt
                        updatedAt
                        authorName
                        creatorName
                    }
                }
            }
        }
        """
        
        variables = {
            "title": name,
            "content": content,
            "description": description or f"Space: {name}",
            "path": name.lower().replace(" ", "-").replace("_", "-"),
            "locale": settings.DEFAULT_LOCALE,
            "editor": "markdown",
            "isPublished": True,
            "isPrivate": False,
            "tags": []
        }
        
        response = await wikijs.graphql_request_without_retry(create_mutation, variables)
        
        if not response or "data" not in response:
            return json.dumps({"error": "Invalid response from Wiki.js API"})
        
        create_result = response.get("data", {}).get("pages", {}).get("create", {})
        response_result = create_result.get("responseResult", {})
        
        if response_result.get("succeeded"):
            page_data = create_result.get("page", {})
            return json.dumps({
                "space_name": name,
                "description": description,
                "status": "created",
                "pageId": page_data.get("id"),
                "path": page_data.get("path"),
                "isPublished": page_data.get("isPublished"),
                "createdAt": page_data.get("createdAt"),
                "updatedAt": page_data.get("updatedAt")
            })
        else:
            error_msg = response_result.get("message", "Unknown error")
            return json.dumps({"error": f"Failed to create space: {error_msg}"})
        
    except Exception as e:
        error_msg = f"Failed to create space '{name}': {str(e)}"
        logger.error(error_msg)
        return json.dumps({"error": error_msg})

@mcp.tool()
async def wikijs_link_file_to_page(file_path: str, page_id: int, relationship: str = "documents") -> str:
    """
    Persist link between code file and Wiki.js page in local database.
    
    Args:
        file_path: Path to the source file
        page_id: Wiki.js page ID
        relationship: Type of relationship (documents, references, etc.)
    
    Returns:
        JSON string with link status
    """
    try:
        db = get_db()
        
        # Calculate file hash
        file_hash = get_file_hash(file_path)
        repo_root = find_repository_root(file_path)
        
        # Create or update mapping
        mapping = db.query(FileMapping).filter(FileMapping.file_path == file_path).first()
        if mapping:
            mapping.page_id = page_id
            mapping.relationship_type = relationship
            mapping.file_hash = file_hash
            mapping.last_updated = datetime.datetime.utcnow()
        else:
            mapping = FileMapping(
                file_path=file_path,
                page_id=page_id,
                relationship_type=relationship,
                file_hash=file_hash,
                repository_root=repo_root or ""
            )
            db.add(mapping)
        
        db.commit()
        
        result = {
            "linked": True,
            "file_path": file_path,
            "page_id": page_id,
            "relationship": relationship
        }
        
        logger.info(f"Linked file {file_path} to page {page_id}")
        return json.dumps(result)
        
    except Exception as e:
        error_msg = f"Failed to link file to page: {str(e)}"
        logger.error(error_msg)
        return json.dumps({"error": error_msg})

@mcp.tool()
async def wikijs_sync_file_docs(file_path: str, change_summary: str, snippet: str = None) -> str:
    """
    Sync a code change to the linked Wiki.js page.
    
    Args:
        file_path: Path to the changed file
        change_summary: Summary of changes made
        snippet: Code snippet showing changes (optional)
    
    Returns:
        JSON string with sync status
    """
    try:
        await wikijs.authenticate()
        
        # For now, just log the sync request
        # In a full implementation, this would:
        # 1. Find the linked page
        # 2. Update the page content with change summary
        # 3. Add the code snippet if provided
        
        sync_data = {
            "file_path": file_path,
            "change_summary": change_summary,
            "snippet": snippet,
            "timestamp": datetime.datetime.now().isoformat(),
            "status": "logged"
        }
        
        logger.info(f"File sync requested: {file_path} - {change_summary}")
        
        return json.dumps(sync_data)
        
    except Exception as e:
        error_msg = f"Failed to sync file docs: {str(e)}"
        logger.error(error_msg)
        return json.dumps({"error": error_msg})

@mcp.tool()
async def wikijs_generate_file_overview(file_path: str, include_functions: bool = True, include_classes: bool = True, include_dependencies: bool = True, include_examples: bool = False, target_page_id: int = None) -> str:
    """
    Create or update a structured overview page for a file.
    
    Args:
        file_path: Path to the source file
        include_functions: Include function documentation
        include_classes: Include class documentation
        include_dependencies: Include import/dependency information
        include_examples: Include usage examples
        target_page_id: Specific page ID to update (optional)
    
    Returns:
        JSON string with overview page details
    """
    try:
        await wikijs.authenticate()
        
        # For now, create a simple overview page
        # In a full implementation, this would:
        # 1. Parse the source file
        # 2. Extract functions, classes, dependencies
        # 3. Generate structured documentation
        
        file_name = os.path.basename(file_path)
        file_ext = os.path.splitext(file_name)[1]
        
        content = f"# {file_name}\n\n"
        content += f"Documentation for `{file_path}`\n\n"
        content += f"**File Type:** {file_ext}\n"
        content += f"**Last Updated:** {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n"
        
        if include_functions:
            content += "## Functions\n\n*Function documentation will be generated here.*\n\n"
        
        if include_classes:
            content += "## Classes\n\n*Class documentation will be generated here.*\n\n"
        
        if include_dependencies:
            content += "## Dependencies\n\n*Import and dependency information will be listed here.*\n\n"
        
        if include_examples:
            content += "## Examples\n\n*Usage examples will be provided here.*\n\n"
        
        content += "---\n*This documentation was auto-generated by the Wiki.js MCP server.*"
        
        # Create or update page using direct GraphQL
        if target_page_id:
            # Update existing page
            update_mutation = """
            mutation($id: Int!, $content: String!) {
                pages {
                    update(id: $id, content: $content) {
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
                            tags {
                                id
                                title
                                tag
                            }
                        }
                    }
                }
            }
            """
            
            variables = {
                "id": target_page_id,
                "content": content
            }
            
            response = await wikijs.graphql_request_without_retry(update_mutation, variables)
            
            if not response or "data" not in response:
                return json.dumps({"error": "Invalid response from Wiki.js API"})
            
            update_result = response.get("data", {}).get("pages", {}).get("update", {})
            response_result = update_result.get("responseResult", {})
            
            if response_result.get("succeeded"):
                page_data = update_result.get("page", {})
                
                # Extract tags from response
                page_tags = []
                if page_data.get("tags"):
                    page_tags = [tag.get("tag", "") for tag in page_data.get("tags", []) if tag.get("tag")]
                
                return json.dumps({
                    "pageId": page_data.get("id"),
                    "title": page_data.get("title"),
                    "path": page_data.get("path"),
                    "tags": page_tags,
                    "action": "updated"
                })
            else:
                error_msg = response_result.get("message", "Unknown error")
                return json.dumps({"error": f"Failed to update page: {error_msg}"})
        else:
            # Create new page
            create_mutation = """
            mutation($title: String!, $content: String!, $description: String!, $path: String!, $editor: String!, $isPrivate: Boolean!, $locale: String!, $tags: [String]!) {
                pages {
                    create(title: $title, content: $content, description: $description, path: $path, editor: $editor, isPrivate: $isPrivate, locale: $locale, tags: $tags, isPublished: true) {
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
                            tags {
                                id
                                title
                                tag
                            }
                        }
                    }
                }
            }
            """
            
            # Create safe path using slugify
            safe_path = slugify(file_path, separator='')
            
            # Remove file extension for path
            file_name_no_ext = os.path.splitext(file_name)[0]
            
            variables = {
                "title": f"Documentation: {file_name}",
                "content": content,
                "description": f"Auto-generated documentation for {file_path}",
                "path": file_name_no_ext,
                "editor": "markdown",
                "isPrivate": False,
                "locale": settings.DEFAULT_LOCALE,
                "tags": ["documentation", "auto-generated"]
            }
            
            response = await wikijs.graphql_request_without_retry(create_mutation, variables)
            
            if not response or "data" not in response:
                return json.dumps({"error": "Invalid response from Wiki.js API"})
            
            create_result = response.get("data", {}).get("pages", {}).get("create", {})
            response_result = create_result.get("responseResult", {})
            
            if response_result.get("succeeded"):
                page_data = create_result.get("page", {})
                
                # Extract tags from response
                page_tags = []
                if page_data.get("tags"):
                    page_tags = [tag.get("tag", "") for tag in page_data.get("tags", []) if tag.get("tag")]
                
                return json.dumps({
                    "pageId": page_data.get("id"),
                    "title": page_data.get("title"),
                    "path": page_data.get("path"),
                    "tags": page_tags,
                    "action": "created",
                    "file_path": file_path
                })
            else:
                error_msg = response_result.get("message", "Unknown error")
                return json.dumps({"error": f"Failed to create page: {error_msg}"})
        
    except Exception as e:
        error_msg = f"Failed to generate file overview: {str(e)}"
        logger.error(error_msg)
        return json.dumps({"error": error_msg})

@mcp.tool()
async def wikijs_bulk_update_project_docs(summary: str, affected_files: list, context: str, auto_create_missing: bool = True) -> str:
    """
    Batch update pages for large changes across multiple files.
    
    Args:
        summary: Overall project change summary
        affected_files: List of file paths that were changed
        context: Additional context about the changes
        auto_create_missing: Create pages for files without mappings
    
    Returns:
        JSON string with bulk update results
    """
    try:
        await wikijs.authenticate()
        
        # Create a summary page for the bulk update
        summary_content = f"# Project Update Summary\n\n"
        summary_content += f"**Date:** {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
        summary_content += f"**Summary:** {summary}\n\n"
        summary_content += f"**Context:** {context}\n\n"
        summary_content += f"## Affected Files ({len(affected_files)})\n\n"
        
        for file_path in affected_files:
            summary_content += f"- `{file_path}`\n"
        
        summary_content += "\n---\n*This summary was auto-generated by the Wiki.js MCP server.*"
        
        # Create summary page using direct GraphQL
        create_mutation = """
        mutation($title: String!, $content: String!, $description: String!, $path: String!, $editor: String!, $isPrivate: Boolean!, $locale: String!, $tags: [String]!) {
            pages {
                create(title: $title, content: $content, description: $description, path: $path, editor: $editor, isPrivate: $isPrivate, locale: $locale, tags: $tags, isPublished: true) {
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
                        tags {
                            id
                            title
                            tag
                        }
                    }
                }
            }
        }
        """
        
        # Create safe timestamp for path
        timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M')
        
        variables = {
            "title": f"Update Summary - {datetime.datetime.now().strftime('%Y-%m-%d')}",
            "content": summary_content,
            "description": f"Bulk update summary: {summary}",
            "path": f"updates{timestamp}",
            "editor": "markdown",
            "isPrivate": False,
            "locale": settings.DEFAULT_LOCALE,
            "tags": ["bulk-update", "automated"]
        }
        
        response = await wikijs.graphql_request_without_retry(create_mutation, variables)
        
        if not response or "data" not in response:
            return json.dumps({"error": "Invalid response from Wiki.js API"})
        
        create_result = response.get("data", {}).get("pages", {}).get("create", {})
        response_result = create_result.get("responseResult", {})
        
        if response_result.get("succeeded"):
            summary_data = create_result.get("page", {})
            
            # Extract tags from response
            summary_tags = []
            if summary_data.get("tags"):
                summary_tags = [tag.get("tag", "") for tag in summary_data.get("tags", []) if tag.get("tag")]
            
            summary_data["tags"] = summary_tags
        else:
            error_msg = response_result.get("message", "Unknown error")
            return json.dumps({"error": f"Failed to create summary page: {error_msg}"})
        
        # For now, just log the bulk update
        # In a full implementation, this would:
        # 1. Find all linked pages for affected files
        # 2. Update each page with change information
        # 3. Create pages for new files if auto_create_missing is True
        
        bulk_data = {
            "summary": summary,
            "affected_files": affected_files,
            "context": context,
            "auto_create_missing": auto_create_missing,
            "summary_page": summary_data,
            "total_files": len(affected_files),
            "updated": 0,
            "created": 0,
            "errors": [],
            "status": "logged"
        }
        
        logger.info(f"Bulk update requested: {summary} - {len(affected_files)} files affected")
        
        return json.dumps(bulk_data)
        
    except Exception as e:
        error_msg = f"Failed to bulk update project docs: {str(e)}"
        logger.error(error_msg)
        return json.dumps({"error": error_msg})

@mcp.tool()
async def wikijs_manage_collections(collection_name: str, description: str = None, space_ids: List[int] = None) -> str:
    """
    Manage Wiki.js collections (groups of spaces/pages).
    Note: This is a placeholder as Wiki.js collections API may vary by version.
    
    Args:
        collection_name: Name of the collection
        description: Collection description
        space_ids: List of space IDs to include
    
    Returns:
        JSON string with collection details
    """
    try:
        # This is a conceptual implementation
        # Actual Wiki.js API for collections may differ
        result = {
            "collection_name": collection_name,
            "description": description,
            "space_ids": space_ids or [],
            "status": "managed",
            "note": "Collection management depends on Wiki.js version and configuration"
        }
        
        logger.info(f"Managed collection: {collection_name}")
        return json.dumps(result)
        
    except Exception as e:
        error_msg = f"Failed to manage collection: {str(e)}"
        logger.error(error_msg)
        return json.dumps({"error": error_msg})

@mcp.tool()
async def wikijs_connection_status() -> str:
    """
    Check the status of the Wiki.js connection and authentication.
    
    Returns:
        JSON string with connection status
    """
    try:
        auth_success = await wikijs.authenticate()
        
        if auth_success:
            # Test with a simple API call
            response = await wikijs.graphql_request("query { pages { list { id } } }")
            
            result = {
                "connected": True,
                "authenticated": True,
                "api_url": settings.WIKIJS_API_URL,
                "auth_method": "token" if settings.token else "session",
                "status": "healthy"
            }
        else:
            result = {
                "connected": False,
                "authenticated": False,
                "api_url": settings.WIKIJS_API_URL,
                "status": "authentication_failed"
            }
        
        return json.dumps(result)
        
    except Exception as e:
        result = {
            "connected": False,
            "authenticated": False,
            "api_url": settings.WIKIJS_API_URL,
            "error": str(e),
            "status": "connection_failed"
        }
        return json.dumps(result)

@mcp.tool()
async def wikijs_repository_context() -> str:
    """
    Show current repository context and Wiki.js organization.
    
    Returns:
        JSON string with repository context
    """
    try:
        repo_root = find_repository_root()
        db = get_db()
        
        # Get repository context from database
        context = db.query(RepositoryContext).filter(
            RepositoryContext.root_path == repo_root
        ).first()
        
        # Get file mappings for this repository
        mappings = db.query(FileMapping).filter(
            FileMapping.repository_root == repo_root
        ).all()
        
        result = {
            "repository_root": repo_root,
            "space_name": context.space_name if context else settings.DEFAULT_SPACE_NAME,
            "space_id": context.space_id if context else None,
            "mapped_files": len(mappings),
            "mappings": [
                {
                    "file_path": m.file_path,
                    "page_id": m.page_id,
                    "relationship": m.relationship_type,
                    "last_updated": m.last_updated.isoformat() if m.last_updated else None
                }
                for m in mappings[:10]  # Limit to first 10 for brevity
            ]
        }
        
        return json.dumps(result)
        
    except Exception as e:
        error_msg = f"Failed to get repository context: {str(e)}"
        logger.error(error_msg)
        return json.dumps({"error": error_msg})

@mcp.tool()
async def wikijs_create_repo_structure(repo_name: str, description: str = None, sections: list = None) -> str:
    """
    Create a complete repository documentation structure with nested pages.
    
    Args:
        repo_name: Repository name (will be the root page)
        description: Repository description
        sections: List of main sections to create (e.g., ["Overview", "API", "Components", "Deployment"])
    
    Returns:
        JSON string with created structure details
    """
    try:
        await wikijs.authenticate()
        
        if not sections:
            sections = ["Overview", "API", "Components", "Deployment"]
        
        # Create root repository page
        root_content = f"# {repo_name}\n\n"
        if description:
            root_content += f"{description}\n\n"
        root_content += "## Sections\n\n"
        for section in sections:
            root_content += f"- [{section}]({repo_name.lower()}/{section.lower()})\n"
        
        # Create root page directly
        root_mutation = """
        mutation($title: String!, $content: String!, $description: String!, $path: String!, $locale: String!, $editor: String!, $isPublished: Boolean!, $isPrivate: Boolean!, $tags: [String]!) {
            pages {
                create(
                    title: $title,
                    content: $content,
                    description: $description,
                    path: $path,
                    locale: $locale,
                    editor: $editor,
                    isPublished: $isPublished,
                    isPrivate: $isPrivate,
                    tags: $tags
                ) {
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
                    }
                }
            }
        }
        """
        
        root_variables = {
            "title": repo_name,
            "content": root_content,
            "description": description or f"Documentation for {repo_name}",
            "path": repo_name.lower().replace(" ", "-"),
            "locale": settings.DEFAULT_LOCALE,
            "editor": "markdown",
            "isPublished": True,
            "isPrivate": False,
            "tags": []
        }
        
        root_response = await wikijs.graphql_request_without_retry(root_mutation, root_variables)
        
        if not root_response or "data" not in root_response:
            return json.dumps({"error": "Invalid response from Wiki.js API"})
        
        root_result = root_response.get("data", {}).get("pages", {}).get("create", {})
        root_response_result = root_result.get("responseResult", {})
        
        if not root_response_result.get("succeeded"):
            error_msg = root_response_result.get("message", "Unknown error")
            return json.dumps({"error": f"Failed to create root page: {error_msg}"})
        
        root_data = root_result.get("page", {})
        
        # Create section pages
        created_sections = []
        for section in sections:
            section_content = f"# {section}\n\nThis section contains {section.lower()} documentation for {repo_name}.\n\n## Contents\n\n*Content will be added here.*"
            
            # Create section page directly
            section_mutation = """
            mutation($title: String!, $content: String!, $description: String!, $path: String!, $locale: String!, $editor: String!, $isPublished: Boolean!, $isPrivate: Boolean!, $tags: [String]!) {
                pages {
                    create(
                        title: $title,
                        content: $content,
                        description: $description,
                        path: $path,
                        locale: $locale,
                        editor: $editor,
                        isPublished: $isPublished,
                        isPrivate: $isPrivate,
                        tags: $tags
                    ) {
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
            """
            
            section_variables = {
                "title": section,
                "content": section_content,
                "description": f"Section: {section}",
                "path": f"{repo_name.lower().replace(' ', '-')}/{section.lower()}",
                "locale": settings.DEFAULT_LOCALE,
                "editor": "markdown",
                "isPublished": True,
                "isPrivate": False,
                "tags": []
            }
            
            section_response = await wikijs.graphql_request_without_retry(section_mutation, section_variables)
            section_result = section_response.get("data", {}).get("pages", {}).get("create", {})
            
            if section_result.get("responseResult", {}).get("succeeded"):
                section_data = section_result.get("page", {})
                created_sections.append({
                    "pageId": section_data.get("id"),
                    "title": section,
                    "path": section_data.get("path")
                })
        
        return json.dumps({
            "repo_name": repo_name,
            "description": description,
            "root_page": root_data,
            "sections": created_sections,
            "total_sections": len(created_sections),
            "status": "created"
        })
        
    except Exception as e:
        error_msg = f"Failed to create repository structure: {str(e)}"
        logger.error(error_msg)
        return json.dumps({"error": error_msg})

@mcp.tool()
async def wikijs_create_nested_page(title: str, content: str, parent_path: str, create_parent_if_missing: bool = True) -> str:
    """
    Create a nested page using hierarchical paths (e.g., "repo/api/endpoints").
    
    Args:
        title: Page title
        content: Page content
        parent_path: Full path to parent (e.g., "my-repo/api")
        create_parent_if_missing: Create parent pages if they don't exist
    
    Returns:
        JSON string with page details
    """
    try:
        await wikijs.authenticate()
        
        # Build the full path
        full_path = f"{parent_path}/{title.lower().replace(' ', '-').replace('_', '-')}"
        
        # Check if parent exists and create if needed
        parent_exists = False
        if create_parent_if_missing:
            # Try to create parent page if it doesn't exist
            try:
                parent_title = parent_path.split("/")[-1].replace("-", " ").title()
                parent_content = f"# {parent_title}\n\nParent page for {title}"
                
                # Use proper create mutation with all required parameters
                parent_mutation = """
                mutation($title: String!, $content: String!, $description: String!, $path: String!, $locale: String!, $editor: String!, $isPublished: Boolean!, $isPrivate: Boolean!, $tags: [String]!) {
                    pages {
                        create(
                            title: $title,
                            content: $content,
                            description: $description,
                            path: $path,
                            locale: $locale,
                            editor: $editor,
                            isPublished: $isPublished,
                            isPrivate: $isPrivate,
                            tags: $tags
                        ) {
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
                                isPublished
                            }
                        }
                    }
                }
                """
                
                parent_variables = {
                    "title": parent_title,
                    "content": parent_content,
                    "description": f"Parent page: {parent_title}",
                    "path": parent_path,
                    "locale": settings.DEFAULT_LOCALE,
                    "editor": "markdown",
                    "isPublished": True,
                    "isPrivate": False,
                    "tags": []
                }
                
                parent_response = await wikijs.graphql_request_without_retry(parent_mutation, parent_variables)
                parent_result = parent_response.get("data", {}).get("pages", {}).get("create", {})
                
                if parent_result.get("responseResult", {}).get("succeeded"):
                    parent_exists = True
            except:
                # Parent might already exist, continue
                pass
        
        # Create the nested page with proper mutation
        create_mutation = """
        mutation($title: String!, $content: String!, $description: String!, $path: String!, $locale: String!, $editor: String!, $isPublished: Boolean!, $isPrivate: Boolean!, $tags: [String]!) {
            pages {
                create(
                    title: $title,
                    content: $content,
                    description: $description,
                    path: $path,
                    locale: $locale,
                    editor: $editor,
                    isPublished: $isPublished,
                    isPrivate: $isPrivate,
                    tags: $tags
                ) {
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
                        isPublished
                        createdAt
                        updatedAt
                    }
                }
            }
        }
        """
        
        variables = {
            "title": title,
            "content": content,
            "description": f"Nested page: {title}",
            "path": full_path,
            "locale": settings.DEFAULT_LOCALE,
            "editor": "markdown",
            "isPublished": True,
            "isPrivate": False,
            "tags": []
        }
        
        response = await wikijs.graphql_request_without_retry(create_mutation, variables)
        
        if not response or "data" not in response:
            return json.dumps({"error": "Invalid response from Wiki.js API"})
        
        create_result = response.get("data", {}).get("pages", {}).get("create", {})
        response_result = create_result.get("responseResult", {})
        
        if response_result.get("succeeded"):
            page_data = create_result.get("page", {})
            return json.dumps({
                "pageId": page_data.get("id"),
                "title": page_data.get("title"),
                "path": page_data.get("path"),
                "description": page_data.get("description"),
                "content": page_data.get("content"),
                "isPublished": page_data.get("isPublished"),
                "createdAt": page_data.get("createdAt"),
                "updatedAt": page_data.get("updatedAt"),
                "parentPath": parent_path,
                "fullPath": full_path,
                "parentCreated": parent_exists,
                "status": "created"
            })
        else:
            error_msg = response_result.get("message", "Unknown error")
            return json.dumps({"error": f"Failed to create nested page: {error_msg}"})
        
    except Exception as e:
        error_msg = f"Failed to create nested page: {str(e)}"
        logger.error(error_msg)
        return json.dumps({"error": error_msg})

@mcp.tool()
async def wikijs_get_page_children(page_id: int = None, page_path: str = None) -> str:
    """
    Get all child pages of a given page for hierarchical navigation.
    
    Args:
        page_id: Parent page ID (optional)
        page_path: Parent page path (optional)
    
    Returns:
        JSON string with child pages list
    """
    try:
        await wikijs.authenticate()
        
        # Get the parent page first using correct API
        if page_id:
            parent_query = """
            query($id: Int!) {
                pages {
                    single(id: $id) {
                        id
                        path
                        title
                    }
                }
            }
            """
            parent_response = await wikijs.graphql_request(parent_query, {"id": page_id})
            parent_data = parent_response.get("data", {}).get("pages", {}).get("single")
        elif page_path:
            # Use list query and filter by path since singleByPath might not exist
            parent_query = """
            query {
                pages {
                    list {
                        id
                        path
                        title
                    }
                }
            }
            """
            parent_response = await wikijs.graphql_request(parent_query)
            all_pages = parent_response.get("data", {}).get("pages", {}).get("list", [])
            parent_data = None
            for page in all_pages:
                if page.get("path") == page_path:
                    parent_data = page
                    break
        else:
            return json.dumps({"error": "Either page_id or page_path must be provided"})
        
        if not parent_data:
            return json.dumps({"error": "Parent page not found"})
        
        parent_path = parent_data["path"]
        
        # Get all pages using correct API - reuse the same query
        all_pages = parent_response.get("data", {}).get("pages", {}).get("list", [])
        
        # Filter for direct children (path starts with parent_path/ but no additional slashes)
        children = []
        for page in all_pages:
            page_path_str = page["path"]
            if page_path_str.startswith(f"{parent_path}/"):
                # Check if it's a direct child (no additional slashes after parent)
                remaining_path = page_path_str[len(parent_path) + 1:]
                if "/" not in remaining_path:  # Direct child
                    children.append({
                        "pageId": page["id"],
                        "title": page["title"],
                        "path": page["path"],
                        "description": page.get("description", ""),
                        "lastModified": page.get("updatedAt"),
                        "isPublished": page.get("isPublished", True)
                    })
        
        result = {
            "parent": {
                "pageId": parent_data["id"],
                "title": parent_data["title"],
                "path": parent_data["path"]
            },
            "children": children,
            "total_children": len(children)
        }
        
        return json.dumps(result)
        
    except Exception as e:
        error_msg = f"Failed to get page children: {str(e)}"
        logger.error(error_msg)
        return json.dumps({"error": error_msg})

@mcp.tool()
async def wikijs_create_documentation_hierarchy(project_name: str, file_mappings: list, auto_organize: bool = True) -> str:
    """
    Create a complete documentation hierarchy for a project based on file structure.
    
    Args:
        project_name: Name of the project/repository
        file_mappings: List of {"file_path": "src/components/Button.tsx", "doc_path": "components/button"} mappings
        auto_organize: Automatically organize files into logical sections
    
    Returns:
        JSON string with created hierarchy details
    """
    try:
        await wikijs.authenticate()
        
        # Create project root page
        root_content = f"# {project_name} Documentation\n\n"
        root_content += "This documentation was automatically generated from the project structure.\n\n"
        root_content += "## File Structure\n\n"
        
        # Group files by category
        categories = {}
        for mapping in file_mappings:
            file_path = mapping.get("file_path", "")
            doc_path = mapping.get("doc_path", "")
            
            # Extract category from file path
            category = "Other"
            if "/" in file_path:
                category = file_path.split("/")[0].title()
            
            if category not in categories:
                categories[category] = []
            categories[category].append({
                "file_path": file_path,
                "doc_path": doc_path
            })
        
        # Create category pages
        created_pages = []
        for category, files in categories.items():
            category_content = f"# {category}\n\n"
            category_content += f"Documentation for {category.lower()} components and files.\n\n"
            category_content += "## Files\n\n"
            
            for file_info in files:
                file_path = file_info["file_path"]
                doc_path = file_info["doc_path"]
                category_content += f"- [{file_path}]({project_name.lower()}/{category.lower()}/{doc_path})\n"
            
            # Create category page directly using GraphQL
            category_path = f"{project_name.lower().replace(' ', '-')}/{category.lower()}"
            
            category_mutation = """
            mutation($title: String!, $content: String!, $description: String!, $path: String!, $locale: String!, $editor: String!, $isPublished: Boolean!, $isPrivate: Boolean!, $tags: [String]!) {
                pages {
                    create(
                        title: $title,
                        content: $content,
                        description: $description,
                        path: $path,
                        locale: $locale,
                        editor: $editor,
                        isPublished: $isPublished,
                        isPrivate: $isPrivate,
                        tags: $tags
                    ) {
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
                            isPublished
                            createdAt
                            updatedAt
                        }
                    }
                }
            }
            """
            
            category_variables = {
                "title": category,
                "content": category_content,
                "description": f"Category: {category}",
                "path": category_path,
                "locale": settings.DEFAULT_LOCALE,
                "editor": "markdown",
                "isPublished": True,
                "isPrivate": False,
                "tags": []
            }
            
            category_response = await wikijs.graphql_request_without_retry(category_mutation, category_variables)
            category_result = category_response.get("data", {}).get("pages", {}).get("create", {})
            
            if category_result.get("responseResult", {}).get("succeeded"):
                category_data = category_result.get("page", {})
                created_pages.append({
                    "pageId": category_data.get("id"),
                    "title": category,
                    "path": category_data.get("path"),
                    "description": category_data.get("description"),
                    "content": category_data.get("content"),
                    "isPublished": category_data.get("isPublished"),
                    "createdAt": category_data.get("createdAt"),
                    "updatedAt": category_data.get("updatedAt"),
                    "parentPath": project_name.lower().replace(" ", "-"),
                    "fullPath": category_path,
                    "status": "created"
                })
        
        return json.dumps({
            "project_name": project_name,
            "file_mappings": file_mappings,
            "categories": list(categories.keys()),
            "created_pages": created_pages,
            "total_pages": len(created_pages),
            "status": "created"
        })
        
    except Exception as e:
        error_msg = f"Failed to create documentation hierarchy: {str(e)}"
        logger.error(error_msg)
        return json.dumps({"error": error_msg})

@mcp.tool()
async def wikijs_delete_page(page_id: int = None, page_path: str = None, remove_file_mapping: bool = True) -> str:
    """
    Delete a specific page from Wiki.js.
    
    Args:
        page_id: Page ID to delete (optional)
        page_path: Page path to delete (optional)
        remove_file_mapping: Also remove file-to-page mapping from local database
    
    Returns:
        JSON string with deletion status
    """
    try:
        await wikijs.authenticate()
        
        # Get page ID if only path provided
        if page_path and not page_id:
            get_query = """
            query($path: String!, $locale: String!) {
                pages {
                    singleByPath(path: $path, locale: $locale) {
                        id
                        title
                        path
                    }
                }
            }
            """
            get_response = await wikijs.graphql_request(get_query, {"path": page_path, "locale": "en"})
            page_data = get_response.get("data", {}).get("pages", {}).get("singleByPath")
            
            if not page_data:
                return json.dumps({"error": f"Page with path '{page_path}' not found"})
            
            page_id = page_data["id"]
        
        if not page_id:
            return json.dumps({"error": "Either page_id or page_path must be provided"})
        
        # Use proper delete mutation
        delete_mutation = """
        mutation($id: Int!) {
            pages {
                delete(id: $id) {
                    responseResult {
                        succeeded
                        errorCode
                        slug
                        message
                    }
                }
            }
        }
        """
        
        response = await wikijs.graphql_request(delete_mutation, {"id": page_id})
        
        if not response or "data" not in response:
            return json.dumps({"error": "Invalid response from Wiki.js API"})
        
        delete_result = response.get("data", {}).get("pages", {}).get("delete", {})
        response_result = delete_result.get("responseResult", {})
        
        if response_result.get("succeeded"):
            result = {
                "pageId": page_id,
                "status": "deleted",
                "message": "Page successfully deleted"
            }
            
            # Log the deletion for safety (actual deletion is performed)
            logger.info(f"Deleted page ID: {page_id}")
            
            return json.dumps(result)
        else:
            error_msg = response_result.get("message", "Unknown error")
            return json.dumps({"error": f"Failed to delete page: {error_msg}"})
        
    except Exception as e:
        error_msg = f"Failed to delete page: {str(e)}"
        logger.error(error_msg)
        return json.dumps({"error": error_msg})

@mcp.tool()
async def wikijs_batch_delete_pages(
    page_ids: List[int] = None, 
    page_paths: List[str] = None,
    path_pattern: str = None,
    confirm_deletion: bool = False,
    remove_file_mappings: bool = True
) -> str:
    """
    Batch delete multiple pages from Wiki.js.
    
    Args:
        page_ids: List of page IDs to delete (optional)
        page_paths: List of page paths to delete (optional)
        path_pattern: Pattern to match paths (e.g., "frontend-app/*" for all pages under frontend-app)
        confirm_deletion: Must be True to actually delete pages (safety check)
        remove_file_mappings: Also remove file-to-page mappings from local database
    
    Returns:
        JSON string with batch deletion results
    """
    try:
        if not confirm_deletion:
            return json.dumps({
                "error": "confirm_deletion must be True to proceed with batch deletion",
                "safety_note": "This is a safety check to prevent accidental deletions"
            })
        
        await wikijs.authenticate()
        
        pages_to_delete = []
        
        # Collect pages by IDs
        if page_ids:
            for page_id in page_ids:
                get_query = """
                query($id: Int!) {
                    pages {
                        single(id: $id) {
                            id
                            path
                            title
                        }
                    }
                }
                """
                get_response = await wikijs.graphql_request(get_query, {"id": page_id})
                page_data = get_response.get("data", {}).get("pages", {}).get("single")
                if page_data:
                    pages_to_delete.append(page_data)
        
        # Collect pages by paths
        if page_paths:
            for page_path in page_paths:
                get_query = """
                query($path: String!) {
                    pages {
                        singleByPath(path: $path, locale: "en") {
                            id
                            path
                            title
                        }
                    }
                }
                """
                get_response = await wikijs.graphql_request(get_query, {"path": page_path})
                page_data = get_response.get("data", {}).get("pages", {}).get("singleByPath")
                if page_data:
                    pages_to_delete.append(page_data)
        
        # Collect pages by pattern
        if path_pattern:
            # Get all pages and filter by pattern
            all_pages_query = """
            query {
                pages {
                    list {
                        id
                        title
                        path
                    }
                }
            }
            """
            
            response = await wikijs.graphql_request(all_pages_query)
            all_pages = response.get("data", {}).get("pages", {}).get("list", [])
            
            # Simple pattern matching (supports * wildcard)
            import fnmatch
            for page in all_pages:
                if fnmatch.fnmatch(page["path"], path_pattern):
                    pages_to_delete.append(page)
        
        if not pages_to_delete:
            return json.dumps({"error": "No pages found to delete"})
        
        # Remove duplicates
        unique_pages = {}
        for page in pages_to_delete:
            unique_pages[page["id"]] = page
        pages_to_delete = list(unique_pages.values())
        
        # Delete pages using direct GraphQL
        deleted_pages = []
        failed_deletions = []
        
        delete_mutation = """
        mutation($id: Int!) {
            pages {
                delete(id: $id) {
                    responseResult {
                        succeeded
                        errorCode
                        slug
                        message
                    }
                }
            }
        }
        """
        
        for page in pages_to_delete:
            try:
                response = await wikijs.graphql_request_without_retry(delete_mutation, {"id": page["id"]})
                
                if not response or "data" not in response:
                    failed_deletions.append({
                        "pageId": page["id"],
                        "title": page["title"],
                        "path": page["path"],
                        "error": "Invalid response from Wiki.js API"
                    })
                    continue
                
                delete_result = response.get("data", {}).get("pages", {}).get("delete", {})
                response_result = delete_result.get("responseResult", {})
                
                if response_result.get("succeeded"):
                    deleted_pages.append({
                        "pageId": page["id"],
                        "title": page["title"],
                        "path": page["path"]
                    })
                    
                    # Remove file mapping if requested
                    if remove_file_mappings:
                        try:
                            db = get_db()
                            mapping = db.query(FileMapping).filter(FileMapping.page_id == page["id"]).first()
                            if mapping:
                                db.delete(mapping)
                                db.commit()
                        except Exception as e:
                            logger.warning(f"Failed to remove file mapping for page {page['id']}: {e}")
                else:
                    error_msg = response_result.get("message", "Unknown error")
                    failed_deletions.append({
                        "pageId": page["id"],
                        "title": page["title"],
                        "path": page["path"],
                        "error": error_msg
                    })
            except Exception as e:
                failed_deletions.append({
                    "pageId": page["id"],
                    "title": page["title"],
                    "path": page["path"],
                    "error": str(e)
                })
        
        result = {
            "total_found": len(pages_to_delete),
            "deleted_count": len(deleted_pages),
            "failed_count": len(failed_deletions),
            "deleted_pages": deleted_pages,
            "failed_deletions": failed_deletions,
            "status": "completed"
        }
        
        logger.info(f"Batch deletion completed: {len(deleted_pages)} deleted, {len(failed_deletions)} failed")
        return json.dumps(result)
        
    except Exception as e:
        error_msg = f"Batch deletion failed: {str(e)}"
        logger.error(error_msg)
        return json.dumps({"error": error_msg})

@mcp.tool()
async def wikijs_delete_hierarchy(
    root_path: str,
    delete_mode: str = "children_only",
    confirm_deletion: bool = False,
    remove_file_mappings: bool = True
) -> str:
    """
    Delete an entire page hierarchy (folder structure) from Wiki.js.
    
    Args:
        root_path: Root path of the hierarchy to delete (e.g., "frontend-app" or "frontend-app/components")
        delete_mode: Deletion mode - "children_only", "include_root", or "root_only"
        confirm_deletion: Must be True to actually delete pages (safety check)
        remove_file_mappings: Also remove file-to-page mappings from local database
    
    Returns:
        JSON string with hierarchy deletion results
    """
    try:
        if not confirm_deletion:
            return json.dumps({
                "error": "confirm_deletion must be True to proceed with hierarchy deletion",
                "safety_note": "This is a safety check to prevent accidental deletions",
                "preview_mode": "Set confirm_deletion=True to actually delete"
            })
        
        valid_modes = ["children_only", "include_root", "root_only"]
        if delete_mode not in valid_modes:
            return json.dumps({
                "error": f"Invalid delete_mode. Must be one of: {valid_modes}"
            })
        
        await wikijs.authenticate()
        
        # Get all pages to find hierarchy
        all_pages_query = """
        query {
            pages {
                list {
                    id
                    title
                    path
                }
            }
        }
        """
        
        response = await wikijs.graphql_request(all_pages_query)
        all_pages = response.get("data", {}).get("pages", {}).get("list", [])
        
        # Find root page
        root_page = None
        for page in all_pages:
            if page["path"] == root_path:
                root_page = page
                break
        
        if not root_page and delete_mode in ["include_root", "root_only"]:
            return json.dumps({"error": f"Root page not found: {root_path}"})
        
        # Find child pages
        child_pages = []
        for page in all_pages:
            page_path = page["path"]
            if page_path.startswith(f"{root_path}/"):
                child_pages.append(page)
        
        # Determine pages to delete based on mode
        pages_to_delete = []
        
        if delete_mode == "children_only":
            pages_to_delete = child_pages
        elif delete_mode == "include_root":
            pages_to_delete = child_pages + ([root_page] if root_page else [])
        elif delete_mode == "root_only":
            pages_to_delete = [root_page] if root_page else []
        
        if not pages_to_delete:
            return json.dumps({
                "message": f"No pages found to delete for path: {root_path}",
                "delete_mode": delete_mode,
                "root_found": root_page is not None,
                "children_found": len(child_pages)
            })
        
        # Sort by depth (deepest first) to avoid dependency issues
        pages_to_delete.sort(key=lambda x: x["path"].count("/"), reverse=True)
        
        # Delete pages using direct GraphQL
        deleted_pages = []
        failed_deletions = []
        
        delete_mutation = """
        mutation($id: Int!) {
            pages {
                delete(id: $id) {
                    responseResult {
                        succeeded
                        errorCode
                        slug
                        message
                    }
                }
            }
        }
        """
        
        for page in pages_to_delete:
            try:
                response = await wikijs.graphql_request_without_retry(delete_mutation, {"id": page["id"]})
                
                if not response or "data" not in response:
                    failed_deletions.append({
                        "pageId": page["id"],
                        "title": page["title"],
                        "path": page["path"],
                        "error": "Invalid response from Wiki.js API"
                    })
                    continue
                
                delete_result = response.get("data", {}).get("pages", {}).get("delete", {})
                response_result = delete_result.get("responseResult", {})
                
                if response_result.get("succeeded"):
                    deleted_pages.append({
                        "pageId": page["id"],
                        "title": page["title"],
                        "path": page["path"],
                        "depth": page["path"].count("/")
                    })
                    
                    # Remove file mapping if requested
                    if remove_file_mappings:
                        try:
                            db = get_db()
                            mapping = db.query(FileMapping).filter(FileMapping.page_id == page["id"]).first()
                            if mapping:
                                db.delete(mapping)
                                db.commit()
                        except Exception as e:
                            logger.warning(f"Failed to remove file mapping for page {page['id']}: {e}")
                else:
                    error_msg = response_result.get("message", "Unknown error")
                    failed_deletions.append({
                        "pageId": page["id"],
                        "title": page["title"],
                        "path": page["path"],
                        "error": error_msg
                    })
            except Exception as e:
                failed_deletions.append({
                    "pageId": page["id"],
                    "title": page["title"],
                    "path": page["path"],
                    "error": str(e)
                })
        
        result = {
            "root_path": root_path,
            "delete_mode": delete_mode,
            "total_found": len(pages_to_delete),
            "deleted_count": len(deleted_pages),
            "failed_count": len(failed_deletions),
            "deleted_pages": deleted_pages,
            "failed_deletions": failed_deletions,
            "hierarchy_summary": {
                "root_page_found": root_page is not None,
                "child_pages_found": len(child_pages),
                "max_depth": max([p["path"].count("/") for p in pages_to_delete]) if pages_to_delete else 0
            },
            "status": "completed"
        }
        
        logger.info(f"Hierarchy deletion completed for {root_path}: {len(deleted_pages)} deleted, {len(failed_deletions)} failed")
        return json.dumps(result)
        
    except Exception as e:
        error_msg = f"Hierarchy deletion failed: {str(e)}"
        logger.error(error_msg)
        return json.dumps({"error": error_msg})

@mcp.tool()
async def wikijs_cleanup_orphaned_mappings() -> str:
    """
    Clean up file-to-page mappings for pages that no longer exist in Wiki.js.
    
    Returns:
        JSON string with cleanup results
    """
    try:
        await wikijs.authenticate()
        db = get_db()
        
        # Get all file mappings
        mappings = db.query(FileMapping).all()
        
        if not mappings:
            return json.dumps({
                "message": "No file mappings found",
                "cleaned_count": 0
            })
        
        # Check which pages still exist
        orphaned_mappings = []
        valid_mappings = []
        
        for mapping in mappings:
            try:
                get_query = """
                query($id: Int!) {
                    pages {
                        single(id: $id) {
                            id
                            title
                            path
                        }
                    }
                }
                """
                get_response = await wikijs.graphql_request(get_query, {"id": mapping.page_id})
                page_data = get_response.get("data", {}).get("pages", {}).get("single")
                
                if page_data:
                    valid_mappings.append({
                        "file_path": mapping.file_path,
                        "page_id": mapping.page_id,
                        "page_title": page_data["title"]
                    })
                else:
                    orphaned_mappings.append({
                        "file_path": mapping.file_path,
                        "page_id": mapping.page_id,
                        "last_updated": mapping.last_updated.isoformat() if mapping.last_updated else None
                    })
                    # Delete orphaned mapping
                    db.delete(mapping)
                    
            except Exception as e:
                # If we can't check the page, consider it orphaned
                orphaned_mappings.append({
                    "file_path": mapping.file_path,
                    "page_id": mapping.page_id,
                    "error": str(e)
                })
                db.delete(mapping)
        
        db.commit()
        
        result = {
            "total_mappings": len(mappings),
            "valid_mappings": len(valid_mappings),
            "orphaned_mappings": len(orphaned_mappings),
            "cleaned_count": len(orphaned_mappings),
            "orphaned_details": orphaned_mappings,
            "status": "completed"
        }
        
        logger.info(f"Cleaned up {len(orphaned_mappings)} orphaned file mappings")
        return json.dumps(result)
        
    except Exception as e:
        error_msg = f"Cleanup failed: {str(e)}"
        logger.error(error_msg)
        return json.dumps({"error": error_msg})

@mcp.tool()
async def wikijs_get_page_by_slug(slug: str) -> str:
    """
    Retrieve page metadata and content from Wiki.js by slug/path.
    
    Args:
        slug: Page slug/path
    
    Returns:
        JSON string with page data
    """
    try:
        await wikijs.authenticate()
        
        # Use singleByPath with required locale parameter
        query = """
        query($path: String!, $locale: String!) {
            pages {
                singleByPath(path: $path, locale: $locale) {
                    id
                    title
                    path
                    content
                    description
                    isPublished
                    locale
                    createdAt
                    updatedAt
                    authorName
                    creatorName
                }
            }
        }
        """
        
        variables = {
            "path": slug,
            "locale": settings.DEFAULT_LOCALE
        }
        
        response = await wikijs.graphql_request(query, variables)
        
        if not response or "data" not in response:
            return json.dumps({"error": "Invalid response from Wiki.js API"})
        
        page_data = response.get("data", {}).get("pages", {}).get("singleByPath")
        
        if not page_data:
            return json.dumps({"error": "Page not found"})
        
        result = {
            "pageId": page_data["id"],
            "title": page_data["title"],
            "path": page_data["path"],
            "content": page_data.get("content", ""),
            "description": page_data.get("description", ""),
            "isPublished": page_data.get("isPublished", True),
            "locale": page_data.get("locale", "en"),
            "createdAt": page_data.get("createdAt"),
            "updatedAt": page_data.get("updatedAt"),
            "authorName": page_data.get("authorName"),
            "creatorName": page_data.get("creatorName")
        }
        
        return json.dumps(result)
        
    except Exception as e:
        error_msg = f"Failed to get page by slug: {str(e)}"
        logger.error(error_msg)
        return json.dumps({"error": error_msg})

@mcp.tool()
async def wikijs_graphql_introspection() -> str:
    """
    Perform GraphQL introspection to get the API schema.
    
    Returns:
        JSON string with GraphQL schema information
    """
    try:
        await wikijs.authenticate()
        
        # Simple introspection query to get basic schema info
        introspection_query = """
        query {
          __schema {
            queryType {
              name
              fields {
                name
                description
                args {
                  name
                  type {
                    name
                  }
                }
              }
            }
            mutationType {
              name
              fields {
                name
                description
                args {
                  name
                  type {
                    name
                  }
                }
              }
            }
            types {
              name
              kind
              description
            }
          }
        }
        """
        
        response = await wikijs.graphql_request(introspection_query)
        
        if not response or "data" not in response:
            return json.dumps({"error": "Invalid response from GraphQL introspection"})
        
        schema_data = response.get("data", {}).get("__schema", {})
        
        # Extract basic information
        query_type = schema_data.get("queryType", {})
        mutation_type = schema_data.get("mutationType", {})
        
        # Find pages-related queries
        pages_queries = []
        if query_type and query_type.get("fields"):
            for field in query_type.get("fields", []):
                field_name = field.get("name", "")
                if "page" in field_name.lower() or "Page" in field_name:
                    pages_queries.append({
                        "name": field_name,
                        "description": field.get("description"),
                        "args": [arg.get("name") for arg in field.get("args", [])]
                    })
        
        # Find pages-related mutations
        pages_mutations = []
        if mutation_type and mutation_type.get("fields"):
            for field in mutation_type.get("fields", []):
                field_name = field.get("name", "")
                if "page" in field_name.lower() or "Page" in field_name:
                    pages_mutations.append({
                        "name": field_name,
                        "description": field.get("description"),
                        "args": [arg.get("name") for arg in field.get("args", [])]
                    })
        
        # Find pages-related types
        pages_types = []
        for type_info in schema_data.get("types", []):
            type_name = type_info.get("name", "")
            if "page" in type_name.lower() or "Page" in type_name:
                pages_types.append({
                    "name": type_name,
                    "kind": type_info.get("kind"),
                    "description": type_info.get("description")
                })
        
        result = {
            "query_type_name": query_type.get("name") if query_type else None,
            "mutation_type_name": mutation_type.get("name") if mutation_type else None,
            "pages_queries": pages_queries,
            "pages_mutations": pages_mutations,
            "pages_types": pages_types,
            "total_types": len(schema_data.get("types", [])),
            "status": "success"
        }
        
        return json.dumps(result, indent=2)
        
    except Exception as e:
        error_msg = f"GraphQL introspection failed: {str(e)}"
        logger.error(error_msg)
        return json.dumps({"error": error_msg})

@mcp.tool()
async def wikijs_get_page_schema_details() -> str:
    """
    Get detailed schema information for Page-related types.
    
    Returns:
        JSON string with detailed Page schema information
    """
    try:
        await wikijs.authenticate()
        
        # Get detailed information about PageQuery and PageMutation
        detailed_query = """
        query {
          __type(name: "PageQuery") {
            name
            kind
            fields {
              name
              description
              args {
                name
                description
                type {
                  name
                  kind
                }
                defaultValue
              }
              type {
                name
                kind
              }
            }
          }
        }
        """
        
        response = await wikijs.graphql_request(detailed_query)
        
        if not response or "data" not in response:
            return json.dumps({"error": "Invalid response from GraphQL query"})
        
        page_query_type = response.get("data", {}).get("__type", {})
        
        # Get PageMutation details
        mutation_query = """
        query {
          __type(name: "PageMutation") {
            name
            kind
            fields {
              name
              description
              args {
                name
                description
                type {
                  name
                  kind
                }
                defaultValue
              }
              type {
                name
                kind
              }
            }
          }
        }
        """
        
        mutation_response = await wikijs.graphql_request(mutation_query)
        page_mutation_type = mutation_response.get("data", {}).get("__type", {}) if mutation_response and "data" in mutation_response else {}
        
        # Get Page type details
        page_type_query = """
        query {
          __type(name: "Page") {
            name
            kind
            fields {
              name
              description
              type {
                name
                kind
              }
            }
          }
        }
        """
        
        page_response = await wikijs.graphql_request(page_type_query)
        page_type = page_response.get("data", {}).get("__type", {}) if page_response and "data" in page_response else {}
        
        result = {
            "page_query": {
                "name": page_query_type.get("name"),
                "kind": page_query_type.get("kind"),
                "fields": page_query_type.get("fields", [])
            },
            "page_mutation": {
                "name": page_mutation_type.get("name"),
                "kind": page_mutation_type.get("kind"),
                "fields": page_mutation_type.get("fields", [])
            },
            "page_type": {
                "name": page_type.get("name"),
                "kind": page_type.get("kind"),
                "fields": page_type.get("fields", [])
            },
            "status": "success"
        }
        
        return json.dumps(result, indent=2)
        
    except Exception as e:
        error_msg = f"Failed to get page schema details: {str(e)}"
        logger.error(error_msg)
        return json.dumps({"error": error_msg})

def main():
    """Main entry point for the MCP server."""
    import asyncio
    
    async def run_server():
        await wikijs.authenticate()
        logger.info("Wiki.js MCP Server started")
        
    # Run the server
    mcp.run()

if __name__ == "__main__":
    main() 