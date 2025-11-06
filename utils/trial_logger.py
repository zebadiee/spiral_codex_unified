#!/usr/bin/env python3
"""
trial_logger.py - Trial logging system for ingest operations

Provides comprehensive logging of all ingest attempts with detailed metadata
for analysis, debugging, and learning from failures.
"""

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
import re
from collections import defaultdict, Counter


@dataclass
class IngestTrial:
    """Single ingest attempt with full metadata"""
    trial_id: str
    timestamp: str
    source_type: str
    url: str
    fetch_method: str
    query: Optional[str] = None
    success: bool = False
    error: Optional[str] = None
    response_time_ms: int = 0
    content_length: int = 0
    license: Optional[str] = None
    robots_txt_respected: bool = True
    rate_limit_applied: bool = False
    checksum: Optional[str] = None
    bullshit_score: Optional[float] = None
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class TrialLogger:
    """Comprehensive trial logging system"""

    def __init__(self, log_path: Optional[str] = None):
        self.log_path = Path(log_path) if log_path else Path("logs/ingest_trials.jsonl")
        self.logger = logging.getLogger("trial_logger")
        self._ensure_log_directory()

    def _ensure_log_directory(self):
        """Ensure log directory exists"""
        self.log_path.parent.mkdir(parents=True, exist_ok=True)

    def log_trial(self, trial: IngestTrial) -> None:
        """Log a single trial"""
        try:
            trial_data = asdict(trial)
            trial_data["logged_at"] = datetime.now(timezone.utc).isoformat()

            with open(self.log_path, 'a', encoding='utf-8') as f:
                f.write(json.dumps(trial_data, default=str) + '\n')

        except Exception as e:
            self.logger.error(f"Failed to log trial {trial.trial_id}: {e}")

    def get_trials(self, limit: Optional[int] = None, source_type: Optional[str] = None,
                   since_hours: Optional[int] = None) -> List[IngestTrial]:
        """Retrieve trials from log"""
        trials = []

        try:
            if not self.log_path.exists():
                return trials

            cutoff_time = None
            if since_hours:
                cutoff_time = datetime.now(timezone.utc).timestamp() - (since_hours * 3600)

            with open(self.log_path, 'r', encoding='utf-8') as f:
                for line in f:
                    try:
                        data = json.loads(line.strip())

                        # Apply filters
                        if source_type and data.get("source_type") != source_type:
                            continue

                        if cutoff_time:
                            trial_time = datetime.fromisoformat(data.get("timestamp", "").replace('Z', '+00:00')).timestamp()
                            if trial_time < cutoff_time:
                                continue

                        # Create IngestTrial object
                        trial = IngestTrial(**data)
                        trials.append(trial)

                    except Exception as e:
                        self.logger.warning(f"Error parsing trial log entry: {e}")
                        continue

                    if limit and len(trials) >= limit:
                        break

        except Exception as e:
            self.logger.error(f"Error reading trial log: {e}")

        return trials

    def generate_summary(self, since_hours: int = 24) -> Dict[str, Any]:
        """Generate summary statistics for trials"""
        trials = self.get_trials(since_hours=since_hours)

        if not trials:
            return {
                "period_hours": since_hours,
                "total_trials": 0,
                "successes": 0,
                "failures": 0,
                "success_rate": 0.0,
                "failure_categories": {},
                "top_failure": None,
                "source_performance": {},
                "bullshit_scores": {},
                "response_times": {}
            }

        # Basic statistics
        total_trials = len(trials)
        successes = sum(1 for t in trials if t.success)
        failures = total_trials - successes
        success_rate = successes / total_trials if total_trials > 0 else 0

        # Failure analysis
        failure_categories = Counter()
        error_messages = []

        source_performance = defaultdict(lambda: {"successes": 0, "failures": 0, "total_time": 0})
        bullshit_scores = []
        response_times = []

        for trial in trials:
            # Source performance
            source_performance[trial.source_type]["total_time"] += trial.response_time_ms
            if trial.success:
                source_performance[trial.source_type]["successes"] += 1
                if trial.bullshit_score is not None:
                    bullshit_scores.append(trial.bullshit_score)
            else:
                source_performance[trial.source_type]["failures"] += 1
                if trial.error:
                    failure_categories[self._categorize_error(trial.error)] += 1
                    error_messages.append(trial.error)

            if trial.response_time_ms > 0:
                response_times.append(trial.response_time_ms)

        # Calculate averages
        for source, stats in source_performance.items():
            total = stats["successes"] + stats["failures"]
            if total > 0:
                stats["success_rate"] = stats["successes"] / total
                stats["avg_response_time"] = stats["total_time"] / total

        # Find top failure
        top_failure = None
        if error_messages:
            error_counter = Counter(error_messages)
            top_failure = error_counter.most_common(1)[0]

        # Bullshit score statistics
        bullshit_stats = {}
        if bullshit_scores:
            bullshit_stats = {
                "count": len(bullshit_scores),
                "average": sum(bullshit_scores) / len(bullshit_scores),
                "min": min(bullshit_scores),
                "max": max(bullshit_scores),
                "distribution": self._calculate_distribution(bullshit_scores)
            }

        # Response time statistics
        response_stats = {}
        if response_times:
            response_stats = {
                "count": len(response_times),
                "average": sum(response_times) / len(response_times),
                "min": min(response_times),
                "max": max(response_times),
                "p50": self._percentile(response_times, 50),
                "p95": self._percentile(response_times, 95)
            }

        return {
            "period_hours": since_hours,
            "total_trials": total_trials,
            "successes": successes,
            "failures": failures,
            "success_rate": success_rate,
            "failure_categories": dict(failure_categories.most_common(10)),
            "top_failure": top_failure,
            "source_performance": dict(source_performance),
            "bullshit_scores": bullshit_stats,
            "response_times": response_stats
        }

    def get_failures_by_category(self, since_hours: int = 24) -> Dict[str, List[IngestTrial]]:
        """Group failures by error category"""
        trials = self.get_trials(since_hours=since_hours)
        failures = [t for t in trials if not t.success]

        categorized = defaultdict(list)
        for trial in failures:
            if trial.error:
                category = self._categorize_error(trial.error)
                categorized[category].append(trial)
            else:
                categorized["Unknown"].append(trial)

        return dict(categorized)

    def _categorize_error(self, error_message: str) -> str:
        """Categorize error messages"""
        error_lower = error_message.lower()

        if any(keyword in error_lower for keyword in ["timeout", "timed out"]):
            return "timeout"
        elif any(keyword in error_lower for keyword in ["404", "not found"]):
            return "not_found"
        elif any(keyword in error_lower for keyword in ["403", "forbidden", "unauthorized"]):
            return "access_denied"
        elif any(keyword in error_lower for keyword in ["429", "rate limit", "too many requests"]):
            return "rate_limit"
        elif any(keyword in error_lower for keyword in ["connection", "network", "dns"]):
            return "network"
        elif any(keyword in error_lower for keyword in ["parse", "json", "xml"]):
            return "parsing"
        elif any(keyword in error_lower for keyword in ["license", "permission", "robots"]):
            return "license_restriction"
        elif any(keyword in error_lower for keyword in ["duplicate", "exists"]):
            return "duplicate"
        else:
            return "other"

    def _calculate_distribution(self, values: List[float], bins: int = 5) -> Dict[str, int]:
        """Calculate distribution of values"""
        if not values:
            return {}

        min_val, max_val = min(values), max(values)
        if min_val == max_val:
            return {"uniform": len(values)}

        bin_width = (max_val - min_val) / bins
        distribution = {}

        for i in range(bins):
            bin_start = min_val + i * bin_width
            bin_end = min_val + (i + 1) * bin_width
            bin_label = f"{bin_start:.2f}-{bin_end:.2f}"

            count = sum(1 for v in values if bin_start <= v < bin_end)
            distribution[bin_label] = count

        return distribution

    def _percentile(self, values: List[float], percentile: int) -> float:
        """Calculate percentile of values"""
        if not values:
            return 0

        sorted_values = sorted(values)
        index = int(len(sorted_values) * percentile / 100)
        return sorted_values[min(index, len(sorted_values) - 1)]

    def generate_labeled_trials(self, output_path: Optional[str] = None) -> str:
        """Generate labeled trials file for machine learning"""
        trials = self.get_trials(since_hours=24 * 7)  # Last week

        labeled_data = []
        for trial in trials:
            # Create features and labels
            features = {
                "source_type": trial.source_type,
                "response_time_ms": trial.response_time_ms,
                "content_length": trial.content_length,
                "robots_txt_respected": trial.robots_txt_respected,
                "rate_limit_applied": trial.rate_limit_applied,
            }

            # Add metadata features
            if trial.metadata:
                features.update({
                    f"meta_{k}": v for k, v in trial.metadata.items()
                    if isinstance(v, (str, int, float, bool))
                })

            # Label (success/failure)
            label = {
                "success": trial.success,
                "error_category": self._categorize_error(trial.error) if trial.error else "success",
                "bullshit_score": trial.bullshit_score
            }

            labeled_entry = {
                "trial_id": trial.trial_id,
                "timestamp": trial.timestamp,
                "features": features,
                "label": label
            }

            labeled_data.append(labeled_entry)

        # Write to file
        if not output_path:
            output_path = "logs/trials_labeled.jsonl"

        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        with open(output_file, 'w', encoding='utf-8') as f:
            for entry in labeled_data:
                f.write(json.dumps(entry, default=str) + '\n')

        return str(output_file)

    def generate_top5_failures(self, output_path: Optional[str] = None) -> str:
        """Generate top 5 failures report"""
        failures_by_category = self.get_failures_by_category(since_hours=24 * 7)

        # Get top 5 failure categories
        top_categories = sorted(
            failures_by_category.items(),
            key=lambda x: len(x[1]),
            reverse=True
        )[:5]

        # Generate report
        report_lines = [
            "# Top 5 Failure Categories - Last 7 Days",
            f"Generated: {datetime.now(timezone.utc).isoformat()}",
            ""
        ]

        for i, (category, trials) in enumerate(top_categories, 1):
            report_lines.extend([
                f"## {i}. {category} ({len(trials)} failures)",
                ""
            ])

            # Sample failure examples
            sample_trials = trials[:3]
            for trial in sample_trials:
                report_lines.extend([
                    f"**Trial ID:** {trial.trial_id}",
                    f"**Source:** {trial.source_type}",
                    f"**URL:** {trial.url}",
                    f"**Error:** {trial.error}",
                    f"**Timestamp:** {trial.timestamp}",
                    ""
                ])

            if len(trials) > 3:
                report_lines.append(f"... and {len(trials) - 3} more failures in this category")
            report_lines.append("")

        # Write report
        if not output_path:
            output_path = "data/lessons/failures_top5.md"

        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(report_lines))

        return str(output_file)

    def cleanup_old_logs(self, days_to_keep: int = 30) -> int:
        """Clean up old trial logs"""
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=days_to_keep)

        if not self.log_path.exists():
            return 0

        temp_file = self.log_path.with_suffix('.tmp.jsonl')
        kept_count = 0
        removed_count = 0

        try:
            with open(self.log_path, 'r', encoding='utf-8') as infile, \
                 open(temp_file, 'w', encoding='utf-8') as outfile:

                for line in infile:
                    try:
                        data = json.loads(line.strip())
                        trial_time = datetime.fromisoformat(
                            data.get("timestamp", "").replace('Z', '+00:00')
                        )

                        if trial_time >= cutoff_date:
                            outfile.write(line)
                            kept_count += 1
                        else:
                            removed_count += 1

                    except Exception:
                        # Keep malformed lines
                        outfile.write(line)
                        kept_count += 1

            # Replace original file
            temp_file.replace(self.log_path)

            self.logger.info(f"Cleaned up {removed_count} old trial logs, kept {kept_count}")
            return removed_count

        except Exception as e:
            self.logger.error(f"Error cleaning up old logs: {e}")
            if temp_file.exists():
                temp_file.unlink()
            return 0


# Global instance for easy access
_logger_instance = None

def get_logger() -> TrialLogger:
    """Get global trial logger instance"""
    global _logger_instance
    if _logger_instance is None:
        _logger_instance = TrialLogger()
    return _logger_instance

def log_trial(trial: IngestTrial) -> None:
    """Log a trial using the global logger"""
    get_logger().log_trial(trial)