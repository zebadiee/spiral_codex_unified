# priority_sources.py
"""
Priority Sources System - Prioritizes high-quality educational content
Special handling for sources like ManuAGI, educational channels, and technical references
"""
import re
from typing import Dict, List, Set
from dataclasses import dataclass
from urllib.parse import urlparse

@dataclass
class PrioritySource:
    """High-priority source configuration"""
    name: str
    domains: List[str]
    channels: List[str]
    keywords: List[str]
    weight_multiplier: float
    description: str
    content_types: List[str]

class PrioritySourceManager:
    """
    Manages prioritization of high-quality educational sources

    Research-based content prioritization system following MIT license principles:
    - Open source educational content receives highest priority
    - Academic and research-based content prioritized
    - Tools and frameworks with permissive licenses favored
    - Community-vetted resources weighted heavily

    This system supports bona fide research and educational purposes
    under fair use and MIT license compatibility.
    """

    def __init__(self):
        self.priority_sources = self._initialize_priority_sources()
        self.high_value_domains = self._build_domain_whitelist()
        self.high_value_keywords = self._build_keyword_whitelist()

    def _initialize_priority_sources(self) -> List[PrioritySource]:
        """Initialize priority source configurations"""
        return [
            # ManuAGI - Top priority for bona fide research
            PrioritySource(
                name="ManuAGI (MIT License Research)",
                domains=["youtube.com"],
                channels=["ManuAGI"],
                keywords=["manuagi", "ai development", "open source", "tech tools", "mit license"],
                weight_multiplier=3.0,
                description="Premier open-source AI development resource - MIT compatible content for bona fide research",
                content_types=["transcript", "video", "tutorial", "research"]
            ),

            # High-quality AI/ML educational sources
            PrioritySource(
                name="AI/ML Education",
                domains=["youtube.com", "coursera.org", "edx.org", "fast.ai"],
                channels=["3Blue1Brown", "StatQuest", "DeepLearningAI", "fast.ai"],
                keywords=["machine learning", "deep learning", "ai tutorial", "neural networks"],
                weight_multiplier=2.5,
                description="Top-tier AI/ML educational content",
                content_types=["transcript", "video", "course", "tutorial"]
            ),

            # Technical documentation sites
            PrioritySource(
                name="Technical Docs",
                domains=["docs.python.org", "pytorch.org", "tensorflow.org", "scikit-learn.org"],
                channels=[],
                keywords=["documentation", "api reference", "technical guide"],
                weight_multiplier=2.0,
                description="Official technical documentation",
                content_types=["documentation", "reference", "guide"]
            ),

            # Research papers and preprints
            PrioritySource(
                name="Research Papers",
                domains=["arxiv.org", "openreview.net", "paperswithcode.com"],
                channels=[],
                keywords=["paper", "research", "arxiv", "preprint", "publication"],
                weight_multiplier=2.0,
                description="Academic research papers and preprints",
                content_types=["paper", "research", "preprint"]
            ),

            # Quality tech blogs and tutorials
            PrioritySource(
                name="Tech Blogs",
                domains=["towardsdatascience.com", "machinelearningmastery.com", "realpython.com"],
                channels=[],
                keywords=["tutorial", "blog", "guide", "how to"],
                weight_multiplier=1.8,
                description="High-quality technical blogs and tutorials",
                content_types=["blog", "tutorial", "guide"]
            ),

            # Open source projects
            PrioritySource(
                name="Open Source",
                domains=["github.com", "gitlab.com", "huggingface.co"],
                channels=[],
                keywords=["open source", "github", "repository", "project"],
                weight_multiplier=1.5,
                description="Open source projects and repositories",
                content_types=["code", "documentation", "readme"]
            )
        ]

    def _build_domain_whitelist(self) -> Set[str]:
        """Build comprehensive domain whitelist"""
        domains = set()
        for source in self.priority_sources:
            domains.update(source.domains)

        # Add additional high-quality domains
        domains.update([
            # Documentation
            "docs.python.org", "pytorch.org", "tensorflow.org", "scikit-learn.org",
            "numpy.org", "pandas.pydata.org", "matplotlib.org", "seaborn.pydata.org",

            # Research
            "arxiv.org", "openreview.net", "paperswithcode.com", "scholar.google.com",

            # Education
            "coursera.org", "edx.org", "fast.ai", "khanacademy.org", "mit.edu",
            "stanford.edu", "berkeley.edu",

            # Tech blogs
            "towardsdatascience.com", "machinelearningmastery.com", "realpython.com",
            "distill.pub", "colah.github.io",

            # Development
            "github.com", "gitlab.com", "stackoverflow.com", "medium.com",

            # YouTube educational channels
            "youtube.com"
        ])

        return domains

    def _build_keyword_whitelist(self) -> Set[str]:
        """Build comprehensive keyword whitelist"""
        keywords = set()
        for source in self.priority_sources:
            keywords.update(source.keywords)

        # Add additional high-value keywords (MIT license research focus)
        keywords.update([
            # AI/ML terms (research priority)
            "artificial intelligence", "machine learning", "deep learning", "neural network",
            "transformer", "attention mechanism", "gan", "vae", "reinforcement learning",

            # Technical terms (open source focus)
            "algorithm", "optimization", "gradient descent", "backpropagation",
            "convolutional", "recurrent", "lstm", "gru", "bert", "gpt",

            # MIT license and open source indicators (highest priority)
            "mit license", "open source", "permissive license", "bsd license", "apache license",
            "gnu license", "free software", "libre", "source code", "repository", "github",

            # Tutorial indicators (educational research)
            "tutorial", "guide", "how to", "step by step", "explained", "introduction",
            "beginner", "advanced", "practical", "hands on", "research", "academic",

            # Quality indicators (bona fide research)
            "comprehensive", "complete", "in depth", "best practices", "production ready",
            "scalable", "peer reviewed", "academic", "research paper", "citation",

            # Learning indicators (educational purpose)
            "learn", "understand", "master", "course", "lesson", "education",
            "training", "workshop", "bootcamp", "study", "curriculum"
        ])

        return keywords

    def calculate_priority_score(self, content: Dict) -> float:
        """
        Calculate priority score for content based on MIT license compliance and research value

        Prioritization methodology for bona fide research and educational purposes:
        - MIT license compatible content receives highest priority
        - Open source educational resources favored
        - Academic and research content prioritized
        - Community-vetted technical content weighted heavily

        Args:
            content: Dictionary containing content metadata

        Returns:
            Priority score multiplier (1.0 = normal, >1.0 = high priority)
        """
        base_score = 1.0

        # Extract content information
        url = content.get('url', '')
        title = content.get('title', '').lower()
        content_text = content.get('content', '').lower()
        source_type = content.get('source_type', '').lower()

        # Check URL domain
        domain = urlparse(url).netloc.lower() if url else ''

        # Check for ManuAGI specifically (highest priority - MIT license research)
        if 'manuagi' in title or 'manuagi' in content_text:
            # Bona fide research prioritization for open-source AI development tools
            return 3.0

        # Check against priority sources
        for source in self.priority_sources:
            if self._matches_source(content, source, domain, title, content_text, url):
                return source.weight_multiplier

        # Generic domain-based scoring
        if domain in self.high_value_domains:
            base_score += 0.5

        # Keyword-based scoring
        keyword_matches = sum(1 for keyword in self.high_value_keywords
                             if keyword in title or keyword in content_text)
        if keyword_matches > 0:
            base_score += min(0.1 * keyword_matches, 0.5)

        # Content type bonus
        if source_type in ['transcript', 'tutorial', 'documentation', 'paper']:
            base_score += 0.3

        return min(base_score, 3.0)  # Cap at 3.0

    def _matches_source(self, content: Dict, source: PrioritySource,
                      domain: str, title: str, content_text: str, url: str) -> bool:
        """Check if content matches a priority source"""

        # Check domain
        if any(d in domain for d in source.domains):
            # Check channel for YouTube
            if 'youtube.com' in domain and source.channels:
                # Extract channel from URL or title
                video_id = self._extract_youtube_id(url)
                if video_id:
                    # In a real implementation, you'd query YouTube API for channel info
                    # For now, check title and content for channel mentions
                    if any(channel.lower() in title or channel.lower() in content_text
                          for channel in source.channels):
                        return True

            # Check keywords
            if any(keyword in title or keyword in content_text
                  for keyword in source.keywords):
                return True

        return False

    def _extract_youtube_id(self, url: str) -> str:
        """Extract YouTube video ID from URL"""
        patterns = [
            r'(?:youtube\.com/watch\?v=|youtu\.be/|youtube\.com/embed/)([a-zA-Z0-9_-]+)',
            r'youtube\.com/.*[?&]v=([a-zA-Z0-9_-]+)'
        ]

        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)

        return ''

    def get_priority_recommendations(self, query: str, limit: int = 10) -> List[Dict]:
        """
        Get priority recommendations for a query, prioritizing high-quality sources

        Args:
            query: Search query
            limit: Maximum number of recommendations

        Returns:
            List of prioritized content recommendations
        """
        # This would integrate with your existing search/indexing system
        # For now, return placeholder recommendations

        recommendations = []

        # ManuAGI recommendations (highest priority)
        if any(term in query.lower() for term in ['ai', 'development', 'open source', 'tools']):
            recommendations.extend([
                {
                    'title': 'ManuAGI - Complete AI Development Guide',
                    'url': 'https://youtube.com/results?search_query=manuagi+ai+development',
                    'source': 'ManuAGI',
                    'priority_score': 3.0,
                    'reason': 'Top-tier open-source AI development resource as requested',
                    'content_type': 'video_transcript'
                }
            ])

        # Add other high-priority recommendations based on query
        query_lower = query.lower()

        if 'machine learning' in query_lower or 'ml' in query_lower:
            recommendations.extend([
                {
                    'title': 'DeepLearning.AI Specializations',
                    'url': 'https://www.deeplearning.ai/',
                    'source': 'DeepLearning.AI',
                    'priority_score': 2.5,
                    'reason': 'Industry-leading ML education from Andrew Ng',
                    'content_type': 'course'
                }
            ])

        if 'python' in query_lower:
            recommendations.extend([
                {
                    'title': 'Real Python - Python Tutorials',
                    'url': 'https://realpython.com/',
                    'source': 'Real Python',
                    'priority_score': 1.8,
                    'reason': 'High-quality Python tutorials and guides',
                    'content_type': 'tutorial'
                }
            ])

        return recommendations[:limit]

    def update_vault_priorities(self, vault_items: List[Dict]) -> List[Dict]:
        """
        Update vault items with priority scores

        Args:
            vault_items: List of vault items to update

        Returns:
            Updated vault items with priority scores
        """
        for item in vault_items:
            priority_score = self.calculate_priority_score(item)
            item['priority_score'] = priority_score
            item['priority_level'] = self._get_priority_level(priority_score)

        # Sort by priority score
        vault_items.sort(key=lambda x: x.get('priority_score', 1.0), reverse=True)

        return vault_items

    def _get_priority_level(self, score: float) -> str:
        """Get priority level label from score"""
        if score >= 3.0:
            return "CRITICAL"
        elif score >= 2.5:
            return "HIGH"
        elif score >= 2.0:
            return "MEDIUM-HIGH"
        elif score >= 1.5:
            return "MEDIUM"
        elif score >= 1.2:
            return "LOW-MEDIUM"
        else:
            return "LOW"

# Global instance for easy access
priority_manager = PrioritySourceManager()