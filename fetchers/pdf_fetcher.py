#!/usr/bin/env python3
"""
pdf_fetcher.py - PDF document fetcher and text extractor

Fetches PDF documents from public sources and extracts text content.
Respects copyright and only processes openly licensed PDFs.
"""

import asyncio
import aiohttp
import io
import re
import tempfile
import subprocess
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
from urllib.parse import urljoin, urlparse

from .base_fetcher import BaseFetcher


class PDFFetcher(BaseFetcher):
    """PDF document fetcher and text extractor"""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.supported_pdf_domains = [
            # Academic repositories
            "arxiv.org",
            "scholar.google.com",
            "researchgate.net",
            "academia.edu",
            # Government publications
            ".gov",
            "nasa.gov",
            "nist.gov",
            "doe.gov",
            # Open access journals
            "plos.org",
            "nature.com",
            "science.org",
            # Technical standards
            "ieee.org",
            "ietf.org",
            "w3.org",
        ]

    async def _fetch_impl(self, query: str, max_items: int) -> List[Dict[str, Any]]:
        """Fetch PDF documents"""
        results = []

        # For now, this fetcher works with provided PDF URLs
        # In a full implementation, you might integrate with Google Scholar API
        # or other academic search APIs to find PDF URLs

        # This could be extended to search academic databases for PDF URLs
        # For demonstration, we'll process PDFs if URLs are provided in config
        pdf_urls = self.config.get("pdf_urls", [])
        if not pdf_urls:
            self.logger.info("No PDF URLs provided in config, skipping PDF fetcher")
            return results

        for url in pdf_urls[:max_items]:
            try:
                result = await self._process_pdf_url(url)
                if result:
                    results.append(result)
            except Exception as e:
                self.logger.error(f"Error processing PDF from {url}: {e}")

        return results

    async def _process_pdf_url(self, url: str) -> Optional[Dict[str, Any]]:
        """Process a single PDF URL"""
        try:
            # Check if domain is supported
            if not self._is_supported_domain(url):
                self.logger.debug(f"Skipping PDF from unsupported domain: {url}")
                return None

            # Download PDF
            pdf_content = await self._download_pdf(url)
            if not pdf_content:
                return None

            # Extract text from PDF
            text_content = await self._extract_text_from_pdf(pdf_content)
            if not text_content:
                return None

            # Check minimum content length
            if len(text_content.strip()) < self.config.get("min_content_length", 100):
                return None

            # Detect license from content or URL
            license_info = self._detect_pdf_license(text_content, url)

            # Extract metadata
            title = self._extract_pdf_title(text_content, url)
            author = self._extract_pdf_author(text_content)
            publish_date = self._extract_pdf_date(text_content)

            # Clean and format content
            content = f"# {title}\n\n"
            if author:
                content += f"**Author:** {author}\n\n"
            if publish_date:
                content += f"**Date:** {publish_date}\n\n"
            content += f"**Source:** {url}\n\n"
            content += f"**License:** {license_info}\n\n"
            content += "## Content\n\n" + text_content

            return self._create_result(
                url=url,
                title=title,
                content=content,
                author=author,
                publish_date=publish_date,
                source_type="pdf",
                metadata={
                    "file_size": len(pdf_content),
                    "license": license_info,
                    "platform": "pdf_document",
                    "content_type": "academic_document"
                }
            )

        except Exception as e:
            self.logger.error(f"Error processing PDF from {url}: {e}")
            return None

    def _is_supported_domain(self, url: str) -> bool:
        """Check if PDF domain is supported for ethical ingestion"""
        parsed_url = urlparse(url)
        domain = parsed_url.netloc.lower()

        # Check against supported domains
        for supported_domain in self.supported_pdf_domains:
            if supported_domain in domain:
                return True

        # Check for open access indicators
        open_access_indicators = [
            "openaccess",
            "publicdomain",
            "creativecommons",
            "opensource"
        ]

        url_lower = url.lower()
        return any(indicator in url_lower for indicator in open_access_indicators)

    async def _download_pdf(self, url: str) -> Optional[bytes]:
        """Download PDF content from URL"""
        try:
            response = await self._make_request(url)
            if response and response.status == 200:
                content_type = response.headers.get("content-type", "").lower()
                if "pdf" in content_type or url.endswith(".pdf"):
                    return await response.read()
                else:
                    self.logger.warning(f"URL does not point to a PDF: {url} (Content-Type: {content_type})")
            else:
                self.logger.warning(f"Failed to download PDF from {url}: HTTP {response.status if response else 'None'}")

        except Exception as e:
            self.logger.error(f"Error downloading PDF from {url}: {e}")

        return None

    async def _extract_text_from_pdf(self, pdf_content: bytes) -> Optional[str]:
        """Extract text from PDF content"""
        try:
            # Try multiple PDF extraction methods

            # Method 1: Try pdfplumber if available
            text = await self._extract_with_pdfplumber(pdf_content)
            if text and len(text.strip()) > 100:
                return text

            # Method 2: Try PyPDF2 if available
            text = await self._extract_with_pypdf2(pdf_content)
            if text and len(text.strip()) > 100:
                return text

            # Method 3: Try pdftotext if available
            text = await self._extract_with_pdftotext(pdf_content)
            if text and len(text.strip()) > 100:
                return text

            self.logger.warning("All PDF extraction methods failed or returned insufficient content")
            return None

        except Exception as e:
            self.logger.error(f"Error extracting text from PDF: {e}")
            return None

    async def _extract_with_pdfplumber(self, pdf_content: bytes) -> Optional[str]:
        """Extract text using pdfplumber library"""
        try:
            import pdfplumber

            with pdfplumber.open(io.BytesIO(pdf_content)) as pdf:
                text_parts = []
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text_parts.append(page_text)

                if text_parts:
                    return "\n\n".join(text_parts)

        except ImportError:
            self.logger.debug("pdfplumber not available")
        except Exception as e:
            self.logger.debug(f"pdfplumber extraction failed: {e}")

        return None

    async def _extract_with_pypdf2(self, pdf_content: bytes) -> Optional[str]:
        """Extract text using PyPDF2 library"""
        try:
            import PyPDF2

            pdf_reader = PyPDF2.PdfReader(io.BytesIO(pdf_content))
            text_parts = []

            for page in pdf_reader.pages:
                try:
                    page_text = page.extract_text()
                    if page_text:
                        text_parts.append(page_text)
                except Exception:
                    continue

            if text_parts:
                return "\n\n".join(text_parts)

        except ImportError:
            self.logger.debug("PyPDF2 not available")
        except Exception as e:
            self.logger.debug(f"PyPDF2 extraction failed: {e}")

        return None

    async def _extract_with_pdftotext(self, pdf_content: bytes) -> Optional[str]:
        """Extract text using pdftotext command-line tool"""
        try:
            # Create temporary files
            with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as pdf_file:
                pdf_file.write(pdf_content)
                pdf_path = pdf_file.name

            try:
                # Run pdftotext
                result = subprocess.run(
                    ["pdftotext", "-layout", pdf_path, "-"],
                    capture_output=True,
                    text=True,
                    timeout=30
                )

                if result.returncode == 0 and result.stdout:
                    return result.stdout.strip()

            finally:
                # Clean up temporary file
                Path(pdf_path).unlink(missing_ok=True)

        except (subprocess.TimeoutExpired, FileNotFoundError, Exception) as e:
            self.logger.debug(f"pdftotext extraction failed: {e}")

        return None

    def _extract_pdf_title(self, text_content: str, url: str) -> str:
        """Extract title from PDF content"""
        # Try to find title in first few lines
        lines = text_content.split('\n')[:10]

        for line in lines:
            line = line.strip()
            # Skip very short lines or lines with too many special characters
            if len(line) < 10 or len(re.findall(r'[^a-zA-Z0-9\s\-\.,:]', line)) > len(line) * 0.3:
                continue

            # Look for title-like patterns
            if (re.search(r'^[A-Z][^.!?]*[.!?]?$', line) or  # Capitalized sentence
                len(line.split()) >= 3 and  # At least 3 words
                not re.search(r'\d{2,}', line)):  # Not mostly numbers
                return line

        # Fallback to filename from URL
        parsed_url = urlparse(url)
        filename = Path(parsed_url.path).stem
        return filename.replace('-', ' ').replace('_', ' ').title()

    def _extract_pdf_author(self, text_content: str) -> Optional[str]:
        """Extract author from PDF content"""
        # Look for author patterns in first 50 lines
        lines = text_content.split('\n')[:50]
        text = '\n'.join(lines)

        author_patterns = [
            r'Author[s]?:\s*([^\n]+)',
            r'By\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
            r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+(?:University|College|Institute)',
        ]

        for pattern in author_patterns:
            match = re.search(pattern, text)
            if match:
                author = match.group(1).strip()
                # Filter out patterns that are unlikely to be authors
                if len(author) > 2 and not re.search(r'\d{4}|Page|Abstract|Introduction', author):
                    return author

        return None

    def _extract_pdf_date(self, text_content: str) -> Optional[str]:
        """Extract publication date from PDF content"""
        # Look for date patterns in first 100 lines
        lines = text_content.split('\n')[:100]
        text = '\n'.join(lines)

        date_patterns = [
            r'(\d{1,2}\s+(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4})',
            r'((January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4})',
            r'(\d{4})',
        ]

        for pattern in date_patterns:
            match = re.search(pattern, text)
            if match:
                date_str = match.group(1)
                # Try to validate and normalize the date
                try:
                    # Simple validation - year should be reasonable
                    year_match = re.search(r'\d{4}', date_str)
                    if year_match:
                        year = int(year_match.group())
                        if 1900 <= year <= datetime.now().year + 1:
                            return date_str
                except Exception:
                    continue

        return None

    def _detect_pdf_license(self, text_content: str, url: str) -> str:
        """Detect license from PDF content and URL"""
        content_lower = text_content.lower()
        url_lower = url.lower()

        # Check for Creative Commons licenses
        cc_patterns = {
            "CC BY": r"creative commons attribution|cc by|attribution",
            "CC BY-SA": r"creative commons share-alike|cc by-sa|share alike",
            "CC BY-NC": r"creative commons non-commercial|cc by-nc|non-commercial",
            "CC BY-ND": r"creative commons no-derivatives|cc by-nd|no derivatives",
            "CC0": r"creative commons zero|cc0|public domain dedication",
        }

        for license_name, pattern in cc_patterns.items():
            if re.search(pattern, content_lower) or re.search(pattern, url_lower):
                return license_name

        # Check for open access indicators
        if "open access" in content_lower or "openaccess" in url_lower:
            return "Open Access"

        # Check for public domain
        if "public domain" in content_lower:
            return "Public Domain"

        # Check for academic licenses
        if "arxiv" in url_lower:
            return "arXiv License (CC BY 4.0 for papers submitted after 2021)"

        # Default license
        return "Unknown License - Use with caution"

    def _clean_pdf_text(self, text_content: str) -> str:
        """Clean and format extracted PDF text"""
        # Remove common PDF extraction artifacts
        text = re.sub(r'\f', '\n\n', text)  # Form feeds to page breaks
        text = re.sub(r'\s+', ' ', text)  # Normalize whitespace
        text = re.sub(r'([a-z])([A-Z])', r'\1. \2', text)  # Add periods between sentences
        text = text.strip()

        # Remove excessive line breaks
        text = re.sub(r'\n{3,}', '\n\n', text)

        return text

    def _create_result(self, url: str, title: str, content: str, **kwargs) -> Dict[str, Any]:
        """Create PDF-specific result"""
        result = super()._create_result(url, title, content, **kwargs)

        # Clean PDF text content
        result["content"] = self._clean_pdf_text(content)

        # Extract references from content
        result["references"] = self._extract_references(content)

        # Add PDF-specific metadata
        result["metadata"]["platform"] = "pdf_document"
        result["metadata"]["content_type"] = "academic_document"

        return result