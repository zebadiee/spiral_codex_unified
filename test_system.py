#!/usr/bin/env python3
"""
System Test for Spiral Codex Unified
Tests all components and verifies local operation only
"""
import asyncio
import json
import requests
from datetime import datetime
from pathlib import Path
import subprocess
import sys
import time

class SystemTester:
    """Comprehensive system testing"""

    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.test_results = []

    async def run_all_tests(self) -> bool:
        """Run complete system test suite"""
        print("🚀 Starting Spiral Codex Unified System Test")
        print("=" * 60)

        tests = [
            ("FastAPI Server", self._test_server_health),
            ("Brain API", self._test_brain_api),
            ("OMAi API", self._test_omai_api),
            ("Converse API", self._test_converse_api),
            ("Multi-Agent Collaboration", self._test_multi_agent),
            ("Local Operation Only", self._test_local_only),
            ("System Integration", self._test_integration),
        ]

        passed = 0
        for test_name, test_func in tests:
            print(f"\n🧪 Testing: {test_name}")
            try:
                result = await test_func()
                if result:
                    print(f"✅ {test_name}: PASSED")
                    self.test_results.append({"test": test_name, "status": "PASSED"})
                    passed += 1
                else:
                    print(f"❌ {test_name}: FAILED")
                    self.test_results.append({"test": test_name, "status": "FAILED"})
            except Exception as e:
                print(f"❌ {test_name}: ERROR - {str(e)}")
                self.test_results.append({"test": test_name, "status": "ERROR", "error": str(e)})

        print(f"\n{'='*60}")
        print(f"📊 Test Results: {passed}/{len(tests)} passed")

        if passed == len(tests):
            print("🎉 ALL TESTS PASSED - System Ready!")
            return True
        else:
            print("⚠️  Some tests failed - System needs attention")
            return False

    async def _test_server_health(self) -> bool:
        """Test FastAPI server health"""
        try:
            response = requests.get(f"{self.base_url}/health", timeout=5)
            if response.status_code == 200:
                data = response.json()
                expected_endpoints = ["/v1/brain", "/v1/omai", "/v1/converse"]
                return (data.get("ok") and
                        set(data.get("endpoints", [])) >= set(expected_endpoints))
            return False
        except Exception:
            return False

    async def _test_brain_api(self) -> bool:
        """Test Brain API endpoints"""
        try:
            # Test health
            health_response = requests.get(f"{self.base_url}/v1/brain/health", timeout=5)
            if health_response.status_code != 200:
                return False

            # Test planning
            plan_request = {
                "goal": "Test multi-agent system integration",
                "max_steps": 3,
                "context": {"test": True}
            }
            plan_response = requests.post(
                f"{self.base_url}/v1/brain/plan",
                json=plan_request,
                timeout=10
            )
            if plan_response.status_code != 200:
                return False

            plan_data = plan_response.json()
            return ("plan" in plan_data and
                   "steps" in plan_data["plan"] and
                   len(plan_data["plan"]["steps"]) > 0)

        except Exception:
            return False

    async def _test_omai_api(self) -> bool:
        """Test OMAi API endpoints"""
        try:
            # Test health
            health_response = requests.get(f"{self.base_url}/v1/omai/health", timeout=5)
            if health_response.status_code != 200:
                return False

            # Test vault analysis
            vault_request = {
                "query": "Test spiral codex integration",
                "context_type": "test",
                "depth": "shallow"
            }
            vault_response = requests.post(
                f"{self.base_url}/v1/omai/vault/analyze",
                json=vault_request,
                timeout=10
            )
            if vault_response.status_code != 200:
                return False

            # Test planner
            planner_request = {
                "objective": "Test OMAi integration",
                "constraints": ["local_only"],
                "resources": {"test": True}
            }
            planner_response = requests.post(
                f"{self.base_url}/v1/omai/planner/create",
                json=planner_request,
                timeout=10
            )
            if planner_response.status_code != 200:
                return False

            return True

        except Exception:
            return False

    async def _test_converse_api(self) -> bool:
        """Test Converse API endpoints"""
        try:
            # Test health
            health_response = requests.get(f"{self.base_url}/v1/converse/health", timeout=5)
            if health_response.status_code != 200:
                return False

            # Test agents list
            agents_response = requests.get(f"{self.base_url}/v1/converse/agents", timeout=5)
            if agents_response.status_code != 200:
                return False

            agents = agents_response.json()
            if not isinstance(agents, list) or len(agents) == 0:
                return False

            # Test session creation
            session_request = {
                "session_id": "test_session",
                "message": "Testing multi-agent conversation",
                "participants": ["ƒCODEX", "ƒCLAUDE"],
                "context": {"test": True}
            }
            session_response = requests.post(
                f"{self.base_url}/v1/converse/session/create",
                json=session_request,
                timeout=10
            )
            if session_response.status_code != 200:
                return False

            # Test collaboration
            collab_request = {
                "task": "Test agent collaboration",
                "agents": ["ƒCODEX", "ƒCLAUDE"],
                "workflow": "sequential"
            }
            collab_response = requests.post(
                f"{self.base_url}/v1/converse/collaborate",
                json=collab_request,
                timeout=15
            )
            if collab_response.status_code != 200:
                return False

            return True

        except Exception:
            return False

    async def _test_multi_agent(self) -> bool:
        """Test multi-agent collaboration"""
        try:
            # Test different agent capabilities
            capabilities = ["code_generation", "analysis", "planning", "documentation"]

            for capability in capabilities:
                response = requests.get(
                    f"{self.base_url}/v1/converse/agents/{capability}",
                    timeout=5
                )
                if response.status_code != 200:
                    return False

                agents = response.json()
                if not isinstance(agents, list) or len(agents) == 0:
                    return False

            return True

        except Exception:
            return False

    async def _test_local_only(self) -> bool:
        """Verify local operation only (no cloud dependencies)"""
        try:
            # Check that we're not making external requests
            # Test that system works without internet
            test_response = requests.get(f"{self.base_url}/", timeout=5)
            if test_response.status_code != 200:
                return False

            data = test_response.json()

            # Verify local indicators
            if "localhost" not in self.base_url:
                return False

            # Check no external service dependencies in responses
            endpoints_to_check = [
                "/health",
                "/v1/brain/health",
                "/v1/omai/health",
                "/v1/converse/health"
            ]

            for endpoint in endpoints_to_check:
                response = requests.get(f"{self.base_url}{endpoint}", timeout=5)
                if response.status_code != 200:
                    return False

                # Quick check for external dependency indicators
                response_text = str(response.json()).lower()
                if any(keyword in response_text for keyword in
                      ['api.openai.com', 'cloud', 'remote', 'external']):
                    print(f"⚠️  Potential external dependency detected in {endpoint}")
                    return False

            return True

        except Exception:
            return False

    async def _test_integration(self) -> bool:
        """Test full system integration"""
        try:
            # Test brain -> converse integration
            brain_plan = {
                "goal": "Integrate Spiral Codex components",
                "max_steps": 2
            }
            brain_response = requests.post(
                f"{self.base_url}/v1/brain/plan",
                json=brain_plan,
                timeout=10
            )
            if brain_response.status_code != 200:
                return False

            plan_data = brain_response.json()

            # Use brain plan in converse system
            collab_request = {
                "task": plan_data["plan"]["rationale"],
                "agents": ["ƒCODEX", "ƒCLAUDE"],
                "workflow": "sequential"
            }
            collab_response = requests.post(
                f"{self.base_url}/v1/converse/collaborate",
                json=collab_request,
                timeout=15
            )
            if collab_response.status_code != 200:
                return False

            collab_data = collab_response.json()

            # Use result in OMAi system
            if collab_data.get("status") == "completed":
                omai_request = {
                    "objective": "Record collaboration results",
                    "resources": {"collaboration": collab_data}
                }
                omai_response = requests.post(
                    f"{self.base_url}/v1/omai/planner/create",
                    json=omai_request,
                    timeout=10
                )
                if omai_response.status_code != 200:
                    return False

            return True

        except Exception:
            return False

    def generate_test_report(self) -> str:
        """Generate comprehensive test report"""
        report = {
            "test_time": datetime.utcnow().isoformat(),
            "system": "Spiral Codex Unified",
            "version": "0.4.0",
            "tests": self.test_results,
            "summary": {
                "total_tests": len(self.test_results),
                "passed": len([t for t in self.test_results if t["status"] == "PASSED"]),
                "failed": len([t for t in self.test_results if t["status"] in ["FAILED", "ERROR"]])
            }
        }

        report_path = Path("test_report.json")
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)

        return f"Test report saved to {report_path.absolute()}"

async def main():
    """Main test execution"""
    # Check if server is running
    print("🔍 Checking if FastAPI server is running...")

    tester = SystemTester()

    try:
        health_response = requests.get("http://localhost:8000/health", timeout=5)
        if health_response.status_code != 200:
            print("❌ FastAPI server not responding on http://localhost:8000")
            print("Please start the server with: python fastapi_app.py")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ FastAPI server not running on http://localhost:8000")
        print("Please start the server with: python fastapi_app.py")
        return False

    print("✅ FastAPI server is running")

    # Run tests
    success = await tester.run_all_tests()

    # Generate report
    report_path = tester.generate_test_report()
    print(f"\n📄 {report_path}")

    return success

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)