#!/usr/bin/env python3
"""
Spiral Codex - Trial Summarization Engine
Converts trial/error logs into structured lessons for OMAi ingestion
"""

import json
import sys
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any
from collections import defaultdict

sys.path.insert(0, str(Path(__file__).parent.parent))
from utils.trials import TrialLogger, ErrorCategory

class TrialSummarizer:
    """Convert trials into actionable lessons"""
    
    def __init__(self, trials_log: str = "logs/trials.jsonl"):
        self.logger = TrialLogger()
        self.output_dir = Path("data")
        self.output_dir.mkdir(exist_ok=True)
        self.lessons_file = self.output_dir / "omai_lessons.jsonl"
        self.summary_file = self.output_dir / "trial_summary.md"
    
    def _extract_lesson(self, failure_group: List[Dict]) -> Dict[str, Any]:
        """Extract a lesson from a group of similar failures"""
        if not failure_group:
            return {}
        
        # Use first failure as representative
        first = failure_group[0]
        error = first.get("error", {})
        
        # Build lesson
        lesson = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "category": error.get("category", "unknown"),
            "pattern": first["action"],
            "occurrences": len(failure_group),
            "error_type": error.get("type", "Unknown"),
            "error_message": error.get("message", ""),
            "contexts": [f.get("context", "") for f in failure_group if f.get("context")],
            "proposed_fix": self._suggest_fix(error.get("category"), error.get("message", ""))
        }
        
        return lesson
    
    def _suggest_fix(self, category: str, message: str) -> str:
        """Generate fix suggestion based on error category"""
        fixes = {
            "timeout": "Consider increasing timeout values or implementing retry logic with exponential backoff",
            "network": "Check network connectivity, DNS resolution, and firewall rules. Implement fallback providers.",
            "provider": "Verify API keys in .env.local, check rate limits, and ensure provider service is available",
            "syntax": "Review code syntax, check indentation, and validate Python version compatibility",
            "dependency": "Run 'pip install -r requirements.txt' and verify all dependencies are installed",
            "permission": "Check file/directory permissions with 'ls -la' and adjust with chmod/chown if needed",
            "config": "Verify .env.local configuration, check port availability, and validate service bindings"
        }
        
        base_fix = fixes.get(category, "Investigate error logs and stack traces for root cause")
        
        # Context-specific enhancements
        if "port" in message.lower():
            return base_fix + " | Check if port is already in use with 'lsof -i' or 'netstat -tuln'"
        if "module" in message.lower():
            return base_fix + " | Ensure virtual environment is activated and dependencies are up-to-date"
        if "key" in message.lower():
            return base_fix + " | Verify API key format and expiration date"
        
        return base_fix
    
    def summarize(self, since_hours: int = 24) -> Dict[str, Any]:
        """Generate comprehensive trial summary"""
        print(f"📊 Summarizing trials from last {since_hours} hours...")
        
        # Get statistical summary
        stats = self.logger.generate_summary(since_hours)
        print(f"   Total: {stats['total_trials']} | Success: {stats['successes']} | Failures: {stats['failures']}")
        
        # Group failures by category
        failures_by_cat = self.logger.get_failures_by_category(since_hours)
        
        # Extract lessons
        lessons = []
        for category, failures in failures_by_cat.items():
            # Group by action pattern
            by_action = defaultdict(list)
            for f in failures:
                by_action[f["action"]].append(f)
            
            # Create lesson for each unique failure pattern
            for action, group in by_action.items():
                lesson = self._extract_lesson(group)
                if lesson:
                    lessons.append(lesson)
        
        print(f"   Extracted {len(lessons)} unique lessons")
        
        # Write lessons to JSONL
        with self.lessons_file.open("a", encoding="utf-8") as f:
            for lesson in lessons:
                f.write(json.dumps(lesson) + "\n")
        
        # Generate markdown summary
        self._generate_markdown(stats, lessons)
        
        return {
            "stats": stats,
            "lessons": lessons,
            "lessons_file": str(self.lessons_file),
            "summary_file": str(self.summary_file)
        }
    
    def _generate_markdown(self, stats: Dict, lessons: List[Dict]):
        """Generate human-readable markdown summary"""
        md = f"""# Trial Summary - {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}

## 📊 Statistics ({stats['period_hours']}h window)

- **Total Trials**: {stats['total_trials']}
- **Success Rate**: {stats['success_rate']}%
- **Failures**: {stats['failures']}
- **Top Failure Category**: {stats.get('top_failure', 'None')}

## 🔍 Failure Breakdown

"""
        
        for cat, count in stats['failure_categories'].items():
            md += f"- **{cat.upper()}**: {count} occurrences\n"
        
        md += "\n## 🧠 Extracted Lessons\n\n"
        
        for i, lesson in enumerate(lessons, 1):
            md += f"### {i}. {lesson['pattern']}\n\n"
            md += f"- **Category**: `{lesson['category']}`\n"
            md += f"- **Occurrences**: {lesson['occurrences']}\n"
            md += f"- **Error**: {lesson['error_type']}\n"
            md += f"- **Fix**: {lesson['proposed_fix']}\n\n"
        
        md += "\n---\n*Auto-generated by Spiral Codex Trial Summarizer*\n"
        
        with self.summary_file.open("w", encoding="utf-8") as f:
            f.write(md)
        
        print(f"✅ Summary written to {self.summary_file}")

def main():
    """CLI entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Summarize trials into lessons")
    parser.add_argument("--hours", type=int, default=24, help="Hours to look back")
    parser.add_argument("--output", help="Override output directory")
    
    args = parser.parse_args()
    
    summarizer = TrialSummarizer()
    result = summarizer.summarize(since_hours=args.hours)
    
    print(f"\n✨ Lesson extraction complete!")
    print(f"   Lessons: {result['lessons_file']}")
    print(f"   Summary: {result['summary_file']}")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
