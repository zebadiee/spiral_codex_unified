#!/usr/bin/env python3
"""Test RAG functionality"""
from utils.rag import init_db, add_snippet, retrieve, available, enrich_prompt

def test_rag():
    """Test RAG initialization and retrieval"""
    print("Testing RAG functionality...")
    
    # Initialize database
    init_db()
    print("✅ Initialized embeddings database")
    
    # Add test snippets
    snippets = [
        ("The Spiral Codex uses glyph-based routing with symbols like ⊕⊡⊠⊨⊚", "README.md", {"type": "architecture"}),
        ("Agent orchestrator routes tasks to Codex, Claude, VibeKeeper and Archivist", "agent_orchestrator.py", {"type": "code"}),
        ("Privacy filter skips notes with #private tag or private: true frontmatter", "omai_ingest.py", {"type": "feature"}),
        ("Ledger sink logs every conversation turn to JSONL with SHA-256 hashes", "ledger.py", {"type": "feature"}),
        ("Wean telemetry tracks provider usage and latency in CSV format", "telemetry.py", {"type": "feature"}),
    ]
    
    for content, source, metadata in snippets:
        snippet_id = add_snippet(content, source, metadata)
        print(f"  Added snippet #{snippet_id}: {source}")
    
    print(f"\n✅ RAG available: {available()}")
    
    # Test retrieval
    print("\nTesting retrieval...")
    queries = [
        "How does agent routing work?",
        "What privacy features exist?",
        "Tell me about telemetry",
    ]
    
    for query in queries:
        results = retrieve(query, top_k=2)
        print(f"\nQuery: '{query}'")
        print(f"Found {len(results)} results:")
        for i, result in enumerate(results, 1):
            print(f"  {i}. [{result['source']}] {result['content'][:80]}...")
    
    # Test prompt enrichment
    print("\n\nTesting prompt enrichment...")
    base_prompt = "Explain the agent system"
    enriched = enrich_prompt(base_prompt, "agent routing system", max_snippets=2)
    
    print(f"Base prompt length: {len(base_prompt)} chars")
    print(f"Enriched prompt length: {len(enriched)} chars")
    print(f"Context added: {len(enriched) > len(base_prompt)}")
    
    print("\n🎉 RAG tests complete!")

if __name__ == "__main__":
    test_rag()
