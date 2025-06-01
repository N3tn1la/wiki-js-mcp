# Deletion Tools Documentation

## Overview

The Wiki.js MCP server includes **comprehensive deletion tools** for managing pages and hierarchies. These tools provide safe, flexible options for cleaning up documentation, reorganizing content, and maintaining your Wiki.js instance.

## 🛡️ Safety Features

All deletion tools include **built-in safety mechanisms**:
- **Confirmation required**: `confirm_deletion=True` must be explicitly set
- **Preview mode**: See what will be deleted before confirming
- **Detailed reporting**: Know exactly what was deleted or failed
- **File mapping cleanup**: Automatically clean up orphaned database entries

## 🗑️ Deletion Tools (4 Total)

### 1. `wikijs_delete_page`
Delete a specific page from Wiki.js.

**Usage:**
```python
# Delete by page ID
await wikijs_delete_page(page_id=123)

# Delete by page path
await wikijs_delete_page(page_path="frontend-app/components/button")

# Keep file mappings (don't clean up database)
await wikijs_delete_page(page_id=123, remove_file_mapping=False)
```

**Returns:**
```json
{
  "deleted": true,
  "pageId": 123,
  "title": "Button Component",
  "path": "frontend-app/components/button",
  "status": "deleted",
  "file_mapping_removed": true
}
```

### 2. `wikijs_batch_delete_pages`
Delete multiple pages with flexible selection criteria.

**Selection Methods:**

**By Page IDs:**
```python
await wikijs_batch_delete_pages(
    page_ids=[123, 124, 125],
    confirm_deletion=True
)
```

**By Page Paths:**
```python
await wikijs_batch_delete_pages(
    page_paths=["frontend-app/old-component", "backend-api/deprecated"],
    confirm_deletion=True
)
```

**By Pattern Matching:**
```python
# Delete all pages under frontend-app
await wikijs_batch_delete_pages(
    path_pattern="frontend-app/*",
    confirm_deletion=True
)

# Delete all test pages
await wikijs_batch_delete_pages(
    path_pattern="*test*",
    confirm_deletion=True
)
```

**Safety Check (Preview Mode):**
```python
# Preview what would be deleted (safe - won't actually delete)
result = await wikijs_batch_delete_pages(
    path_pattern="frontend-app/*",
    confirm_deletion=False  # Safety check
)
# Returns: {"error": "confirm_deletion must be True...", "safety_note": "..."}
```

**Returns:**
```json
{
  "total_found": 5,
  "deleted_count": 4,
  "failed_count": 1,
  "deleted_pages": [
    {"pageId": 123, "title": "Button", "path": "frontend-app/button"},
    {"pageId": 124, "title": "Modal", "path": "frontend-app/modal"}
  ],
  "failed_deletions": [
    {"pageId": 125, "title": "Protected", "path": "frontend-app/protected", "error": "Access denied"}
  ],
  "status": "completed"
}
```

### 3. `wikijs_delete_hierarchy`
Delete entire page hierarchies (folder structures) with precise control.

**Deletion Modes:**

**Children Only** (default):
```python
# Delete all child pages but keep the root page
await wikijs_delete_hierarchy(
    root_path="frontend-app",
    delete_mode="children_only",
    confirm_deletion=True
)
```

**Include Root**:
```python
# Delete the entire hierarchy including the root page
await wikijs_delete_hierarchy(
    root_path="frontend-app",
    delete_mode="include_root",
    confirm_deletion=True
)
```

**Root Only**:
```python
# Delete only the root page, leave children orphaned
await wikijs_delete_hierarchy(
    root_path="frontend-app",
    delete_mode="root_only",
    confirm_deletion=True
)
```

**Preview Mode:**
```python
# Preview hierarchy deletion (safe)
result = await wikijs_delete_hierarchy(
    root_path="frontend-app",
    delete_mode="include_root",
    confirm_deletion=False
)
# Returns preview with safety warnings
```

**Returns:**
```json
{
  "root_path": "frontend-app",
  "delete_mode": "children_only",
  "total_found": 8,
  "deleted_count": 7,
  "failed_count": 1,
  "deleted_pages": [
    {"pageId": 124, "title": "Button", "path": "frontend-app/components/button", "depth": 2},
    {"pageId": 125, "title": "Modal", "path": "frontend-app/components/modal", "depth": 2}
  ],
  "failed_deletions": [],
  "hierarchy_summary": {
    "root_page_found": true,
    "child_pages_found": 8,
    "max_depth": 3
  },
  "status": "completed"
}
```

### 4. `wikijs_cleanup_orphaned_mappings`
Clean up file-to-page mappings for pages that no longer exist.

**Usage:**
```python
# Clean up orphaned mappings
await wikijs_cleanup_orphaned_mappings()
```

**Returns:**
```json
{
  "total_mappings": 25,
  "valid_mappings": 22,
  "orphaned_mappings": 3,
  "cleaned_count": 3,
  "orphaned_details": [
    {"file_path": "src/deleted-component.tsx", "page_id": 999, "last_updated": "2024-01-15T10:30:00Z"},
    {"file_path": "src/old-util.ts", "page_id": 998, "error": "Page not found"}
  ],
  "status": "completed"
}
```

