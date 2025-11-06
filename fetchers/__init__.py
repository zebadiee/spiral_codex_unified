"""
Fetchers package for Spiral Codex ethical content ingestion
"""

from .reddit_fetcher import RedditFetcher
from .arxiv_fetcher import ArxivFetcher
from .archive_fetcher import ArchiveFetcher
from .youtube_fetcher import YouTubeFetcher
from .pdf_fetcher import PDFFetcher

__all__ = [
    "RedditFetcher",
    "ArxivFetcher",
    "ArchiveFetcher",
    "YouTubeFetcher",
    "PDFFetcher"
]