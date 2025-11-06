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
    CONFIG = "config"
    NETWORK = "network"
    PROVIDER = "provider"
    SYNTAX = "syntax"
    DEPENDENCY = "dependency"
    PERMISSION = "permission"
    UNKNOWN = "unknown"

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
        
        if any(kw in error_str for kw in ["no module", "import", "not found", "modulenotfound"]):
            return ErrorCategory.DEPENDENCY
        
        if any(kw in error_str for kw in ["permission", "access denied", "forbidden"]):
            return ErrorCategory.PERMISSION
        
        if any(kw in error_str for kw in ["config", "configuration", "env", "environment"]):
            return ErrorCategory.CONFIG
        
        # Check context clues
        if "uvicorn" in context.lower() or "port" in error_str:
            return ErrorCategory.CONFIG
        
        return ErrorCategory.UNKNOWN
    
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
