#!/usr/bin/env python3
"""
archive_fetcher.py - Internet Archive content fetcher

Fetches public domain and openly licensed content from the Internet Archive.
Respects licensing and only fetches content that is legally accessible.
"""

import asyncio
import aiohttp
import json
import re
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
from urllib.parse import urlencode, quote

from .base_fetcher import BaseFetcher


class ArchiveFetcher(BaseFetcher):
    """Internet Archive content fetcher"""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.archive_api = "https://archive.org/advancedsearch.php"
        self.archive_metadata = "https://archive.org/metadata"
        self.archive_download = "https://archive.org/download"

    async def _fetch_impl(self, query: str, max_items: int) -> List[Dict[str, Any]]:
        """Fetch Internet Archive content"""
        results = []

        try:
            # Search for items using Internet Archive API
            items = await self._search_items(query, max_items)

            for item in items:
                try:
                    result = await self._process_archive_item(item)
                    if result:
                        results.append(result)
                except Exception as e:
                    self.logger.error(f"Error processing Archive item {item.get('identifier')}: {e}")

        except Exception as e:
            self.logger.error(f"Error fetching Internet Archive content: {e}")

        return results

    async def _search_items(self, query: str, max_items: int) -> List[Dict[str, Any]]:
        """Search for items using Internet Archive API"""
        items = []

        # Prepare search parameters
        params = {
            "q": quote(query),
            "fl[]": "identifier,title,creator,date,description,licenseurl,mediatype,language,item_size",
            "output": "json",
            "rows": min(max_items, 100),  # Archive.org limit
            "page": 1,
            # Filter for openly licensed content
            "and": [
                "licenseurl:(* OR publicdomain OR cc-by OR cc-by-sa OR cc0)",
                "-mediatype:(web OR collection)"
            ]
        }

        try:
            # Make request to Internet Archive API
            url = f"{self.archive_api}?{urlencode(params, doseq=True)}"
            response = await self._make_request(url)

            if response and response.status == 200:
                data = await response.json()
                if "response" in data and "docs" in data["response"]:
                    items = data["response"]["docs"]
                    self.logger.info(f"Found {len(items)} Archive items for query: {query}")
            else:
                self.logger.warning(f"Archive API request failed with status: {response.status if response else 'None'}")

        except Exception as e:
            self.logger.error(f"Error searching Archive items: {e}")

        return items

    async def _process_archive_item(self, item: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Process a single Archive item"""
        identifier = item.get("identifier", "")
        if not identifier:
            return None

        try:
            # Get detailed metadata
            metadata = await self._get_item_metadata(identifier)
            if not metadata:
                return None

            # Check if content is accessible and properly licensed
            if not self._is_content_accessible(metadata):
                self.logger.debug(f"Skipping {identifier}: not openly licensed or accessible")
                return None

            # Get the main text file
            text_content = await self._get_text_content(identifier, metadata)
            if not text_content:
                return None

            # Check minimum content length
            if len(text_content.strip()) < self.config.get("min_content_length", 100):
                return None

            # Extract metadata
            title = item.get("title", identifier)
            creator = item.get("creator", [])
            if isinstance(creator, list) and creator:
                author = ", ".join(creator)
            elif isinstance(creator, str):
                author = creator
            else:
                author = None

            date = item.get("date", "")
            publish_date = self._parse_archive_date(date)

            # Build content
            content_parts = [f"# {title}"]

            if author:
                content_parts.append(f"**Author:** {author}")

            if date:
                content_parts.append(f"**Date:** {date}")

            description = item.get("description", "")
            if description:
                content_parts.append(f"\n## Description\n\n{description}")

            content_parts.append(f"\n## Content\n\n{text_content}")

            content = "\n\n".join(content_parts)

            return self._create_result(
                url=f"https://archive.org/details/{identifier}",
                title=title,
                content=content,
                author=author,
                publish_date=publish_date,
                source_type="archive",
                metadata={
                    "identifier": identifier,
                    "mediatype": item.get("mediatype", ""),
                    "language": item.get("language", ""),
                    "item_size": item.get("item_size", 0),
                    "license_url": item.get("licenseurl", ""),
                    "platform": "internet_archive",
                    "content_type": "archived_content"
                }
            )

        except Exception as e:
            self.logger.error(f"Error processing Archive item {identifier}: {e}")
            return None

    async def _get_item_metadata(self, identifier: str) -> Optional[Dict[str, Any]]:
        """Get detailed metadata for an Archive item"""
        try:
            url = f"{self.archive_metadata}/{identifier}"
            response = await self._make_request(url)

            if response and response.status == 200:
                data = await response.json()
                return data

        except Exception as e:
            self.logger.debug(f"Error fetching metadata for {identifier}: {e}")

        return None

    def _is_content_accessible(self, metadata: Dict[str, Any]) -> bool:
        """Check if content is openly licensed and accessible"""
        # Check license
        license_url = metadata.get("metadata", {}).get("licenseurl", "")
        if license_url and not self._is_permissive_license(license_url):
            return False

        # Check if item is dark (restricted)
        if metadata.get("is_dark", False):
            return False

        # Check access restrictions
        metadata_fields = metadata.get("metadata", {})
        if metadata_fields.get("access") == "restricted":
            return False

        # Check for no-index
        if metadata.get("noindex", False):
            return False

        return True

    def _is_permissive_license(self, license_url: str) -> bool:
        """Check if license allows content ingestion"""
        permissive_licenses = [
            "creativecommons.org/licenses/by",
            "creativecommons.org/publicdomain",
            "creativecommons.org/CC0",
            "opensource.org",
            "gnu.org/licenses",
            "rightsstatements.org",
            "public domain"
        ]

        license_lower = license_url.lower()
        return any(license_pattern in license_lower for license_pattern in permissive_licenses)

    async def _get_text_content(self, identifier: str, metadata: Dict[str, Any]) -> Optional[str]:
        """Get text content from Archive item"""
        try:
            # Get file list
            files = metadata.get("files", {})

            # Look for text files in order of preference
            preferred_extensions = [".txt", ".md", ".text", ".html", ".htm"]
            selected_file = None

            # First try to find files with preferred extensions
            for filename, file_info in files.items():
                if any(filename.lower().endswith(ext) for ext in preferred_extensions):
                    if not selected_file or len(filename) < len(selected_file):
                        selected_file = filename

            # If no preferred file found, look for any text-based file
            if not selected_file:
                for filename, file_info in files.items():
                    file_format = file_info.get("format", "").lower()
                    if "text" in file_format or "html" in file_format:
                        selected_file = filename
                        break

            if not selected_file:
                return None

            # Download the selected file
            download_url = f"{self.archive_download}/{identifier}/{selected_file}"
            response = await self._make_request(download_url)

            if response and response.status == 200:
                content = await response.text()

                # Clean up content if it's HTML
                if selected_file.lower().endswith(('.html', '.htm')):
                    content = self._extract_text_from_html(content)

                return content

        except Exception as e:
            self.logger.debug(f"Error getting text content for {identifier}: {e}")

        return None

    def _extract_text_from_html(self, html_content: str) -> str:
        """Extract text content from HTML"""
        # Remove script and style elements
        html_content = re.sub(r'<script[^>]*>.*?</script>', '', html_content, flags=re.DOTALL | re.IGNORECASE)
        html_content = re.sub(r'<style[^>]*>.*?</style>', '', html_content, flags=re.DOTALL | re.IGNORECASE)

        # Remove HTML tags
        text = re.sub(r'<[^>]+>', ' ', html_content)

        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text)
        text = text.strip()

        return text

    def _parse_archive_date(self, date_str: str) -> Optional[str]:
        """Parse date from Archive metadata"""
        if not date_str:
            return None

        try:
            # Try various date formats
            date_formats = [
                "%Y-%m-%d",
                "%Y-%m",
                "%Y",
                "%Y-%m-%d %H:%M:%S",
            ]

            for fmt in date_formats:
                try:
                    parsed_date = datetime.strptime(date_str, fmt)
                    return parsed_date.strftime("%Y-%m-%d")
                except ValueError:
                    continue

        except Exception:
            pass

        return None

    def _detect_archive_license(self, metadata: Dict[str, Any]) -> Optional[str]:
        """Detect license for Archive content"""
        metadata_fields = metadata.get("metadata", {})
        license_url = metadata_fields.get("licenseurl", "")

        if not license_url:
            return "Unknown License"

        # Map known license URLs to standard names
        license_mapping = {
            "creativecommons.org/licenses/by": "CC BY",
            "creativecommons.org/licenses/by-sa": "CC BY-SA",
            "creativecommons.org/licenses/by-nc": "CC BY-NC",
            "creativecommons.org/publicdomain": "Public Domain",
            "creativecommons.org/CC0": "CC0",
            "gnu.org/licenses/gpl": "GPL",
            "opensource.org/licenses/MIT": "MIT",
            "opensource.org/licenses/Apache-2.0": "Apache-2.0",
            "rightsstatements.org/vocab/NoC-US/1.0/": "No Copyright - United States",
        }

        for pattern, license_name in license_mapping.items():
            if pattern in license_url:
                return license_name

        return license_url  # Return URL if mapping not found

    def _create_result(self, url: str, title: str, content: str, **kwargs) -> Dict[str, Any]:
        """Create Archive-specific result"""
        result = super()._create_result(url, title, content, **kwargs)

        # Detect license from metadata
        metadata = kwargs.get("metadata", {})
        result["license"] = "Archive Content"  # Will be updated with specific license

        # Add Archive-specific metadata
        result["metadata"]["platform"] = "internet_archive"
        result["metadata"]["content_type"] = "archived_content"

        # Extract references from content
        result["references"] = self._extract_references(content)

        return result