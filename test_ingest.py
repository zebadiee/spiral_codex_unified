#!/usr/bin/env python3
"""
Test suite for content ingestion pipeline
"""

import sys
import tempfile
from pathlib import Path
from datetime import datetime, timedelta

sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.ingest import ContentIngestionPipeline, IngestSource, ingest_url
from utils.bullshit import TopicType

def test_basic_ingestion():
    """Test basic content ingestion"""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmppath = Path(tmpdir)
        pipeline = ContentIngestionPipeline(
            data_dir=tmppath / "data",
            vault_dir=tmppath / "vault",
            ledger_dir=tmppath / "ledger"
        )
        
        # Ingest high-quality content
        content = pipeline.ingest(
            url="https://theiet.org/electrical-principles-lecture",
            title="Electrical Principles - BS 7671 Requirements",
            text="This lecture covers BS 7671 requirements for electrical installations. " * 100,
            transcript="According to BS 7671, maximum Zs for 32A Type B MCB is 1.37Ω. " * 50,
            date=datetime.utcnow() - timedelta(days=90),
            topic_type=TopicType.REGULATION,
            source_type="institutional",
            author="Dr. Smith",
            verified=True,
            license="CC-BY-4.0"
        )
        
        assert content is not None, "Should ingest content"
        assert content.credibility.trust_level in ("high", "medium"), "Should be trustworthy"
        assert content.transcript is not None, "Should have transcript"
        
        print(f"✅ Basic ingestion: {content.credibility.total:.3f} ({content.credibility.trust_level})")
        
        # Check database
        stats = pipeline.get_stats()
        assert stats['total_content'] == 1, "Should have 1 item"
        assert stats['with_transcript'] == 1, "Should have transcript"
        
        print(f"✅ Database stats: {stats}")

def test_duplicate_prevention():
    """Test that duplicates are prevented"""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmppath = Path(tmpdir)
        pipeline = ContentIngestionPipeline(data_dir=tmppath / "data")
        
        url = "https://example.com/test"
        
        # First ingest
        content1 = pipeline.ingest(
            url=url,
            title="Test Content",
            text="Test content text",
            source_type="test"
        )
        
        assert content1 is not None, "First ingest should succeed"
        
        # Second ingest (duplicate)
        content2 = pipeline.ingest(
            url=url,
            title="Test Content",
            text="Test content text",
            source_type="test"
        )
        
        assert content2 is None, "Duplicate should be filtered"
        
        stats = pipeline.get_stats()
        assert stats['total_content'] == 1, "Should only have 1 item"
        
        print("✅ Duplicate prevention works")

def test_trust_level_filtering():
    """Test trust level classification"""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmppath = Path(tmpdir)
        pipeline = ContentIngestionPipeline(data_dir=tmppath / "data")
        
        # High-trust source
        high_trust = pipeline.ingest(
            url="https://theiet.org/high-quality",
            title="IET Official Publication",
            text="Technical content with BS 7671 references. " * 100,
            transcript="Detailed transcript with IEEE 802.3 standards. " * 50,
            date=datetime.utcnow(),
            source_type="official",
            verified=True
        )
        
        # Low-trust source
        low_trust = pipeline.ingest(
            url="https://random-blog.xyz/post",
            title="Random Blog Post",
            text="Um, like, electricity is cool.",
            date=datetime.utcnow() - timedelta(days=365 * 5),
            source_type="unknown"
        )
        
        assert high_trust is not None
        assert low_trust is not None
        
        assert high_trust.credibility.total > low_trust.credibility.total
        print(f"✅ Trust levels: high={high_trust.credibility.total:.3f}, low={low_trust.credibility.total:.3f}")

def test_vault_note_generation():
    """Test vault note creation"""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmppath = Path(tmpdir)
        vault_dir = tmppath / "vault"
        
        pipeline = ContentIngestionPipeline(
            data_dir=tmppath / "data",
            vault_dir=vault_dir
        )
        
        content = pipeline.ingest(
            url="https://theiet.org/test-lecture",
            title="Test Lecture on Electrical Safety",
            text="Important safety standards for electrical work. " * 50,
            transcript="BS 7671 specifies requirements for safe installations. " * 30,
            date=datetime.utcnow(),
            source_type="institutional",
            verified=True
        )
        
        assert content is not None
        
        # Check if vault note was created
        vault_files = list((vault_dir / "03-Federated-Data").glob("*.md"))
        assert len(vault_files) > 0, "Should create vault note"
        
        note_content = vault_files[0].read_text()
        assert "BS 7671" in note_content, "Note should contain content"
        assert "credibility_score" in note_content, "Note should have frontmatter"
        
        print(f"✅ Vault note created: {vault_files[0].name}")

def test_search_high_trust():
    """Test searching for high-trust content"""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmppath = Path(tmpdir)
        pipeline = ContentIngestionPipeline(data_dir=tmppath / "data")
        
        # Ingest multiple items with different trust levels
        for i in range(5):
            pipeline.ingest(
                url=f"https://theiet.org/lecture-{i}",
                title=f"Lecture {i}",
                text=f"Technical content with standards BS {7670+i}. " * 50,
                date=datetime.utcnow(),
                source_type="official"
            )
        
        for i in range(3):
            pipeline.ingest(
                url=f"https://random-blog.com/post-{i}",
                title=f"Blog Post {i}",
                text="Random content",
                source_type="unknown"
            )
        
        # Search for high-trust only
        high_trust_items = pipeline.search_high_trust(min_score=0.50)
        
        assert len(high_trust_items) > 0, "Should find high-trust items"
        assert all(item['credibility_score'] >= 0.50 for item in high_trust_items)
        
        print(f"✅ Found {len(high_trust_items)} high-trust items")

def run_all_tests():
    """Run complete test suite"""
    print("🧪 Running Ingest Pipeline Test Suite\n")
    
    test_basic_ingestion()
    test_duplicate_prevention()
    test_trust_level_filtering()
    test_vault_note_generation()
    test_search_high_trust()
    
    print("\n" + "="*60)
    print("✨ All ingest pipeline tests passed!")
    print("="*60)

if __name__ == "__main__":
    run_all_tests()