## 🎯 Common Use Cases

### 1. Clean Up Test Documentation
```python
# Remove all test pages
await wikijs_batch_delete_pages(
    path_pattern="*test*",
    confirm_deletion=True
)
```

### 2. Remove Deprecated Project
```python
# Delete entire project hierarchy
await wikijs_delete_hierarchy(
    root_path="old-mobile-app",
    delete_mode="include_root",
    confirm_deletion=True
)
```

### 3. Reorganize Documentation Structure
```python
# Step 1: Preview what will be affected
preview = await wikijs_delete_hierarchy(
    root_path="frontend-app/old-structure",
    delete_mode="children_only",
    confirm_deletion=False
)

# Step 2: Delete old structure
await wikijs_delete_hierarchy(
    root_path="frontend-app/old-structure",
    delete_mode="children_only", 
    confirm_deletion=True
)

# Step 3: Clean up orphaned mappings
await wikijs_cleanup_orphaned_mappings()
```

### 4. Bulk Cleanup by Pattern
```python
# Remove all draft pages
await wikijs_batch_delete_pages(
    path_pattern="*draft*",
    confirm_deletion=True
)

# Remove all pages from a specific author/date
await wikijs_batch_delete_pages(
    path_pattern="temp-*",
    confirm_deletion=True
)
```

### 5. Maintenance Operations
```python
# Regular cleanup of orphaned mappings
cleanup_result = await wikijs_cleanup_orphaned_mappings()
print(f"Cleaned up {cleanup_result['cleaned_count']} orphaned mappings")

# Remove specific outdated pages
await wikijs_batch_delete_pages(
    page_paths=[
        "old-api/v1/endpoints",
        "deprecated/legacy-components",
        "archive/old-docs"
    ],
    confirm_deletion=True
)
```

## 🔒 Safety Best Practices

### 1. Always Preview First
```python
# GOOD: Preview before deleting
preview = await wikijs_delete_hierarchy("important-docs", confirm_deletion=False)
print(f"Would delete {preview.get('total_found', 0)} pages")

# Then confirm if safe
if input("Proceed? (y/N): ").lower() == 'y':
    await wikijs_delete_hierarchy("important-docs", confirm_deletion=True)
```

### 2. Use Specific Patterns
```python
# GOOD: Specific pattern
await wikijs_batch_delete_pages(path_pattern="test-project/temp/*", confirm_deletion=True)

# DANGEROUS: Too broad
# await wikijs_batch_delete_pages(path_pattern="*", confirm_deletion=True)  # DON'T DO THIS
```

### 3. Check Results
```python
result = await wikijs_batch_delete_pages(
    path_pattern="old-docs/*",
    confirm_deletion=True
)

print(f"Deleted: {result['deleted_count']}")
print(f"Failed: {result['failed_count']}")

# Check for failures
if result['failed_deletions']:
    print("Failed deletions:")
    for failure in result['failed_deletions']:
        print(f"  - {failure['title']}: {failure['error']}")
```

### 4. Regular Maintenance
```python
# Weekly cleanup routine
async def weekly_cleanup():
    # Clean up orphaned mappings
    cleanup = await wikijs_cleanup_orphaned_mappings()
    print(f"Cleaned {cleanup['cleaned_count']} orphaned mappings")
    
    # Remove temp/test pages
    temp_cleanup = await wikijs_batch_delete_pages(
        path_pattern="temp-*",
        confirm_deletion=True
    )
    print(f"Removed {temp_cleanup['deleted_count']} temp pages")
```

## ⚠️ Important Notes

### Deletion Order
- **Hierarchy deletion** processes pages from deepest to shallowest to avoid dependency issues
- **Child pages are deleted before parent pages** automatically
- **Failed deletions** are reported with specific error messages

### File Mappings
- **Automatic cleanup**: File-to-page mappings are removed by default when pages are deleted
- **Manual control**: Set `remove_file_mappings=False` to preserve mappings
- **Orphaned cleanup**: Use `wikijs_cleanup_orphaned_mappings()` for maintenance

### Pattern Matching
- **Supports wildcards**: Use `*` for pattern matching (e.g., `"frontend-*"`, `"*test*"`)
- **Case sensitive**: Patterns match exactly as written
- **Path-based**: Patterns match against the full page path

### Error Handling
- **Graceful failures**: Individual page deletion failures don't stop batch operations
- **Detailed reporting**: All failures are logged with specific error messages
- **Partial success**: Operations can succeed partially with detailed results

## 🧪 Testing

All deletion tools have been thoroughly tested:
- ✅ Single page deletion
- ✅ Batch deletion with safety checks
- ✅ Pattern-based deletion
- ✅ Hierarchy deletion modes
- ✅ Orphaned mappings cleanup
- ✅ File mapping integration
- ✅ Error handling and reporting

The tools are **production-ready** and safe for enterprise use with proper confirmation procedures. 