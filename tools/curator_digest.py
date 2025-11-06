#!/usr/bin/env python3
"""
Curator Cockpit Daily Digest Generator

Generates a comprehensive daily brief synthesizing multiple data sources:
- Wean trends and recommendations
- Top failures from classifier
- RAG quality metrics
- System stability results
- Vault indexing statistics
"""

import json
import csv
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional
import argparse

class CuratorDigestGenerator:
    def __init__(self, base_dir: str = "/home/zebadiee/Documents/spiral_codex_unified"):
        self.base_dir = Path(base_dir)
        self.data_dir = self.base_dir / "data"
        self.reports_dir = self.data_dir / "reports"
        self.logs_dir = self.base_dir / "logs"
        self.vault_dir = self.base_dir / "codex_root" / "vault"

    def load_wean_recommendations(self) -> Dict[str, Any]:
        """Load wean optimization recommendations."""
        wean_file = self.reports_dir / "wean_recommendation.md"
        if not wean_file.exists():
            return {"error": "Wean recommendation file not found"}

        with open(wean_file, 'r') as f:
            content = f.read()

        # Extract key metrics from wean report
        return {
            "file_path": str(wean_file),
            "analysis_date": self._extract_field(content, "Analysis Date"),
            "current_setting": self._extract_field(content, "Current Setting"),
            "recommended_setting": self._extract_field(content, "Recommended Setting"),
            "overall_success_rate": self._extract_field(content, "Overall Success Rate"),
            "total_requests": self._extract_field(content, "Total Requests"),
            "average_latency": self._extract_field(content, "Average Latency"),
            "failure_rate": self._extract_field(content, "Failure Rate")
        }

    def load_failure_data(self) -> Dict[str, Any]:
        """Load and analyze failure classification data."""
        trials_file = self.logs_dir / "trials.jsonl"
        if not trials_file.exists():
            return {"error": "Trials log file not found"}

        failures = []
        successes = []
        error_categories = {}

        with open(trials_file, 'r') as f:
            for line in f:
                if line.strip():
                    try:
                        entry = json.loads(line)
                        if entry.get('success'):
                            successes.append(entry)
                        else:
                            failures.append(entry)
                            if 'error' in entry and 'category' in entry['error']:
                                category = entry['error']['category']
                                error_categories[category] = error_categories.get(category, 0) + 1
                    except json.JSONDecodeError:
                        continue

        # Get top failure categories
        top_failures = sorted(error_categories.items(), key=lambda x: x[1], reverse=True)[:5]

        return {
            "file_path": str(trials_file),
            "total_trials": len(successes) + len(failures),
            "success_count": len(successes),
            "failure_count": len(failures),
            "success_rate": (len(successes) / (len(successes) + len(failures)) * 100) if (len(successes) + len(failures)) > 0 else 0,
            "top_failure_categories": top_failures,
            "recent_failures": failures[:3]  # Most recent 3 failures
        }

    def load_rag_metrics(self) -> Dict[str, Any]:
        """Load RAG quality evaluation metrics."""
        rag_file = self.data_dir / "ablation" / "rag_eval.json"
        if not rag_file.exists():
            return {"error": "RAG evaluation file not found"}

        with open(rag_file, 'r') as f:
            data = json.load(f)

        metrics = data.get('metrics', {})
        return {
            "file_path": str(rag_file),
            "timestamp": data.get('timestamp'),
            "methodology": data.get('methodology'),
            "total_queries": metrics.get('total_queries', 0),
            "enhanced_win_rate": metrics.get('enhanced_win_rate', 0),
            "legacy_win_rate": metrics.get('legacy_win_rate', 0),
            "tie_rate": metrics.get('tie_rate', 0),
            "overall_improvement": metrics.get('overall_improvement', 0),
            "overall_enhanced_relevance": metrics.get('overall_enhanced_relevance', 0),
            "overall_legacy_relevance": metrics.get('overall_legacy_relevance', 0)
        }

    def load_stability_data(self) -> Dict[str, Any]:
        """Load system stability data from wean logs."""
        wean_file = self.logs_dir / "wean.csv"
        if not wean_file.exists():
            return {"error": "Wean log file not found"}

        provider_stats = {}
        total_requests = 0
        successful_requests = 0
        total_latency = 0

        with open(wean_file, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                provider = row['provider']
                success = int(row['ok'])
                latency = float(row['latency_ms'])

                total_requests += 1
                total_latency += latency
                if success:
                    successful_requests += 1

                if provider not in provider_stats:
                    provider_stats[provider] = {
                        'requests': 0,
                        'successes': 0,
                        'total_latency': 0
                    }

                provider_stats[provider]['requests'] += 1
                provider_stats[provider]['total_latency'] += latency
                if success:
                    provider_stats[provider]['successes'] += 1

        # Calculate success rates and average latencies
        for provider, stats in provider_stats.items():
            stats['success_rate'] = (stats['successes'] / stats['requests'] * 100) if stats['requests'] > 0 else 0
            stats['avg_latency'] = stats['total_latency'] / stats['requests'] if stats['requests'] > 0 else 0

        overall_success_rate = (successful_requests / total_requests * 100) if total_requests > 0 else 0
        overall_avg_latency = total_latency / total_requests if total_requests > 0 else 0

        return {
            "file_path": str(wean_file),
            "total_requests": total_requests,
            "overall_success_rate": overall_success_rate,
            "overall_avg_latency": overall_avg_latency,
            "provider_performance": provider_stats
        }

    def load_vault_stats(self) -> Dict[str, Any]:
        """Load vault indexing statistics."""
        if not self.vault_dir.exists():
            return {"error": "Vault directory not found"}

        # Count vault files
        vault_files = list(self.vault_dir.glob("*.json"))
        total_files = len(vault_files)

        # Get most recent analysis
        recent_file = None
        most_recent_time = None
        for file_path in vault_files:
            try:
                file_time = datetime.fromtimestamp(file_path.stat().st_mtime)
                if most_recent_time is None or file_time > most_recent_time:
                    most_recent_time = file_time
                    recent_file = file_path
            except:
                continue

        recent_analysis = None
        if recent_file:
            try:
                with open(recent_file, 'r') as f:
                    recent_analysis = json.load(f)
            except:
                pass

        return {
            "vault_path": str(self.vault_dir),
            "total_analysis_files": total_files,
            "most_recent_analysis": recent_file.name if recent_file else None,
            "most_recent_timestamp": recent_analysis.get('timestamp') if recent_analysis else None,
            "latest_query": recent_analysis.get('query') if recent_analysis else None,
            "latest_confidence": recent_analysis.get('analysis', {}).get('confidence') if recent_analysis else None
        }

    def determine_go_no_go(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Determine overall system health and go/no-go recommendation."""
        score = 100
        issues = []
        recommendations = []

        # Check wean performance
        wean = data.get('wean', {})
        if isinstance(wean, dict) and 'overall_success_rate' in wean:
            success_rate = float(wean['overall_success_rate'].rstrip('%')) if isinstance(wean['overall_success_rate'], str) else 0
            if success_rate < 70:
                score -= 30
                issues.append(f"Low overall success rate: {success_rate}%")
            elif success_rate < 85:
                score -= 15
                issues.append(f"Moderate success rate: {success_rate}%")

        # Check failure patterns
        failures = data.get('failures', {})
        if isinstance(failures, dict) and 'success_rate' in failures:
            failure_success_rate = failures['success_rate']
            if failure_success_rate < 60:
                score -= 25
                issues.append(f"High trial failure rate: {100-failure_success_rate:.1f}%")

        # Check RAG quality
        rag = data.get('rag', {})
        if isinstance(rag, dict) and 'overall_improvement' in rag:
            improvement = rag['overall_improvement']
            if improvement < -20:
                score -= 20
                issues.append(f"RAG performance degradation: {improvement:.1f}%")

        # Check stability
        stability = data.get('stability', {})
        if isinstance(stability, dict) and 'overall_success_rate' in stability:
            stability_success_rate = stability['overall_success_rate']
            if stability_success_rate < 75:
                score -= 25
                issues.append(f"System instability: {stability_success_rate:.1f}% success rate")

        # Determine recommendation
        if score >= 85:
            recommendation = "GO"
            status_emoji = "✅"
            priority = "LOW"
        elif score >= 70:
            recommendation = "GO WITH MONITORING"
            status_emoji = "⚠️"
            priority = "MEDIUM"
        else:
            recommendation = "NO-GO"
            status_emoji = "❌"
            priority = "HIGH"

        return {
            "overall_score": score,
            "recommendation": recommendation,
            "status_emoji": status_emoji,
            "priority": priority,
            "issues": issues,
            "next_actions": self._generate_next_actions(data, score)
        }

    def _generate_next_actions(self, data: Dict[str, Any], score: float) -> List[str]:
        """Generate next action items based on data analysis."""
        actions = []

        # Wean-related actions
        wean = data.get('wean', {})
        if isinstance(wean, dict) and 'recommended_setting' in wean:
            actions.append(f"Implement WEAN_LOCAL_PCT={wean['recommended_setting']} optimization")

        # Failure-related actions
        failures = data.get('failures', {})
        if isinstance(failures, dict) and 'top_failure_categories' in failures:
            top_category = failures['top_failure_categories'][0] if failures['top_failure_categories'] else None
            if top_category:
                actions.append(f"Address top failure category: {top_category[0]} ({top_category[1]} occurrences)")

        # RAG-related actions
        rag = data.get('rag', {})
        if isinstance(rag, dict) and 'overall_improvement' in rag:
            improvement = rag['overall_improvement']
            if improvement < 0:
                actions.append("Investigate RAG quality regression and optimize retrieval")

        # System health actions
        if score < 80:
            actions.append("Schedule immediate system health review")

        actions.append("Review detailed reports in data/reports/ directory")
        actions.append("Update monitoring thresholds based on current performance")

        return actions[:5]  # Limit to top 5 actions

    def generate_digest(self, output_dir: Optional[str] = None) -> str:
        """Generate the complete daily digest."""
        today = datetime.now().strftime("%Y-%m-%d")

        # Collect all data sources
        data = {
            "wean": self.load_wean_recommendations(),
            "failures": self.load_failure_data(),
            "rag": self.load_rag_metrics(),
            "stability": self.load_stability_data(),
            "vault": self.load_vault_stats()
        }

        # Generate recommendation
        recommendation = self.determine_go_no_go(data)

        # Generate digest content
        digest_content = self._format_digest(today, data, recommendation)

        # Determine output directory
        if output_dir is None:
            output_dir = self.reports_dir

        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)

        # Write digest file
        digest_file = Path(output_dir) / f"digest_{today}.md"
        with open(digest_file, 'w') as f:
            f.write(digest_content)

        return str(digest_file)

    def _format_digest(self, date: str, data: Dict[str, Any], recommendation: Dict[str, Any]) -> str:
        """Format the digest content into markdown."""
        digest = f"""# Curator Cockpit Daily Digest

**Date:** {date}
**Generated:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")}
**Status:** {recommendation['status_emoji']} {recommendation['recommendation']} (Score: {recommendation['overall_score']}/100)
**Priority:** {recommendation['priority']}

---

## 🎯 Executive Summary

The Spiral Codex system shows {"healthy" if recommendation['overall_score'] >= 80 else "degraded" if recommendation['overall_score'] >= 60 else "critical"} performance with an overall score of {recommendation['overall_score']}/100. Key metrics indicate{" strong system stability with minor optimization opportunities" if recommendation['overall_score'] >= 85 else " some areas requiring attention" if recommendation['overall_score'] >= 70 else " significant issues requiring immediate action"}.

**Key Issues:**
"""

        if recommendation['issues']:
            for issue in recommendation['issues']:
                digest += f"- {issue}\n"
        else:
            digest += "- No critical issues detected\n"

        digest += f"""
**System Status:** {recommendation['recommendation']}

---

## 📊 System Health Indicators

### Wean Performance Analysis
"""

        wean = data.get('wean', {})
        if isinstance(wean, dict) and 'error' not in wean:
            digest += f"""- **Current Setting:** {wean.get('current_setting', 'N/A')}
- **Recommended Setting:** {wean.get('recommended_setting', 'N/A')}
- **Overall Success Rate:** {wean.get('overall_success_rate', 'N/A')}
- **Total Requests:** {wean.get('total_requests', 'N/A')}
- **Average Latency:** {wean.get('average_latency', 'N/A')}
- **Failure Rate:** {wean.get('failure_rate', 'N/A')}

📄 **Detailed Report:** [{wean.get('file_path', '')}]({wean.get('file_path', '')})

"""
        else:
            digest += f"- ⚠️ Wean data unavailable: {wean.get('error', 'Unknown error')}\n\n"

        digest += """### Trial/Failure Classification
"""

        failures = data.get('failures', {})
        if isinstance(failures, dict) and 'error' not in failures:
            digest += f"""- **Total Trials:** {failures.get('total_trials', 0)}
- **Success Rate:** {failures.get('success_rate', 0):.1f}%
- **Successes:** {failures.get('success_count', 0)}
- **Failures:** {failures.get('failure_count', 0)}

**Top Failure Categories:**
"""
            for category, count in failures.get('top_failure_categories', []):
                digest += f"- {category}: {count} occurrences\n"

            digest += f"\n📄 **Full Trial Log:** [{failures.get('file_path', '')}]({failures.get('file_path', '')})\n\n"
        else:
            digest += f"- ⚠️ Failure classification data unavailable: {failures.get('error', 'Unknown error')}\n\n"

        digest += """### RAG Quality Metrics
"""

        rag = data.get('rag', {})
        if isinstance(rag, dict) and 'error' not in rag:
            digest += f"""- **Methodology:** {rag.get('methodology', 'N/A')}
- **Total Queries:** {rag.get('total_queries', 0)}
- **Enhanced Win Rate:** {rag.get('enhanced_win_rate', 0):.1f}%
- **Legacy Win Rate:** {rag.get('legacy_win_rate', 0):.1f}%
- **Tie Rate:** {rag.get('tie_rate', 0):.1f}%
- **Overall Improvement:** {rag.get('overall_improvement', 0):.1f}%
- **Enhanced Relevance:** {rag.get('overall_enhanced_relevance', 0):.3f}
- **Legacy Relevance:** {rag.get('overall_legacy_relevance', 0):.3f}

📄 **RAG Evaluation:** [{rag.get('file_path', '')}]({rag.get('file_path', '')})

"""
        else:
            digest += f"- ⚠️ RAG evaluation data unavailable: {rag.get('error', 'Unknown error')}\n\n"

        digest += """### System Stability
"""

        stability = data.get('stability', {})
        if isinstance(stability, dict) and 'error' not in stability:
            digest += f"""- **Total Requests:** {stability.get('total_requests', 0)}
- **Overall Success Rate:** {stability.get('overall_success_rate', 0):.1f}%
- **Overall Average Latency:** {stability.get('overall_avg_latency', 0):.2f}ms

**Provider Performance:**
"""
            for provider, stats in stability.get('provider_performance', {}).items():
                digest += f"- **{provider}:** {stats['success_rate']:.1f}% success, {stats['avg_latency']:.2f}ms avg latency\n"

            digest += f"\n📄 **Stability Data:** [{stability.get('file_path', '')}]({stability.get('file_path', '')})\n\n"
        else:
            digest += f"- ⚠️ Stability data unavailable: {stability.get('error', 'Unknown error')}\n\n"

        digest += """### Vault Content Insights
"""

        vault = data.get('vault', {})
        if isinstance(vault, dict) and 'error' not in vault:
            digest += f"""- **Total Analysis Files:** {vault.get('total_analysis_files', 0)}
- **Most Recent Analysis:** {vault.get('most_recent_analysis', 'N/A')}
- **Latest Query:** "{vault.get('latest_query', 'N/A')}"
- **Latest Confidence:** {vault.get('latest_confidence', 'N/A')}

📁 **Vault Directory:** [{vault.get('vault_path', '')}]({vault.get('vault_path', '')})

"""
        else:
            digest += f"- ⚠️ Vault data unavailable: {vault.get('error', 'Unknown error')}\n\n"

        digest += f"""---

## 🚨 Go/No-Go Recommendation

**Decision:** {recommendation['status_emoji']} {recommendation['recommendation']}
**Confidence:** {recommendation['overall_score']}/100
**Priority:** {recommendation['priority']}

### Next Actions
"""

        for i, action in enumerate(recommendation.get('next_actions', []), 1):
            digest += f"{i}. {action}\n"

        digest += """

---

## 📋 Quick Links to Detailed Reports

- **Wean Optimization:** [data/reports/wean_recommendation.md](data/reports/wean_recommendation.md)
- **Trial Logs:** [logs/trials.jsonl](logs/trials.jsonl)
- **RAG Evaluation:** [data/ablation/rag_eval.json](data/ablation/rag_eval.json)
- **System Stability:** [logs/wean.csv](logs/wean.csv)
- **Vault Analysis:** [codex_root/vault/](codex_root/vault/)

---

## 📈 Monitoring Commands

```bash
# Check system health
make health

# Monitor wean performance in real-time
watch -n 30 "awk -F, 'NR>1 {tot++; if(\\$7==1) ok++} END {printf \\"Success: %.1f%% (%d/%d)\\\\n\\", ok/tot*100, ok, tot}' logs/wean.csv"

# Extract recent lessons
make lessons

# Run reflection cycle
make reflect
```

---

*Digest generated by Curator Cockpit Autosummary System*
*Next digest: """ + datetime.now().strftime('%Y-%m-%d') + """ 00:10 UTC*
"""

        return digest

    def _extract_field(self, content: str, field_name: str) -> str:
        """Extract a field value from markdown content."""
        lines = content.split('\n')
        for line in lines:
            if f"**{field_name}:**" in line:
                return line.split("**", 2)[-1].strip()
        return "N/A"


def main():
    parser = argparse.ArgumentParser(description="Generate Curator Cockpit Daily Digest")
    parser.add_argument("--output-dir", help="Output directory for digest file")
    parser.add_argument("--base-dir", default="/home/zebadiee/Documents/spiral_codex_unified",
                       help="Base directory of Spiral Codex project")

    args = parser.parse_args()

    generator = CuratorDigestGenerator(args.base_dir)

    try:
        digest_file = generator.generate_digest(args.output_dir)
        print(f"✅ Daily digest generated: {digest_file}")

        # Also print a quick summary
        with open(digest_file, 'r') as f:
            content = f.read()
            # Extract just the executive summary
            lines = content.split('\n')
            in_summary = False
            for line in lines:
                if "## 🎯 Executive Summary" in line:
                    in_summary = True
                elif in_summary and line.startswith("## "):
                    break
                elif in_summary:
                    print(line)

    except Exception as e:
        print(f"❌ Error generating digest: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()