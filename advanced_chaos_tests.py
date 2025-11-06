#!/usr/bin/env python3
"""
Advanced Chaos Engineering Tests for Converse API
Implements stress testing, error injection, and resource exhaustion scenarios
"""
import asyncio
import time
import json
import random
import aiohttp
from typing import List, Dict, Any
from chaos_test_framework import ChaosTestSuite, ChaosTestResult, SLOMonitor
import logging

logger = logging.getLogger(__name__)

class AdvancedChaosTests:
    """Advanced chaos testing scenarios"""

    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url

    async def test_high_concurrency_burst(self, burst_size: int = 100) -> List[ChaosTestResult]:
        """Test system under high concurrent load burst"""
        logger.info(f"Testing high concurrency burst: {burst_size} concurrent requests")

        test_suite = ChaosTestSuite(self.base_url)
        endpoints = []

        # Generate burst of requests
        for i in range(burst_size):
            endpoints.append({
                "endpoint": "/v1/converse/run",
                "method": "POST",
                "payload": test_suite.generate_test_endpoints(1, ["stress"])[0]["payload"]
            })

        async with test_suite.executor as executor:
            results = await executor.run_parallel_tests(endpoints, burst_size, "burst_test")

        return results

    async def test_large_payloads(self, num_requests: int = 50) -> List[ChaosTestResult]:
        """Test with large payload sizes"""
        logger.info(f"Testing large payloads: {num_requests} requests")

        test_suite = ChaosTestSuite(self.base_url)
        endpoints = []

        for i in range(num_requests):
            # Generate large messages
            seed = hash(f"large_payload_{i}") % (2**31)
            large_payload = {
                "session_id": f"large_test_{i}_{int(time.time())}",
                "message": "A" * 10000,  # 10KB message
                "participants": ["ƒCODEX", "ƒCLAUDE"],
                "context": {
                    "sender": "ƒCODEX",
                    "message_type": "text",
                    "metadata": {
                        "large_data": "x" * 5000,
                        "test_seed": seed,
                        "test_scenario": "large_payload"
                    }
                }
            }

            endpoints.append({
                "endpoint": "/v1/converse/run",
                "method": "POST",
                "payload": large_payload
            })

        async with test_suite.executor as executor:
            results = await executor.run_parallel_tests(endpoints, 10, "large_payload")

        return results

    async def test_rapid_session_creation(self, num_sessions: int = 100) -> List[ChaosTestResult]:
        """Test rapid session creation and management"""
        logger.info(f"Testing rapid session creation: {num_sessions} sessions")

        test_suite = ChaosTestSuite(self.base_url)
        endpoints = []

        for i in range(num_sessions):
            session_payload = {
                "session_id": f"rapid_session_{i}_{int(time.time())}",
                "message": f"Rapid session test message {i}",
                "participants": ["ƒCODEX"],
                "context": {
                    "sender": "ƒCODEX",
                    "message_type": "text",
                    "metadata": {"rapid_test": True}
                }
            }

            endpoints.append({
                "endpoint": "/v1/converse/run",
                "method": "POST",
                "payload": session_payload
            })

        async with test_suite.executor as executor:
            results = await executor.run_parallel_tests(endpoints, 20, "rapid_sessions")

        return results

    async def test_mixed_workload(self, duration_seconds: int = 30) -> List[ChaosTestResult]:
        """Test mixed workload over time"""
        logger.info(f"Testing mixed workload for {duration_seconds} seconds")

        test_suite = ChaosTestSuite(self.base_url)
        start_time = time.time()
        all_results = []

        async with test_suite.executor as executor:
            while time.time() - start_time < duration_seconds:
                # Random workload mix
                endpoints = test_suite.generate_test_endpoints(
                    random.randint(5, 15),
                    ["random", "collaboration", "debugging", "planning", "stress"]
                )

                batch_results = await executor.run_parallel_tests(
                    endpoints, random.randint(5, 10), "mixed_workload"
                )
                all_results.extend(batch_results)

                # Brief pause between batches
                await asyncio.sleep(0.1)

        return all_results

    async def test_error_conditions(self) -> List[ChaosTestResult]:
        """Test various error conditions"""
        logger.info("Testing error conditions")

        test_suite = ChaosTestSuite(self.base_url)
        error_scenarios = []

        # Invalid endpoints
        error_scenarios.append({
            "endpoint": "/v1/converse/invalid",
            "method": "GET",
            "payload": {}
        })

        # Invalid payload
        error_scenarios.append({
            "endpoint": "/v1/converse/run",
            "method": "POST",
            "payload": {"invalid": "payload"}
        })

        # Missing required fields
        error_scenarios.append({
            "endpoint": "/v1/converse/run",
            "method": "POST",
            "payload": {"session_id": "test"}  # Missing message and participants
        })

        # Very long session ID
        error_scenarios.append({
            "endpoint": "/v1/converse/run",
            "method": "POST",
            "payload": {
                "session_id": "x" * 1000,
                "message": "test",
                "participants": ["ƒCODEX"]
            }
        })

        async with test_suite.executor as executor:
            results = await executor.run_parallel_tests(error_scenarios, 5, "error_conditions")

        return results

    async def run_comprehensive_stress_test(self) -> Dict[str, Any]:
        """Run comprehensive stress test suite"""
        logger.info("Starting comprehensive stress test suite")

        all_results = []
        test_results = {}

        # Test 1: High concurrency burst
        results = await self.test_high_concurrency_burst(100)
        all_results.extend(results)
        test_results["high_concurrency_burst"] = SLOMonitor.calculate_metrics(results)

        # Test 2: Large payloads
        results = await self.test_large_payloads(50)
        all_results.extend(results)
        test_results["large_payloads"] = SLOMonitor.calculate_metrics(results)

        # Test 3: Rapid session creation
        results = await self.test_rapid_session_creation(100)
        all_results.extend(results)
        test_results["rapid_session_creation"] = SLOMonitor.calculate_metrics(results)

        # Test 4: Mixed workload
        results = await self.test_mixed_workload(30)
        all_results.extend(results)
        test_results["mixed_workload"] = SLOMonitor.calculate_metrics(results)

        # Test 5: Error conditions
        results = await self.test_error_conditions()
        all_results.extend(results)
        test_results["error_conditions"] = SLOMonitor.calculate_metrics(results)

        # Overall metrics
        overall_metrics = SLOMonitor.calculate_metrics(all_results)

        return {
            "test_results": test_results,
            "overall_metrics": overall_metrics,
            "all_results": all_results
        }

