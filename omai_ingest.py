#!/usr/bin/env python3
"""
omai_ingest.py

Utility for collecting project knowledge artifacts for OMAi components.
Skips any file that is tagged with ``#private`` so sensitive material
is not surfaced during ingestion runs.

Enhanced privacy filtering:
- Frontmatter: private: true
- Tags: #private, #secret, #draft (configurable via OMAI_IGNORE_TAGS)
- Paths: .private/, _private/, /Private/ (configurable via OMAI_IGNORE_PATHS)
"""

from __future__ import annotations

import argparse
import json
import os
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple, Set


DEFAULT_SOURCE = Path("codex_root/vault")
DEFAULT_OUTPUT = Path("codex_root/ingest_cache.json")
DEFAULT_EXTENSIONS = {".md", ".markdown", ".txt", ".json", ".yaml"}

# Privacy configuration from environment
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

FRONTMATTER_RE = re.compile(r'^---\n(.*?)\n---\n', re.DOTALL)


@dataclass
class IngestResult:
    """Represents the outcome of an ingestion run."""

    records: List[Dict[str, str]] = field(default_factory=list)
    skipped: List[Tuple[str, str]] = field(default_factory=list)  # (path, reason)


class OMAiIngestor:
    """Collects text artifacts while respecting #private tags and other privacy markers."""

    def __init__(
        self,
        source: Path,
        *,
        ignore_tag: str = "#private",
        extensions: Optional[Iterable[str]] = None,
        ignore_tags: Optional[Set[str]] = None,
        ignore_paths: Optional[List[str]] = None,
    ) -> None:
        self.source = source
        self.ignore_tag = ignore_tag.lower()
        self.extensions = {ext.lower() for ext in (extensions or DEFAULT_EXTENSIONS)}
        self.ignore_tags = ignore_tags or IGNORE_TAGS
        self.ignore_paths = ignore_paths or IGNORE_PATHS

    def ingest(self) -> IngestResult:
        """Traverse the source directory and capture eligible files."""
        result = IngestResult()

        if not self.source.exists():
            result.skipped.append((str(self.source), "missing_source"))
            return result

        for path in sorted(self.source.rglob("*")):
            if not path.is_file():
                continue

            if not self._is_supported(path):
                result.skipped.append((str(path), "unsupported_extension"))
                continue

            if self._is_private(path):
                result.skipped.append((str(path), "private_tagged"))
                continue

            content = self._read_text(path)
            if content is None:
                result.skipped.append((str(path), "unreadable"))
                continue

            result.records.append(
                {
                    "path": str(path.relative_to(self.source)),
                    "full_path": str(path),
                    "content": content,
                }
            )

        return result

    def _is_supported(self, path: Path) -> bool:
        return path.suffix.lower() in self.extensions

    def _is_private(self, path: Path) -> bool:
        """Check if file should be skipped due to privacy markers."""
        # 1. Check path patterns (fastest check first)
        if self._looks_private_path(str(path)):
            return True
        
        # 2. Check filename for basic tag
        tag = self.ignore_tag
        tag_plain = tag.replace("#", "")
        name_lower = path.name.lower()
        if tag in name_lower or tag_plain in name_lower:
            return True

        # 3. Check file content for privacy markers
        try:
            content = path.read_text(encoding="utf-8")
            
            # Check frontmatter for private: true
            if self._has_private_frontmatter(content):
                return True
            
            # Check for privacy tags in content
            content_lower = content.lower()
            if tag in content_lower:
                return True
            
            # Check for additional ignore tags
            for ignore_tag in self.ignore_tags:
                if f"#{ignore_tag}" in content_lower:
                    return True
                    
        except UnicodeDecodeError:
            # If a file cannot be decoded as UTF-8, treat it as private and skip.
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
        if name.startswith("_") and name != "_index.md":  # Allow _index.md
            return True
        
        # Check custom ignore patterns
        for pattern in self.ignore_paths:
            if pattern and pattern.lower() in lower:
                return True
        
        return False
    
    def _has_private_frontmatter(self, content: str) -> bool:
        """Check YAML frontmatter for private: true."""
        match = FRONTMATTER_RE.match(content)
        if not match:
            return False
        
        try:
            # Simple parser - look for "private: true" line
            fm_text = match.group(1).lower()
            if "private:" in fm_text:
                # Check if value is truthy
                for line in fm_text.split("\n"):
                    if line.strip().startswith("private:"):
                        value = line.split(":", 1)[1].strip()
                        if value in ["true", "yes", "1"]:
                            return True
        except Exception:
            pass
        
        return False

    def _read_text(self, path: Path) -> Optional[str]:
        try:
            return path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            return None
        except OSError:
            return None


def write_output(result: IngestResult, output_path: Path) -> None:
    """Serialize ingestion results to disk."""
    payload = {
        "records": result.records,
        "skipped": result.skipped,
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Ingest OMAi knowledge artifacts.")
    parser.add_argument(
        "--source",
        type=Path,
        default=DEFAULT_SOURCE,
        help="Directory to scan for knowledge artifacts.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help="Optional JSON output path for collected records.",
    )
    parser.add_argument(
        "--extensions",
        nargs="*",
        default=None,
        help="Optional list of file extensions to include (defaults to markdown, text, json, yaml).",
    )
    parser.add_argument(
        "--no-write",
        action="store_true",
        help="If set, do not write results to disk; just print summary counts.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    extensions = set(args.extensions) if args.extensions else None

    ingestor = OMAiIngestor(args.source, extensions=extensions)
    result = ingestor.ingest()

    print(f"[omai_ingest] collected={len(result.records)} skipped={len(result.skipped)}")

    if args.no_write:
        return

    write_output(result, args.output)
    print(f"[omai_ingest] wrote payload to {args.output}")


if __name__ == "__main__":
    main()
