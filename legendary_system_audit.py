#!/usr/bin/env python3
"""
🔬 LEGENDARY SYSTEM AUDIT - Complete Integrity Verification
Finds and plugs ALL Swiss cheese holes in your OMAi Spiral Codex system
CRITICAL PATH - Nothing forgotten, everything verified!
"""
import requests
import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path

# Quantum colors for critical feedback
RED = "\033[31m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
BLUE = "\033[34m"
MAGENTA = "\033[35m"
CYAN = "\033[36m"
QUANTUM = "\033[38;5;93m"
BOLD = "\033[1m"
RESET = "\033[0m"

# Critical symbols
CRITICAL = "🚨"
WARNING = "⚠️"
GOOD = "✅"
QUANTUM_ACTIVE = "⊚"
HOLES = "🕳️"

class LegendaryAuditor:
    """Complete system integrity auditor - finds ALL holes"""

    def __init__(self):
        self.base_url = "http://localhost:8000"
        self.issues = []
        self.warnings = []
        self.successes = []
        self.start_time = datetime.now()

    def log_critical(self, message):
        """Log critical finding"""
        self.issues.append(message)
        print(f"{RED}{CRITICAL} CRITICAL: {message}{RESET}")

    def log_warning(self, message):
        """Log warning finding"""
        self.warnings.append(message)
        print(f"{YELLOW}{WARNING} WARNING: {message}{RESET}")

    def log_success(self, message):
        """Log success finding"""
        self.successes.append(message)
        print(f"{GREEN}{GOOD} {message}{RESET}")

    def test_brain_integrity(self):
        """Test quantum brain integrity"""
        print(f"\n{BOLD}{QUANTUM}🧠 QUANTUM BRAIN INTEGRITY AUDIT{RESET}")
        print("=" * 60)

        try:
            # Test brain stats
            response = requests.get(f"{self.base_url}/v1/brain/stats", timeout=5)
            if response.status_code == 200:
                stats = response.json()
                print(f"Brain Status: {stats.get('status', 'Unknown')}")
                print(f"Total Entries: {stats.get('total_entries', 0)}")
                print(f"Thought Count: {stats.get('thought_count', 0)}")
                print(f"Protocol: {stats.get('protocol', 'Unknown')}")

                # HOLE DETECTION: Only 7 entries, 3 thoughts - too few!
                if stats.get('total_entries', 0) < 20:
                    self.log_warning(f"Low brain entries: {stats.get('total_entries')} (<20 recommended)")

                if stats.get('thought_count', 0) < 10:
                    self.log_critical(f"Critical: Low thought count: {stats.get('thought_count')} (<10 needed)")

                if stats.get('status') != '⊚ active':
                    self.log_critical(f"Brain not quantum active: {stats.get('status')}")

            else:
                self.log_critical(f"Brain stats unreachable: HTTP {response.status_code}")

        except Exception as e:
            self.log_critical(f"Brain audit failed: {e}")

    def test_ledger_integrity(self):
        """Test brain ledger for completeness"""
        print(f"\n{BOLD}{QUANTUM}📜 LEDGER INTEGRITY AUDIT{RESET}")
        print("=" * 60)

        try:
            response = requests.get(f"{self.base_url}/v1/brain/ledger", timeout=5)
            if response.status_code == 200:
                ledger = response.json()
                print(f"Ledger Entries: {len(ledger)}")

                # HOLE DETECTION: Check for missing record types
                record_types = set(entry.get('record_type', 'unknown') for entry in ledger)
                print(f"Record Types: {record_types}")

                if 'glyph' in record_types and len(record_types) < 3:
                    self.log_warning(f"Limited record types: {record_types} (need more diversity)")

                # Check for recent entries
                if ledger:
                    latest = max(entry.get('timestamp', '') for entry in ledger)
                    print(f"Latest Entry: {latest}")

                    # Check if entries are recent (last hour)
                    try:
                        latest_time = datetime.fromisoformat(latest.replace('Z', '+00:00'))
                        if (datetime.now(latest_time.tzinfo) - latest_time).total_seconds() > 3600:
                            self.log_warning("No ledger entries in last hour - possible hole")
                    except:
                        self.log_warning("Cannot parse ledger timestamps")

            else:
                self.log_critical(f"Ledger unreachable: HTTP {response.status_code}")

        except Exception as e:
            self.log_critical(f"Ledger audit failed: {e}")

    def test_converse_system(self):
        """Test converse system integrity"""
        print(f"\n{BOLD}{QUANTUM}💬 CONVERSE SYSTEM AUDIT{RESET}")
        print("=" * 60)

        try:
            response = requests.get(f"{self.base_url}/v1/converse/status", timeout=5)
            if response.status_code == 200:
                status = response.json()
                print(f"Converse Status: {status.get('status', 'Unknown')}")
                print(f"Active Sessions: {status.get('active_sessions', 0)}")
                print(f"Active Collaborations: {status.get('active_collaborations', 0)}")
                print(f"Available Agents: {status.get('available_agents', 0)}")

                # HOLE DETECTION: Too many active sessions?
                sessions = status.get('active_sessions', 0)
                if sessions > 100:
                    self.log_warning(f"High session count: {sessions} (>100 may indicate memory leak)")
                elif sessions == 0:
                    self.log_critical("No active sessions - system possibly down")

                collaborations = status.get('active_collaborations', 0)
                if collaborations == 0:
                    self.log_warning("No active collaborations - missing parallel processing")

                agents = status.get('available_agents', 0)
                if agents < 4:
                    self.log_critical(f"Low agent count: {agents} (<4 needed for redundancy)")

            else:
                self.log_critical(f"Converse status unreachable: HTTP {response.status_code}")

        except Exception as e:
            self.log_critical(f"Converse audit failed: {e}")

    def test_agents_system(self):
        """Test all available agents"""
        print(f"\n{BOLD}{QUANTUM}🤖 AGENT SYSTEM AUDIT{RESET}")
        print("=" * 60)

        try:
            response = requests.get(f"{self.base_url}/v1/converse/agents", timeout=5)
            if response.status_code == 200:
                agents = response.json()
                print(f"Available Agents: {len(agents)}")

                for agent in agents:
                    print(f"  • {agent}")

                # HOLE DETECTION: Test each agent capability
                for agent in agents:
                    try:
                        agent_response = requests.get(f"{self.base_url}/v1/converse/agents/{agent}", timeout=3)
                        if agent_response.status_code != 200:
                            self.log_warning(f"Agent {agent} not responding properly")
                        else:
                            agent_info = agent_response.json()
                            if not agent_info:
                                self.log_warning(f"Agent {agent} returned empty info")

                    except:
                        self.log_warning(f"Cannot reach agent {agent}")

                # Check for missing essential agents
                essential_agents = ['claude', 'codex', 'gemini', 'omai']
                missing_agents = [a for a in essential_agents if a not in agents]
                if missing_agents:
                    self.log_critical(f"Missing essential agents: {missing_agents}")

            else:
                self.log_critical(f"Agents unreachable: HTTP {response.status_code}")

        except Exception as e:
            self.log_critical(f"Agent audit failed: {e}")

    def test_priority_system(self):
        """Test MIT license priority system integration"""
        print(f"\n{BOLD}{QUANTUM}🎯 PRIORITY SYSTEM AUDIT{RESET}")
        print("=" * 60)

        # Test local priority scoring
        try:
            sys.path.append(str(Path(__file__).parent))
            from utils.priority_sources import priority_manager

            # Test ManuAGI priority
            test_content = {
                'url': 'https://github.com/manuagi',
                'title': 'ManuAGI Open Source AI Development',
                'content': 'MIT license educational content for AI development',
                'source_type': 'tutorial'
            }

            score = priority_manager.calculate_priority_score(test_content)
            level = priority_manager._get_priority_level(score)

            print(f"ManuAGI Priority Score: {score:.2f}")
            print(f"Priority Level: {level}")

            if score < 3.0:
                self.log_critical(f"ManuAGI not getting max priority: {score:.2f} (<3.0)")
            else:
                self.log_success(f"ManuAGI correctly prioritized: {score:.2f}")

            # Test random content priority
            random_content = {
                'url': 'https://example.com',
                'title': 'Random Blog',
                'content': 'some random content',
                'source_type': 'blog'
            }

            random_score = priority_manager.calculate_priority_score(random_content)
            print(f"Random Content Score: {random_score:.2f}")

            if random_score > 1.5:
                self.log_warning(f"Random content too highly prioritized: {random_score:.2f}")

        except Exception as e:
            self.log_critical(f"Priority system test failed: {e}")

    def test_omai_integration(self):
        """Test OMAi system integration"""
        print(f"\n{BOLD}{QUANTUM}🌀 OMAI INTEGRATION AUDIT{RESET}")
        print("=" * 60)

        endpoints_to_test = [
            "/v1/omai/health",
            "/v1/omai/status",
            "/v1/omai/ledger"
        ]

        for endpoint in endpoints_to_test:
            try:
                response = requests.get(f"{self.base_url}{endpoint}", timeout=3)
                if response.status_code == 200:
                    print(f"✅ {endpoint} - Online")
                else:
                    self.log_warning(f"{endpoint} - HTTP {response.status_code}")
            except:
                self.log_critical(f"{endpoint} - Unreachable")

    def test_file_system_integrity(self):
        """Test critical file system components"""
        print(f"\n{BOLD}{QUANTUM}📁 FILE SYSTEM AUDIT{RESET}")
        print("=" * 60)

        critical_files = [
            "utils/priority_sources.py",
            "utils/enhanced_vault_manager.py",
            "fetchers/youtube_transcript_fetcher.py",
            "tools/priority_content_manager.py",
            "docs/MIT_LICENSE_RESEARCH_COMPLIANCE.md",
            "fastapi_app.py"
        ]

        for file_path in critical_files:
            if Path(file_path).exists():
                print(f"✅ {file_path}")
            else:
                self.log_critical(f"Missing critical file: {file_path}")

        # Check data directories
        data_dirs = ["data", "logs", "ledger"]
        for dir_path in data_dirs:
            if Path(dir_path).exists():
                print(f"✅ {dir_path}/ directory")
            else:
                self.log_warning(f"Missing data directory: {dir_path}")

    def run_complete_audit(self):
        """Run the complete legendary audit"""
        print(f"{BOLD}{QUANTUM}🔬 LEGENDARY SYSTEM AUDIT STARTING{RESET}")
        print(f"{QUANTUM}{'='*70}{RESET}")
        print(f"Time: {self.start_time}")
        print(f"Goal: Find and plug ALL Swiss cheese holes")
        print(f"CRITICAL PATH - Nothing forgotten!{RESET}")
        print(f"{QUANTUM}{'='*70}{RESET}\n")

        # Run all audits
        self.test_brain_integrity()
        self.test_ledger_integrity()
        self.test_converse_system()
        self.test_agents_system()
        self.test_priority_system()
        self.test_omai_integration()
        self.test_file_system_integrity()

        # Generate final report
        self.generate_report()

    def generate_report(self):
        """Generate comprehensive audit report"""
        end_time = datetime.now()
        duration = end_time - self.start_time

        print(f"\n{BOLD}{QUANTUM}📊 LEGENDARY AUDIT REPORT{RESET}")
        print(f"{QUANTUM}{'='*70}{RESET}")
        print(f"Duration: {duration}")
        print(f"Critical Issues: {len(self.issues)}")
        print(f"Warnings: {len(self.warnings)}")
        print(f"Successes: {len(self.successes)}")

        if self.issues:
            print(f"\n{RED}{CRITICAL} CRITICAL ISSUES (Must Fix):{RESET}")
            for i, issue in enumerate(self.issues, 1):
                print(f"{i}. {issue}")

        if self.warnings:
            print(f"\n{YELLOW}{WARNING} WARNINGS (Should Fix):{RESET}")
            for i, warning in enumerate(self.warnings, 1):
                print(f"{i}. {warning}")

        if self.successes:
            print(f"\n{GREEN}{GOOD} WORKING CORRECTLY:{RESET}")
            for i, success in enumerate(self.successes, 1):
                print(f"{i}. {success}")

        # Overall system health
        total_checks = len(self.issues) + len(self.warnings) + len(self.successes)
        if total_checks == 0:
            health_score = 0
        else:
            health_score = len(self.successes) / total_checks * 100

        print(f"\n{BOLD}SYSTEM HEALTH SCORE: {health_score:.1f}%{RESET}")

        if health_score >= 90:
            print(f"{GREEN}🏆 EXCELLENT - System is legendary!{RESET}")
        elif health_score >= 75:
            print(f"{YELLOW}👍 GOOD - System has minor issues{RESET}")
        elif health_score >= 50:
            print(f"{RED}⚠️  FAIR - System needs attention{RESET}")
        else:
            print(f"{RED}🚨 CRITICAL - System has major holes!{RESET}")

        print(f"\n{QUANTUM}{'='*70}{RESET}")
        print(f"Audit Complete: {end_time}")
        print(f"Remember: Plug the holes, make it legendary!{RESET}")

if __name__ == "__main__":
    auditor = LegendaryAuditor()
    auditor.run_complete_audit()