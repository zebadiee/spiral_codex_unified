#!/usr/bin/env python3
"""
Spiral Codex - Trial/Error Capture & Classification System
Captures all failures with automatic categorization for reinforcement learning.
"""

import json
import time
import traceback
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any, Literal
from enum import Enum

class ErrorCategory(str, Enum):
    """Automatic error classification categories"""
    TIMEOUT = "timeout"
    NETWORK = "network"
    CONFIG = "config"
    PROVIDER = "provider"
    SYNTAX = "syntax"
    OTHER = "other"

class TrialLogger:
    """Unified trial/error capture with automatic classification"""
    
    def __init__(self, log_dir: str = "logs"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.trials_log = self.log_dir / "trials.jsonl"
        self._ensure_log()
    
    def _ensure_log(self):
        """Initialize trials log if it doesn't exist"""
        if not self.trials_log.exists():
            self.trials_log.touch()
    
    def _classify_error(self, error: Exception, context: str = "") -> ErrorCategory:
        """Automatically classify error type based on exception and context"""
        error_str = str(error).lower()
        error_type = type(error).__name__.lower()
        tb_str = traceback.format_exc().lower()
        
        # Classification rules
        if any(kw in error_str for kw in ["timeout", "timed out", "time out"]):
            return ErrorCategory.TIMEOUT
        
        if any(kw in error_str for kw in ["connection", "network", "unreachable", "dns"]):
            return ErrorCategory.NETWORK
        
        if any(kw in error_str for kw in ["api key", "authentication", "unauthorized", "rate limit"]):
            return ErrorCategory.PROVIDER
        
        if any(kw in error_type for kw in ["syntax", "parse", "indent"]):
            return ErrorCategory.SYNTAX
        
        if any(kw in error_str for kw in ["config", "configuration", "env", "environment"]):
            return ErrorCategory.CONFIG

        # Check context clues
        if "uvicorn" in context.lower() or "port" in error_str:
            return ErrorCategory.CONFIG

        # All other patterns (dependency, permission, etc.) map to "other"
        if any(kw in error_str for kw in ["no module", "import", "not found", "modulenotfound",
                                          "permission", "access denied", "forbidden"]):
            return ErrorCategory.OTHER

        return ErrorCategory.OTHER
    
    def log_trial(
        self,
        action: str,
        success: bool,
        error: Optional[Exception] = None,
        context: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Log a trial/error event with automatic classification
        
        Args:
            action: What was attempted
            success: Whether it succeeded
            error: Exception if failed
            context: Additional context string
            metadata: Extra structured data
        
        Returns:
            The logged trial entry
        """
        timestamp = datetime.utcnow().isoformat() + "Z"
        
        entry = {
            "timestamp": timestamp,
            "action": action,
            "success": success,
            "context": context or "",
            "metadata": metadata or {}
        }
        
        if not success and error:
            error_category = self._classify_error(error, context or "")
            entry.update({
                "error": {
                    "type": type(error).__name__,
                    "message": str(error),
                    "category": error_category.value,
                    "traceback": traceback.format_exc()
                }
            })
        
        # Append to JSONL
        with self.trials_log.open("a", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")
        
        return entry
    
    def log_success(self, action: str, context: Optional[str] = None, **metadata):
        """Convenience method for logging success"""
        return self.log_trial(action, True, context=context, metadata=metadata)
    
    def log_failure(self, action: str, error: Exception, context: Optional[str] = None, **metadata):
        """Convenience method for logging failure"""
        return self.log_trial(action, False, error=error, context=context, metadata=metadata)
    
    def get_recent_trials(self, limit: int = 100) -> list:
        """Retrieve recent trial entries"""
        if not self.trials_log.exists():
            return []
        
        trials = []
        with self.trials_log.open("r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    trials.append(json.loads(line))
        
        return trials[-limit:]
    
    def get_failures_by_category(self, since_hours: int = 24) -> Dict[str, list]:
        """Group recent failures by error category"""
        cutoff = datetime.utcnow().timestamp() - (since_hours * 3600)
        failures = {}
        
        for trial in self.get_recent_trials(limit=1000):
            if trial.get("success"):
                continue
            
            trial_time = datetime.fromisoformat(trial["timestamp"].rstrip("Z")).timestamp()
            if trial_time < cutoff:
                continue
            
            category = trial.get("error", {}).get("category", "unknown")
            if category not in failures:
                failures[category] = []
            failures[category].append(trial)
        
        return failures
    
    def generate_summary(self, since_hours: int = 24) -> Dict[str, Any]:
        """Generate statistical summary of trials"""
        trials = self.get_recent_trials(limit=1000)
        cutoff = datetime.utcnow().timestamp() - (since_hours * 3600)
        
        recent = [
            t for t in trials
            if datetime.fromisoformat(t["timestamp"].rstrip("Z")).timestamp() >= cutoff
        ]
        
        total = len(recent)
        successes = sum(1 for t in recent if t.get("success"))
        failures = total - successes
        
        failure_categories = {}
        for trial in recent:
            if not trial.get("success"):
                cat = trial.get("error", {}).get("category", "unknown")
                failure_categories[cat] = failure_categories.get(cat, 0) + 1
        
        return {
            "period_hours": since_hours,
            "total_trials": total,
            "successes": successes,
            "failures": failures,
            "success_rate": round(successes / total * 100, 2) if total > 0 else 0,
            "failure_categories": failure_categories,
            "top_failure": max(failure_categories.items(), key=lambda x: x[1])[0] if failure_categories else None
        }

    def generate_labeled_trials(self) -> str:
        """Generate trials_labeled.jsonl with all trials and their labels"""
        labeled_path = self.log_dir / "trials_labeled.jsonl"

        if not self.trials_log.exists():
            # Create empty labeled file
            labeled_path.touch()
            return str(labeled_path)

        # Read all trials and ensure they have labels
        labeled_trials = []
        with self.trials_log.open("r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    trial = json.loads(line)

                    # Ensure error has category label
                    if not trial.get("success") and "error" in trial:
                        if "category" not in trial["error"]:
                            # Try to classify from error message
                            error_msg = trial["error"].get("message", "")
                            error_type = trial["error"].get("type", "")
                            context = trial.get("context", "")

                            # Simple classification fallback
                            category = self._classify_error_from_strings(error_msg, error_type, context)
                            trial["error"]["category"] = category

                    labeled_trials.append(trial)

        # Write labeled trials
        with labeled_path.open("w", encoding="utf-8") as f:
            for trial in labeled_trials:
                f.write(json.dumps(trial, default=str) + "\n")

        return str(labeled_path)

    def _classify_error_from_strings(self, error_msg: str, error_type: str, context: str) -> str:
        """Classify error from string representations"""
        error_msg = error_msg.lower()
        error_type = error_type.lower()
        context = context.lower()

        # Classification rules
        if any(kw in error_msg for kw in ["timeout", "timed out", "time out"]):
            return "timeout"

        if any(kw in error_msg for kw in ["connection", "network", "unreachable", "dns"]):
            return "network"

        if any(kw in error_msg for kw in ["api key", "authentication", "unauthorized", "rate limit"]):
            return "provider"

        if any(kw in error_type for kw in ["syntax", "parse", "indent"]):
            return "syntax"

        if any(kw in error_msg for kw in ["config", "configuration", "env", "environment"]):
            return "config"

        if "uvicorn" in context or "port" in error_msg:
            return "config"

        return "other"

    def generate_top5_failures(self, since_hours: int = 24) -> str:
        """Generate TOP5 failure patterns summary"""
        failures_by_category = self.get_failures_by_category(since_hours)

        # Count failures per category
        category_counts = {cat: len(trials) for cat, trials in failures_by_category.items()}

        # Sort by count and get top 5
        top5 = sorted(category_counts.items(), key=lambda x: x[1], reverse=True)[:5]

        # Ensure data/lessons directory exists
        lessons_dir = Path("data/lessons")
        lessons_dir.mkdir(parents=True, exist_ok=True)

        # Generate markdown content
        content = []
        content.append(f"# TOP5 Failure Patterns - {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}")
        content.append("")
        content.append("## 📊 Failure Analysis (24h window)")
        content.append("")
        content.append(f"- **Total Failures**: {sum(category_counts.values())}")
        content.append(f"- **Unique Categories**: {len(category_counts)}")
        content.append(f"- **Top Category**: {top5[0][0] if top5 else 'None'}")
        content.append("")
        content.append("## 🔥 TOP5 Failure Categories")
        content.append("")

        for i, (category, count) in enumerate(top5, 1):
            percentage = (count / sum(category_counts.values()) * 100) if category_counts else 0
            content.append(f"### {i}. **{category.upper()}** - {count} occurrences ({percentage:.1f}%)")

            # Add recent examples
            examples = failures_by_category.get(category, [])[:3]  # Show up to 3 examples
            for example in examples:
                action = example.get("action", "unknown")
                error_msg = example.get("error", {}).get("message", "No message")
                content.append(f"   - **{action}**: {error_msg[:100]}...")

            content.append("")

        if len(top5) < 5:
            content.append("### Note: Fewer than 5 failure categories detected")
            content.append("")

        content.append("---")
        content.append("*Auto-generated by Spiral Codex Failure Classifier*")

        # Write to file
        output_file = lessons_dir / "failures_top5.md"
        with output_file.open("w", encoding="utf-8") as f:
            f.write("\n".join(content))

        return str(output_file)


# Global singleton instance
_logger: Optional[TrialLogger] = None

def get_logger() -> TrialLogger:
    """Get or create global TrialLogger instance"""
    global _logger
    if _logger is None:
        _logger = TrialLogger()
    return _logger

# Convenience functions
def log_success(action: str, context: Optional[str] = None, **metadata):
    """Log successful trial"""
    return get_logger().log_success(action, context, **metadata)

def log_failure(action: str, error: Exception, context: Optional[str] = None, **metadata):
    """Log failed trial"""
    return get_logger().log_failure(action, error, context, **metadata)

def trial_summary(since_hours: int = 24) -> Dict[str, Any]:
    """Get trial summary"""
    return get_logger().generate_summary(since_hours)
