#!/usr/bin/env python3
"""
Spiral Codex - Content Ingestion Pipeline
Search → Fetch → Score → Index → Vault integration with privacy filtering

Handles:
- Multi-source discovery (YouTube, Internet Archive, ArXiv, institutional sites)
- Transcript extraction with legal safeguards
- Bullshit scoring and credibility assessment
- BM25 + vector indexing for RAG
- Vault note generation with ledger logging
- Privacy filtering integration
"""

import json
import hashlib
import re
import sqlite3
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from urllib.parse import urlparse
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.bullshit import BullshitSensor, CredibilityScore, TopicType
from utils.trials import log_success, log_failure

# Privacy filter integration (if available)
try:
    from utils.privacy_filter import should_ingest
    PRIVACY_FILTER_AVAILABLE = True
except ImportError:
    PRIVACY_FILTER_AVAILABLE = False
    def should_ingest(path: Path) -> bool:
        return True


@dataclass
class IngestSource:
    """Metadata for an ingest source"""
    url: str
    title: str
    domain: str
    source_type: str  # youtube, archive, arxiv, institutional, publisher
    date: Optional[datetime]
    author: Optional[str] = None
    channel: Optional[str] = None
    verified: bool = False
    license: Optional[str] = None
    
    def to_dict(self) -> Dict:
        d = asdict(self)
        if d['date']:
            d['date'] = d['date'].isoformat()
        return d

@dataclass
class IngestContent:
    """Processed content ready for indexing"""
    source: IngestSource
    raw_text: Optional[str]
    clean_text: Optional[str]
    transcript: Optional[str]
    summary: str
    key_terms: List[str]
    credibility: CredibilityScore
    
    def to_dict(self) -> Dict:
        return {
            "source": self.source.to_dict(),
            "has_transcript": self.transcript is not None,
            "summary": self.summary,
            "key_terms": self.key_terms,
            "credibility": self.credibility.to_dict()
        }


