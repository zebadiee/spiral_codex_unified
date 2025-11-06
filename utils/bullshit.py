#!/usr/bin/env python3
"""
Spiral Codex - Bullshit Sensor (Credibility Scoring System)
Implements multi-factor credibility assessment for ingested content.

Scoring components:
- SourceScore: Domain authority and provenance
- TranscriptQuality: Availability and lexical quality
- ConsensusScore: Cross-source factual agreement
- CitationDensity: Technical rigor and references
- FreshnessScore: Recency vs. topic type

Higher score = more trustworthy. Range: 0.0 to 1.0
"""

import re
from typing import Dict, List, Optional, Set, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum

class SourceType(str, Enum):
    """Categorized source types by authority level"""
    OFFICIAL = "official"           # IET, IEEE, BSI, gov.uk
    INSTITUTIONAL = "institutional" # Universities, research labs
    PUBLISHER = "publisher"         # O'Reilly, Wiley, technical publishers
    VERIFIED = "verified"           # Verified experts/channels
    COMMUNITY = "community"         # Stack Overflow, technical blogs
    UNKNOWN = "unknown"            # Unverified sources

class TopicType(str, Enum):
    """Topic classification for freshness weighting"""
    REGULATION = "regulation"       # BS 7671, electrical regulations
    STANDARD = "standard"           # Technical standards
    FUNDAMENTAL = "fundamental"     # Physics, math, core theory
    TOOL = "tool"                  # Software, frameworks
    PRACTICE = "practice"          # Best practices, patterns

@dataclass
class CredibilityScore:
    """Complete credibility assessment result"""
    total: float
    source_score: float
    transcript_quality: float
    consensus_score: float
    citation_density: float
    freshness_score: float
    trust_level: str  # "high", "medium", "low"
    
    def to_dict(self) -> Dict:
        return {
            "total": round(self.total, 3),
            "source_score": round(self.source_score, 3),
            "transcript_quality": round(self.transcript_quality, 3),
            "consensus_score": round(self.consensus_score, 3),
            "citation_density": round(self.citation_density, 3),
            "freshness_score": round(self.freshness_score, 3),
            "trust_level": self.trust_level
        }

# Default scoring weights (tunable via config)
DEFAULT_WEIGHTS = {
    "source": 0.35,
    "transcript": 0.25,
    "consensus": 0.15,
    "citation": 0.15,
    "freshness": 0.10
}

# Authoritative domain patterns
OFFICIAL_DOMAINS = {
    "theiet.org", "iet.org",
    "ieee.org", "ieeexplore.ieee.org",
    "gov.uk", "legislation.gov.uk",
    "bsigroup.com", "shop.bsigroup.com",
    "iec.ch",
    "arxiv.org",
    "archive.org"
}

INSTITUTIONAL_DOMAINS = {
    ".ac.uk", ".edu", ".edu.au",
    "mit.edu", "stanford.edu", "ox.ac.uk", "cam.ac.uk"
}

PUBLISHER_DOMAINS = {
    "oreilly.com", "wiley.com", "springer.com",
    "elsevier.com", "pearson.com", "routledge.com"
}

# Technical standards and reference patterns
STANDARD_PATTERNS = [
    r"\bBS\s*7671\b",
    r"\bIEEE\s*\d+",
    r"\bIEC\s*\d+",
    r"\bISO\s*\d+",
    r"\b(?:AS|NZS)\s*\d+",
]

# Technical claim patterns (for citation density)
TECHNICAL_PATTERNS = [
    r"\b(?:equation|formula|theorem|lemma|proof)\s*\d*\b",
    r"\b(?:figure|table|diagram)\s*\d+",
    r"\[[^\]]{1,50}\]",  # Citation brackets
    r"\bZ[sn]\s*[<>=≤≥]\s*[\d.]+",  # Electrical impedance specs
    r"\bP\.?F\.?\s*=\s*cos\s*[φθ]",  # Power factor
    r"\b\d+\.?\d*\s*(?:kW|kVA|A|V|Ω|Hz|kWh)\b",  # Units
]

