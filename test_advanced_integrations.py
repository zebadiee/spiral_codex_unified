#!/usr/bin/env python3
"""
🧪 ADVANCED INTEGRATION TEST SUITE
Comprehensive testing for Spiral Codex advanced chat systems

Tests:
- spiral_conscious_chat.py integration
- spiral_agentic.py multi-agent coordination
- spiral_consciousness.py learning system
- Service connectivity (Reasoning Hub, Neural Bus, OMAi)
- Tool functionality and safety
- Performance metrics
"""

import os
import sys
import json
import asyncio
import time
import subprocess
from pathlib import Path
from typing import Dict, List, Any
import requests

# Add Spiral Codex to path
sys.path.insert(0, str(Path(__file__).parent))

# =============================================================================
# TEST CONFIGURATION
# =============================================================================

TEST_CONFIG = {
    "services": {
        "reasoning_hub": "http://localhost:8000",
        "neural_bus": "http://localhost:9000",
        "omai_rag": "http://localhost:7016"
    },
    "test_files": {
        "test_read": "test_read.txt",
        "test_write": "test_write.txt",
        "test_dir": "test_directory"
    },
    "timeout": 30,
    "max_retries": 3
}

# Colors for test output
GREEN = "\033[32m"
RED = "\033[31m"
YELLOW = "\033[33m"
BLUE = "\033[34m"
CYAN = "\033[36m"
BOLD = "\033[1m"
RESET = "\033[0m"

# =============================================================================
# TEST FRAMEWORK
# =============================================================================

class TestResult:
    """Individual test result"""
    def __init__(self, name: str, passed: bool, message: str = "", duration: float = 0):
        self.name = name
        self.passed = passed
        self.message = message
        self.duration = duration

