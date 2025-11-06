#!/usr/bin/env python3
"""Test enhanced RAG functionality with BM25 + vector tie-break"""

from utils.rag import (
    init_db, add_snippet, add_test_snippets, retrieve, retrieve_legacy,
    available, enrich_prompt, reset_models
)

def test_enhanced_rag():
    """Test enhanced RAG with BM25 + vector tie-break"""
    print("🧪 Testing Enhanced RAG (BM25 + Vector Tie-Break)")
    print("=" * 60)

    # Initialize database
    init_db()
    print("✅ Initialized embeddings database")

    # Add test snippets if needed
    add_test_snippets()

    print(f"\n✅ RAG available: {available()}")

    # Reset models to ensure fresh training
    reset_models()

    # Test queries
    test_queries = [
        "How does agent routing work?",
        "What privacy features exist?",
        "Tell me about telemetry",
        "BM25 scoring algorithm",
        "Vector embeddings",
        "API documentation",
        "Database storage",
        "Reflection training"
    ]

    print("\n🔍 Comparing Legacy vs Enhanced Retrieval")
    print("-" * 50)

    for query in test_queries:
        print(f"\nQuery: '{query}'")
        print("-" * 30)

        # Legacy retrieval
        legacy_results = retrieve_legacy(query, top_k=3)
        print(f"Legacy: Found {len(legacy_results)} results")
        for i, result in enumerate(legacy_results, 1):
            print(f"  {i}. [{result['source']}] {result['content'][:60]}...")

        # Enhanced retrieval
        enhanced_results = retrieve(query, top_k=3)
        print(f"Enhanced: Found {len(enhanced_results)} results")
        for i, result in enumerate(enhanced_results, 1):
            bm25 = result.get('bm25_score', 0)
            vector = result.get('vector_score', 0)
            method = result.get('rank_method', 'unknown')
            print(f"  {i}. [{result['source']}] BM25:{bm25:.3f} Vec:{vector:.3f} {result['content'][:60]}...")
            print(f"     Method: {method}")

    # Test prompt enrichment
    print("\n\n✍️ Testing Prompt Enrichment")
    print("-" * 30)

    base_prompt = "Explain the agent system architecture"
    enriched = enrich_prompt(base_prompt, "agent routing architecture", max_snippets=3)

    print(f"Base prompt length: {len(base_prompt)} chars")
    print(f"Enriched prompt length: {len(enriched)} chars")
    print(f"Context added: {len(enriched) > len(base_prompt)}")

    print("\n🎉 Enhanced RAG tests complete!")

if __name__ == "__main__":
    test_enhanced_rag()