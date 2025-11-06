# youtube_transcript_fetcher.py
"""
YouTube Transcript Fetcher - Fetches and prioritizes educational content transcripts
Special integration with ManuAGI and other high-value educational channels
"""
import os
import re
import json
import requests
from datetime import datetime, timezone
from typing import List, Dict, Optional
from dataclasses import dataclass
from pathlib import Path

try:
    from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound
    YOUTUBE_API_AVAILABLE = True
except ImportError:
    YOUTUBE_API_AVAILABLE = False
    print("Warning: youtube_transcript_api not installed. Install with: pip install youtube-transcript-api")

from utils.priority_sources import priority_manager

@dataclass
class TranscriptMetadata:
    """Metadata for fetched transcript"""
    video_id: str
    title: str
    channel: str
    upload_date: str
    duration: str
    description: str
    tags: List[str]
    url: str
    priority_score: float
    priority_level: str

class YouTubeTranscriptFetcher:
    """Fetches and processes YouTube transcripts with priority scoring"""

    def __init__(self):
        if YOUTUBE_API_AVAILABLE:
            self.api = YouTubeTranscriptApi()
        else:
            self.api = None

        # High-priority educational channels
        self.priority_channels = [
            "ManuAGI",
            "3Blue1Brown",
            "StatQuest with Josh Starmer",
            "DeepLearningAI",
            "fast.ai",
            "Two Minute Papers",
            "Lex Fridman",
            "Yannic Kilcher",
            "AI Coffee Break with Letitia",
            "Machine Learning Street Talk"
        ]

        # Educational content keywords
        self.educational_keywords = [
            "tutorial", "explained", "introduction", "beginner", "advanced",
            "machine learning", "artificial intelligence", "deep learning",
            "neural networks", "transformer", "attention", "gan", "vae",
            "python", "programming", "code", "development", "open source",
            "research", "paper", "study", "learn", "course", "lecture"
        ]

    def fetch_transcript(self, video_id: str, video_url: str = None) -> Optional[Dict]:
        """
        Fetch transcript for a YouTube video

        Args:
            video_id: YouTube video ID
            video_url: Full YouTube URL (optional)

        Returns:
            Dictionary with transcript and metadata, or None if failed
        """
        if not self.api:
            print("YouTube API not available")
            return None

        try:
            # Get transcript
            transcript_list = self.api.get_transcript(video_id, languages=['en'])

            # Get video metadata
            metadata = self._get_video_metadata(video_id, video_url)

            # Process transcript
            transcript_text = " ".join([entry['text'] for entry in transcript_list])

            # Calculate priority score
            content_data = {
                'url': video_url or f"https://youtube.com/watch?v={video_id}",
                'title': metadata.get('title', ''),
                'content': transcript_text,
                'source_type': 'youtube_transcript',
                'channel': metadata.get('channel', ''),
                'tags': metadata.get('tags', [])
            }

            priority_score = priority_manager.calculate_priority_score(content_data)

            return {
                'video_id': video_id,
                'transcript': transcript_text,
                'metadata': metadata,
                'priority_score': priority_score,
                'priority_level': priority_manager._get_priority_level(priority_score),
                'raw_transcript': transcript_list,
                'url': video_url or f"https://youtube.com/watch?v={video_id}",
                'fetched_at': datetime.now(timezone.utc).isoformat()
            }

        except TranscriptsDisabled:
            print(f"Transcripts disabled for video: {video_id}")
        except NoTranscriptFound:
            print(f"No transcript found for video: {video_id}")
        except Exception as e:
            print(f"Error fetching transcript for {video_id}: {str(e)}")

        return None

    def _get_video_metadata(self, video_id: str, video_url: str = None) -> Dict:
        """Get video metadata (placeholder implementation)"""
        # In a real implementation, you'd use YouTube Data API v3
        # For now, return basic metadata

        return {
            'video_id': video_id,
            'title': f"YouTube Video {video_id}",
            'channel': 'Unknown Channel',
            'upload_date': '2024-01-01T00:00:00Z',
            'duration': 'PT10M30S',
            'description': 'Video description would go here',
            'tags': [],
            'view_count': 0,
            'like_count': 0
        }

    def _extract_video_id(self, url: str) -> Optional[str]:
        """Extract video ID from YouTube URL"""
        patterns = [
            r'(?:youtube\.com/watch\?v=|youtu\.be/|youtube\.com/embed/)([a-zA-Z0-9_-]+)',
            r'youtube\.com/.*[?&]v=([a-zA-Z0-9_-]+)'
        ]

        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)

        return None

    def fetch_channel_transcripts(self, channel_name: str, max_videos: int = 10) -> List[Dict]:
        """
        Fetch transcripts from a specific channel

        Args:
            channel_name: Name of the YouTube channel
            max_videos: Maximum number of videos to fetch

        Returns:
            List of transcript data dictionaries
        """
        # This is a placeholder - in a real implementation, you'd use YouTube Data API
        # to get channel videos and then fetch their transcripts

        print(f"Fetching transcripts from channel: {channel_name}")
        print("(Note: This is a placeholder implementation)")

        # Return placeholder data for demonstration
        placeholder_transcripts = []

        if channel_name == "ManuAGI":
            placeholder_transcripts = [
                {
                    'video_id': 'manuagi_demo_1',
                    'transcript': "This is a placeholder transcript for a ManuAGI video about AI development tools...",
                    'metadata': {
                        'title': 'ManuAGI: Complete AI Development Workflow',
                        'channel': 'ManuAGI',
                        'upload_date': '2024-01-15T10:00:00Z',
                        'duration': 'PT25M30S',
                        'description': 'Complete guide to AI development using open source tools',
                        'tags': ['AI', 'development', 'open source', 'tools', 'tutorial']
                    },
                    'priority_score': 3.0,
                    'priority_level': 'CRITICAL',
                    'url': 'https://youtube.com/watch?v=manuagi_demo_1',
                    'fetched_at': datetime.now(timezone.utc).isoformat()
                },
                {
                    'video_id': 'manuagi_demo_2',
                    'transcript': "In this ManuAGI video, we explore advanced AI development techniques...",
                    'metadata': {
                        'title': 'Advanced AI Development with ManuAGI',
                        'channel': 'ManuAGI',
                        'upload_date': '2024-01-20T14:30:00Z',
                        'duration': 'PT30M15S',
                        'description': 'Advanced techniques for AI development',
                        'tags': ['AI', 'advanced', 'development', 'manuagi', 'tutorial']
                    },
                    'priority_score': 3.0,
                    'priority_level': 'CRITICAL',
                    'url': 'https://youtube.com/watch?v=manuagi_demo_2',
                    'fetched_at': datetime.now(timezone.utc).isoformat()
                }
            ]

        return placeholder_transcripts[:max_videos]

    def search_and_fetch(self, query: str, max_results: int = 5) -> List[Dict]:
        """
        Search for videos and fetch their transcripts

        Args:
            query: Search query
            max_results: Maximum results to return

        Returns:
            List of transcript data dictionaries
        """
        # Get priority recommendations
        recommendations = priority_manager.get_priority_recommendations(query, max_results)

        results = []
        for rec in recommendations:
            if 'youtube.com' in rec.get('url', ''):
                video_id = self._extract_video_id(rec['url'])
                if video_id:
                    transcript_data = self.fetch_transcript(video_id, rec['url'])
                    if transcript_data:
                        # Add recommendation metadata
                        transcript_data['recommendation_reason'] = rec.get('reason', '')
                        transcript_data['search_query'] = query
                        results.append(transcript_data)

        return results

    def process_transcript_for_vault(self, transcript_data: Dict) -> Dict:
        """
        Process transcript data for vault indexing

        Args:
            transcript_data: Raw transcript data

        Returns:
            Processed data ready for vault indexing
        """
        metadata = transcript_data.get('metadata', {})

        # Create vault-ready entry
        vault_entry = {
            'title': metadata.get('title', 'Untitled Video'),
            'path': f"vault/transcripts/{transcript_data['video_id']}.md",
            'content': transcript_data.get('transcript', ''),
            'source_type': 'youtube_transcript',
            'source_url': transcript_data.get('url', ''),
            'channel': metadata.get('channel', ''),
            'video_id': transcript_data['video_id'],
            'upload_date': metadata.get('upload_date', ''),
            'duration': metadata.get('duration', ''),
            'tags': metadata.get('tags', []),
            'priority_score': transcript_data.get('priority_score', 1.0),
            'priority_level': transcript_data.get('priority_level', 'MEDIUM'),
            'credibility_score': min(transcript_data.get('priority_score', 1.0), 1.0),
            'weight': 2.0 if transcript_data.get('priority_score', 1.0) >= 2.0 else 1.0,
            'fetched_at': transcript_data.get('fetched_at', ''),
            'sections': [],
            'tables': []
        }

        # Extract sections from transcript (basic implementation)
        content = transcript_data.get('transcript', '')
        if content:
            sections = self._extract_sections(content)
            vault_entry['sections'] = sections

        # Add frontmatter for Obsidian
        frontmatter = {
            'source': 'YouTube Transcript',
            'channel': metadata.get('channel', ''),
            'video_id': transcript_data['video_id'],
            'priority_level': vault_entry['priority_level'],
            'priority_score': vault_entry['priority_score'],
            'tags': ['transcript'] + metadata.get('tags', []),
            'created': transcript_data.get('fetched_at', ''),
            'type': 'transcript'
        }

        vault_entry['frontmatter'] = frontmatter

        return vault_entry

    def _extract_sections(self, content: str) -> List[Dict]:
        """Extract sections from transcript content"""
        sections = []

        # Split transcript into sections (basic heuristic)
        # Look for timestamp patterns or topic changes
        lines = content.split('\n')
        current_section = []
        section_start = 0

        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue

            # Check for section markers (timestamps, topic indicators)
            if re.match(r'^\d{1,2}:\d{2}:\d{2}', line) or any(keyword in line.lower() for keyword in ['introduction', 'conclusion', 'summary', 'overview', 'example']):
                if current_section:
                    sections.append({
                        'start_time': section_start,
                        'end_time': i,
                        'content': ' '.join(current_section),
                        'type': 'transcript_section'
                    })
                current_section = [line]
                section_start = i
            else:
                current_section.append(line)

        # Add final section
        if current_section:
            sections.append({
                'start_time': section_start,
                'end_time': len(lines),
                'content': ' '.join(current_section),
                'type': 'transcript_section'
            })

        return sections

    def save_to_vault(self, vault_entry: Dict, vault_path: str = None) -> str:
        """
        Save processed transcript to vault

        Args:
            vault_entry: Processed vault entry
            vault_path: Path to vault directory

        Returns:
            Path to saved file
        """
        if not vault_path:
            vault_path = Path.home() / "Documents" / "Obsidian" / "OMAi"

        vault_path = Path(vault_path)
        vault_path.mkdir(parents=True, exist_ok=True)

        # Create markdown file
        file_path = vault_path / f"Transcripts/{vault_entry['video_id']}.md"
        file_path.parent.mkdir(parents=True, exist_ok=True)

        # Generate frontmatter
        frontmatter = vault_entry.get('frontmatter', {})
        frontmatter_str = '\n'.join([f"---"] + [f"{k}: {v}" for k, v in frontmatter.items()] + ["---"])

        # Generate content
        content = f"{frontmatter_str}\n\n"
        content += f"# {vault_entry['title']}\n\n"
        content += f"**Channel**: {vault_entry['channel']}\n"
        content += f"**Video ID**: {vault_entry['video_id']}\n"
        content += f"**Priority**: {vault_entry['priority_level']} (Score: {vault_entry['priority_score']})\n"
        content += f"**URL**: {vault_entry.get('source_url', '')}\n\n"

        if vault_entry.get('sections'):
            content += "## Transcript Sections\n\n"
            for i, section in enumerate(vault_entry['sections']):
                content += f"### Section {i+1}\n\n"
                content += f"{section['content']}\n\n"

        content += "## Full Transcript\n\n"
        content += vault_entry['content']

        # Save file
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)

        return str(file_path)

# Global instance
youtube_fetcher = YouTubeTranscriptFetcher()