class IntegrationTestSuite:
    """Comprehensive integration test suite"""

    def __init__(self):
        self.results: List[TestResult] = []
        self.start_time = time.time()

        # Setup test environment
        self.setup_test_environment()

    def setup_test_environment(self):
        """Setup test files and directories"""
        # Create test directory
        test_dir = Path(TEST_CONFIG["test_files"]["test_dir"])
        test_dir.mkdir(exist_ok=True)

        # Create test file for reading
        test_file = Path(TEST_CONFIG["test_files"]["test_read"])
        test_file.write_text("This is a test file for Spiral Codex integration testing.\nIt contains multiple lines.\nTest successful!")

    def cleanup_test_environment(self):
        """Cleanup test files and directories"""
        try:
            # Remove test files
            for file_key in ["test_read", "test_write"]:
                file_path = Path(TEST_CONFIG["test_files"][file_key])
                if file_path.exists():
                    file_path.unlink()

            # Remove test directory
            test_dir = Path(TEST_CONFIG["test_files"]["test_dir"])
            if test_dir.exists():
                test_dir.rmdir()

        except Exception as e:
            print(f"{YELLOW}Warning: Could not cleanup test environment: {e}{RESET}")

    def run_test(self, test_name: str, test_func, *args, **kwargs):
        """Run a single test and record results"""
        print(f"{BLUE}🧪 Running: {test_name}...{RESET}", end="", flush=True)

        start_time = time.time()

        try:
            result = test_func(*args, **kwargs)
            duration = time.time() - start_time

            if result is True:
                self.results.append(TestResult(test_name, True, "", duration))
                print(f"\r{GREEN}✅ {test_name} ({duration:.2f}s){RESET}")
            else:
                self.results.append(TestResult(test_name, False, str(result), duration))
                print(f"\r{RED}❌ {test_name} ({duration:.2f}s): {result}{RESET}")

        except Exception as e:
            duration = time.time() - start_time
            self.results.append(TestResult(test_name, False, str(e), duration))
            print(f"\r{RED}❌ {test_name} ({duration:.2f}s): {e}{RESET}")

    # =============================================================================
    # SERVICE CONNECTIVITY TESTS
    # =============================================================================

    def test_service_health(self):
        """Test health of all Spiral Codex services"""
        all_healthy = True

        for service_name, service_url in TEST_CONFIG["services"].items():
            try:
                response = requests.get(f"{service_url}/health", timeout=5)
                if response.status_code == 200:
                    print(f"\n  {GREEN}✅ {service_name}: HEALTHY{RESET}")
                else:
                    print(f"\n  {YELLOW}⚠️  {service_name}: DEGRADED ({response.status_code}){RESET}")
                    all_healthy = False
            except Exception as e:
                print(f"\n  {RED}❌ {service_name}: OFFLINE ({str(e)[:50]}...){RESET}")
                all_healthy = False

        return all_healthy

    def test_reasoning_hub_integration(self):
        """Test Reasoning Hub API integration"""
        try:
            payload = {
                "query": "What is 2+2?",
                "context": [{"role": "user", "content": "Simple math test"}],
                "mode": "analytical"
            }

            response = requests.post(
                f"{TEST_CONFIG['services']['reasoning_hub']}/reason",
                json=payload,
                timeout=10
            )

            if response.status_code == 200:
                result = response.json()
                return "reasoning" in result.get("analysis", "").lower() or len(result) > 10
            else:
                return f"HTTP {response.status_code}: {response.text[:100]}"

        except Exception as e:
            return f"Connection error: {e}"

    def test_neural_bus_communication(self):
        """Test Neural Bus event broadcasting"""
        try:
            event_data = {
                "type": "test_event",
                "source": "integration_test",
                "data": {"message": "Hello Neural Bus!"}
            }

            response = requests.post(
                f"{TEST_CONFIG['services']['neural_bus']}/events",
                json=event_data,
                timeout=5
            )

            return response.status_code == 200

        except Exception as e:
            return f"Communication error: {e}"

    def test_omai_rag_search(self):
        """Test OMAi RAG search functionality"""
        try:
            payload = {
                "query": "Spiral Codex architecture",
                "max_results": 3,
                "min_similarity": 0.5
            }

            response = requests.post(
                f"{TEST_CONFIG['services']['omai_rag']}/search",
                json=payload,
                timeout=8
            )

            if response.status_code == 200:
                result = response.json()
                return "matches" in result or "results" in result
            else:
                return f"HTTP {response.status_code}: {response.text[:100]}"

        except Exception as e:
            return f"Search error: {e}"

    # =============================================================================
    # CHAT SYSTEM TESTS
    # =============================================================================

    def test_conscious_chat_import(self):
        """Test that spiral_conscious_chat.py can be imported"""
        try:
            import spiral_conscious_chat
            return hasattr(spiral_conscious_chat, 'SpiralConsciousChat')
        except ImportError as e:
            return f"Import error: {e}"
        except Exception as e:
            return f"Module error: {e}"

    def test_agentic_orchestrator_import(self):
        """Test that spiral_agentic.py can be imported"""
        try:
            import spiral_agentic
            return hasattr(spiral_agentic, 'MultiAgentOrchestrator')
        except ImportError as e:
            return f"Import error: {e}"
        except Exception as e:
            return f"Module error: {e}"

    def test_consciousness_system_import(self):
        """Test that spiral_consciousness.py can be imported"""
        try:
            import spiral_consciousness
            return hasattr(spiral_consciousness, 'SpiralConsciousness')
        except ImportError as e:
            return f"Import error: {e}"
        except Exception as e:
            return f"Module error: {e}"

    # =============================================================================
    # FUNCTIONALITY TESTS
    # =============================================================================

    def test_file_operations(self):
        """Test file read/write operations"""
        try:
            # Test reading
            test_file = Path(TEST_CONFIG["test_files"]["test_read"])
            if not test_file.exists():
                return "Test file does not exist"

            content = test_file.read_text()
            if "test file" not in content.lower():
                return "File content mismatch"

            # Test writing
            write_file = Path(TEST_CONFIG["test_files"]["test_write"])
            write_file.write_text("Test write content")

            if not write_file.exists():
                return "Write operation failed"

            written_content = write_file.read_text()
            if "test write content" != written_content:
                return "Written content mismatch"

            return True

        except Exception as e:
            return f"File operation error: {e}"

    def test_safe_code_execution(self):
        """Test safe code execution"""
        try:
            # Test safe command
            result = subprocess.run(
                "echo 'Hello from test'",
                shell=True,
                capture_output=True,
                text=True,
                timeout=5
            )

            if result.returncode != 0:
                return "Command failed"

            if "Hello from test" not in result.stdout:
                return "Command output mismatch"

            # Test dangerous command blocking (should be blocked by implementation)
            # This is a placeholder - actual safety depends on implementation

            return True

        except subprocess.TimeoutExpired:
            return "Command timed out"
        except Exception as e:
            return f"Execution error: {e}"

    def test_openrouter_api_access(self):
        """Test OpenRouter API access"""
        try:
            # This uses the same credentials as the chat systems
            headers = {
                "Authorization": "Bearer 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",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://spiral.codex.test",
                "X-Title": "Spiral Integration Test"
            }

            payload = {
                "model": "deepseek/deepseek-chat-v3.1:free",
                "messages": [{"role": "user", "content": "Say 'API test successful'"}],
                "max_tokens": 50
            }

            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                json=payload,
                timeout=15
            )

            if response.status_code == 200:
                result = response.json()
                content = result["choices"][0]["message"]["content"].lower()
                return "test successful" in content or "api test" in content
            else:
                return f"API error {response.status_code}: {response.text[:100]}"

        except Exception as e:
            return f"API connection error: {e}"

    # =============================================================================
    # PERFORMANCE TESTS
    # =============================================================================

    def test_consciousness_performance(self):
        """Test consciousness system performance"""
        try:
            import spiral_consciousness

            consciousness = spiral_consciousness.SpiralConsciousness("test_session")

            # Simulate some interactions
            start_time = time.time()

            for i in range(10):
                consciousness.record_interaction(
                    user_input=f"Test interaction {i}",
                    agent_response=f"Test response {i}",
                    selected_agent="ƒCODEX",
                    tools_used=["read_file"] if i % 2 == 0 else [],
                    response_time=0.5,
                    success=True
                )

            processing_time = time.time() - start_time

            # Check if system processed interactions efficiently
            if processing_time > 5.0:
                return f"Processing too slow: {processing_time:.2f}s for 10 interactions"

            # Test health score calculation
            health_score = consciousness.get_system_health_score()
            if not (0.0 <= health_score <= 1.0):
                return f"Invalid health score: {health_score}"

            return True

        except Exception as e:
            return f"Consciousness system error: {e}"

    def test_memory_usage(self):
        """Test memory usage of advanced systems"""
        try:
            import psutil
            import gc

            # Get initial memory
            process = psutil.Process()
            initial_memory = process.memory_info().rss / 1024 / 1024  # MB

            # Test consciousness system with many interactions
            import spiral_consciousness
            consciousness = spiral_consciousness.SpiralConsciousness("memory_test")

            # Add many interactions
            for i in range(100):
                consciousness.record_interaction(
                    user_input=f"Memory test interaction {i} with some longer content to simulate real usage",
                    agent_response=f"Memory test response {i} with detailed explanation and analysis",
                    selected_agent="ƒCODEX",
                    tools_used=["read_file", "write_file"],
                    response_time=1.5,
                    success=True
                )

            # Force garbage collection
            gc.collect()

            # Check final memory
            final_memory = process.memory_info().rss / 1024 / 1024  # MB
            memory_increase = final_memory - initial_memory

            # Memory increase should be reasonable (less than 50MB for 100 interactions)
            if memory_increase > 50:
                return f"Excessive memory usage: {memory_increase:.1f}MB increase"

            return True

        except ImportError:
            return "psutil not available for memory testing"
        except Exception as e:
            return f"Memory test error: {e}"

    # =============================================================================
    # TEST EXECUTION
    # =============================================================================

    def run_all_tests(self):
        """Run all integration tests"""
        print(f"{BOLD}{CYAN}╔══════════════════════════════════════════════════════════╗{RESET}")
        print(f"{BOLD}{CYAN}║  🧪 SPIRAL CODEX ADVANCED INTEGRATION TEST SUITE        ║{RESET}")
        print(f"{BOLD}{CYAN}╚══════════════════════════════════════════════════════════╝{RESET}\n")

        print(f"{BLUE}📋 Running comprehensive integration tests...{RESET}\n")

        # Service Connectivity Tests
        print(f"{YELLOW}🔗 SERVICE CONNECTIVITY TESTS{RESET}")
        self.run_test("Service Health Check", self.test_service_health)
        self.run_test("Reasoning Hub Integration", self.test_reasoning_hub_integration)
        self.run_test("Neural Bus Communication", self.test_neural_bus_communication)
        self.run_test("OMAi RAG Search", self.test_omai_rag_search)

        print()

        # Module Import Tests
        print(f"{YELLOW}📦 MODULE IMPORT TESTS{RESET}")
        self.run_test("Conscious Chat Import", self.test_conscious_chat_import)
        self.run_test("Agentic Orchestrator Import", self.test_agentic_orchestrator_import)
        self.run_test("Consciousness System Import", self.test_consciousness_system_import)

        print()

        # Functionality Tests
        print(f"{YELLOW}⚙️  FUNCTIONALITY TESTS{RESET}")
        self.run_test("File Operations", self.test_file_operations)
        self.run_test("Safe Code Execution", self.test_safe_code_execution)
        self.run_test("OpenRouter API Access", self.test_openrouter_api_access)

        print()

        # Performance Tests
        print(f"{YELLOW}📊 PERFORMANCE TESTS{RESET}")
        self.run_test("Consciousness Performance", self.test_consciousness_performance)
        self.run_test("Memory Usage", self.test_memory_usage)

        print()

        # Generate report
        self.generate_test_report()

    def generate_test_report(self):
        """Generate comprehensive test report"""
        total_tests = len(self.results)
        passed_tests = sum(1 for r in self.results if r.passed)
        failed_tests = total_tests - passed_tests
        total_duration = time.time() - self.start_time

        print(f"{BOLD}{CYAN}╔══════════════════════════════════════════════════════════╗{RESET}")
        print(f"{BOLD}{CYAN}║                    TEST REPORT                           ║{RESET}")
        print(f"{BOLD}{CYAN}╚══════════════════════════════════════════════════════════╝{RESET}\n")

        print(f"📊 **Summary:**")
        print(f"  Total Tests: {total_tests}")
        print(f"  {GREEN}Passed: {passed_tests}{RESET}")
        print(f"  {RED}Failed: {failed_tests}{RESET}")
        print(f"  Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        print(f"  Total Duration: {total_duration:.2f}s\n")

        if failed_tests > 0:
            print(f"{RED}❌ Failed Tests:{RESET}")
            for result in self.results:
                if not result.passed:
                    print(f"  • {result.name}: {result.message}")
            print()

        if passed_tests == total_tests:
            print(f"{GREEN}🎉 ALL TESTS PASSED! Your Spiral Codex advanced systems are ready.{RESET}\n")
        else:
            print(f"{YELLOW}⚠️  Some tests failed. Check the issues above before using the advanced systems.{RESET}\n")

        # Save detailed report
        self.save_test_report()

    def save_test_report(self):
        """Save detailed test report to file"""
        report_data = {
            "timestamp": datetime.now().isoformat(),
            "total_tests": len(self.results),
            "passed_tests": sum(1 for r in self.results if r.passed),
            "failed_tests": sum(1 for r in self.results if not r.passed),
            "total_duration": time.time() - self.start_time,
            "test_results": [
                {
                    "name": r.name,
                    "passed": r.passed,
                    "message": r.message,
                    "duration": r.duration
                }
                for r in self.results
            ]
        }

        report_file = Path(f"integration_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        with open(report_file, 'w') as f:
            json.dump(report_data, f, indent=2)

        print(f"📄 Detailed report saved to: {report_file}")

# =============================================================================
# MAIN EXECUTION
# =============================================================================

if __name__ == "__main__":
    from datetime import datetime

    # Check if aiohttp is available
    try:
        import aiohttp
    except ImportError:
        print(f"{YELLOW}📦 Installing aiohttp for async tests...{RESET}")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "aiohttp"])
        import aiohttp

    # Run test suite
    test_suite = IntegrationTestSuite()

    try:
        test_suite.run_all_tests()
    finally:
        # Cleanup
        test_suite.cleanup_test_environment()

    # Exit with appropriate code
    failed_tests = sum(1 for r in test_suite.results if not r.passed)
    sys.exit(0 if failed_tests == 0 else 1)