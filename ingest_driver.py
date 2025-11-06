#!/usr/bin/env python3
"""
ingest_driver.py - Main Ingest Orchestrator with Provenance Tracking

Core orchestrator for the Spiral Codex ethical content ingestion system.
Coordinates fetchers, applies bullshit scoring, manages provenance tracking,
and integrates with existing OMAi/vault systems.

Usage:
    python ingest_driver.py --query "electrical principles IET" --max-items 50
    python ingest_driver.py --config ingest_config.json --sources reddit,arxiv
"""

import json
import time
import hashlib
import asyncio
import logging
import argparse
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field, asdict
import sys

# Add current directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from bullshit import BullshitScorer, ContentMetadata, BullshitScore
from utils.trial_logger import TrialLogger, IngestTrial




@dataclass
class IngestResult:
    """Result of a complete ingest operation"""
    query: str
    start_time: str
    end_time: str
    total_trials: int
    successful_ingests: int
    failed_ingests: int
    bullshit_scores: Dict[str, float] = field(default_factory=dict)
    sources_used: List[str] = field(default_factory=list)
    trials: List[IngestTrial] = field(default_factory=list)
    enhanced_vault_entries: List[Dict[str, Any]] = field(default_factory=list)


class IngestDriver:
    """Main orchestrator for ethical content ingestion"""

    def __init__(self, config_path: Optional[str] = None):
        self.config = self._load_config(config_path)
        self.logger = self._setup_logging()
        self.bullshit_scorer = BullshitScorer(self.config.get("bullshit_config"))
        self.trial_logger = TrialLogger()
        self.data_dir = Path("data")
        self.vault_index_path = self.data_dir / "vault_index.json"

        # Ensure directories exist
        self.data_dir.mkdir(exist_ok=True)

        # Load fetchers dynamically
        self.fetchers = self._load_fetchers()

        # Load existing vault index
        self.vault_index = self._load_vault_index()

    def _load_config(self, config_path: Optional[str]) -> Dict[str, Any]:
        """Load ingestion configuration"""
        default_config = {
            "max_items_per_source": 20,
            "max_total_items": 100,
            "timeout_seconds": 30,
            "rate_limit_delay": 1.0,
            "respect_robots_txt": True,
            "allowed_licenses": ["CC BY", "CC BY-SA", "CC0", "MIT", "Apache-2.0", "Public Domain"],
            "min_content_length": 100,
            "max_content_length": 1000000,  # 1MB
            "enabled_sources": ["reddit", "arxiv", "archive", "youtube", "pdf"],
            "bullshit_threshold": 0.7,  # Don't ingest content scoring above this
            "deduplication_enabled": True,
            "retry_attempts": 3,
            "retry_delay": 5.0,
            "parallel_fetches": 5,
            "integration": {
                "omai_enabled": True,
                "reflection_cycle_enabled": True,
                "wean_telemetry": True
            }
        }

        if config_path and Path(config_path).exists():
            try:
                with open(config_path, 'r') as f:
                    user_config = json.load(f)
                # Merge with defaults
                for key, value in user_config.items():
                    if isinstance(value, dict) and key in default_config and isinstance(default_config[key], dict):
                        default_config[key].update(value)
                    else:
                        default_config[key] = value
            except Exception as e:
                self.logger.warning(f"Failed to load config from {config_path}: {e}")

        return default_config

    def _setup_logging(self) -> logging.Logger:
        """Setup logging configuration"""
        logger = logging.getLogger("ingest_driver")
        logger.setLevel(logging.INFO)

        # Create logs directory
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)

        # File handler
        file_handler = logging.FileHandler(log_dir / "ingest_driver.log")
        file_handler.setLevel(logging.INFO)

        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)

        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

        return logger

    def _load_fetchers(self) -> Dict[str, Any]:
        """Dynamically load source fetchers"""
        fetchers = {}

        try:
            # Import fetchers
            from fetchers.reddit_fetcher import RedditFetcher
            from fetchers.arxiv_fetcher import ArxivFetcher
            from fetchers.archive_fetcher import ArchiveFetcher
            from fetchers.youtube_fetcher import YouTubeFetcher
            from fetchers.pdf_fetcher import PDFFetcher

            fetchers["reddit"] = RedditFetcher(self.config)
            fetchers["arxiv"] = ArxivFetcher(self.config)
            fetchers["archive"] = ArchiveFetcher(self.config)
            fetchers["youtube"] = YouTubeFetcher(self.config)
            fetchers["pdf"] = PDFFetcher(self.config)

        except ImportError as e:
            self.logger.warning(f"Some fetchers not available: {e}")

        return fetchers

    def _load_vault_index(self) -> Dict[str, Any]:
        """Load existing vault index or create new one"""
        if self.vault_index_path.exists():
            try:
                with open(self.vault_index_path, 'r') as f:
                    return json.load(f)
            except Exception as e:
                self.logger.warning(f"Failed to load vault index: {e}")

        # Return default structure
        return {
            "metadata": {
                "created_at": datetime.now(timezone.utc).isoformat(),
                "ingest_system": "spiral_codex_v1",
                "total_documents": 0
            },
            "documents": [],
            "credibility_distribution": {
                "highly_credible": 0,
                "credible": 0,
                "moderate": 0,
                "questionable": 0,
                "high_bullshit_risk": 0
            }
        }

    def _generate_trial_id(self, url: str, source_type: str) -> str:
        """Generate unique trial ID"""
        content = f"{url}_{source_type}_{datetime.now().isoformat()}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]

    def _log_trial(self, trial: IngestTrial) -> None:
        """Log trial using trial logger"""
        self.trial_logger.log_trial(trial)

    def _calculate_checksum(self, content: str) -> str:
        """Calculate content checksum for deduplication"""
        return hashlib.sha256(content.encode()).hexdigest()

    def _is_duplicate(self, checksum: str) -> bool:
        """Check if content already exists in vault"""
        for doc in self.vault_index.get("documents", []):
            if doc.get("content_sha256") == checksum:
                return True
        return False

    def _apply_bullshit_scoring(self, content_metadata: ContentMetadata) -> Tuple[Optional[BullshitScore], bool]:
        """Apply bullshit scoring and determine if content should be ingested"""
        try:
            score = self.bullshit_scorer.score_content(content_metadata)

            # Check against threshold
            should_ingest = score.overall_score <= self.config["bullshit_threshold"]

            return score, should_ingest

        except Exception as e:
            self.logger.error(f"Bullshit scoring failed: {e}")
            return None, False

    def _enhance_vault_entry(self, content_metadata: ContentMetadata, bullshit_score: BullshitScore, trial: IngestTrial) -> Dict[str, Any]:
        """Create enhanced vault entry with credibility scores"""

        # Extract content for vault
        content = content_metadata.content

        # Parse title and sections
        title = content_metadata.title or "Untitled Content"

        vault_entry = {
            "title": title,
            "source_url": content_metadata.url,
            "source_type": content_metadata.source_type,
            "author": content_metadata.author,
            "publish_date": content_metadata.publish_date,
            "license": content_metadata.license,
            "content": content,
            "content_sha256": self._calculate_checksum(content),
            "word_count": content_metadata.word_count,
            "char_count": len(content),
            "ingest_metadata": {
                "ingested_at": trial.timestamp,
                "trial_id": trial.trial_id,
                "fetch_method": trial.fetch_method,
                "response_time_ms": trial.response_time_ms,
                "robots_txt_respected": trial.robots_txt_respected,
                "rate_limit_applied": trial.rate_limit_applied
            },
            "credibility_score": {
                "overall_bullshit_score": bullshit_score.overall_score,
                "credibility_tier": self.bullshit_scorer.get_credibility_tier(bullshit_score),
                "source_score": bullshit_score.source_score,
                "quality_score": bullshit_score.quality_score,
                "consensus_score": bullshit_score.consensus_score,
                "citation_score": bullshit_score.citation_score,
                "freshness_score": bullshit_score.freshness_score,
                "confidence": bullshit_score.confidence
            },
            "references": content_metadata.references,
            "citation_count": content_metadata.citation_count,
            "tags": [content_metadata.source_type, "ingested"],
            "frontmatter": {
                "title": title,
                "source": content_metadata.source_type,
                "credibility_score": bullshit_score.overall_score,
                "bullshit_score": bullshit_score.overall_score,
                "ingested_by": "spiral_codex_ingest_v1"
            },
            "is_private": False,
            "weight": max(0.1, 1.0 - bullshit_score.overall_score)  # Higher weight for more credible content
        }

        return vault_entry

    def _update_vault_index(self, entries: List[Dict[str, Any]]) -> None:
        """Update vault index with new entries"""
        for entry in entries:
            # Add to documents
            self.vault_index["documents"].append(entry)

            # Update credibility distribution
            credibility_score = entry["credibility_score"]["overall_bullshit_score"]
            tier = self.bullshit_scorer.get_credibility_tier(BullshitScore(
                overall_score=credibility_score,
                source_score=0, quality_score=0, consensus_score=0,
                citation_score=0, freshness_score=0, confidence=0
            ))

            tier_key = tier.lower().replace(" ", "_")
            if tier_key in self.vault_index["credibility_distribution"]:
                self.vault_index["credibility_distribution"][tier_key] += 1

        # Update metadata
        self.vault_index["metadata"]["total_documents"] = len(self.vault_index["documents"])
        self.vault_index["metadata"]["last_updated"] = datetime.now(timezone.utc).isoformat()

        # Save updated index
        with open(self.vault_index_path, 'w', encoding='utf-8') as f:
            json.dump(self.vault_index, f, indent=2, ensure_ascii=False)

    async def fetch_from_source(self, source_type: str, query: str) -> List[IngestTrial]:
        """Fetch content from a specific source"""
        if source_type not in self.fetchers:
            self.logger.warning(f"Fetcher for {source_type} not available")
            return []

        fetcher = self.fetchers[source_type]
        trials = []

        try:
            # Fetch content from source
            fetch_results = await fetcher.fetch(query, max_items=self.config["max_items_per_source"])

            for result in fetch_results:
                trial = IngestTrial(
                    trial_id=self._generate_trial_id(result.get("url", ""), source_type),
                    timestamp=datetime.now(timezone.utc).isoformat(),
                    source_type=source_type,
                    url=result.get("url", ""),
                    fetch_method=result.get("fetch_method", "unknown"),
                    query=query,
                    success=result.get("success", False),
                    error=result.get("error"),
                    response_time_ms=result.get("response_time_ms", 0),
                    content_length=len(result.get("content", "")),
                    license=result.get("license"),
                    robots_txt_respected=result.get("robots_txt_respected", True),
                    rate_limit_applied=result.get("rate_limit_applied", False),
                    checksum=self._calculate_checksum(result.get("content", "")),
                    metadata=result.get("metadata", {})
                )

                # Apply bullshit scoring if fetch was successful
                if trial.success and trial.content_length >= self.config["min_content_length"]:
                    content_metadata = ContentMetadata(
                        url=trial.url,
                        title=result.get("title", ""),
                        content=result.get("content", ""),
                        source_type=source_type,
                        author=result.get("author"),
                        publish_date=result.get("publish_date"),
                        license=result.get("license"),
                        word_count=len(result.get("content", "").split()),
                        citation_count=result.get("citation_count", 0),
                        references=result.get("references", []),
                        fetch_metadata=trial.metadata
                    )

                    bullshit_score, should_ingest = self._apply_bullshit_scoring(content_metadata)
                    if bullshit_score:
                        trial.bullshit_score = bullshit_score.overall_score

                        # Only proceed if content passes bullshit threshold
                        if should_ingest:
                            # Check for duplicates
                            if self.config["deduplication_enabled"] and self._is_duplicate(trial.checksum):
                                trial.error = "Duplicate content detected"
                                self.logger.info(f"Skipping duplicate: {trial.url}")
                            else:
                                # Create enhanced vault entry
                                vault_entry = self._enhance_vault_entry(content_metadata, bullshit_score, trial)
                                trial.metadata["vault_entry"] = vault_entry

                trials.append(trial)
                self._log_trial(trial)

                # Apply rate limiting
                if self.config["rate_limit_delay"] > 0:
                    await asyncio.sleep(self.config["rate_limit_delay"])

        except Exception as e:
            self.logger.error(f"Error fetching from {source_type}: {e}")

            # Log failed trial
            trial = IngestTrial(
                trial_id=self._generate_trial_id(f"error_{source_type}", source_type),
                timestamp=datetime.now(timezone.utc).isoformat(),
                source_type=source_type,
                url="",
                fetch_method="error",
                query=query,
                success=False,
                error=str(e)
            )
            trials.append(trial)
            self._log_trial(trial)

        return trials

    async def ingest(self, query: str, sources: Optional[List[str]] = None, max_items: Optional[int] = None) -> IngestResult:
        """Main ingest orchestration"""
        start_time = datetime.now(timezone.utc)
        self.logger.info(f"Starting ingest for query: {query}")

        # Determine sources to use
        sources_to_use = sources or self.config["enabled_sources"]
        if isinstance(sources_to_use, str):
            sources_to_use = [s.strip() for s in sources_to_use.split(",")]

        sources_to_use = [s for s in sources_to_use if s in self.fetchers]

        if not sources_to_use:
            raise ValueError("No valid sources available for fetching")

        max_items = max_items or self.config["max_total_items"]

        # Initialize result
        result = IngestResult(
            query=query,
            start_time=start_time.isoformat(),
            end_time="",  # Will be set at the end
            total_trials=0,
            successful_ingests=0,
            failed_ingests=0,
            sources_used=sources_to_use
        )

        # Fetch from all sources
        all_trials = []
        vault_entries = []

        # Create tasks for parallel fetching
        tasks = []
        for source_type in sources_to_use:
            task = asyncio.create_task(self.fetch_from_source(source_type, query))
            tasks.append(task)

        # Wait for all fetches to complete
        try:
            source_trials = await asyncio.gather(*tasks, return_exceptions=True)

            for trials in source_trials:
                if isinstance(trials, Exception):
                    self.logger.error(f"Source fetch failed: {trials}")
                else:
                    all_trials.extend(trials)

                    # Extract vault entries from successful trials
                    for trial in trials:
                        if trial.success and "vault_entry" in trial.metadata:
                            vault_entries.append(trial.metadata["vault_entry"])

        except Exception as e:
            self.logger.error(f"Error during parallel fetching: {e}")

        # Update result statistics
        result.trials = all_trials
        result.total_trials = len(all_trials)
        result.successful_ingests = len(vault_entries)
        result.failed_ingests = result.total_trials - result.successful_ingests

        # Calculate bullshit score statistics
        successful_scores = [t.bullshit_score for t in all_trials if t.bullshit_score is not None]
        if successful_scores:
            result.bullshit_scores = {
                "average": sum(successful_scores) / len(successful_scores),
                "min": min(successful_scores),
                "max": max(successful_scores),
                "count": len(successful_scores)
            }

        # Update vault with new entries
        if vault_entries:
            # Sort by credibility (best first)
            vault_entries.sort(key=lambda x: x["credibility_score"]["overall_bullshit_score"])

            # Limit by max_items
            vault_entries = vault_entries[:max_items]

            self._update_vault_index(vault_entries)
            result.enhanced_vault_entries = vault_entries

        # Set end time
        end_time = datetime.now(timezone.utc)
        result.end_time = end_time.isoformat()

        self.logger.info(f"Ingest completed: {result.successful_ingests} successful, {result.failed_ingests} failed")

        # Integration with reflection cycle
        if self.config["integration"]["reflection_cycle_enabled"]:
            self._update_reflection_cycle(result)

        return result

    def _update_reflection_cycle(self, result: IngestResult) -> None:
        """Update reflection cycle with ingest results"""
        try:
            reflection_data = {
                "timestamp": result.end_time,
                "type": "content_ingest",
                "query": result.query,
                "sources_used": result.sources_used,
                "success_rate": result.successful_ingests / max(result.total_trials, 1),
                "total_items": result.successful_ingests,
                "bullshit_scores": result.bullshit_scores,
                "learning_opportunities": self._extract_learning_opportunities(result)
            }

            reflection_file = Path("data/reflections") / f"{datetime.now().strftime('%Y-%m-%d')}.jsonl"
            reflection_file.parent.mkdir(parents=True, exist_ok=True)

            with open(reflection_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(reflection_data, default=str) + '\n')

        except Exception as e:
            self.logger.error(f"Failed to update reflection cycle: {e}")

    def _extract_learning_opportunities(self, result: IngestResult) -> List[str]:
        """Extract learning opportunities from ingest results"""
        opportunities = []

        if result.failed_ingests > result.successful_ingests:
            opportunities.append("High failure rate detected - review fetcher configurations")

        if result.bullshit_scores.get("average", 0) > 0.6:
            opportunities.append("High bullshit scores detected - improve source selection or quality filters")

        if not result.enhanced_vault_entries:
            opportunities.append("No content ingested - review query terms and source availability")

        # Analyze source performance
        source_performance = {}
        for trial in result.trials:
            if trial.source_type not in source_performance:
                source_performance[trial.source_type] = {"success": 0, "total": 0}
            source_performance[trial.source_type]["total"] += 1
            if trial.success:
                source_performance[trial.source_type]["success"] += 1

        for source, stats in source_performance.items():
            if stats["total"] > 0:
                success_rate = stats["success"] / stats["total"]
                if success_rate < 0.3:
                    opportunities.append(f"Poor performance from {source} - investigate fetcher issues")

        return opportunities

    def print_summary(self, result: IngestResult) -> None:
        """Print ingest summary"""
        print("\n" + "="*60)
        print("🌀 SPIRAL CODEX INGESTION SUMMARY")
        print("="*60)
        print(f"Query: {result.query}")
        print(f"Duration: {result.start_time} to {result.end_time}")
        print(f"Sources Used: {', '.join(result.sources_used)}")
        print(f"Total Trials: {result.total_trials}")
        print(f"Successful Ingests: {result.successful_ingests}")
        print(f"Failed Ingests: {result.failed_ingests}")

        if result.bullshit_scores:
            print(f"\n📊 BULLSHIT SCORE ANALYSIS:")
            print(f"  Average: {result.bullshit_scores['average']:.3f}")
            print(f"  Range: {result.bullshit_scores['min']:.3f} - {result.bullshit_scores['max']:.3f}")
            print(f"  Count: {result.bullshit_scores['count']}")

        if result.enhanced_vault_entries:
            print(f"\n✅ INGESTED CONTENT:")
            for i, entry in enumerate(result.enhanced_vault_entries[:5]):  # Show top 5
                score = entry["credibility_score"]["overall_bullshit_score"]
                tier = entry["credibility_score"]["credibility_tier"]
                print(f"  {i+1}. {entry['title'][:50]}... [{tier}: {score:.3f}]")

            if len(result.enhanced_vault_entries) > 5:
                print(f"  ... and {len(result.enhanced_vault_entries) - 5} more")

        print(f"\n📁 Vault index updated: {self.vault_index_path}")
        print(f"📋 Trial log: {self.trial_logger.log_path}")
        print("="*60)


