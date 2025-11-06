# Vault Index Schema Documentation

## Overview

The Enhanced OMAi Vault Indexer creates a structured JSON index of vault documents with rich metadata, section extraction, and intelligent deduplication. This document describes the schema and features of the vault index system.

## Schema Structure

### Root Level

```json
{
  "metadata": {...},
  "documents": [...],
  "duplicates": [...],
  "skipped": [...]
}
```

#### metadata
Contains indexing metadata and statistics.

| Field | Type | Description |
|-------|------|-------------|
| `indexed_at` | string | ISO timestamp when index was created |
| `processing_time_seconds` | number | Time taken to create the index |
| `total_documents` | number | Total documents successfully indexed |
| `duplicates_found` | number | Number of duplicates detected |
| `skipped_files` | number | Number of files skipped |
| `source_directory` | string | Source directory path |
| `extensions_supported` | array | List of file extensions processed |

#### documents
Array of indexed documents with enhanced metadata.

#### duplicates
Array of duplicate file information. Each entry is a tuple of `[path, reason]`.

#### skipped
Array of skipped file information. Each entry is a tuple of `[path, reason]`.

## Document Schema

Each document in the `documents` array contains the following fields:

### Core Fields

| Field | Type | Description |
|-------|------|-------------|
| `title` | string | Document title extracted from heading or filename |
| `path` | string | Relative path from source directory |
| `full_path` | string | Absolute file path |
| `content` | string | Full document content |
| `content_sha256` | string | SHA256 hash of content for deduplication |

### Enhanced Fields

| Field | Type | Description |
|-------|------|-------------|
| `sections` | array | Extracted document sections (headings, code blocks, tables) |
| `tables` | array | Structured table data |
| `weight` | number | Search ranking weight based on content type |
| `tags` | array | Extracted tags from content and frontmatter |
| `frontmatter` | object | Parsed YAML frontmatter |
| `created_at` | string | File creation timestamp |
| `modified_at` | string | File modification timestamp |
| `word_count` | number | Total word count in document |
| `char_count` | number | Total character count in document |
| `is_private` | boolean | Privacy flag (should always be false for indexed docs) |

## Section Schema

Each section in the `sections` array represents a structured component of the document:

| Field | Type | Description |
|-------|------|-------------|
| `type` | string | Section type: "heading", "code", "table", "paragraph" |
| `title` | string \| null | Section title (for headings) |
| `level` | number \| null | Heading level (1-6) or null |
| `content` | string | Section content |
| `language` | string \| null | Programming language for code blocks |
| `rows` | number | Number of rows (for tables) |
| `metadata` | object | Additional section-specific metadata |

### Section Types

#### Heading Sections
- `type`: "heading"
- `title`: Heading text
- `level`: 1-6 (H1-H6)
- `metadata.level`: Heading level

#### Code Sections
- `type`: "code"
- `language`: Programming language identifier
- `metadata.language`: Language identifier

#### Table Sections
- `type`: "table"
- `rows`: Number of data rows
- `metadata`: Complete table structure with headers and rows

## Table Schema

Each table in the `tables` array contains structured table data:

| Field | Type | Description |
|-------|------|-------------|
| `headers` | array | Column headers |
| `rows` | array | Data rows as objects with header keys |
| `row_count` | number | Number of data rows |
| `column_count` | number | Number of columns |

Example:
```json
{
  "headers": ["Parameter", "Value", "Notes"],
  "rows": [
    {"Parameter": "Model", "Value": "gpt-4", "Notes": "Base model"},
    {"Parameter": "Epochs", "Value": "10", "Notes": "Standard training"}
  ],
  "row_count": 2,
  "column_count": 3
}
```

## Weighting System

The indexing system automatically assigns weights to documents based on their content type and metadata:

### Default Weights

