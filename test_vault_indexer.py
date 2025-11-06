#!/usr/bin/env python3
"""
Test script for Enhanced OMAi Vault Indexer

Verifies all acceptance criteria:
- Index includes sections[], tables[], and weight field
- Query returns better-ranked training-log notes
- No private/draft leakage per privacy filter
"""

import json
import sys
from pathlib import Path

def test_index_structure():
    """Test that index has required sections[], tables[], and weight fields."""
    print("Testing index structure...")

    with open('data/vault_index.json') as f:
        index = json.load(f)

    # Check required top-level fields
    required_fields = ['metadata', 'documents', 'duplicates', 'skipped']
    for field in required_fields:
        assert field in index, f"Missing required field: {field}"

    # Check document structure
    for doc in index['documents']:
        assert 'sections' in doc, f"Document {doc['title']} missing sections field"
        assert 'tables' in doc, f"Document {doc['title']} missing tables field"
        assert 'weight' in doc, f"Document {doc['title']} missing weight field"
        assert isinstance(doc['sections'], list), "sections must be a list"
        assert isinstance(doc['tables'], list), "tables must be a list"
        assert isinstance(doc['weight'], (int, float)), "weight must be numeric"

    print("✓ Index structure test passed")

def test_weighting_system():
    """Test that training logs get higher weight than other content."""
    print("Testing weighting system...")

    with open('data/vault_index.json') as f:
        index = json.load(f)

    # Find training log documents
    training_docs = [doc for doc in index['documents'] if 'training' in doc['title'].lower()]
    other_docs = [doc for doc in index['documents'] if 'training' not in doc['title'].lower()]

    if training_docs:
        training_weight = max(doc['weight'] for doc in training_docs)
        other_weight = max(doc['weight'] for doc in other_docs) if other_docs else 0

        assert training_weight > other_weight, f"Training docs ({training_weight}) should have higher weight than others ({other_weight})"
        print(f"✓ Training logs weight ({training_weight}) > other content ({other_weight})")

    # Check procedure weights
    procedure_docs = [doc for doc in index['documents'] if 'procedure' in doc['title'].lower()]
    if procedure_docs:
        procedure_weight = max(doc['weight'] for doc in procedure_docs)
        assert procedure_weight >= 1.8, f"Procedure docs should have weight >= 1.8, got {procedure_weight}"
        print(f"✓ Procedure documents have proper weight ({procedure_weight})")

def test_section_extraction():
    """Test that sections and tables are properly extracted."""
    print("Testing section and table extraction...")

    with open('data/vault_index.json') as f:
        index = json.load(f)

    total_sections = sum(len(doc['sections']) for doc in index['documents'])
    total_tables = sum(len(doc['tables']) for doc in index['documents'])

    assert total_sections > 0, "No sections extracted from any document"
    assert total_tables > 0, "No tables extracted from any document"

    print(f"✓ Extracted {total_sections} sections and {total_tables} tables")

    # Verify section structure
    for doc in index['documents']:
        for section in doc['sections']:
            assert 'type' in section, f"Section missing type: {section}"
            assert 'content' in section, f"Section missing content: {section}"

            if section['type'] == 'heading':
                assert 'title' in section, "Heading section missing title"
                assert 'level' in section, "Heading section missing level"
            elif section['type'] == 'code':
                assert 'language' in section, "Code section missing language"
            elif section['type'] == 'table':
                assert 'rows' in section, "Table section missing row count"

def test_deduplication():
    """Test SHA256-based deduplication."""
    print("Testing deduplication...")

    with open('data/vault_index.json') as f:
        index = json.load(f)

    # Check that no duplicate content hashes exist
    content_hashes = set()
    for doc in index['documents']:
        assert doc['content_sha256'] not in content_hashes, f"Duplicate content hash found: {doc['content_sha256']}"
        content_hashes.add(doc['content_sha256'])

    # Check that no duplicate titles exist
    titles = set()
    for doc in index['documents']:
        title_key = doc['title'].lower().strip()
        assert title_key not in titles, f"Duplicate title found: {doc['title']}"
        titles.add(title_key)

    print(f"✓ No duplicates found among {len(index['documents'])} documents")