class ContentIngestionPipeline:
    """Main ingestion pipeline orchestrator"""
    
    def __init__(
        self,
        data_dir: Path = Path("data"),
        vault_dir: Optional[Path] = None,
        ledger_dir: Path = Path("ledger")
    ):
        """
        Initialize pipeline
        
        Args:
            data_dir: Directory for indexes and logs
            vault_dir: OMAi vault directory (optional)
            ledger_dir: Ledger directory for audit trail
        """
        self.data_dir = Path(data_dir)
        self.vault_dir = Path(vault_dir) if vault_dir else None
        self.ledger_dir = Path(ledger_dir)
        
        # Ensure directories exist
        self.data_dir.mkdir(parents=True, exist_ok=True)
        if self.vault_dir:
            self.vault_dir.mkdir(parents=True, exist_ok=True)
        self.ledger_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize components
        self.sensor = BullshitSensor()
        self.db_path = self.data_dir / "ingest.sqlite"
        self.log_path = self.data_dir / "ingest_log.jsonl"
        
        self._init_database()
    
    def _init_database(self):
        """Initialize SQLite database for content index"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Main content table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS content (
                id TEXT PRIMARY KEY,
                url TEXT UNIQUE NOT NULL,
                title TEXT,
                domain TEXT,
                source_type TEXT,
                date TEXT,
                author TEXT,
                channel TEXT,
                verified INTEGER,
                license TEXT,
                has_transcript INTEGER,
                raw_text TEXT,
                clean_text TEXT,
                transcript TEXT,
                summary TEXT,
                key_terms TEXT,
                credibility_score REAL,
                trust_level TEXT,
                source_score REAL,
                transcript_quality REAL,
                citation_density REAL,
                freshness_score REAL,
                indexed_at TEXT,
                vault_note_path TEXT
            )
        ''')
        
        # Create indexes
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_domain ON content(domain)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_credibility ON content(credibility_score DESC)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_trust ON content(trust_level)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_date ON content(date DESC)')
        
        conn.commit()
        conn.close()
    
    def _generate_content_id(self, url: str) -> str:
        """Generate deterministic ID from URL"""
        return hashlib.sha256(url.encode()).hexdigest()[:16]
    
    def _extract_domain(self, url: str) -> str:
        """Extract domain from URL"""
        parsed = urlparse(url)
        return parsed.netloc or parsed.path.split('/')[0]
    
    def _normalize_text(self, text: str) -> str:
        """Normalize text: remove timestamps, clean whitespace"""
        if not text:
            return ""
        
        # Remove timestamp patterns [00:00:00] or (00:00)
        text = re.sub(r'\[?\d{1,2}:\d{2}(?::\d{2})?\]?', '', text)
        
        # Remove filler words
        fillers = ['um', 'uh', 'er', 'ah', 'like', 'you know']
        for filler in fillers:
            text = re.sub(rf'\b{filler}\b', '', text, flags=re.I)
        
        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def _extract_summary(self, text: str, max_lines: int = 3) -> str:
        """Extract brief summary from text"""
        if not text:
            return ""
        
        sentences = re.split(r'[.!?]\s+', text)
        summary_sentences = sentences[:max_lines]
        return '. '.join(s.strip() for s in summary_sentences if s.strip()) + '.'
    
    def _extract_key_terms(self, text: str, max_terms: int = 10) -> List[str]:
        """Extract key technical terms (simple approach)"""
        if not text:
            return []
        
        # Look for capitalized terms and technical patterns
        terms = set()
        
        # Standards
        standards = re.findall(r'\b(?:BS|IEEE|IEC|ISO|AS|NZS)\s*\d+\b', text, re.I)
        terms.update(s.upper() for s in standards)
        
        # Technical terms (capitalized multi-word)
        tech_terms = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)+\b', text)
        terms.update(tech_terms[:5])
        
        # Electrical units and concepts
        electrical = re.findall(r'\b(?:voltage|current|resistance|impedance|power factor|transformer|circuit)\b', text, re.I)
        terms.update(electrical[:5])
        
        return list(terms)[:max_terms]
    
    def ingest(
        self,
        url: str,
        title: str,
        text: Optional[str] = None,
        transcript: Optional[str] = None,
        date: Optional[datetime] = None,
        topic_type: TopicType = TopicType.FUNDAMENTAL,
        **metadata
    ) -> Optional[IngestContent]:
        """
        Ingest a single content item
        
        Args:
            url: Source URL
            title: Content title
            text: Main content text
            transcript: Transcript if available
            date: Publication date
            topic_type: Content topic classification
            **metadata: Additional metadata (author, channel, verified, license)
        
        Returns:
            IngestContent if successful, None if filtered or failed
        """
        try:
            # Check if already ingested
            content_id = self._generate_content_id(url)
            if self._is_indexed(content_id):
                log_success("ingest_skip", context=url, reason="already_indexed")
                return None
            
            # Build source metadata
            domain = self._extract_domain(url)
            source = IngestSource(
                url=url,
                title=title,
                domain=domain,
                source_type=metadata.get('source_type', 'unknown'),
                date=date,
                author=metadata.get('author'),
                channel=metadata.get('channel'),
                verified=metadata.get('verified', False),
                license=metadata.get('license')
            )
            
            # Process content
            raw_text = text
            clean_text = self._normalize_text(text) if text else None
            clean_transcript = self._normalize_text(transcript) if transcript else None
            
            # Use transcript preferentially for summary/terms
            primary_text = clean_transcript or clean_text or ""
            summary = self._extract_summary(primary_text)
            key_terms = self._extract_key_terms(primary_text)
            
            # Compute credibility score
            credibility = self.sensor.compute_score(
                domain=domain,
                text=clean_text,
                transcript=clean_transcript,
                date=date,
                topic_type=topic_type,
                metadata=metadata
            )
            
            # Build content object
            content = IngestContent(
                source=source,
                raw_text=raw_text,
                clean_text=clean_text,
                transcript=clean_transcript,
                summary=summary,
                key_terms=key_terms,
                credibility=credibility
            )
            
            # Store in database
            self._store_content(content_id, content)
            
            # Generate vault note if vault directory provided
            vault_path = None
            if self.vault_dir and credibility.trust_level in ("high", "medium"):
                vault_path = self._create_vault_note(content_id, content)
            
            # Log to ledger
            self._log_to_ledger(content_id, content, vault_path)
            
            # Log success
            log_success(
                "ingest_complete",
                context=url,
                content_id=content_id,
                credibility=credibility.total,
                trust_level=credibility.trust_level
            )
            
            return content
            
        except Exception as e:
            log_failure("ingest_failed", e, context=url)
            return None
    
    def _is_indexed(self, content_id: str) -> bool:
        """Check if content is already indexed"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT 1 FROM content WHERE id = ?', (content_id,))
        exists = cursor.fetchone() is not None
        conn.close()
        return exists
    
    def _store_content(self, content_id: str, content: IngestContent):
        """Store content in SQLite database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO content VALUES (
                ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
            )
        ''', (
            content_id,
            content.source.url,
            content.source.title,
            content.source.domain,
            content.source.source_type,
            content.source.date.isoformat() if content.source.date else None,
            content.source.author,
            content.source.channel,
            int(content.source.verified),
            content.source.license,
            int(content.transcript is not None),
            content.raw_text,
            content.clean_text,
            content.transcript,
            content.summary,
            ','.join(content.key_terms),
            content.credibility.total,
            content.credibility.trust_level,
            content.credibility.source_score,
            content.credibility.transcript_quality,
            content.credibility.citation_density,
            content.credibility.freshness_score,
            datetime.utcnow().isoformat(),
            None  # vault_note_path filled later
        ))
        
        conn.commit()
        conn.close()
    
    def _create_vault_note(self, content_id: str, content: IngestContent) -> Optional[Path]:
        """
        Create OMAi vault note with frontmatter
        
        Args:
            content_id: Content ID
            content: Ingested content
        
        Returns:
            Path to created note, or None if filtered
        """
        if not self.vault_dir:
            return None
        
        # Sanitize title for filename
        safe_title = re.sub(r'[^\w\s-]', '', content.source.title)[:50]
        safe_title = re.sub(r'[-\s]+', '-', safe_title).strip('-')
        
        note_filename = f"{content_id}-{safe_title}.md"
        note_path = self.vault_dir / "03-Federated-Data" / note_filename
        note_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Check privacy filter
        if PRIVACY_FILTER_AVAILABLE and not should_ingest(note_path):
            return None
        
        # Build frontmatter
        frontmatter = {
            "type": "training-source",
            "source": content.source.source_type,
            "url": content.source.url,
            "domain": content.source.domain,
            "date": content.source.date.isoformat() if content.source.date else None,
            "author": content.source.author,
            "channel": content.source.channel,
            "verified": content.source.verified,
            "license": content.source.license or "See source",
            "credibility_score": round(content.credibility.total, 3),
            "trust_level": content.credibility.trust_level,
            "has_transcript": content.transcript is not None,
            "ingest_id": content_id,
            "ingested_at": datetime.utcnow().isoformat() + "Z"
        }
        
        # Build note content
        note_content = f"""---
{chr(10).join(f'{k}: {json.dumps(v) if not isinstance(v, (str, int, float, bool, type(None))) else v}' for k, v in frontmatter.items())}
---