def save_advanced_results(test_results: Dict[str, Any]):
    """Save advanced test results"""
    from datetime import datetime, timezone

    comprehensive_data = {
        "test_timestamp": datetime.now(timezone.utc).isoformat(),
        "test_type": "advanced_chaos_engineering",
        "individual_tests": {}
    }

    for test_name, metrics in test_results["test_results"].items():
        comprehensive_data["individual_tests"][test_name] = {
            "total_requests": metrics.total_requests,
            "successful_requests": metrics.successful_requests,
            "failed_requests": metrics.failed_requests,
            "error_rate": metrics.error_rate,
            "p95_latency_ms": metrics.p95_latency_ms,
            "mean_latency_ms": metrics.mean_latency_ms,
            "stability_score": metrics.stability_score
        }

    comprehensive_data["overall_summary"] = {
        "total_requests": test_results["overall_metrics"].total_requests,
        "successful_requests": test_results["overall_metrics"].successful_requests,
        "failed_requests": test_results["overall_metrics"].failed_requests,
        "error_rate": test_results["overall_metrics"].error_rate,
        "p95_latency_ms": test_results["overall_metrics"].p95_latency_ms,
        "mean_latency_ms": test_results["overall_metrics"].mean_latency_ms,
        "stability_score": test_results["overall_metrics"].stability_score
    }

    comprehensive_data["assessment"] = {
        "overall_stability": "Excellent" if test_results["overall_metrics"].stability_score >= 0.9 else
                           "Good" if test_results["overall_metrics"].stability_score >= 0.8 else
                           "Fair" if test_results["overall_metrics"].stability_score >= 0.7 else "Poor",
        "bottlenecks": [],
        "recommendations": []
    }

    # Identify potential bottlenecks
    for test_name, metrics in test_results["test_results"].items():
        if metrics.p95_latency_ms > 100:
            comprehensive_data["assessment"]["bottlenecks"].append(
                f"High latency in {test_name}: {metrics.p95_latency_ms:.2f}ms"
            )
        if metrics.error_rate > 0.05:
            comprehensive_data["assessment"]["bottlenecks"].append(
                f"High error rate in {test_name}: {metrics.error_rate:.2%}"
            )

    with open("data/reports/advanced_chaos_results.json", "w") as f:
        json.dump(comprehensive_data, f, indent=2)

    logger.info("Advanced test results saved to data/reports/advanced_chaos_results.json")

async def main():
    """Main advanced chaos test execution"""
    import os
    os.makedirs("data/reports", exist_ok=True)

    # Run advanced stress tests
    advanced_tests = AdvancedChaosTests()
    test_results = await advanced_tests.run_comprehensive_stress_test()

    # Save results
    save_advanced_results(test_results)

    # Print summary
    print(f"\n{'='*60}")
    print("ADVANCED CHAOS TEST SUMMARY")
    print(f"{'='*60}")

    for test_name, metrics in test_results["test_results"].items():
        print(f"\n{test_name.upper()}:")
        print(f"  Requests: {metrics.total_requests}")
        print(f"  Success Rate: {(1-metrics.error_rate):.2%}")
        print(f"  p95 Latency: {metrics.p95_latency_ms:.2f}ms")
        print(f"  Stability: {metrics.stability_score:.3f}")

    overall = test_results["overall_metrics"]
    print(f"\nOVERALL:")
    print(f"  Total Requests: {overall.total_requests}")
    print(f"  Overall Success Rate: {(1-overall.error_rate):.2%}")
    print(f"  Overall p95 Latency: {overall.p95_latency_ms:.2f}ms")
    print(f"  Overall Stability Score: {overall.stability_score:.3f}")
    print(f"{'='*60}")

if __name__ == "__main__":
    asyncio.run(main())