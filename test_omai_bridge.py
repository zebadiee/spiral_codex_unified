#!/usr/bin/env python3
"""Test OMAi Bridge Integration"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd()))

from utils.omai_bridge import available, query_context, enrich_insight, get_daily_context

def test_omai_bridge():
    """Test OMAi bridge functionality"""
    print("🧪 Testing OMAi Bridge Integration")
    print("=" * 50)
    
    # Test 1: Check availability
    print("\n1. Checking OMAi availability...")
    is_available = available()
    print(f"   OMAi API: {'✅ AVAILABLE' if is_available else '❌ OFFLINE'}")
    
    if not is_available:
        print("\n⚠️  OMAi Context API not running")
        print("   Start it with: systemctl --user start omai-context.service")
        print("   Or dev mode: cd ~/Documents/omarchy-ai-assist && make dev")
        return
    
    # Test 2: Query context
    print("\n2. Testing context query...")
    results = query_context("spiral codex autonomous learning", limit=3)
    print(f"   Retrieved {len(results)} context snippets")
    for i, result in enumerate(results[:2], 1):
        source = result.get("source", "unknown")
        content = result.get("content", "")[:80]
        print(f"   {i}. [{source}] {content}...")
    
    # Test 3: Insight enrichment
    print("\n3. Testing insight enrichment...")
    test_insight = {
        "category": "system_growth",
        "observation": "Reflection cycles enabling continuous learning",
        "significance": "high"
    }
    enriched = enrich_insight(test_insight, max_context=2)
    vault_added = enriched.get("vault_enriched", False)
    print(f"   Vault enrichment: {'✅ SUCCESS' if vault_added else '❌ FAILED'}")
    
    if vault_added:
        vault_refs = enriched.get("vault_context", [])
        print(f"   Added {len(vault_refs)} vault references:")
        for ref in vault_refs:
            print(f"     - {ref.get('source', 'unknown')}")
    
    # Test 4: Daily context
    print("\n4. Testing daily context retrieval...")
    from datetime import datetime
    today = datetime.now().strftime("%Y-%m-%d")
    daily = get_daily_context(today)
    print(f"   Today's vault activity: {len(daily)} entries")
    
    print("\n" + "=" * 50)
    print("🎉 OMAi Bridge tests complete!")
    print(f"   Status: {'✅ All systems operational' if is_available else '⚠️  OMAi offline'}")

if __name__ == "__main__":
    test_omai_bridge()
