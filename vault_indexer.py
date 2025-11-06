#!/usr/bin/env python3
"""
Enhanced OMAi Vault Indexer

Features:
- SHA256-based deduplication by title and content
- Section extraction (headings, code blocks, tables)
- Field weighting for training-log and procedures
- Enhanced privacy filtering
- Rich schema with structured data extraction
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple, Any
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Configuration
DEFAULT_SOURCE = Path("codex_root/vault")
DEFAULT_OUTPUT = Path("data/vault_index.json")
DEFAULT_EXTENSIONS = {".md", ".markdown", ".txt", ".json", ".yaml"}

# Privacy configuration
IGNORE_TAGS = {
    t.strip().lower()
    for t in os.getenv("OMAI_IGNORE_TAGS", "private,secret,draft").split(",")
    if t.strip()
}
IGNORE_PATHS = [
    p.strip()
    for p in os.getenv("OMAI_IGNORE_PATHS", ".trash,.private,_private,/Private/,/Archive/_ignore").split(",")
    if p.strip()
]

# Weighting configuration
WEIGHT_CONFIG = {
    "training-log": 2.0,
    "training_log": 2.0,
    "procedure": 1.8,
    "procedures": 1.8,
    "guide": 1.5,
    "manual": 1.5,
    "reference": 1.3,
    "default": 1.0
}

# Regex patterns
FRONTMATTER_RE = re.compile(r'^---\n(.*?)\n---\n', re.DOTALL)
HEADING_RE = re.compile(r'^(#{1,6})\s+(.+)$', re.MULTILINE)
CODE_BLOCK_RE = re.compile(r'```(\w+)?\n(.*?)\n```', re.DOTALL)
TABLE_RE = re.compile(r'^\|(.+)\|\s*$\n^\|[-:\s|]+\|\s*$\n((?:^\|.+\|\s*$\n?)*)', re.MULTILINE)
INLINE_CODE_RE = re.compile(r'`([^`]+)`')
LINK_RE = re.compile(r'\[([^\]]+)\]\(([^)]+)\)')

@dataclass
class Section:
    """Represents a section within a document."""
    type: str  # heading, code, table, paragraph
    title: Optional[str] = None
    level: Optional[int] = None  # For headings
    content: str = ""
    language: Optional[str] = None  # For code blocks
    rows: int = 0  # For tables
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class VaultDocument:
    """Enhanced document representation with rich metadata."""
    title: str
    path: str
    full_path: str
    content: str
    content_sha256: str
    sections: List[Section] = field(default_factory=list)
    tables: List[Dict[str, Any]] = field(default_factory=list)
    weight: float = 1.0
    tags: List[str] = field(default_factory=list)
    frontmatter: Dict[str, Any] = field(default_factory=dict)
    created_at: Optional[str] = None
    modified_at: Optional[str] = None
    word_count: int = 0
    char_count: int = 0
    is_private: bool = False

@dataclass
class VaultIndex:
    """Enhanced vault index with deduplication and rich metadata."""
    documents: List[VaultDocument] = field(default_factory=list)
    duplicates: List[Tuple[str, str]] = field(default_factory=list)  # (path, reason)
    skipped: List[Tuple[str, str]] = field(default_factory=list)  # (path, reason)
    metadata: Dict[str, Any] = field(default_factory=dict)

class EnhancedVaultIndexer:
    """Enhanced vault indexer with deduplication and rich field extraction."""

    def __init__(
        self,
        source: Path,
        *,
        extensions: Optional[Set[str]] = None,
        ignore_tags: Optional[Set[str]] = None,
        ignore_paths: Optional[List[str]] = None,
    ) -> None:
        self.source = source
        self.extensions = extensions or DEFAULT_EXTENSIONS
        self.ignore_tags = ignore_tags or IGNORE_TAGS
        self.ignore_paths = ignore_paths or IGNORE_PATHS
        self.content_hashes: Dict[str, str] = {}  # sha256 -> path
        self.titles: Dict[str, str] = {}  # title -> path

    def index_vault(self) -> VaultIndex:
        """Index the vault with enhanced processing."""
        index = VaultIndex()
        start_time = datetime.now()

        if not self.source.exists():
            logger.error(f"Source directory does not exist: {self.source}")
            index.skipped.append((str(self.source), "missing_source"))
            return index

        logger.info(f"Starting vault indexing from: {self.source}")

        for path in sorted(self.source.rglob("*")):
            if not path.is_file():
                continue

            if not self._is_supported(path):
                index.skipped.append((str(path), "unsupported_extension"))
                continue

            if self._is_private(path):
                index.skipped.append((str(path), "private_tagged"))
                continue

            try:
                doc = self._process_document(path)
                if doc:
                    # Check for duplicates
                    dup_reason = self._check_duplicates(doc)
                    if dup_reason:
                        index.duplicates.append((doc.path, dup_reason))
                        logger.info(f"Duplicate found: {doc.path} - {dup_reason}")
                        continue

                    index.documents.append(doc)
                    logger.info(f"Indexed: {doc.path} (sections: {len(doc.sections)}, tables: {len(doc.tables)})")

            except Exception as e:
                logger.error(f"Error processing {path}: {e}")
                index.skipped.append((str(path), f"processing_error: {e}"))

        # Calculate final metadata
        end_time = datetime.now()
        index.metadata = {
            "indexed_at": end_time.isoformat(),
            "processing_time_seconds": (end_time - start_time).total_seconds(),
            "total_documents": len(index.documents),
            "duplicates_found": len(index.duplicates),
            "skipped_files": len(index.skipped),
            "source_directory": str(self.source),
            "extensions_supported": list(self.extensions)
        }

        logger.info(f"Indexing complete: {len(index.documents)} documents, {len(index.duplicates)} duplicates, {len(index.skipped)} skipped")
        return index

    def _process_document(self, path: Path) -> Optional[VaultDocument]:
        """Process a single document and extract rich metadata."""
        try:
            content = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            return None

        # Extract title
        title = self._extract_title(content, path)

        # Calculate content hash
        content_hash = hashlib.sha256(content.encode("utf-8")).hexdigest()

        # Extract frontmatter
        frontmatter = self._extract_frontmatter(content)

        # Extract sections and tables
        sections, tables = self._extract_sections_and_tables(content)

        # Calculate weight
        weight = self._calculate_weight(title, content, frontmatter)

        # Get file stats
        stat = path.stat()
        created_at = datetime.fromtimestamp(stat.st_ctime).isoformat()
        modified_at = datetime.fromtimestamp(stat.st_mtime).isoformat()

        # Extract tags
        tags = self._extract_tags(content, frontmatter)

        # Count words and characters
        word_count = len(content.split())
        char_count = len(content)

        return VaultDocument(
            title=title,
            path=str(path.relative_to(self.source)),
            full_path=str(path),
            content=content,
            content_sha256=content_hash,
            sections=sections,
            tables=tables,
            weight=weight,
            tags=tags,
            frontmatter=frontmatter,
            created_at=created_at,
            modified_at=modified_at,
            word_count=word_count,
            char_count=char_count,
            is_private=False
        )

    def _extract_title(self, content: str, path: Path) -> str:
        """Extract title from content or use filename."""
        # Try to find first heading
        heading_match = HEADING_RE.search(content)
        if heading_match:
            return heading_match.group(2).strip()

        # Try frontmatter title
        frontmatter = self._extract_frontmatter(content)
        if "title" in frontmatter:
            return str(frontmatter["title"])

        # Use filename
        return path.stem.replace("_", " ").replace("-", " ").title()

    def _extract_frontmatter(self, content: str) -> Dict[str, Any]:
        """Extract YAML frontmatter from content."""
        match = FRONTMATTER_RE.match(content)
        if not match:
            return {}

        try:
            fm_text = match.group(1)
            # Simple YAML parsing (for basic key-value pairs)
            frontmatter = {}
            for line in fm_text.split("\n"):
                if ":" in line and not line.strip().startswith("#"):
                    key, value = line.split(":", 1)
                    key = key.strip()
                    value = value.strip()

                    # Handle boolean values
                    if value.lower() in ["true", "false"]:
                        value = value.lower() == "true"
                    # Handle numeric values
                    elif value.isdigit():
                        value = int(value)
                    # Remove quotes from string values
                    elif value.startswith('"') and value.endswith('"'):
                        value = value[1:-1]
                    elif value.startswith("'") and value.endswith("'"):
                        value = value[1:-1]

                    frontmatter[key] = value

            return frontmatter
        except Exception:
            return {}

    def _extract_sections_and_tables(self, content: str) -> Tuple[List[Section], List[Dict[str, Any]]]:
        """Extract sections (headings, code blocks) and tables from content."""
        sections = []
        tables = []

        # Extract headings
        for match in HEADING_RE.finditer(content):
            level = len(match.group(1))
            title = match.group(2).strip()
            sections.append(Section(
                type="heading",
                title=title,
                level=level,
                content=match.group(0),
                metadata={"level": level}
            ))

        # Extract code blocks
        for match in CODE_BLOCK_RE.finditer(content):
            language = match.group(1) or "text"
            code = match.group(2)
            sections.append(Section(
                type="code",
                language=language,
                content=code,
                metadata={"language": language}
            ))

        # Extract tables
        for match in TABLE_RE.finditer(content):
            table_content = match.group(0)

            # Parse table structure
            lines = [line.strip() for line in table_content.split('\n') if line.strip()]
            if len(lines) >= 3:
                # Parse header
                header_line = lines[0]
                headers = [h.strip() for h in header_line.split('|')[1:-1] if h.strip()]

                # Parse data rows
                data_rows = []
                for line in lines[2:]:  # Skip separator line
                    if line.startswith('|') and line.endswith('|'):
                        cells = [c.strip() for c in line.split('|')[1:-1] if c.strip()]
                        if len(cells) >= len(headers):
                            # Pad cells if fewer than headers
                            while len(cells) < len(headers):
                                cells.append('')
                            data_rows.append(dict(zip(headers, cells)))

                if data_rows and headers:
                    table_data = {
                        "headers": headers,
                        "rows": data_rows,
                        "row_count": len(data_rows),
                        "column_count": len(headers)
                    }
                    tables.append(table_data)

                    sections.append(Section(
                        type="table",
                        content=table_content,
                        rows=len(data_rows),
                        metadata=table_data
                    ))

        return sections, tables

    def _calculate_weight(self, title: str, content: str, frontmatter: Dict[str, Any]) -> float:
        """Calculate document weight based on content and metadata."""
        # Start with default weight
        weight = WEIGHT_CONFIG["default"]

        # Check title and content for weight indicators
        title_lower = title.lower()
        content_lower = content.lower()

        for keyword, keyword_weight in WEIGHT_CONFIG.items():
            if keyword != "default":
                if keyword in title_lower or keyword in content_lower:
                    weight = max(weight, keyword_weight)

        # Check frontmatter for weight indicators
        if "weight" in frontmatter:
            try:
                weight = float(frontmatter["weight"])
            except (ValueError, TypeError):
                pass

        # Check tags in frontmatter
        if "tags" in frontmatter:
            tags = frontmatter["tags"]
            if isinstance(tags, list):
                for tag in tags:
                    tag_lower = str(tag).lower()
                    for keyword, keyword_weight in WEIGHT_CONFIG.items():
                        if keyword != "default" and keyword in tag_lower:
                            weight = max(weight, keyword_weight)

        return weight

    def _extract_tags(self, content: str, frontmatter: Dict[str, Any]) -> List[str]:
        """Extract tags from content and frontmatter."""
        tags = set()

        # Extract from frontmatter
        if "tags" in frontmatter:
            if isinstance(frontmatter["tags"], list):
                tags.update(str(tag) for tag in frontmatter["tags"])
            elif isinstance(frontmatter["tags"], str):
                tags.update(tag.strip() for tag in frontmatter["tags"].split(","))

        # Extract from content (hashtags)
        hashtag_pattern = r'#([a-zA-Z0-9_-]+)'
        content_tags = re.findall(hashtag_pattern, content)
        tags.update(content_tags)

        return list(tags)

    def _check_duplicates(self, doc: VaultDocument) -> Optional[str]:
        """Check for duplicates based on title and content hash."""
        # Check content hash duplicate
        if doc.content_sha256 in self.content_hashes:
            return f"content_duplicate_of_{self.content_hashes[doc.content_sha256]}"

        # Check title duplicate
        title_key = doc.title.lower().strip()
        if title_key in self.titles:
            return f"title_duplicate_of_{self.titles[title_key]}"

        # Register for future duplicate checks
        self.content_hashes[doc.content_sha256] = doc.path
        self.titles[title_key] = doc.path

        return None

    def _is_supported(self, path: Path) -> bool:
        """Check if file extension is supported."""
        return path.suffix.lower() in self.extensions

    def _is_private(self, path: Path) -> bool:
        """Enhanced privacy checking."""
        # Check path patterns
        if self._looks_private_path(str(path)):
            return True

        # Check filename
        name_lower = path.name.lower()
        if any(f"#{tag}" in name_lower or tag in name_lower for tag in self.ignore_tags):
            return True

        # Check file content
        try:
            content = path.read_text(encoding="utf-8")

            # Check frontmatter
            if self._has_private_frontmatter(content):
                return True

            # Check content for privacy tags
            content_lower = content.lower()
            if any(f"#{tag}" in content_lower for tag in self.ignore_tags):
                return True

        except UnicodeDecodeError:
            return True
        except OSError:
            return True

        return False

    def _looks_private_path(self, path_str: str) -> bool:
        """Check if path matches privacy patterns."""
        lower = path_str.lower()

        # Check directory markers
        for pattern in ["/.trash/", "/.private/", "/_private/", "/private/"]:
            if pattern in lower:
                return True

        # Check filename prefix
        name = Path(path_str).name.lower()
        if name.startswith("_") and name != "_index.md":
            return True

        # Check custom ignore patterns
        for pattern in self.ignore_paths:
            if pattern and pattern.lower() in lower:
                return True

        return False

    def _has_private_frontmatter(self, content: str) -> bool:
        """Check if frontmatter contains private markers."""
        match = FRONTMATTER_RE.match(content)
        if not match:
            return False

        try:
            fm_text = match.group(1).lower()
            if "private:" in fm_text:
                for line in fm_text.split("\n"):
                    if line.strip().startswith("private:"):
                        value = line.split(":", 1)[1].strip()
                        return value in ["true", "yes", "1"]
        except Exception:
            pass

        return False

def write_index(index: VaultIndex, output_path: Path) -> None:
    """Write vault index to JSON file."""
    # Convert to dict for JSON serialization
    index_dict = {
        "metadata": index.metadata,
        "documents": [
            {
                "title": doc.title,
                "path": doc.path,
                "full_path": doc.full_path,
                "content": doc.content,
                "content_sha256": doc.content_sha256,
                "sections": [
                    {
                        "type": sec.type,
                        "title": sec.title,
                        "level": sec.level,
                        "content": sec.content,
                        "language": sec.language,
                        "rows": sec.rows,
                        "metadata": sec.metadata
                    } for sec in doc.sections
                ],
                "tables": doc.tables,
                "weight": doc.weight,
                "tags": doc.tags,
                "frontmatter": doc.frontmatter,
                "created_at": doc.created_at,
                "modified_at": doc.modified_at,
                "word_count": doc.word_count,
                "char_count": doc.char_count,
                "is_private": doc.is_private
            } for doc in index.documents
        ],
        "duplicates": index.duplicates,
        "skipped": index.skipped
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(index_dict, indent=2, ensure_ascii=False), encoding="utf-8")
    logger.info(f"Vault index written to: {output_path}")

def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Enhanced OMAi Vault Indexer")
    parser.add_argument(
        "--source",
        type=Path,
        default=DEFAULT_SOURCE,
        help="Directory to scan for vault documents."
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help="Output path for vault index JSON."
    )
    parser.add_argument(
        "--extensions",
        nargs="*",
        default=None,
        help="File extensions to include."
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging."
    )
    return parser.parse_args()

def main() -> None:
    """Main entry point."""
    args = parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    extensions = set(args.extensions) if args.extensions else None

    indexer = EnhancedVaultIndexer(
        source=args.source,
        extensions=extensions
    )

    index = indexer.index_vault()
    write_index(index, args.output)

    print(f"\nVault indexing complete:")
    print(f"  Documents indexed: {len(index.documents)}")
    print(f"  Duplicates found: {len(index.duplicates)}")
    print(f"  Files skipped: {len(index.skipped)}")
    print(f"  Output written to: {args.output}")
    print(f"  Processing time: {index.metadata.get('processing_time_seconds', 0):.2f}s")

if __name__ == "__main__":
    main()