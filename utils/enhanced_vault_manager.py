# enhanced_vault_manager.py
"""
Enhanced Vault Manager - Integrates priority sources with vault indexing
Special handling for YouTube transcripts and educational content prioritization
"""
import json
import os
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime, timezone

from utils.priority_sources import priority_manager
from fetchers.youtube_transcript_fetcher import youtube_fetcher

class EnhancedVaultManager:
    """Enhanced vault management with priority source integration"""

    def __init__(self, vault_path: str = None):
        self.vault_path = Path(vault_path or Path.home() / "Documents" / "Obsidian" / "OMAi")
        self.vault_path.mkdir(parents=True, exist_ok=True)

        # Subdirectories
        self.transcripts_dir = self.vault_path / "Transcripts"
        self.papers_dir = self.vault_path / "Papers"
        self.tutorials_dir = self.vault_path / "Tutorials"
        self.documentation_dir = self.vault_path / "Documentation"

        # Create directories
        for dir_path in [self.transcripts_dir, self.papers_dir, self.tutorials_dir, self.documentation_dir]:
            dir_path.mkdir(exist_ok=True)

    def fetch_and_prioritize_transcripts(self, channels: List[str] = None, max_per_channel: int = 5) -> Dict:
        """
        Fetch transcripts from priority channels and integrate with vault

        Args:
            channels: List of channel names to fetch from (defaults to priority channels)
            max_per_channel: Maximum videos to fetch per channel

        Returns:
            Dictionary with fetch results and statistics
        """
        if not channels:
            channels = ["ManuAGI", "3Blue1Brown", "StatQuest with Josh Starmer", "DeepLearningAI"]

        results = {
            'fetched_videos': 0,
            'high_priority_count': 0,
            'channels_processed': len(channels),
            'errors': [],
            'files_created': []
        }

        for channel in channels:
            try:
                print(f"Fetching transcripts from channel: {channel}")
                channel_transcripts = youtube_fetcher.fetch_channel_transcripts(channel, max_per_channel)

                for transcript_data in channel_transcripts:
                    # Process for vault
                    vault_entry = youtube_fetcher.process_transcript_for_vault(transcript_data)

                    # Determine appropriate directory based on priority
                    if vault_entry['priority_level'] in ['CRITICAL', 'HIGH']:
                        vault_entry['path'] = str(self.transcripts_dir / f"{vault_entry['video_id']}.md")
                    else:
                        vault_entry['path'] = str(self.tutorials_dir / f"{vault_entry['video_id']}.md")

                    # Save to vault
                    file_path = youtube_fetcher.save_to_vault(vault_entry, str(self.vault_path))
                    results['files_created'].append(file_path)

                    results['fetched_videos'] += 1
                    if vault_entry['priority_level'] in ['CRITICAL', 'HIGH']:
                        results['high_priority_count'] += 1

            except Exception as e:
                error_msg = f"Error processing channel {channel}: {str(e)}"
                results['errors'].append(error_msg)
                print(error_msg)

        return results

    def prioritize_existing_vault(self) -> Dict:
        """
        Apply priority scoring to existing vault items

        Returns:
            Dictionary with prioritization results
        """
        vault_index_file = self.vault_path.parent.parent / "data" / "vault_index.json"

        if not vault_index_file.exists():
            return {'error': 'Vault index file not found', 'processed_items': 0}

        try:
            with open(vault_index_file, 'r', encoding='utf-8') as f:
                vault_items = json.load(f)

            original_count = len(vault_items)

            # Apply priority scoring
            prioritized_items = priority_manager.update_vault_priorities(vault_items)

            # Update priority statistics
            priority_stats = {
                'critical': 0,
                'high': 0,
                'medium_high': 0,
                'medium': 0,
                'low_medium': 0,
                'low': 0
            }

            for item in prioritized_items:
                level = item.get('priority_level', 'LOW')
                priority_stats[level.lower()] = priority_stats.get(level.lower(), 0) + 1

            # Save updated index
            with open(vault_index_file, 'w', encoding='utf-8') as f:
                json.dump(prioritized_items, f, indent=2)

            return {
                'processed_items': original_count,
                'priority_distribution': priority_stats,
                'top_priority_items': prioritized_items[:10],
                'manuagi_items': [item for item in prioritized_items if 'manuagi' in item.get('title', '').lower() or 'manuagi' in item.get('content', '').lower()]
            }

        except Exception as e:
            return {'error': f'Error processing vault index: {str(e)}', 'processed_items': 0}

    def search_priority_content(self, query: str, limit: int = 10) -> List[Dict]:
        """
        Search for priority content related to query

        Args:
            query: Search query
            limit: Maximum results to return

        Returns:
            List of priority content items
        """
        vault_index_file = self.vault_path.parent.parent / "data" / "vault_index.json"

        if not vault_index_file.exists():
            return []

        try:
            with open(vault_index_file, 'r', encoding='utf-8') as f:
                vault_items = json.load(f)

            # Filter and sort by priority
            query_lower = query.lower()
            matching_items = []

            for item in vault_items:
                title = item.get('title', '').lower()
                content = item.get('content', '').lower()
                tags = [tag.lower() for tag in item.get('tags', [])]

                # Check for matches
                if (query_lower in title or
                    query_lower in content or
                    any(query_lower in tag for tag in tags)):

                    # Calculate relevance score
                    relevance_score = 0
                    if query_lower in title:
                        relevance_score += 10
                    if query_lower in content:
                        relevance_score += 5
                    if any(query_lower in tag for tag in tags):
                        relevance_score += 7

                    # Apply priority multiplier
                    priority_score = item.get('priority_score', 1.0)
                    final_score = relevance_score * priority_score

                    item['_relevance_score'] = final_score
                    matching_items.append(item)

            # Sort by final score and return top results
            matching_items.sort(key=lambda x: x.get('_relevance_score', 0), reverse=True)

            return matching_items[:limit]

        except Exception as e:
            print(f"Error searching vault: {str(e)}")
            return []

    def create_priority_dashboard(self) -> str:
        """
        Create a priority dashboard showing top content

        Returns:
            Path to created dashboard file
        """
        vault_index_file = self.vault_path.parent.parent / "data" / "vault_index.json"

        if not vault_index_file.exists():
            return "Vault index not found"

        try:
            with open(vault_index_file, 'r', encoding='utf-8') as f:
                vault_items = json.load(f)

            # Get top priority items
            top_items = sorted(vault_items, key=lambda x: x.get('priority_score', 1.0), reverse=True)[:20]

            # Get ManuAGI items
            manuagi_items = [item for item in vault_items
                           if 'manuagi' in item.get('title', '').lower() or 'manuagi' in item.get('content', '').lower()]

            # Create dashboard content
            dashboard_content = f"""# Priority Content Dashboard

*Generated: {datetime.now(timezone.utc).isoformat()}*

## 🏆 Top Priority Content

| Priority | Title | Type | Score |
|----------|-------|------|-------|
"""

            for item in top_items:
                priority_emoji = self._get_priority_emoji(item.get('priority_level', 'MEDIUM'))
                title = item.get('title', 'Untitled')[:50] + '...' if len(item.get('title', '')) > 50 else item.get('title', 'Untitled')
                content_type = item.get('source_type', 'unknown')
                score = f"{item.get('priority_score', 1.0):.2f}"

                dashboard_content += f"| {priority_emoji} | [{title}]({item.get('path', '')}) | {content_type} | {score} |\n"

            if manuagi_items:
                dashboard_content += f"""

## 🎯 ManuAGI Content ({len(manuagi_items)} items)

| Priority | Title | Score |
|----------|-------|------|
"""
                for item in manuagi_items[:10]:
                    priority_emoji = self._get_priority_emoji(item.get('priority_level', 'MEDIUM'))
                    title = item.get('title', 'Untitled')[:60] + '...' if len(item.get('title', '')) > 60 else item.get('title', 'Untitled')
                    score = f"{item.get('priority_score', 1.0):.2f}"

                    dashboard_content += f"| {priority_emoji} | [{title}]({item.get('path', '')}) | {score} |\n"

            # Save dashboard
            dashboard_path = self.vault_path / "DASHBOARDS" / "Priority_Content.md"
            dashboard_path.parent.mkdir(exist_ok=True)

            with open(dashboard_path, 'w', encoding='utf-8') as f:
                f.write(dashboard_content)

            return str(dashboard_path)

        except Exception as e:
            return f"Error creating dashboard: {str(e)}"

    def _get_priority_emoji(self, level: str) -> str:
        """Get emoji for priority level"""
        emoji_map = {
            'CRITICAL': '🔴',
            'HIGH': '🟠',
            'MEDIUM-HIGH': '🟡',
            'MEDIUM': '🟢',
            'LOW-MEDIUM': '🔵',
            'LOW': '⚪'
        }
        return emoji_map.get(level, '⚪')

    def get_priority_recommendations(self, topic: str) -> List[Dict]:
        """
        Get priority recommendations for a specific topic

        Args:
            topic: Topic to get recommendations for

        Returns:
            List of priority recommendations
        """
        # Get base recommendations from priority manager
        base_recommendations = priority_manager.get_priority_recommendations(topic, 5)

        # Enhance with vault-specific recommendations
        vault_recommendations = self.search_priority_content(topic, 5)

        # Combine and prioritize
        all_recommendations = []

        # Add base recommendations (high priority educational sources)
        for rec in base_recommendations:
            rec['source'] = 'priority_sources'
            rec['type'] = 'recommendation'
            all_recommendations.append(rec)

        # Add vault content
        for item in vault_recommendations:
            rec = {
                'title': item.get('title', ''),
                'url': item.get('path', ''),
                'priority_score': item.get('priority_score', 1.0),
                'source': 'vault',
                'type': 'existing_content',
                'relevance': item.get('_relevance_score', 0)
            }
            all_recommendations.append(rec)

        # Sort by priority score and relevance
        all_recommendations.sort(key=lambda x: (x.get('priority_score', 1.0), x.get('relevance', 0)), reverse=True)

        return all_recommendations[:10]

# Global instance
enhanced_vault_manager = EnhancedVaultManager()