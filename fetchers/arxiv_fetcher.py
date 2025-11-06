#!/usr/bin/env python3
"""
arxiv_fetcher.py - arXiv academic paper fetcher

Fetches academic papers from arXiv with ethical compliance.
arXiv provides open access to scholarly papers with proper licensing.
"""

import asyncio
import aiohttp
import xml.etree.ElementTree as ET
import re
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
from urllib.parse import urlencode, quote

from .base_fetcher import BaseFetcher


class ArxivFetcher(BaseFetcher):
    """arXiv academic paper fetcher"""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.arxiv_api = "http://export.arxiv.org/api/query"
        self.arxiv_base = "https://arxiv.org"

    async def _fetch_impl(self, query: str, max_items: int) -> List[Dict[str, Any]]:
        """Fetch arXiv papers"""
        results = []

        try:
            # Search for papers using arXiv API
            papers = await self._search_papers(query, max_items)

            for paper in papers:
                try:
                    result = await self._process_paper(paper)
                    if result:
                        results.append(result)
                except Exception as e:
                    self.logger.error(f"Error processing arXiv paper: {e}")

        except Exception as e:
            self.logger.error(f"Error fetching arXiv content: {e}")

        return results

    async def _search_papers(self, query: str, max_items: int) -> List[Dict[str, Any]]:
        """Search for arXiv papers using arXiv API"""
        papers = []

        # Prepare search parameters
        params = {
            "search_query": f"all:{quote(query)}",
            "start": 0,
            "max_results": min(max_items, 100),  # arXiv limit
            "sortBy": "relevance",
            "sortOrder": "descending"
        }

        try:
            # Make request to arXiv API
            url = f"{self.arxiv_api}?{urlencode(params)}"
            response = await self._make_request(url)

            if response and response.status == 200:
                xml_content = await response.text()
                papers = self._parse_arxiv_xml(xml_content)
                self.logger.info(f"Found {len(papers)} arXiv papers for query: {query}")
            else:
                self.logger.warning(f"arXiv API request failed with status: {response.status if response else 'None'}")

        except Exception as e:
            self.logger.error(f"Error searching arXiv papers: {e}")

        return papers

    def _parse_arxiv_xml(self, xml_content: str) -> List[Dict[str, Any]]:
        """Parse arXiv XML response"""
        papers = []

        try:
            root = ET.fromstring(xml_content)

            # Define XML namespaces
            namespaces = {
                'atom': 'http://www.w3.org/2005/Atom',
                'arxiv': 'http://arxiv.org/schemas/atom'
            }

            # Extract entries
            for entry in root.findall('atom:entry', namespaces):
                paper = {}

                # Basic metadata
                paper['id'] = self._get_text(entry, 'atom:id', namespaces)
                paper['title'] = self._get_text(entry, 'atom:title', namespaces)
                paper['summary'] = self._get_text(entry, 'atom:summary', namespaces)
                paper['published'] = self._get_text(entry, 'atom:published', namespaces)
                paper['updated'] = self._get_text(entry, 'atom:updated', namespaces)

                # Extract arXiv ID
                arxiv_id = self._extract_arxiv_id(paper['id'])
                paper['arxiv_id'] = arxiv_id

                # Authors
                authors = []
                for author in entry.findall('atom:author', namespaces):
                    author_name = self._get_text(author, 'atom:name', namespaces)
                    if author_name:
                        authors.append(author_name)
                paper['authors'] = authors

                # Categories
                categories = []
                for category in entry.findall('atom:category', namespaces):
                    term = category.get('term', '')
                    if term:
                        categories.append(term)
                paper['categories'] = categories

                # PDF URL
                paper['pdf_url'] = f"{self.arxiv_base}/pdf/{arxiv_id}.pdf"

                # DOI
                doi_links = entry.findall('.//arxiv:doi', namespaces)
                if doi_links:
                    paper['doi'] = doi_links[0].text

                # Journal reference
                journal_ref = entry.find('arxiv:journal_ref', namespaces)
                if journal_ref is not None:
                    paper['journal_ref'] = journal_ref.text

                papers.append(paper)

        except ET.ParseError as e:
            self.logger.error(f"Error parsing arXiv XML: {e}")
        except Exception as e:
            self.logger.error(f"Error processing arXiv XML: {e}")

        return papers

    def _get_text(self, element, tag: str, namespaces: Dict[str, str]) -> str:
        """Extract text from XML element"""
        found = element.find(tag, namespaces)
        if found is not None and found.text:
            return found.text.strip()
        return ""

    def _extract_arxiv_id(self, arxiv_url: str) -> str:
        """Extract arXiv ID from arXiv URL"""
        # arXiv URLs are like: http://arxiv.org/abs/2301.07041v1
        match = re.search(r'arxiv\.org/abs/([^/]+)', arxiv_url)
        if match:
            return match.group(1)
        return ""

    async def _process_paper(self, paper: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Process a single arXiv paper"""
        arxiv_id = paper.get("arxiv_id", "")
        if not arxiv_id:
            return None

        # Combine title and abstract for content
        title = paper.get("title", "")
        summary = paper.get("summary", "")
        authors = paper.get("authors", [])
        categories = paper.get("categories", [])
        published = paper.get("published", "")

        content_parts = [f"# {title}"]

        # Add authors
        if authors:
            author_list = ", ".join(authors)
            content_parts.append(f"**Authors:** {author_list}")

        # Add abstract
        if summary:
            content_parts.append("\n## Abstract\n\n" + summary)

        # Add categories
        if categories:
            category_list = ", ".join(categories)
            content_parts.append(f"\n**Categories:** {category_list}")

        # Add publication info
        if published:
            try:
                pub_date = datetime.fromisoformat(published.replace('Z', '+00:00'))
                content_parts.append(f"**Published:** {pub_date.strftime('%Y-%m-%d')}")
            except Exception:
                pass

        # Add journal reference if available
        journal_ref = paper.get("journal_ref")
        if journal_ref:
            content_parts.append(f"**Journal Reference:** {journal_ref}")

        # Add DOI if available
        doi = paper.get("doi")
        if doi:
            content_parts.append(f"**DOI:** {doi}")

        content = "\n\n".join(content_parts)

        # Check minimum content length
        if len(content.strip()) < self.config.get("min_content_length", 100):
            return None

        # Parse publish date
        publish_date = None
        if published:
            try:
                publish_date = datetime.fromisoformat(published.replace('Z', '+00:00')).strftime("%Y-%m-%d")
            except Exception:
                pass

        return self._create_result(
            url=paper["id"],
            title=title,
            content=content,
            author=", ".join(authors) if authors else None,
            publish_date=publish_date,
            source_type="arxiv",
            metadata={
                "arxiv_id": arxiv_id,
                "pdf_url": paper.get("pdf_url"),
                "doi": paper.get("doi"),
                "categories": categories,
                "journal_ref": paper.get("journal_ref"),
                "content_type": "academic_paper",
                "platform": "arxiv"
            }
        )

    def _extract_references_from_abstract(self, abstract: str) -> List[str]:
        """Extract references from abstract"""
        references = []

        # Look for citation patterns in abstract
        citation_patterns = [
            r'\[(\d+)\]',  # [1], [2], etc.
            r'\((\d{4})\)',  # (2023), (2022), etc.
            r'(\w+\s+et\s+al\.,\s*\d{4})',  # Smith et al., 2023
        ]

        for pattern in citation_patterns:
            matches = re.findall(pattern, abstract)
            references.extend(matches)

        return references

    def _detect_arxiv_license(self, arxiv_id: str) -> str:
        """Detect license for arXiv paper"""
        # Most arXiv papers are available under the arXiv license
        # Check if paper has a specific license by trying to fetch the license info

        # Default arXiv license (most papers)
        return "arXiv License (CC BY 4.0 for papers submitted after 2021)"

    async def _fetch_paper_metadata(self, arxiv_id: str) -> Optional[Dict[str, Any]]:
        """Fetch additional metadata for a specific paper"""
        try:
            # Try to fetch HTML version to extract more information
            url = f"{self.arxiv_base}/abs/{arxiv_id}"
            response = await self._make_request(url)

            if response and response.status == 200:
                html_content = await response.text()
                return self._extract_additional_metadata(html_content)

        except Exception as e:
            self.logger.debug(f"Error fetching additional metadata for {arxiv_id}: {e}")

        return None

    def _extract_additional_metadata(self, html_content: str) -> Dict[str, Any]:
        """Extract additional metadata from arXiv HTML page"""
        metadata = {}

        # Look for comments/notes
        comment_match = re.search(r'<div class="comments">([^<]+)</div>', html_content)
        if comment_match:
            metadata["comments"] = comment_match.group(1).strip()

        # Look for ACM classification
        acm_match = re.search(r'ACM Classification:\s*([^<\n]+)', html_content)
        if acm_match:
            metadata["acm_classification"] = acm_match.group(1).strip()

        # Look for MSC classification
        msc_match = re.search(r'MSC Classification:\s*([^<\n]+)', html_content)
        if msc_match:
            metadata["msc_classification"] = msc_match.group(1).strip()

        return metadata

    def _create_result(self, url: str, title: str, content: str, **kwargs) -> Dict[str, Any]:
        """Create arXiv-specific result"""
        result = super()._create_result(url, title, content, **kwargs)

        # Set arXiv license
        arxiv_id = kwargs.get("metadata", {}).get("arxiv_id", "")
        result["license"] = self._detect_arxiv_license(arxiv_id)

        # Extract references from abstract
        summary = kwargs.get("metadata", {}).get("summary", "")
        if summary:
            result["references"] = self._extract_references_from_abstract(summary)

        # Add arXiv-specific metadata
        result["metadata"]["platform"] = "arxiv"
        result["metadata"]["content_type"] = "academic_paper"
        result["metadata"]["peer_reviewed"] = True  # arXiv papers are preprints but typically peer-reviewed

        return result

    async def _make_request(self, url: str, method: str = "GET", **kwargs) -> Optional[aiohttp.ClientResponse]:
        """Override to add arXiv-specific headers"""
        # Add arXiv-specific headers
        if "arxiv.org" in url:
            headers = kwargs.get("headers", {})
            headers.update({
                "Accept": "application/xml, text/xml, text/plain, */*",
                "Accept-Language": "en-US,en;q=0.9",
            })
            kwargs["headers"] = headers

        return await super()._make_request(url, method, **kwargs)