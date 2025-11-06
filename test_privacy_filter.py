#!/usr/bin/env python3
"""Test privacy filter in OMAi ingest"""
import tempfile
import json
from pathlib import Path
from omai_ingest import OMAiIngestor

def test_privacy_filter():
    """Test various privacy scenarios"""
    with tempfile.TemporaryDirectory() as tmpdir:
        vault = Path(tmpdir)
        
        # Test 1: Frontmatter private: true
        (vault / "private_fm.md").write_text("""---
title: Secret Note
private: true
---
This should be skipped.""")
        
        # Test 2: #private tag in content
        (vault / "tagged.md").write_text("""# Public content
But this note is #private so skip it""")
        
        # Test 3: Private path
        private_dir = vault / "_private"
        private_dir.mkdir()
        (private_dir / "secret.md").write_text("Secret stuff")
        
        # Test 4: Public note (should be included)
        (vault / "public.md").write_text("""---
title: Public Note
tags: [work, planning]
---
This is public content.""")
        
        # Test 5: Underscore prefix filename
        (vault / "_draft.md").write_text("Draft content")
        
        # Run ingest
        ingestor = OMAiIngestor(vault)
        result = ingestor.ingest()
        
        # Verify results
        print(f"✅ Collected: {len(result.records)} records")
        print(f"✅ Skipped: {len(result.skipped)} items")
        
        # Should only have the public note
        assert len(result.records) == 1, f"Expected 1 record, got {len(result.records)}"
        assert "public.md" in result.records[0]["path"], "Should have public.md"
        
        # Check skipped reasons
        skipped_dict = {Path(p).name: reason for p, reason in result.skipped}
        assert "private_fm.md" in skipped_dict, "Should skip frontmatter private"
        assert "tagged.md" in skipped_dict, "Should skip #private tag"
        assert "secret.md" in skipped_dict, "Should skip _private/ path"
        assert "_draft.md" in skipped_dict, "Should skip _ prefix"
        
        print("\n🎉 All privacy filter tests passed!")
        print("\nSkipped items:")
        for path, reason in result.skipped:
            print(f"  - {Path(path).name}: {reason}")

if __name__ == "__main__":
    test_privacy_filter()