# {content.source.title}

## Summary

{content.summary}

## Key Terms

{', '.join(f'`{term}`' for term in content.key_terms)}

## Credibility Assessment

- **Overall Score**: {content.credibility.total:.3f} ({content.credibility.trust_level} trust)
- **Source Authority**: {content.credibility.source_score:.3f}
- **Transcript Quality**: {content.credibility.transcript_quality:.3f}
- **Citation Density**: {content.credibility.citation_density:.3f}
- **Freshness**: {content.credibility.freshness_score:.3f}

## Content

{'### Transcript' if content.transcript else '### Full Text'}

{content.transcript or content.clean_text or 'No content available'}

---

*Source: [{content.source.domain}]({content.source.url})*  
*Ingested: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}*  
*Content ID: `{content_id}`*
"""
        
        # Write note
        note_path.write_text(note_content, encoding='utf-8')
        
        # Update database with vault path
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            'UPDATE content SET vault_note_path = ? WHERE id = ?',
            (str(note_path), content_id)
        )
        conn.commit()
        conn.close()
        
        return note_path
    
    def _log_to_ledger(
        self,
        content_id: str,
        content: IngestContent,
        vault_path: Optional[Path]
    ):
        """Log ingestion to ledger"""
        ledger_path = self.ledger_dir / "ingest.jsonl"
        
        entry = {
            "ts": datetime.utcnow().isoformat() + "Z",
            "op": "ingest",
            "content_id": content_id,
            "url": content.source.url,
            "domain": content.source.domain,
            "credibility_score": content.credibility.total,
            "trust_level": content.credibility.trust_level,
            "has_transcript": content.transcript is not None,
            "vault_note": str(vault_path) if vault_path else None,
            "success": True
        }
        
        # Compute checksum
        entry_str = json.dumps(entry, sort_keys=True)
        entry["checksum"] = hashlib.sha256(entry_str.encode()).hexdigest()[:16]
        
        # Append to ledger
        with ledger_path.open('a', encoding='utf-8') as f:
            f.write(json.dumps(entry) + '\n')
    
    def search_high_trust(
        self,
        min_score: float = 0.70,
        limit: int = 10
    ) -> List[Dict]:
        """
        Search for high-trust content
        
        Args:
            min_score: Minimum credibility score
            limit: Maximum results
        
        Returns:
            List of content dictionaries
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM content
            WHERE credibility_score >= ?
            ORDER BY credibility_score DESC, date DESC
            LIMIT ?
        ''', (min_score, limit))
        
        results = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return results
    
    def get_stats(self) -> Dict:
        """Get ingestion statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) FROM content')
        total = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM content WHERE trust_level = "high"')
        high_trust = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM content WHERE has_transcript = 1')
        with_transcript = cursor.fetchone()[0]
        
        cursor.execute('SELECT AVG(credibility_score) FROM content')
        avg_score = cursor.fetchone()[0] or 0.0
        
        conn.close()
        
        return {
            "total_content": total,
            "high_trust": high_trust,
            "with_transcript": with_transcript,
            "average_credibility": round(avg_score, 3)
        }


# Convenience function
def ingest_url(
    url: str,
    title: str,
    text: Optional[str] = None,
    transcript: Optional[str] = None,
    **kwargs
) -> Optional[IngestContent]:
    """
    Quick ingest function
    
    Args:
        url: Source URL
        title: Content title
        text: Main text
        transcript: Transcript if available
        **kwargs: Additional metadata
    
    Returns:
        IngestContent if successful
    """
    pipeline = ContentIngestionPipeline()
    return pipeline.ingest(url, title, text=text, transcript=transcript, **kwargs)


__all__ = [
    "ContentIngestionPipeline",
    "IngestSource",
    "IngestContent",
    "ingest_url"
]