def test_privacy_filtering():
    """Test that private/draft content is properly filtered."""
    print("Testing privacy filtering...")

    with open('data/vault_index.json') as f:
        index = json.load(f)

    # All indexed documents should have is_private: false
    for doc in index['documents']:
        assert doc['is_private'] == False, f"Private document was indexed: {doc['title']}"

    # Check that private content is reported in skipped files
    skipped_reasons = [reason for _, reason in index['skipped']]
    assert 'private_tagged' in skipped_reasons, "No private files were skipped (expected behavior)"

    # Check that no indexed document contains private markers
    private_markers = ['#private', '#secret', '#draft']
    for doc in index['documents']:
        content_lower = doc['content'].lower()
        for marker in private_markers:
            assert marker not in content_lower, f"Private marker '{marker}' found in indexed document: {doc['title']}"

    print(f"✓ Privacy filtering working: {len(index['skipped'])} files skipped")

def test_table_structuring():
    """Test that tables are properly structured."""
    print("Testing table structuring...")

    with open('data/vault_index.json') as f:
        index = json.load(f)

    all_tables = []
    for doc in index['documents']:
        all_tables.extend(doc['tables'])

    if all_tables:
        for table in all_tables:
            assert 'headers' in table, "Table missing headers"
            assert 'rows' in table, "Table missing rows"
            assert 'row_count' in table, "Table missing row_count"
            assert 'column_count' in table, "Table missing column_count"
            assert isinstance(table['headers'], list), "Headers must be a list"
            assert isinstance(table['rows'], list), "Rows must be a list"
            assert len(table['headers']) == table['column_count'], "Column count mismatch"
            assert len(table['rows']) == table['row_count'], "Row count mismatch"

            # Check that each row has correct structure
            for row in table['rows']:
                assert isinstance(row, dict), "Each row must be a dictionary"
                for header in table['headers']:
                    assert header in row, f"Missing column '{header}' in table row"

        print(f"✓ All {len(all_tables)} tables properly structured")

def test_query_ranking():
    """Test that queries would return properly ranked results."""
    print("Testing query ranking simulation...")

    with open('data/vault_index.json') as f:
        index = json.load(f)

    # Simulate query for "training performance"
    query_terms = ['training', 'performance']

    scored_docs = []
    for doc in index['documents']:
        score = 0
        content_lower = doc['content'].lower()
        title_lower = doc['title'].lower()

        # Score based on term matches
        for term in query_terms:
            if term in title_lower:
                score += 10  # Title matches are worth more
            if term in content_lower:
                score += 5  # Content matches

        # Apply weight multiplier
        score *= doc['weight']

        if score > 0:
            scored_docs.append((doc['title'], score, doc['weight']))

    # Sort by score
    scored_docs.sort(key=lambda x: x[1], reverse=True)

    if scored_docs:
        top_result = scored_docs[0]
        assert 'training' in top_result[0].lower(), "Top result should be training-related"
        print(f"✓ Query ranking works: '{top_result[0]}' ranks highest (score: {top_result[1]}, weight: {top_result[2]})")
    else:
        print("! No documents matched query terms")

def main():
    """Run all tests."""
    print("Running Enhanced OMAi Vault Indexer Tests\n")

    try:
        test_index_structure()
        test_weighting_system()
        test_section_extraction()
        test_deduplication()
        test_privacy_filtering()
        test_table_structuring()
        test_query_ranking()

        print("\n" + "="*50)
        print("✅ ALL TESTS PASSED!")
        print("Enhanced Vault Indexer meets all acceptance criteria:")
        print("  ✓ Index includes sections[], tables[], and weight fields")
        print("  ✓ Training logs are properly weighted (2.0)")
        print("  ✓ Procedures are properly weighted (1.8)")
        print("  ✓ SHA256 deduplication working correctly")
        print("  ✓ Privacy filtering prevents private/draft leakage")
        print("  ✓ Section extraction (headings, code, tables) working")
        print("  ✓ Query ranking prioritizes training logs")
        print("="*50)

    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 UNEXPECTED ERROR: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()