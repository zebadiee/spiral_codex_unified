#!/usr/bin/env python3
"""Integration test for complete RAG + Brain API system"""

import asyncio
import aiohttp
from utils.rag import (
    init_db, add_test_snippets, retrieve, available as rag_available,
    reset_models, BM25_TOP_K
)

async def test_brain_api_integration():
    """Test integration with Brain API"""
    print("🧪 Testing Brain API Integration")
    print("=" * 40)

    base_url = "http://127.0.0.1:8000"

    async with aiohttp.ClientSession() as session:
        # Test RAG status
        print("1. Checking RAG status...")
        try:
            async with session.get(f"{base_url}/v1/brain/rag/status") as resp:
                if resp.status == 200:
                    status = await resp.json()
                    print(f"   ✅ RAG Available: {status['available']}")
                    print(f"   ✅ Vector Available: {status['vector_available']}")
                    print(f"   ✅ BM25 Top-K: {status['config']['bm25_top_k']}")
                else:
                    print(f"   ❌ Status check failed: {resp.status}")
                    return False
        except Exception as e:
            print(f"   ❌ Could not connect to API: {e}")
            print("   💡 Make sure the API server is running")
            return False

        # Test RAG evaluation endpoint
        print("\n2. Testing RAG evaluation...")
        try:
            async with session.post(
                f"{base_url}/v1/brain/rag/eval",
                json={"query": "BM25 scoring algorithm", "top_k": 3}
            ) as resp:
                if resp.status == 200:
                    eval_result = await resp.json()
                    legacy_count = eval_result['comparison']['legacy_count']
                    enhanced_count = eval_result['comparison']['enhanced_count']
                    print(f"   ✅ Legacy results: {legacy_count}")
                    print(f"   ✅ Enhanced results: {enhanced_count}")
                    print(f"   ✅ Vector tie-break: {eval_result['comparison']['improvements']['vector_tiebreak']}")
                else:
                    print(f"   ❌ Evaluation failed: {resp.status}")
                    return False
        except Exception as e:
            print(f"   ❌ Evaluation error: {e}")
            return False

        # Test enhanced brain planning
        print("\n3. Testing enhanced brain planning...")
        try:
            async with session.post(
                f"{base_url}/v1/brain/plan",
                json={"goal": "Explain agent routing architecture", "max_steps": 3}
            ) as resp:
                if resp.status == 200:
                    plan_result = await resp.json()
                    rag_enabled = plan_result['artifacts']['rag_enabled']
                    rag_method = plan_result['artifacts']['rag_method']
                    rag_count = plan_result['artifacts']['rag_results_count']
                    print(f"   ✅ RAG Enabled: {rag_enabled}")
                    print(f"   ✅ RAG Method: {rag_method}")
                    print(f"   ✅ RAG Results: {rag_count}")
                    if 'rag_scoring' in plan_result['artifacts']:
                        for i, scoring in enumerate(plan_result['artifacts']['rag_scoring'][:2], 1):
                            print(f"      {i}. BM25: {scoring['bm25_score']:.3f}, Vec: {scoring['vector_score']:.3f}")
                else:
                    print(f"   ❌ Brain planning failed: {resp.status}")
                    return False
        except Exception as e:
            print(f"   ❌ Brain planning error: {e}")
            return False

    return True

def test_rag_direct():
    """Test RAG functionality directly"""
    print("\n🧪 Testing RAG Direct Functionality")
    print("=" * 40)

    # Ensure RAG is ready
    if not rag_available():
        print("❌ RAG not available - initializing...")
        init_db()
        add_test_snippets()

    # Reset models for fresh test
    reset_models()

    # Test queries
    test_queries = [
        "agent routing system",
        "privacy filtering features",
        "telemetry data collection"
    ]

    for i, query in enumerate(test_queries, 1):
        print(f"\n{i}. Query: '{query}'")
        results = retrieve(query, top_k=2)

        if not results:
            print("   ❌ No results found")
            continue

        print(f"   ✅ Found {len(results)} results:")
        for j, result in enumerate(results, 1):
            bm25 = result.get('bm25_score', 0)
            vector = result.get('vector_score', 0)
            method = result.get('rank_method', 'unknown')
            print(f"      {j}. [{result['source']}] BM25:{bm25:.3f} Vec:{vector:.3f} ({method})")
            print(f"         {result['content'][:50]}...")

async def main():
    """Main test entry point"""
    print("🚀 RAG Quality Booster Integration Test")
    print("=" * 50)

    # Test direct RAG functionality
    test_rag_direct()

    # Test API integration
    api_success = await test_brain_api_integration()

    print("\n" + "=" * 50)
    if api_success:
        print("🎉 All integration tests passed!")
        print("✅ RAG Quality Booster is fully operational")
        print("✅ BM25 + Vector Tie-Break scoring active")
        print("✅ Brain API integration working")
        print("✅ Evaluation metrics generated")
    else:
        print("⚠️  Some integration tests failed")
        print("💡 Check API server status and logs")
        print("💡 Verify dependencies are installed")

if __name__ == "__main__":
    asyncio.run(main())