| Content Type | Weight | Examples |
|--------------|--------|----------|
| training-log | 2.0 | Training session notes, model performance logs |
| training_log | 2.0 | Alternative format |
| procedure | 1.8 | System procedures, operational guides |
| procedures | 1.8 | Multiple procedures |
| guide | 1.5 | User guides, tutorials |
| manual | 1.5 | Technical manuals |
| reference | 1.3 | API references, documentation |
| default | 1.0 | All other content |

### Weight Calculation Rules

1. **Frontmatter Weight**: If `weight` is specified in frontmatter, it takes precedence
2. **Content-Based**: Keywords in title or content trigger higher weights
3. **Tag-Based**: Tags in frontmatter can also influence weight
4. **Maximum Priority**: Highest applicable weight is used

## Deduplication System

The indexer implements content-based deduplication using two methods:

### Content Hash Deduplication
- Uses SHA256 hash of full document content
- Identifies exact duplicates regardless of filename
- Reports as: `content_duplicate_of_[original_path]`

### Title Deduplication
- Normalizes titles to lowercase and removes whitespace
- Identifies documents with identical titles
- Reports as: `title_duplicate_of_[original_path]`

## Privacy Filtering

The privacy filter prevents indexing of sensitive content through multiple mechanisms:

### Privacy Markers
- **Frontmatter**: `private: true`
- **Tags**: `#private`, `#secret`, `#draft` (configurable)
- **Path patterns**: `.private/`, `_private/`, `/Private/` (configurable)
- **Filename prefixes**: Files starting with `_` (except `_index.md`)

### Environmental Configuration
```bash
OMAI_IGNORE_TAGS="private,secret,draft"
OMAI_IGNORE_PATHS=".trash,.private,_private,/Private/,/Archive/_ignore"
```

## File Format Support

### Supported Extensions
- `.md` - Markdown files
- `.markdown` - Markdown files
- `.txt` - Plain text files
- `.json` - JSON files
- `.yaml` - YAML files

### Extraction Capabilities

#### Markdown Files
- Headings (H1-H6)
- Code blocks with language detection
- Tables with structured parsing
- YAML frontmatter
- Hashtag tags

#### JSON/YAML Files
- Basic content indexing
- Structure preserved in content field

## Usage Examples

### Query Training Logs
```python
# Find high-weight training documents
training_docs = [
    doc for doc in index['documents']
    if doc['weight'] >= 2.0 and 'training' in doc['title'].lower()
]
```

### Extract Code Examples
```python
# Find all Python code blocks
python_code = [
    section for doc in index['documents']
    for section in doc['sections']
    if section['type'] == 'code' and section['language'] == 'python'
]
```

### Search Tables
```python
# Find documents with specific table headers
docs_with_metrics = [
    doc for doc in index['documents']
    if any('metric' in table['headers'][0].lower() for table in doc['tables'])
]
```

## Index Maintenance

### Re-indexing
```bash
# Re-index entire vault
python vault_indexer.py --verbose

# Index specific directory
python vault_indexer.py --source /path/to/docs --output index.json
```

### Performance Considerations
- Content hashing provides O(1) duplicate detection
- Section extraction is performed once during indexing
- Large files are processed efficiently with streaming
- Memory usage scales with document count, not content size

## Error Handling

### Skipped Files
Files may be skipped for various reasons:
- `unsupported_extension` - File type not supported
- `private_tagged` - Contains privacy markers
- `unreadable` - Cannot read file content
- `processing_error` - Error during processing

### Duplicate Detection
Duplicates are tracked but not included in the main document index to ensure clean search results.

## Integration with OMAi

The vault index is designed to integrate seamlessly with OMAi components:

- **RAG Systems**: Use structured sections for better context retrieval
- **Search**: Weighted ranking prioritizes training logs and procedures
- **Query Processing**: Table data enables structured queries
- **Content Filtering**: Privacy filtering ensures secure content delivery

## Schema Version

Current schema version: **1.0**

Future versions will maintain backward compatibility and follow semantic versioning principles.