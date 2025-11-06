#!/usr/bin/env python3
"""
youtube_fetcher.py - YouTube public transcript fetcher

Fetches public YouTube video transcripts with ethical compliance.
Only accesses videos with public transcripts and respects content licensing.
"""

import asyncio
import aiohttp
import json
import re
import html
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
from urllib.parse import urlencode, quote

from .base_fetcher import BaseFetcher


class YouTubeFetcher(BaseFetcher):
    """YouTube public transcript fetcher"""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.youtube_api_base = "https://www.googleapis.com/youtube/v3"
        self.youtube_watch_base = "https://www.youtube.com/watch"
        self.youtube_transcript_base = "https://video.google.com/timedtext"

    async def _fetch_impl(self, query: str, max_items: int) -> List[Dict[str, Any]]:
        """Fetch YouTube video transcripts"""
        results = []

        try:
            # Search for videos using YouTube API
            videos = await self._search_videos(query, max_items)

            for video in videos:
                try:
                    result = await self._process_video(video)
                    if result:
                        results.append(result)
                except Exception as e:
                    self.logger.error(f"Error processing YouTube video {video.get('id')}: {e}")

        except Exception as e:
            self.logger.error(f"Error fetching YouTube content: {e}")

        return results

    async def _search_videos(self, query: str, max_items: int) -> List[Dict[str, Any]]:
        """Search for YouTube videos using YouTube API"""
        videos = []

        # Check if API key is available
        api_key = self.config.get("youtube_api_key")
        if not api_key:
            self.logger.warning("YouTube API key not configured, skipping YouTube fetcher")
            return videos

        # Prepare search parameters
        params = {
            "part": "snippet",
            "q": quote(query),
            "type": "video",
            "maxResults": min(max_items, 50),  # YouTube API limit
            "order": "relevance",
            "videoDuration": "medium",  # Prefer medium-length videos
            "videoCaption": "closedCaption",  # Only videos with captions
            "key": api_key,
            "safeSearch": "moderate"
        }

        try:
            # Make request to YouTube API
            url = f"{self.youtube_api_base}/search?{urlencode(params)}"
            response = await self._make_request(url)

            if response and response.status == 200:
                data = await response.json()
                videos = data.get("items", [])
                self.logger.info(f"Found {len(videos)} YouTube videos for query: {query}")
            else:
                self.logger.warning(f"YouTube API request failed with status: {response.status if response else 'None'}")

        except Exception as e:
            self.logger.error(f"Error searching YouTube videos: {e}")

        return videos

    async def _process_video(self, video: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Process a single YouTube video"""
        video_id = video.get("id", {}).get("videoId", "")
        if not video_id:
            return None

        try:
            # Get video details
            video_details = await self._get_video_details(video_id)
            if not video_details:
                return None

            # Check if video is appropriate
            if not self._is_video_appropriate(video_details):
                self.logger.debug(f"Skipping video {video_id}: not appropriate for ingestion")
                return None

            # Get transcript
            transcript = await self._get_transcript(video_id)
            if not transcript:
                self.logger.debug(f"No transcript available for video {video_id}")
                return None

            # Check minimum content length
            if len(transcript.strip()) < self.config.get("min_content_length", 100):
                return None

            # Extract metadata
            snippet = video.get("snippet", {})
            title = snippet.get("title", "")
            channel_title = snippet.get("channelTitle", "")
            published_at = snippet.get("publishedAt", "")
            description = snippet.get("description", "")

            # Parse publish date
            publish_date = None
            if published_at:
                try:
                    pub_date = datetime.fromisoformat(published_at.replace('Z', '+00:00'))
                    publish_date = pub_date.strftime("%Y-%m-%d")
                except Exception:
                    pass

            # Build content
            content_parts = [f"# {title}"]

            content_parts.append(f"**Channel:** {channel_title}")
            content_parts.append(f"**Video ID:** {video_id}")

            if publish_date:
                content_parts.append(f"**Published:** {publish_date}")

            # Add description if available
            if description and len(description.strip()) > 50:
                # Truncate very long descriptions
                desc = description[:500] + "..." if len(description) > 500 else description
                content_parts.append(f"\n## Description\n\n{desc}")

            # Add transcript
            content_parts.append(f"\n## Transcript\n\n{transcript}")

            content = "\n\n".join(content_parts)

            return self._create_result(
                url=f"https://www.youtube.com/watch?v={video_id}",
                title=title,
                content=content,
                author=channel_title,
                publish_date=publish_date,
                source_type="youtube",
                metadata={
                    "video_id": video_id,
                    "channel_id": snippet.get("channelId", ""),
                    "duration": video_details.get("duration", ""),
                    "view_count": video_details.get("viewCount", 0),
                    "like_count": video_details.get("likeCount", 0),
                    "comment_count": video_details.get("commentCount", 0),
                    "tags": video_details.get("tags", []),
                    "category_id": video_details.get("categoryId", ""),
                    "platform": "youtube",
                    "content_type": "video_transcript"
                }
            )

        except Exception as e:
            self.logger.error(f"Error processing video {video_id}: {e}")
            return None

    async def _get_video_details(self, video_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed video information"""
        api_key = self.config.get("youtube_api_key")
        if not api_key:
            return None

        params = {
            "part": "statistics,contentDetails,status",
            "id": video_id,
            "key": api_key
        }

        try:
            url = f"{self.youtube_api_base}/videos?{urlencode(params)}"
            response = await self._make_request(url)

            if response and response.status == 200:
                data = await response.json()
                items = data.get("items", [])
                if items:
                    return items[0]

        except Exception as e:
            self.logger.debug(f"Error getting video details for {video_id}: {e}")

        return None

    def _is_video_appropriate(self, video_details: Dict[str, Any]) -> bool:
        """Check if video is appropriate for ingestion"""
        # Check video status
        status = video_details.get("status", {})
        upload_status = status.get("uploadStatus", "")
        privacy_status = status.get("privacyStatus", "")

        if upload_status != "processed" or privacy_status != "public":
            return False

        # Check if embeddable
        if not status.get("embeddable", False):
            return False

        # Check content rating
        content_rating = video_details.get("contentDetails", {}).get("contentRating", {})
        if content_rating:
            # Skip videos with content ratings
            return False

        # Skip extremely long or short videos
        duration = video_details.get("contentDetails", {}).get("duration", "")
        if duration:
            # Parse ISO 8601 duration (PT4M13S = 4 minutes 13 seconds)
            duration_seconds = self._parse_duration(duration)
            if duration_seconds < 60 or duration_seconds > 3600:  # 1 minute to 1 hour
                return False

        return True

    def _parse_duration(self, duration_str: str) -> int:
        """Parse ISO 8601 duration string to seconds"""
        # Remove PT prefix
        duration_str = duration_str[2:]

        # Parse components
        hours = 0
        minutes = 0
        seconds = 0

        # Extract hours
        hour_match = re.search(r'(\d+)H', duration_str)
        if hour_match:
            hours = int(hour_match.group(1))

        # Extract minutes
        minute_match = re.search(r'(\d+)M', duration_str)
        if minute_match:
            minutes = int(minute_match.group(1))

        # Extract seconds
        second_match = re.search(r'(\d+)S', duration_str)
        if second_match:
            seconds = int(second_match.group(1))

        return hours * 3600 + minutes * 60 + seconds

    async def _get_transcript(self, video_id: str) -> Optional[str]:
        """Get transcript for YouTube video"""
        try:
            # Try to get transcript from YouTube's timedtext API
            transcript_url = f"{self.youtube_transcript_base}?lang=en&v={video_id}"
            response = await self._make_request(transcript_url)

            if response and response.status == 200:
                xml_content = await response.text()
                transcript = self._parse_transcript_xml(xml_content)
                if transcript:
                    return transcript

            # Try alternative languages if English not available
            languages = ["en-US", "en-GB", "en"]
            for lang in languages:
                if lang == "en":
                    continue  # Already tried
                transcript_url = f"{self.youtube_transcript_base}?lang={lang}&v={video_id}"
                response = await self._make_request(transcript_url)

                if response and response.status == 200:
                    xml_content = await response.text()
                    transcript = self._parse_transcript_xml(xml_content)
                    if transcript:
                        return transcript

        except Exception as e:
            self.logger.debug(f"Error getting transcript for {video_id}: {e}")

        return None

    def _parse_transcript_xml(self, xml_content: str) -> Optional[str]:
        """Parse transcript XML to extract text"""
        try:
            # Remove XML declaration if present
            xml_content = re.sub(r'<\?xml[^>]*\?>', '', xml_content)

            # Extract text from transcript elements
            text_elements = re.findall(r'<text[^>]*>([^<]+)</text>', xml_content)

            if text_elements:
                # Clean up text elements
                cleaned_texts = []
                for text in text_elements:
                    # Decode HTML entities
                    text = html.unescape(text)
                    # Remove timestamps and other markers
                    text = re.sub(r'\d+:\d+:\d+\.\d+', '', text)  # Remove timestamps
                    text = re.sub(r'\s+', ' ', text).strip()
                    if text:
                        cleaned_texts.append(text)

                return " ".join(cleaned_texts)

        except Exception as e:
            self.logger.debug(f"Error parsing transcript XML: {e}")

        return None

    def _detect_youtube_license(self, video_details: Dict[str, Any]) -> str:
        """Detect license for YouTube content"""
        # Most YouTube content is under YouTube's Terms of Service
        # Check for specific licensing information

        license_type = "YouTube Standard License"  # Default

        # Check if video has Creative Commons license
        if "creativeCommon" in str(video_details).lower():
            license_type = "CC BY"  # YouTube supports CC BY

        return license_type

    def _clean_transcript(self, transcript: str) -> str:
        """Clean and format transcript"""
        # Remove common transcript artifacts
        transcript = re.sub(r'\[.*?\]', '', transcript)  # Remove [music], [applause], etc.
        transcript = re.sub(r'\(\s*\)', '', transcript)  # Remove empty parentheses
        transcript = re.sub(r'\s+', ' ', transcript)  # Normalize whitespace
        transcript = transcript.strip()

        # Add basic punctuation if missing
        if transcript and transcript[-1] not in '.!?':
            transcript += '.'

        return transcript

    def _create_result(self, url: str, title: str, content: str, **kwargs) -> Dict[str, Any]:
        """Create YouTube-specific result"""
        result = super()._create_result(url, title, content, **kwargs)

        # Clean transcript content
        result["content"] = self._clean_transcript(content)

        # Detect license
        video_details = kwargs.get("metadata", {})
        result["license"] = self._detect_youtube_license(video_details)

        # Add YouTube-specific metadata
        result["metadata"]["platform"] = "youtube"
        result["metadata"]["content_type"] = "video_transcript"

        # Extract references from transcript (uncommon but possible)
        result["references"] = self._extract_references(content)

        return result