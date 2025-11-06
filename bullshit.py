#!/usr/bin/env python3
"""
bullshit.py - Bullshit Scoring System for Ethical Content Ingestion

Implements a comprehensive scoring system (0-1 scale) to evaluate content credibility
based on source validation, transcript quality, consensus scoring, and citation density.

Formula: bullshit_score = (source_weight * 0.3) + (quality_weight * 0.25) + (consensus_weight * 0.25) + (citation_weight * 0.2)
Lower scores indicate higher credibility (0 = most credible, 1 = bullshit)
"""

import re
import hashlib
import datetime
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Tuple, Any
from urllib.parse import urlparse
import json
from pathlib import Path


@dataclass
class ContentMetadata:
    """Metadata for content being scored"""
    url: str
    title: str
    content: str
    source_type: str  # reddit, arxiv, youtube, archive, pdf
    author: Optional[str] = None
    publish_date: Optional[str] = None
    license: Optional[str] = None
    word_count: int = 0
    citation_count: int = 0
    references: List[str] = field(default_factory=list)
    fetch_metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class BullshitScore:
    """Comprehensive bullshit scoring result"""
    overall_score: float  # 0-1, lower is better
    source_score: float
    quality_score: float
    consensus_score: float
    citation_score: float
    freshness_score: float
    confidence: float
    details: Dict[str, Any] = field(default_factory=dict)
    recommendations: List[str] = field(default_factory=list)