async def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Spiral Codex Ethical Content Ingestion")
    parser.add_argument("--query", required=True, help="Search query for content ingestion")
    parser.add_argument("--sources", help="Comma-separated list of sources (reddit,arxiv,archive,youtube,pdf)")
    parser.add_argument("--max-items", type=int, help="Maximum items to ingest")
    parser.add_argument("--config", help="Configuration file path")
    parser.add_argument("--summary-only", action="store_true", help="Only show summary, no detailed output")

    args = parser.parse_args()

    # Initialize ingest driver
    driver = IngestDriver(args.config)

    try:
        # Run ingestion
        result = await driver.ingest(
            query=args.query,
            sources=args.sources.split(",") if args.sources else None,
            max_items=args.max_items
        )

        # Print summary
        driver.print_summary(result)

        # Additional details if not summary-only
        if not args.summary_only:
            print(f"\n🔍 DETAILED RESULTS:")
            print(f"Success Rate: {result.successful_ingests / max(result.total_trials, 1):.1%}")

            if result.bullshit_scores:
                avg_score = result.bullshit_scores['average']
                if avg_score < 0.3:
                    print(f"✅ High-quality content detected (avg bullshit score: {avg_score:.3f})")
                elif avg_score < 0.6:
                    print(f"⚠️  Moderate content quality (avg bullshit score: {avg_score:.3f})")
                else:
                    print(f"❌ Low-quality content detected (avg bullshit score: {avg_score:.3f})")

    except KeyboardInterrupt:
        print("\n⚠️  Ingestion interrupted by user")
        return 1
    except Exception as e:
        print(f"\n❌ Ingestion failed: {e}")
        return 1

    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)