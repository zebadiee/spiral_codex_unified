#!/usr/bin/env python3
"""
base_fetcher.py - Base class for all content fetchers

Provides common functionality for ethical content fetching including:
- Rate limiting
- Robots.txt compliance
- License detection
- Error handling
- Metadata extraction
"""

import asyncio
import aiohttp
import re
import time
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any, Tuple
from urllib.parse import urlparse, urljoin
from urllib.robotparser import RobotFileParser
import logging


class BaseFetcher(ABC):
    """Base class for all content fetchers with ethical compliance"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(f"fetcher.{self.__class__.__name__.lower()}")
        self.session: Optional[aiohttp.ClientSession] = None
        self.robots_cache: Dict[str, RobotFileParser] = {}
        self.last_request_time: Dict[str, float] = {}
        self.request_count: Dict[str, int] = {}

    async def __aenter__(self):
        """Async context manager entry"""
        connector = aiohttp.TCPConnector(
            limit=10,
            limit_per_host=5,
            ttl_dns_cache=300,
            use_dns_cache=True,
        )

        timeout = aiohttp.ClientTimeout(
            total=self.config.get("timeout_seconds", 30),
            connect=10
        )

        headers = {
            "User-Agent": "SpiralCodex/1.0 (Educational Research; https://github.com/spiral-codex)",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate",
            "Connection": "keep-alive",
        }

        self.session = aiohttp.ClientSession(
            connector=connector,
            timeout=timeout,
            headers=headers
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()

    async def fetch(self, query: str, max_items: int = 20) -> List[Dict[str, Any]]:
        """Main fetch method - must be implemented by subclasses"""
        async with self:
            return await self._fetch_impl(query, max_items)

    @abstractmethod
    async def _fetch_impl(self, query: str, max_items: int) -> List[Dict[str, Any]]:
        """Implementation-specific fetch logic"""
        pass

    async def _make_request(self, url: str, method: str = "GET", **kwargs) -> Optional[aiohttp.ClientResponse]:
        """Make HTTP request with rate limiting and robots.txt compliance"""
        if not self.session:
            raise RuntimeError("Fetcher must be used as async context manager")

        parsed_url = urlparse(url)
        domain = parsed_url.netloc

        # Check robots.txt
        if self.config.get("respect_robots_txt", True):
            if not await self._can_fetch(url):
                self.logger.warning(f"Robots.txt disallows fetching: {url}")
                return None

        # Apply rate limiting
        await self._apply_rate_limiting(domain)

        try:
            self.logger.debug(f"Requesting {url}")
            response = await self.session.request(method, url, **kwargs)

            # Update request statistics
            self.request_count[domain] = self.request_count.get(domain, 0) + 1

            return response

        except asyncio.TimeoutError:
            self.logger.warning(f"Timeout fetching {url}")
            return None
        except aiohttp.ClientError as e:
            self.logger.warning(f"Client error fetching {url}: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Unexpected error fetching {url}: {e}")
            return None

    async def _can_fetch(self, url: str) -> bool:
        """Check if URL can be fetched according to robots.txt"""
        parsed_url = urlparse(url)
        domain = parsed_url.netloc

        # Check cache first
        if domain in self.robots_cache:
            return self.robots_cache[domain].can_fetch(
                self.session.headers["User-Agent"],
                url
            )

        try:
            # Fetch robots.txt
            robots_url = urljoin(f"{parsed_url.scheme}://{domain}", "/robots.txt")
            response = await self._make_request(robots_url)

            if response and response.status == 200:
                robots_content = await response.text()
                rp = RobotFileParser()
                rp.set_url(robots_url)
                try:
                    rp.parse(robots_content.splitlines())
                except Exception:
                    # If parsing fails, assume we can fetch
                    return True

                self.robots_cache[domain] = rp
                return rp.can_fetch(self.session.headers["User-Agent"], url)
            else:
                # No robots.txt found, assume we can fetch
                rp = RobotFileParser()
                rp.set_url(robots_url)
                rp.allow_all = True
                self.robots_cache[domain] = rp
                return True

        except Exception as e:
            self.logger.warning(f"Error checking robots.txt for {domain}: {e}")
            # If we can't check robots.txt, be conservative and allow fetching
            return True

    async def _apply_rate_limiting(self, domain: str) -> None:
        """Apply rate limiting for domain"""
        now = time.time()
        last_request = self.last_request_time.get(domain, 0)

        delay = self.config.get("rate_limit_delay", 1.0)
        time_since_last = now - last_request

        if time_since_last < delay:
            sleep_time = delay - time_since_last
            self.logger.debug(f"Rate limiting {domain}: sleeping {sleep_time:.2f}s")
            await asyncio.sleep(sleep_time)

        self.last_request_time[domain] = time.time()

    async def _fetch_text_content(self, url: str) -> Optional[str]:
        """Fetch text content from URL"""
        response = await self._make_request(url)
        if not response or response.status != 200:
            return None

        try:
            content_type = response.headers.get("content-type", "").lower()
            if "text/html" in content_type or "text/plain" in content_type:
                return await response.text()
            else:
                self.logger.warning(f"Unsupported content type for {url}: {content_type}")
                return None

        except Exception as e:
            self.logger.error(f"Error reading content from {url}: {e}")
            return None

    def _extract_title(self, content: str, url: str) -> str:
        """Extract title from content"""
        # Try HTML title tag first
        title_match = re.search(r'<title[^>]*>([^<]+)</title>', content, re.IGNORECASE)
        if title_match:
            title = title_match.group(1).strip()
            return self._clean_text(title)

        # Try markdown title
        md_title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
        if md_title_match:
            return self._clean_text(md_title_match.group(1))

        # Use URL as fallback
        return url

    def _extract_publish_date(self, content: str, url: str) -> Optional[str]:
        """Extract publish date from content"""
        # Try various date patterns
        date_patterns = [
            r'(\d{4}-\d{2}-\d{2})',
            r'(\d{1,2}/\d{1,2}/\d{4})',
            r'(\d{4}/\d{1,2}/\d{1,2})',
            r'(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4}',
        ]

        for pattern in date_patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                return match.group(1)

        return None

    def _extract_author(self, content: str, url: str) -> Optional[str]:
        """Extract author from content"""
        # Try HTML meta author
        author_match = re.search(r'<meta[^>]*name=["\']author["\'][^>]*content=["\']([^"\']+)["\']', content, re.IGNORECASE)
        if author_match:
            return self._clean_text(author_match.group(1))

        # Try common author patterns
        author_patterns = [
            r'author[s]?:\s*([^\n\r]+)',
            r'by\s+([^\n\r]+)',
            r'written by\s+([^\n\r]+)',
        ]

        for pattern in author_patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                return self._clean_text(match.group(1))

        return None

    def _extract_references(self, content: str) -> List[str]:
        """Extract references/citations from content"""
        references = []

        # Look for URLs in content
        url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
        urls = re.findall(url_pattern, content)
        references.extend(urls)

        # Look for citation patterns
        citation_patterns = [
            r'\[(\d+)\]',
            r'\((\d{4})\)',
            r'doi:\s*([^\s\n\r]+)',
        ]

        for pattern in citation_patterns:
            matches = re.findall(pattern, content)
            references.extend(matches)

        # Remove duplicates and filter
        references = list(set(references))
        references = [ref for ref in references if len(ref.strip()) > 2]

        return references[:20]  # Limit to 20 references

    def _detect_license(self, content: str, url: str) -> Optional[str]:
        """Detect content license"""
        content_lower = content.lower()
        url_lower = url.lower()

        # Check for common licenses
        license_patterns = {
            "CC BY": r"creative commons attribution|cc by|attribution",
            "CC BY-SA": r"creative commons share-alike|cc by-sa|share alike",
            "CC BY-NC": r"creative commons non-commercial|cc by-nc|non-commercial",
            "CC BY-ND": r"creative commons no-derivatives|cc by-nd|no derivatives",
            "CC0": r"creative commons zero|cc0|public domain dedication",
            "MIT": r"mit license|mit|expat license",
            "Apache-2.0": r"apache license|apache-2\.0|apache 2\.0",
            "GPL": r"gpl|general public license",
            "Public Domain": r"public domain|no rights reserved",
        }

        for license_name, pattern in license_patterns.items():
            if re.search(pattern, content_lower) or re.search(pattern, url_lower):
                return license_name

        return None

    def _clean_text(self, text: str) -> str:
        """Clean text content"""
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', '', text)
        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text)
        # Remove leading/trailing whitespace
        text = text.strip()
        # Unescape HTML entities
        text = text.replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>').replace('&quot;', '"')
        return text

    def _sanitize_content(self, content: str, max_length: int = 1000000) -> str:
        """Sanitize and limit content length"""
        # Remove HTML tags (basic)
        content = re.sub(r'<script[^>]*>.*?</script>', '', content, flags=re.DOTALL | re.IGNORECASE)
        content = re.sub(r'<style[^>]*>.*?</style>', '', content, flags=re.DOTALL | re.IGNORECASE)
        content = re.sub(r'<[^>]+>', ' ', content)

        # Normalize whitespace
        content = re.sub(r'\s+', ' ', content)
        content = content.strip()

        # Limit length
        if len(content) > max_length:
            content = content[:max_length] + "... [truncated]"

        return content

    def _create_result(self, url: str, title: str, content: str, **kwargs) -> Dict[str, Any]:
        """Create standardized result dictionary"""
        return {
            "url": url,
            "title": title,
            "content": content,
            "author": self._extract_author(content, url),
            "publish_date": self._extract_publish_date(content, url),
            "license": self._detect_license(content, url),
            "citation_count": len(self._extract_references(content)),
            "references": self._extract_references(content),
            "word_count": len(content.split()),
            "fetch_method": self.__class__.__name__,
            "robots_txt_respected": self.config.get("respect_robots_txt", True),
            "rate_limit_applied": True,
            "metadata": {
                "fetched_at": datetime.now(timezone.utc).isoformat(),
                "content_length": len(content),
                "domain": urlparse(url).netloc,
            },
            **kwargs
        }

    def _is_public_content(self, content: str, url: str) -> bool:
        """Check if content is publicly accessible"""
        # Skip private/draft indicators
        private_indicators = [
            "#private",
            "#draft",
            "#internal",
            "password protected",
            "login required",
            "access denied",
            "private content",
        ]

        content_lower = content.lower()
        if any(indicator in content_lower for indicator in private_indicators):
            return False

        # Skip common private URL patterns
        private_url_patterns = [
            "/private/",
            "/internal/",
            "/admin/",
            "/draft/",
            "?password",
            "?auth",
        ]

        url_lower = url.lower()
        if any(pattern in url_lower for pattern in private_url_patterns):
            return False

        return True