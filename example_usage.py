#!/usr/bin/env python3
"""
example_usage.py - Example usage of the Spiral Codex ethical content ingestion system

Demonstrates how to use the ingest driver to discover, fetch, score, and index
relevant content from multiple public sources while maintaining full provenance
and ethical compliance.
"""

import asyncio
import sys
from pathlib import Path

# Add current directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from ingest_driver import IngestDriver


async def example_basic_search():
    """Basic example: Search for content about electrical principles"""
    print("🔍 Example 1: Basic Search")
    print("=" * 50)

    driver = IngestDriver("ingest_config.json")

    try:
        result = await driver.ingest(
            query="electrical principles IET",
            sources="arxiv,reddit",
            max_items=10
        )

        driver.print_summary(result)
        return result

    except Exception as e:
        print(f"❌ Error: {e}")
        return None


async def example_academic_focus():
    """Example focused on academic sources"""
    print("\n🎓 Example 2: Academic Focus")
    print("=" * 50)

    config = {
        "enabled_sources": ["arxiv"],
        "max_items_per_source": 5,
        "bullshit_threshold": 0.5,  # Stricter for academic content
        "integration": {
            "omai_enabled": True,
            "reflection_cycle_enabled": True,
            "wean_telemetry": True
        }
    }

    driver = IngestDriver()

    try:
        result = await driver.ingest(
            query="machine learning neural networks",
            max_items=5
        )

        print(f"📊 Academic Results:")
        print(f"  Papers found: {result.successful_ingests}")
        print(f"  Average bullshit score: {result.bullshit_scores.get('average', 'N/A'):.3f}")
        print(f"  Sources: {', '.join(result.sources_used)}")

        return result

    except Exception as e:
        print(f"❌ Error: {e}")
        return None


async def example_social_discussion():
    """Example focused on social discussion content"""
    print("\n💬 Example 3: Social Discussion")
    print("=" * 50)

    config = {
        "enabled_sources": ["reddit"],
        "max_items_per_source": 15,
        "bullshit_threshold": 0.8,  # More lenient for social content
        "skip_nsfw": true
    }

    driver = IngestDriver()

    try:
        result = await driver.ingest(
            query="python programming best practices",
            max_items=15
        )

        print(f"💬 Social Discussion Results:")
        print(f"  Discussions found: {result.successful_ingests}")
        print(f"  Success rate: {result.successful_ingests / result.total_trials:.1%}")
        print(f"  Average response time: {result.bullshit_scores.get('average', 'N/A')}")

        # Show sample content
        if result.enhanced_vault_entries:
            print(f"\n📝 Sample Content:")
            for i, entry in enumerate(result.enhanced_vault_entries[:2]):
                print(f"  {i+1}. {entry['title'][:60]}...")
                print(f"     Credibility: {entry['credibility_score']['credibility_tier']}")
                print(f"     Score: {entry['credibility_score']['overall_bullshit_score']:.3f}")

        return result

    except Exception as e:
        print(f"❌ Error: {e}")
        return None


async def example_quality_filtering():
    """Example with strict quality filtering"""
    print("\n⚡ Example 4: Quality Filtering")
    print("=" * 50)

    config = {
        "enabled_sources": ["arxiv", "archive"],
        "bullshit_threshold": 0.3,  # Very strict
        "min_content_length": 500,
        "max_items_per_source": 10
    }

    driver = IngestDriver()

    try:
        result = await driver.ingest(
            query="artificial intelligence ethics",
            max_items=20
        )

        high_quality = [e for e in result.enhanced_vault_entries
                       if e['credibility_score']['overall_bullshit_score'] < 0.3]

        print(f"⚡ High-Quality Results:")
        print(f"  Total found: {result.successful_ingests}")
        print(f"  High quality: {len(high_quality)}")
        print(f"  Quality rate: {len(high_quality) / max(result.successful_ingests, 1):.1%}")

        if high_quality:
            print(f"\n🌟 Best Content:")
            for entry in high_quality[:3]:
                print(f"  ⭐ {entry['title'][:50]}...")
                print(f"     Score: {entry['credibility_score']['overall_bullshit_score']:.3f}")

        return result

    except Exception as e:
        print(f"❌ Error: {e}")
        return None


async def example_multiple_sources():
    """Example using all available sources"""
    print("\n🌐 Example 5: Multiple Sources")
    print("=" * 50)

    driver = IngestDriver("ingest_config.json")

    try:
        result = await driver.ingest(
            query="sustainable energy renewable resources",
            max_items=25
        )

        # Analyze source performance
        source_performance = {}
        for trial in result.trials:
            source = trial.source_type
            if source not in source_performance:
                source_performance[source] = {"success": 0, "total": 0}
            source_performance[source]["total"] += 1
            if trial.success:
                source_performance[source]["success"] += 1

        print(f"🌐 Multi-Source Results:")
        print(f"  Total items: {result.successful_ingests}")
        print(f"  Sources used: {', '.join(result.sources_used)}")

        print(f"\n📊 Source Performance:")
        for source, stats in source_performance.items():
            success_rate = stats["success"] / stats["total"] if stats["total"] > 0 else 0
            print(f"  {source}: {stats['success']}/{stats['total']} ({success_rate:.1%})")

        return result

    except Exception as e:
        print(f"❌ Error: {e}")
        return None


async def main():
    """Run all examples"""
    print("🌀 Spiral Codex Ethical Content Ingestion - Examples")
    print("=" * 60)

    examples = [
        ("Basic Search", example_basic_search),
        ("Academic Focus", example_academic_focus),
        ("Social Discussion", example_social_discussion),
        ("Quality Filtering", example_quality_filtering),
        ("Multiple Sources", example_multiple_sources)
    ]

    results = []

    for name, example_func in examples:
        try:
            result = await example_func()
            results.append((name, result))

            if result:
                print(f"✅ {name} completed successfully")
            else:
                print(f"❌ {name} failed")

        except Exception as e:
            print(f"❌ {name} failed with error: {e}")
            results.append((name, None))

        print("\n" + "-" * 50)

    # Summary
    print("\n📋 SUMMARY")
    print("=" * 30)

    successful_examples = sum(1 for _, result in results if result is not None)
    total_items = sum(result.successful_ingests if result else 0 for _, result in results)

    print(f"Examples completed: {successful_examples}/{len(examples)}")
    print(f"Total items ingested: {total_items}")

    if successful_examples > 0:
        print(f"\n✅ Ethical content ingestion system is working!")
        print(f"📁 Check data/vault_index.json for ingested content")
        print(f"📋 Check logs/ingest_trials.jsonl for trial logs")
        print(f"📊 Check logs/wean.csv for telemetry data")


if __name__ == "__main__":
    asyncio.run(main())