class BullshitScorer:
    """Advanced bullshit detection and credibility scoring system"""

    def __init__(self, config_path: Optional[str] = None):
        self.config = self._load_config(config_path)
        self.trusted_sources = self._load_trusted_sources()
        self.red_flags = self._load_red_flags()
        self.quality_indicators = self._load_quality_indicators()

    def _load_config(self, config_path: Optional[str]) -> Dict[str, Any]:
        """Load scoring configuration"""
        default_config = {
            "source_weights": {
                "arxiv": 0.1,      # Very high credibility
                "reddit": 0.6,     # Medium credibility, depends on subreddit
                "youtube": 0.7,    # Lower credibility, depends on channel
                "archive": 0.3,    # Good credibility if from reputable source
                "pdf": 0.4,        # Varies widely
                "news": 0.3,       # Varies by publication
                "blog": 0.8        # Generally lower credibility
            },
            "quality_thresholds": {
                "min_word_count": 100,
                "min_sentence_length": 5,
                "max_repetition_ratio": 0.3,
                "grammar_penalty_threshold": 0.2
            },
            "citation_requirements": {
                "academic_min": 5,
                "technical_min": 3,
                "news_min": 2,
                "opinion_min": 0
            },
            "freshness_weights": {
                "very_fresh": 0.0,    # < 1 day
                "fresh": 0.1,         # < 1 week
                "recent": 0.2,        # < 1 month
                "moderate": 0.3,      # < 6 months
                "old": 0.5,           # < 1 year
                "very_old": 0.8       # > 1 year
            }
        }

        if config_path and Path(config_path).exists():
            try:
                with open(config_path, 'r') as f:
                    user_config = json.load(f)
                default_config.update(user_config)
            except Exception:
                pass  # Use defaults if config fails to load

        return default_config

    def _load_trusted_sources(self) -> Dict[str, float]:
        """Load trusted source domains and their credibility scores"""
        return {
            # Academic domains
            "arxiv.org": 0.05,
            "scholar.google.com": 0.05,
            "ieee.org": 0.1,
            "acm.org": 0.1,
            "nature.com": 0.05,
            "science.org": 0.05,
            "springer.com": 0.1,
            "sciencedirect.com": 0.1,

            # Government domains
            "gov": 0.1,
            "nasa.gov": 0.05,
            "nist.gov": 0.05,
            "ietf.org": 0.1,

            # Reputable news (lower is better)
            "reuters.com": 0.2,
            "ap.org": 0.2,
            "bbc.com": 0.25,
            "npr.org": 0.3,

            # Technical resources
            "stackoverflow.com": 0.3,
            "github.com": 0.2,
            "medium.com": 0.6,  # Varies widely

            # Reddit - varies by subreddit
            "reddit.com": 0.5,  # Base score, will be adjusted
        }

    def _load_red_flags(self) -> List[str]:
        """Load red flag patterns that indicate potential bullshit"""
        return [
            # Clickbait patterns
            r"you won't believe",
            r"shocking.*truth",
            r"doctors hate",
            r"one weird trick",
            r"must see.*now",
            r"urgent.*alert",

            # Pseudoscience markers
            r"miracle.*cure",
            r"ancient.*secret",
            r"big.*pharma.*hides",
            r"natural.*alternative",
            r"toxins.*cleanse",
            r"quantum.*healing",

            # Conspiracy markers
            r"they don't want.*know",
            r"hidden.*truth",
            r"mainstream.*lies",
            r"deep.*state",
            r"globalist.*agenda",

            # Unreliable claims
            r"100%.*effective",
            r"proven.*fact",
            r"scientists.*prove",
            r"studies.*show.*always",

            # Sensationalism
            r"!!!{3,}",
            r"\?{3,}",
            r"ALL CAPS",
            r"breaking.*exclusive",
        ]

    def _load_quality_indicators(self) -> List[str]:
        """Load patterns that indicate high-quality content"""
        return [
            # Academic indicators
            r"\[\d+\]",  # Citations
            r"et al\.",
            r"\d{4}",   # Year references
            r"abstract",
            r"methodology",
            r"results",
            r"conclusion",

            # Technical indicators
            r"https?://[^\s]+\.(edu|gov|org)",
            r"doi\.org",
            r"isbn",
            r"figure \d+",
            r"table \d+",

            # balanced reporting
            r"however",
            r"on the other hand",
            r"critics argue",
            r"proponents suggest",
            r"further research",
        ]

    def score_content(self, metadata: ContentMetadata) -> BullshitScore:
        """Generate comprehensive bullshit score for content"""

        # Component scores
        source_score = self._score_source(metadata)
        quality_score = self._score_quality(metadata)
        consensus_score = self._score_consensus(metadata)
        citation_score = self._score_citations(metadata)
        freshness_score = self._score_freshness(metadata)

        # Calculate overall score (weighted average)
        weights = self.config.get("weights", {
            "source": 0.3,
            "quality": 0.25,
            "consensus": 0.25,
            "citation": 0.2
        })

        overall_score = (
            source_score * weights["source"] +
            quality_score * weights["quality"] +
            consensus_score * weights["consensus"] +
            citation_score * weights["citation"]
        )

        # Apply freshness penalty
        overall_score = min(1.0, overall_score + freshness_score * 0.1)

        # Calculate confidence based on available data
        confidence = self._calculate_confidence(metadata, {
            "source": source_score,
            "quality": quality_score,
            "consensus": consensus_score,
            "citation": citation_score
        })

        # Generate recommendations
        recommendations = self._generate_recommendations(metadata, {
            "source": source_score,
            "quality": quality_score,
            "consensus": consensus_score,
            "citation": citation_score,
            "overall": overall_score
        })

        return BullshitScore(
            overall_score=round(overall_score, 3),
            source_score=round(source_score, 3),
            quality_score=round(quality_score, 3),
            consensus_score=round(consensus_score, 3),
            citation_score=round(citation_score, 3),
            freshness_score=round(freshness_score, 3),
            confidence=round(confidence, 3),
            details={
                "source_type": metadata.source_type,
                "word_count": metadata.word_count,
                "citation_count": metadata.citation_count,
                "has_references": len(metadata.references) > 0,
                "red_flags_found": self._find_red_flags(metadata.content),
                "quality_indicators": self._find_quality_indicators(metadata.content)
            },
            recommendations=recommendations
        )

    def _score_source(self, metadata: ContentMetadata) -> float:
        """Score content based on source credibility"""
        try:
            parsed_url = urlparse(metadata.url)
            domain = parsed_url.netloc.lower()

            # Check exact domain matches
            for trusted_domain, score in self.trusted_sources.items():
                if trusted_domain in domain:
                    base_score = score
                    break
            else:
                # Default score for unknown domains
                base_score = self.config["source_weights"].get(metadata.source_type, 0.5)

            # Adjust for Reddit-specific logic
            if "reddit.com" in domain and metadata.source_type == "reddit":
                base_score = self._score_reddit_source(metadata)

            # Adjust for YouTube-specific logic
            elif "youtube.com" in domain and metadata.source_type == "youtube":
                base_score = self._score_youtube_source(metadata)

            # Penalty for URL shorteners and suspicious domains
            suspicious_patterns = ["bit.ly", "t.co", "tinyurl.com", "ow.ly"]
            if any(pattern in domain for pattern in suspicious_patterns):
                base_score += 0.2

            return min(1.0, max(0.0, base_score))

        except Exception:
            return 0.5  # Default score if URL parsing fails

    def _score_reddit_source(self, metadata: ContentMetadata) -> float:
        """Score Reddit content based on subreddit credibility"""
        # Extract subreddit from URL or metadata
        subreddit = "unknown"

        if "reddit.com" in metadata.url:
            try:
                match = re.search(r"/r/([^/]+)", metadata.url)
                if match:
                    subreddit = match.group(1).lower()
            except Exception:
                pass

        # Score based on subreddit type
        academic_subreddits = [
            "askscience", "science", "physics", "chemistry", "biology",
            "math", "engineering", "computer", "programming", "statistics"
        ]

        professional_subreddits = [
            "sysadmin", "networking", "security", "devops", "data",
            "machinelearning", "webdev", "java", "python"
        ]

        general_discussion = [
            "todayilearned", "explainlikeimfive", "technology", "gadgets"
        ]

        high_risk_subreddits = [
            "conspiracy", "unpopularopinion", "rant", "politics"
        ]

        if subreddit in academic_subreddits:
            return 0.3
        elif subreddit in professional_subreddits:
            return 0.4
        elif subreddit in general_discussion:
            return 0.5
        elif subreddit in high_risk_subreddits:
            return 0.8
        else:
            return 0.6  # Default for unknown subreddits

    def _score_youtube_source(self, metadata: ContentMetadata) -> float:
        """Score YouTube content based on channel credibility"""
        # This would ideally check channel reputation, subscriber count, etc.
        # For now, use content-based heuristics

        content_lower = metadata.content.lower()

        # Educational indicators
        educational_keywords = [
            "tutorial", "lecture", "course", "university", "mit",
            "stanford", "khan academy", "crash course", "educational"
        ]

        if any(keyword in content_lower for keyword in educational_keywords):
            return 0.4

        # Technical content indicators
        technical_keywords = [
            "how to", "tutorial", "guide", "step by step", "installation",
            "configuration", "troubleshooting", "fix", "repair"
        ]

        if any(keyword in content_lower for keyword in technical_keywords):
            return 0.5

        # Entertainment/clickbait indicators
        clickbait_keywords = [
            "shocking", "unbelievable", "crazy", "insane", "mysterious",
            "secret", "revealed", "exposed", "conspiracy"
        ]

        if any(keyword in content_lower for keyword in clickbait_keywords):
            return 0.8

        return 0.6  # Default YouTube score

    def _score_quality(self, metadata: ContentMetadata) -> float:
        """Score content based on writing quality and structure"""
        content = metadata.content
        score = 0.5  # Base score

        # Length penalties/rewards
        word_count = len(content.split())
        if word_count < self.config["quality_thresholds"]["min_word_count"]:
            score += 0.3  # Penalty for too short
        elif word_count > 1000:
            score -= 0.1  # Reward for substantial content

        # Grammar and readability checks
        sentence_pattern = r'[.!?]+'
        sentences = re.split(sentence_pattern, content)
        avg_sentence_length = sum(len(s.split()) for s in sentences) / max(len(sentences), 1)

        if avg_sentence_length < self.config["quality_thresholds"]["min_sentence_length"]:
            score += 0.2  # Penalty for choppy sentences

        # Repetition detection
        words = content.lower().split()
        word_freq = {}
        for word in words:
            if len(word) > 3:  # Ignore short words
                word_freq[word] = word_freq.get(word, 0) + 1

        if word_freq:
            max_freq = max(word_freq.values())
            repetition_ratio = max_freq / len(words)
            if repetition_ratio > self.config["quality_thresholds"]["max_repetition_ratio"]:
                score += 0.2  # Penalty for excessive repetition

        # Structure analysis
        has_paragraphs = len(content.split('\n\n')) > 1
        has_capitalization = content != content.lower()
        has_punctuation = any(char in content for char in '.!?')

        if not has_paragraphs:
            score += 0.1
        if not has_capitalization:
            score += 0.1
        if not has_punctuation:
            score += 0.1

        # Red flag detection
        red_flags = self._find_red_flags(content)
        score += len(red_flags) * 0.05

        # Quality indicator detection
        quality_indicators = self._find_quality_indicators(content)
        score -= len(quality_indicators) * 0.02

        return min(1.0, max(0.0, score))

    def _score_consensus(self, metadata: ContentMetadata) -> float:
        """Score content based on consensus and cross-referencing"""
        # This would ideally check the content against multiple sources
        # For now, use proxy measures

        score = 0.5  # Base score

        content = metadata.content.lower()

        # Consensus indicators
        consensus_keywords = [
            "research shows", "studies indicate", "experts agree",
            "widely accepted", "consensus", "peer reviewed",
            "meta analysis", "systematic review", "multiple studies"
        ]

        consensus_count = sum(1 for keyword in consensus_keywords if keyword in content)
        score -= consensus_count * 0.05

        # Contrarian indicators
        contrarian_keywords = [
            "mainstream is wrong", "they don't want you to know",
            "conspiracy", "cover up", "hidden truth", "real story"
        ]

        contrarian_count = sum(1 for keyword in contrarian_keywords if keyword in content)
        score += contrarian_count * 0.1

        # Balanced language indicators
        balanced_keywords = [
            "however", "on the other hand", "critics argue",
            "some studies suggest", "evidence is mixed",
            "further research needed", "limitations"
        ]

        balanced_count = sum(1 for keyword in balanced_keywords if keyword in content)
        score -= balanced_count * 0.03

        return min(1.0, max(0.0, score))

    def _score_citations(self, metadata: ContentMetadata) -> float:
        """Score content based on citation density and quality"""
        content = metadata.content
        citation_count = metadata.citation_count
        references = metadata.references

        score = 0.5  # Base score

        # Citation density
        word_count = len(content.split())
        if word_count > 0:
            citation_density = citation_count / word_count * 1000  # Citations per 1000 words

            # Academic standards
            if citation_density > 10:  # Very well cited
                score -= 0.3
            elif citation_density > 5:  # Well cited
                score -= 0.2
            elif citation_density > 2:  # Moderately cited
                score -= 0.1
            elif citation_density == 0 and word_count > 500:  # Long but no citations
                score += 0.2

        # Reference quality
        if references:
            academic_domains = ['.edu', '.gov', 'arxiv.org', 'ieee.org', 'acm.org', 'nature.com', 'science.org']
            academic_refs = sum(1 for ref in references if any(domain in ref.lower() for domain in academic_domains))

            if academic_refs > 0:
                score -= academic_refs * 0.05

        # Citation format indicators
        citation_patterns = [
            r'\[\d+\]',  # Numeric citations [1], [2]
            r'\(\d{4}\)',  # Year citations (2023)
            r'et al\.',  # Academic et al.
            r'doi:',  # DOI references
            r'pp\.\s*\d+',  # Page numbers
        ]

        pattern_matches = sum(len(re.findall(pattern, content)) for pattern in citation_patterns)
        if pattern_matches > 0:
            score -= min(0.2, pattern_matches * 0.02)

        return min(1.0, max(0.0, score))

    def _score_freshness(self, metadata: ContentMetadata) -> float:
        """Score content based on freshness and relevance"""
        if not metadata.publish_date:
            return 0.5  # No date available

        try:
            # Parse various date formats
            publish_date = self._parse_date(metadata.publish_date)
            if not publish_date:
                return 0.5

            now = datetime.datetime.now()
            age_days = (now - publish_date).days

            # Apply freshness weights from config
            weights = self.config["freshness_weights"]

            if age_days < 1:
                return weights["very_fresh"]
            elif age_days < 7:
                return weights["fresh"]
            elif age_days < 30:
                return weights["recent"]
            elif age_days < 180:
                return weights["moderate"]
            elif age_days < 365:
                return weights["old"]
            else:
                return weights["very_old"]

        except Exception:
            return 0.5

    def _parse_date(self, date_str: str) -> Optional[datetime.datetime]:
        """Parse various date formats"""
        formats = [
            "%Y-%m-%d",
            "%Y-%m-%dT%H:%M:%S",
            "%Y-%m-%dT%H:%M:%SZ",
            "%Y/%m/%d",
            "%d/%m/%Y",
            "%B %d, %Y",
            "%d %B %Y",
        ]

        for fmt in formats:
            try:
                return datetime.datetime.strptime(date_str, fmt)
            except ValueError:
                continue

        return None

    def _find_red_flags(self, content: str) -> List[str]:
        """Find red flag patterns in content"""
        content_lower = content.lower()
        found_flags = []

        for pattern in self.red_flags:
            if re.search(pattern, content_lower, re.IGNORECASE):
                found_flags.append(pattern)

        return found_flags

    def _find_quality_indicators(self, content: str) -> List[str]:
        """Find quality indicator patterns in content"""
        content_lower = content.lower()
        found_indicators = []

        for pattern in self.quality_indicators:
            if re.search(pattern, content_lower, re.IGNORECASE):
                found_indicators.append(pattern)

        return found_indicators

    def _calculate_confidence(self, metadata: ContentMetadata, scores: Dict[str, float]) -> float:
        """Calculate confidence in the scoring based on available data"""
        confidence = 0.5  # Base confidence

        # Increase confidence with more metadata
        if metadata.author:
            confidence += 0.1
        if metadata.publish_date:
            confidence += 0.1
        if metadata.license:
            confidence += 0.1
        if metadata.references:
            confidence += 0.1
        if metadata.word_count > 100:
            confidence += 0.1

        # Increase confidence if scores are consistent
        score_values = list(scores.values())
        if len(score_values) > 1:
            score_variance = max(score_values) - min(score_values)
            if score_variance < 0.3:  # Consistent scores
                confidence += 0.1

        return min(1.0, confidence)

    def _generate_recommendations(self, metadata: ContentMetadata, scores: Dict[str, float]) -> List[str]:
        """Generate recommendations based on scoring results"""
        recommendations = []

        if scores["overall"] > 0.7:
            recommendations.append("HIGH BULLSHIT RISK: Verify this content with trusted sources")
        elif scores["overall"] > 0.5:
            recommendations.append("MODERATE RISK: Cross-reference with additional sources")

        if scores["source"] > 0.6:
            recommendations.append("SOURCE WARNING: Source has low credibility")

        if scores["quality"] > 0.6:
            recommendations.append("QUALITY WARNING: Poor writing quality or structure")

        if scores["citation"] > 0.7:
            recommendations.append("CITATION WARNING: Lacks proper citations or references")

        if scores["consensus"] > 0.6:
            recommendations.append("CONSENSUS WARNING: Contrarian or unverified claims")

        if metadata.word_count < 100:
            recommendations.append("LENGTH WARNING: Content is very short, may lack context")

        red_flags = self._find_red_flags(metadata.content)
        if red_flags:
            recommendations.append(f"RED FLAGS DETECTED: {len(red_flags)} suspicious patterns found")

        if not recommendations:
            recommendations.append("Content appears credible based on available indicators")

        return recommendations

    def batch_score(self, metadata_list: List[ContentMetadata]) -> List[BullshitScore]:
        """Score multiple content items efficiently"""
        return [self.score_content(metadata) for metadata in metadata_list]

    def get_credibility_tier(self, score: BullshitScore) -> str:
        """Get credibility tier based on bullshit score"""
        if score.overall_score < 0.2:
            return "HIGHLY_CREDIBLE"
        elif score.overall_score < 0.4:
            return "CREDIBLE"
        elif score.overall_score < 0.6:
            return "MODERATE"
        elif score.overall_score < 0.8:
            return "QUESTIONABLE"
        else:
            return "HIGH_BULLSHIT_RISK"


def main():
    """Example usage of the bullshit scoring system"""
    scorer = BullshitScorer()

    # Example content
    metadata = ContentMetadata(
        url="https://arxiv.org/abs/2301.07041",
        title="Attention Is All You Need",
        content="This paper introduces the Transformer architecture...",
        source_type="arxiv",
        author="Vaswani et al.",
        publish_date="2023-01-01",
        word_count=5000,
        citation_count=15,
        references=["https://arxiv.org/abs/1706.03762"]
    )

    score = scorer.score_content(metadata)

    print(f"Bullshit Score: {score.overall_score}")
    print(f"Credibility Tier: {scorer.get_credibility_tier(score)}")
    print(f"Component Scores: Source={score.source_score}, Quality={score.quality_score}, Consensus={score.consensus_score}, Citations={score.citation_score}")
    print(f"Confidence: {score.confidence}")
    print("Recommendations:")
    for rec in score.recommendations:
        print(f"  - {rec}")


if __name__ == "__main__":
    main()