class BullshitSensor:
    """Main credibility scoring engine"""
    
    def __init__(self, weights: Optional[Dict[str, float]] = None):
        """
        Initialize sensor with custom weights
        
        Args:
            weights: Optional weight overrides for scoring components
        """
        self.weights = {**DEFAULT_WEIGHTS, **(weights or {})}
        self._normalize_weights()
    
    def _normalize_weights(self):
        """Ensure weights sum to 1.0"""
        total = sum(self.weights.values())
        if total > 0:
            self.weights = {k: v/total for k, v in self.weights.items()}
    
    def compute_score(
        self,
        domain: str,
        text: Optional[str] = None,
        transcript: Optional[str] = None,
        date: Optional[datetime] = None,
        topic_type: TopicType = TopicType.FUNDAMENTAL,
        cross_sources: Optional[List[Dict]] = None,
        metadata: Optional[Dict] = None
    ) -> CredibilityScore:
        """
        Compute comprehensive credibility score
        
        Args:
            domain: Source domain (e.g., "theiet.org")
            text: Full text content
            transcript: Transcript text if available
            date: Publication/upload date
            topic_type: Type of content for freshness weighting
            cross_sources: Other sources for consensus checking
            metadata: Additional metadata (channel, author, etc.)
        
        Returns:
            CredibilityScore with detailed breakdown
        """
        metadata = metadata or {}
        
        # Component scores
        src_score = self.source_score(domain, metadata)
        trans_score = self.transcript_quality(transcript)
        
        # Use transcript if available, else text
        content = transcript or text or ""
        cite_score = self.citation_density(content)
        fresh_score = self.freshness_score(date, topic_type)
        
        # Consensus requires cross-source data
        cons_score = 0.0
        if cross_sources and content:
            claims = self.extract_claims(content)
            cons_score = self.consensus_score(claims, cross_sources)
        
        # Weighted total
        total = (
            self.weights["source"] * src_score +
            self.weights["transcript"] * trans_score +
            self.weights["consensus"] * cons_score +
            self.weights["citation"] * cite_score +
            self.weights["freshness"] * fresh_score
        )
        
        # Clamp to [0, 1]
        total = max(0.0, min(1.0, total))
        
        # Trust level classification
        if total >= 0.70:
            trust_level = "high"
        elif total >= 0.50:
            trust_level = "medium"
        else:
            trust_level = "low"
        
        return CredibilityScore(
            total=total,
            source_score=src_score,
            transcript_quality=trans_score,
            consensus_score=cons_score,
            citation_density=cite_score,
            freshness_score=fresh_score,
            trust_level=trust_level
        )
    
    def source_score(self, domain: str, metadata: Dict) -> float:
        """
        Score source authority (0.0 to 1.0)
        
        Args:
            domain: Source domain
            metadata: Channel/author info
        
        Returns:
            Authority score
        """
        domain_lower = domain.lower()
        
        # Official/authoritative domains
        if domain_lower in OFFICIAL_DOMAINS:
            return 1.0
        
        # Institutional domains
        for inst_pattern in INSTITUTIONAL_DOMAINS:
            if inst_pattern in domain_lower:
                return 0.85
        
        # Publisher domains
        if domain_lower in PUBLISHER_DOMAINS:
            return 0.7
        
        # Verified channel/author
        if metadata.get("verified") or metadata.get("channel_verified"):
            return 0.6
        
        # Has author attribution and references
        if metadata.get("author") and metadata.get("has_references"):
            return 0.5
        
        # Unknown/unverified
        return 0.2
    
    def transcript_quality(self, transcript: Optional[str]) -> float:
        """
        Assess transcript quality (0.0 to 1.0)
        
        Args:
            transcript: Transcript text
        
        Returns:
            Quality score
        """
        if not transcript:
            return 0.0
        
        length = len(transcript.split())
        
        # Penalty for low quality indicators
        inaudible_count = len(re.findall(r"\[inaudible\]|\[unclear\]|\[\?\]", transcript, re.I))
        bracket_noise = len(re.findall(r"\[.*?\]", transcript))
        
        inaudible_penalty = min(0.3, inaudible_count * 0.05)
        noise_penalty = min(0.2, (bracket_noise - inaudible_count) * 0.02)
        
        # Lexical diversity (unique words / total words)
        words = transcript.lower().split()
        diversity = len(set(words)) / max(1, len(words))
        
        # Length bonus (normalize around 2000 words)
        length_score = min(1.0, length / 2000)
        
        # Combine factors
        quality = (
            0.4 * length_score +
            0.4 * diversity +
            0.2
        ) - inaudible_penalty - noise_penalty
        
        return max(0.0, min(1.0, quality))
    
    def extract_claims(self, text: str, max_claims: int = 20) -> Set[str]:
        """
        Extract factual claims from text
        
        Simple heuristic: sentences with standards, numbers, technical terms
        
        Args:
            text: Source text
            max_claims: Maximum claims to extract
        
        Returns:
            Set of normalized claim strings
        """
        if not text:
            return set()
        
        claims = set()
        
        # Split into sentences (simple)
        sentences = re.split(r'[.!?]\s+', text)
        
        for sent in sentences:
            sent_lower = sent.lower()
            
            # Look for standard references
            for pattern in STANDARD_PATTERNS:
                if re.search(pattern, sent, re.I):
                    # Normalize and store
                    claim = re.sub(r'\s+', ' ', sent[:200]).strip()
                    claims.add(claim)
                    break
            
            # Look for technical terms
            for pattern in TECHNICAL_PATTERNS:
                if re.search(pattern, sent, re.I):
                    claim = re.sub(r'\s+', ' ', sent[:200]).strip()
                    claims.add(claim)
                    break
            
            if len(claims) >= max_claims:
                break
        
        return claims
    
    def consensus_score(self, claims: Set[str], cross_sources: List[Dict]) -> float:
        """
        Check claim consensus across sources
        
        Args:
            claims: Extracted claims from target source
            cross_sources: List of dicts with 'text' or 'claims' fields
        
        Returns:
            Consensus score (0.0 to 1.0)
        """
        if not claims or not cross_sources:
            return 0.0
        
        matches = 0
        checks = 0
        
        for claim in claims:
            checks += 1
            claim_normalized = claim.lower()
            
            # Check if claim appears in any cross-source
            for src in cross_sources:
                src_text = src.get("text", "").lower()
                src_claims = src.get("claims", [])
                
                # Simple substring match (can be improved with embeddings)
                if claim_normalized in src_text:
                    matches += 1
                    break
                
                # Or check against extracted claims
                for sc in src_claims:
                    if claim_normalized in sc.lower() or sc.lower() in claim_normalized:
                        matches += 1
                        break
        
        return matches / max(1, checks)
    
    def citation_density(self, text: str) -> float:
        """
        Measure technical rigor via citation/reference density
        
        Args:
            text: Source text
        
        Returns:
            Density score (0.0 to 1.0)
        """
        if not text:
            return 0.0
        
        sentences = re.split(r'[.!?]\s+', text)
        if not sentences:
            return 0.0
        
        cited_sentences = 0
        
        for sent in sentences:
            # Check for technical patterns
            for pattern in TECHNICAL_PATTERNS + STANDARD_PATTERNS:
                if re.search(pattern, sent, re.I):
                    cited_sentences += 1
                    break
        
        density = cited_sentences / len(sentences)
        
        # Normalize (assume 30% citation rate is excellent)
        return min(1.0, density / 0.3)
    
    def freshness_score(
        self,
        date: Optional[datetime],
        topic_type: TopicType = TopicType.FUNDAMENTAL
    ) -> float:
        """
        Score recency based on topic type
        
        Args:
            date: Publication date
            topic_type: Type of content
        
        Returns:
            Freshness score (0.0 to 1.0)
        """
        if not date:
            # No date = assume medium freshness
            return 0.5
        
        now = datetime.utcnow()
        age_days = (now - date).days
        
        # Different decay rates by topic
        if topic_type == TopicType.REGULATION:
            # Regulations: prefer within 2 years
            half_life_days = 365 * 2
        elif topic_type == TopicType.STANDARD:
            # Standards: prefer within 3 years
            half_life_days = 365 * 3
        elif topic_type == TopicType.TOOL:
            # Tools: prefer within 1 year
            half_life_days = 365
        elif topic_type == TopicType.PRACTICE:
            # Practices: prefer within 2 years
            half_life_days = 365 * 2
        else:  # FUNDAMENTAL
            # Fundamentals: age matters less, but prefer classic or recent
            # Bonus for very old (classic) or very new
            if age_days > 365 * 10:  # Classic (10+ years)
                return 0.9
            half_life_days = 365 * 5
        
        # Exponential decay
        decay = 0.5 ** (age_days / half_life_days)
        
        return max(0.0, min(1.0, decay))


# Convenience functions for quick scoring

def score_source(
    domain: str,
    text: Optional[str] = None,
    transcript: Optional[str] = None,
    date: Optional[datetime] = None,
    **kwargs
) -> CredibilityScore:
    """
    Quick scoring function with default weights
    
    Args:
        domain: Source domain
        text: Content text
        transcript: Transcript text
        date: Publication date
        **kwargs: Additional metadata
    
    Returns:
        CredibilityScore
    """
    sensor = BullshitSensor()
    return sensor.compute_score(
        domain=domain,
        text=text,
        transcript=transcript,
        date=date,
        metadata=kwargs
    )

def is_trustworthy(score: CredibilityScore, min_threshold: float = 0.70) -> bool:
    """Check if score meets trust threshold"""
    return score.total >= min_threshold

def classify_trust(score: float) -> str:
    """Classify numeric score to trust level"""
    if score >= 0.70:
        return "high"
    elif score >= 0.50:
        return "medium"
    else:
        return "low"


# Export main classes and functions
__all__ = [
    "BullshitSensor",
    "CredibilityScore",
    "SourceType",
    "TopicType",
    "score_source",
    "is_trustworthy",
    "classify_trust",
    "DEFAULT_WEIGHTS"
]
