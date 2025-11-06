#!/usr/bin/env python3
"""
Priority Content Manager - Command line tool for managing priority educational content
Special focus on ManuAGI and high-quality educational sources
"""
import argparse
import json
import sys
from pathlib import Path

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.enhanced_vault_manager import enhanced_vault_manager
from utils.priority_sources import priority_manager
from fetchers.youtube_transcript_fetcher import youtube_fetcher

def fetch_manuagi_content(args):
    """Fetch ManuAGI content with highest priority"""
    print("🎯 Fetching ManuAGI content (Highest Priority)")
    print("=" * 50)

    # Fetch ManuAGI transcripts
    results = enhanced_vault_manager.fetch_and_prioritize_transcripts(
        channels=["ManuAGI"],
        max_per_channel=args.max_videos
    )

    print(f"\n📊 Results:")
    print(f"   Videos fetched: {results['fetched_videos']}")
    print(f"   High priority items: {results['high_priority_count']}")
    print(f"   Files created: {len(results['files_created'])}")

    if results['files_created']:
        print(f"\n📁 Created files:")
        for file_path in results['files_created']:
            print(f"   {file_path}")

    if results['errors']:
        print(f"\n⚠️  Errors encountered:")
        for error in results['errors']:
            print(f"   {error}")

def prioritize_vault(args):
    """Apply priority scoring to existing vault"""
    print("⚡ Prioritizing existing vault content")
    print("=" * 50)

    results = enhanced_vault_manager.prioritize_existing_vault()

    if 'error' in results:
        print(f"❌ Error: {results['error']}")
        return

    print(f"\n📊 Vault Analysis:")
    print(f"   Total items processed: {results['processed_items']}")

    print(f"\n🎯 Priority Distribution:")
    for level, count in results['priority_distribution'].items():
        emoji = enhanced_vault_manager._get_priority_emoji(level.upper())
        print(f"   {emoji} {level.upper()}: {count}")

    print(f"\n🔥 Top Priority Items:")
    for i, item in enumerate(results['top_priority_items'][:5], 1):
        score = item.get('priority_score', 1.0)
        title = item.get('title', 'Untitled')[:60] + '...' if len(item.get('title', '')) > 60 else item.get('title', 'Untitled')
        print(f"   {i}. [{title}] (Score: {score:.2f})")

    manuagi_items = results.get('manuagi_items', [])
    if manuagi_items:
        print(f"\n🎯 ManuAGI Items Found: {len(manuagi_items)}")
        for item in manuagi_items[:3]:
            score = item.get('priority_score', 1.0)
            title = item.get('title', 'Untitled')[:60] + '...' if len(item.get('title', '')) > 60 else item.get('title', 'Untitled')
            print(f"   • [{title}] (Score: {score:.2f})")

def search_content(args):
    """Search for priority content"""
    print(f"🔍 Searching for priority content: '{args.query}'")
    print("=" * 50)

    # Get priority recommendations
    recommendations = priority_manager.get_priority_recommendations(args.query, args.limit)

    if recommendations:
        print(f"\n🎯 Priority Recommendations:")
        for i, rec in enumerate(recommendations, 1):
            score = rec.get('priority_score', 1.0)
            print(f"   {i}. {rec.get('title', 'No title')} (Score: {score:.2f})")
            print(f"      {rec.get('reason', 'No reason provided')}")
            print(f"      URL: {rec.get('url', 'No URL')}")
            print()

    # Search vault content
    vault_results = enhanced_vault_manager.search_priority_content(args.query, args.limit)

    if vault_results:
        print(f"📚 Vault Content:")
        for i, item in enumerate(vault_results, 1):
            score = item.get('priority_score', 1.0)
            relevance = item.get('_relevance_score', 0)
            title = item.get('title', 'Untitled')[:60] + '...' if len(item.get('title', '')) > 60 else item.get('title', 'Untitled')
            content_type = item.get('source_type', 'unknown')
            print(f"   {i}. [{title}] ({content_type})")
            print(f"      Priority: {score:.2f} | Relevance: {relevance}")

def create_dashboard(args):
    """Create priority dashboard"""
    print("📊 Creating Priority Dashboard")
    print("=" * 50)

    dashboard_path = enhanced_vault_manager.create_priority_dashboard()

    if dashboard_path.startswith('Error'):
        print(f"❌ {dashboard_path}")
    else:
        print(f"✅ Dashboard created: {dashboard_path}")
        print(f"📁 Location: {Path(dashboard_path).name}")

def test_priority_scoring(args):
    """Test priority scoring system"""
    print("🧪 Testing Priority Scoring System")
    print("=" * 50)

    # Test content samples
    test_samples = [
        {
            'name': 'ManuAGI AI Development Guide',
            'content': {
                'url': 'https://youtube.com/watch?v=manuagi_demo',
                'title': 'ManuAGI - Complete AI Development Workflow',
                'content': 'comprehensive guide to ai development using open source tools manuagi',
                'source_type': 'youtube_transcript'
            }
        },
        {
            'name': 'Random Blog Post',
            'content': {
                'url': 'https://example.com/blog',
                'title': 'Random Thoughts',
                'content': 'some random content about nothing important',
                'source_type': 'blog'
            }
        },
        {
            'name': 'Research Paper',
            'content': {
                'url': 'https://arxiv.org/abs/1234',
                'title': 'Deep Learning Research Paper',
                'content': 'academic research on neural networks and machine learning algorithms',
                'source_type': 'paper'
            }
        }
    ]

    print("Testing priority scoring on sample content:\n")

    for sample in test_samples:
        content = sample['content']
        score = priority_manager.calculate_priority_score(content)
        level = priority_manager._get_priority_level(score)

        print(f"📄 {sample['name']}")
        print(f"   Title: {content['title']}")
        print(f"   Priority Score: {score:.2f}")
        print(f"   Priority Level: {level}")
        print(f"   Content Type: {content['source_type']}")
        print()

def show_status(args):
    """Show system status"""
    print("🏁 Priority Content System Status")
    print("=" * 50)

    # Check vault index
    vault_index_file = Path.home() / "Documents" / "Obsidian" / "OMAi" / ".." / ".." / "data" / "vault_index.json"
    if vault_index_file.exists():
        try:
            with open(vault_index_file) as f:
                items = json.load(f)
            print(f"✅ Vault index found: {len(items)} items")
        except:
            print("❌ Vault index corrupted")
    else:
        print("❌ Vault index not found")

    # Check YouTube API
    if youtube_fetcher.api:
        print("✅ YouTube API available")
    else:
        print("❌ YouTube API not available (install with: pip install youtube-transcript-api)")

    # Check priority sources
    print(f"✅ Priority sources configured: {len(priority_manager.priority_sources)}")
    print(f"✅ High-value domains: {len(priority_manager.high_value_domains)}")
    print(f"✅ High-value keywords: {len(priority_manager.high_value_keywords)}")

    # Check directories
    vault_path = Path.home() / "Documents" / "Obsidian" / "OMAi"
    if vault_path.exists():
        print(f"✅ Vault directory exists: {vault_path}")
        transcripts_dir = vault_path / "Transcripts"
        if transcripts_dir.exists():
            transcript_files = list(transcripts_dir.glob("*.md"))
            print(f"✅ Transcripts directory: {len(transcript_files)} files")
    else:
        print("❌ Vault directory not found")

def main():
    parser = argparse.ArgumentParser(description="Priority Content Manager - Educational Content Prioritization")
    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # Fetch ManuAGI content
    fetch_parser = subparsers.add_parser('fetch-manuagi', help='Fetch ManuAGI content')
    fetch_parser.add_argument('--max-videos', type=int, default=5, help='Maximum videos to fetch')

    # Prioritize existing vault
    prioritize_parser = subparsers.add_parser('prioritize-vault', help='Apply priority scoring to existing vault')

    # Search content
    search_parser = subparsers.add_parser('search', help='Search for priority content')
    search_parser.add_argument('query', help='Search query')
    search_parser.add_argument('--limit', type=int, default=10, help='Maximum results')

    # Create dashboard
    dashboard_parser = subparsers.add_parser('dashboard', help='Create priority dashboard')

    # Test system
    test_parser = subparsers.add_parser('test', help='Test priority scoring system')

    # Show status
    status_parser = subparsers.add_parser('status', help='Show system status')

    args = parser.parse_args()

    if args.command == 'fetch-manuagi':
        fetch_manuagi_content(args)
    elif args.command == 'prioritize-vault':
        prioritize_vault(args)
    elif args.command == 'search':
        search_content(args)
    elif args.command == 'dashboard':
        create_dashboard(args)
    elif args.command == 'test':
        test_priority_scoring(args)
    elif args.command == 'status':
        show_status(args)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()