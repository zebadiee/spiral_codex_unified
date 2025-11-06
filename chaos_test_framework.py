#!/usr/bin/env python3
"""
Chaos Engineering Framework for Converse API
Implements robustness testing with random seeds, parallel execution, and SLO monitoring
"""
import asyncio
import random
import time
import json
import csv
import aiohttp
import statistics
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
import hashlib
import numpy as np
from concurrent.futures import ThreadPoolExecutor, as_completed
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class ChaosTestResult:
    """Individual test result data structure"""
    test_id: str
    timestamp: str
    endpoint: str
    method: str
    payload_size: int
    status_code: int
    latency_ms: float
    error: Optional[str]
    parallel_group: int
    test_scenario: str
    seed: int

@dataclass
class SLOMetrics:
    """Service Level Objective metrics"""
    p95_latency_ms: float
    p99_latency_ms: float
    mean_latency_ms: float
    error_rate: float
    total_requests: int
    successful_requests: int
    failed_requests: int
    stability_score: float

class ChaosTestScenarios:
    """Collection of chaos test scenarios"""

    @staticmethod
    def generate_random_message(min_length: int = 10, max_length: int = 500) -> str:
        """Generate random message content"""
        messages = [
            "Hello agents, let's collaborate on this task",
            "Can you help me debug this Python code?",
            "I need assistance with system architecture design",
            "Let's plan our development workflow",
            "Can you review this code for best practices?",
            "Help me optimize this algorithm",
            "Let's design a new feature together",
            "I need guidance on API integration",
            "Can you help with database schema design?",
            "Let's discuss deployment strategies",
            "Help me understand this complex problem",
            "Let's create a comprehensive test plan"
        ]
        base_msg = random.choice(messages)
        extra_chars = ''.join(random.choices('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 .!?,',
                                            k=random.randint(min_length, max_length)))
        return f"{base_msg} {extra_chars[:max_length]}"

    @staticmethod
    def create_conversation_payload(seed: int, scenario: str = "random") -> Dict[str, Any]:
        """Create conversation request payload based on scenario"""
        random.seed(seed)

        agents = ["ƒCODEX", "ƒCLAUDE", "ƒCOPILOT", "ƒGEMMA", "ƒDEEPSEEK", "ƒGEMINI"]

        if scenario == "random":
            participants = random.sample(agents, random.randint(1, 3))
            message_type = random.choice(["text", "code", "plan", "analysis"])
        elif scenario == "collaboration":
            participants = random.sample(agents, random.randint(2, 4))
            message_type = random.choice(["plan", "analysis"])
        elif scenario == "debugging":
            participants = ["ƒCODEX", "ƒCLAUDE"]
            message_type = "code"
        elif scenario == "planning":
            participants = ["ƒCLAUDE", "ƒCOPILOT"]
            message_type = "plan"
        else:
            participants = [random.choice(agents)]
            message_type = "text"

        return {
            "session_id": f"chaos_test_{seed}_{int(time.time())}",
            "message": ChaosTestScenarios.generate_random_message(),
            "participants": participants,
            "context": {
                "sender": random.choice(participants),
                "message_type": message_type,
                "metadata": {"test_seed": seed, "test_scenario": scenario}
            }
        }

    @staticmethod
    def create_collaboration_payload(seed: int, scenario: str = "random") -> Dict[str, Any]:
        """Create collaboration request payload"""
        random.seed(seed)

        agents = ["ƒCODEX", "ƒCLAUDE", "ƒCOPILOT", "ƒGEMMA", "ƒDEEPSEEK", "ƒGEMINI"]

        tasks = [
            "Design a microservices architecture",
            "Implement a caching solution",
            "Create a database schema",
            "Build a REST API",
            "Set up CI/CD pipeline",
            "Optimize query performance",
            "Create a responsive UI",
            "Implement authentication system"
        ]

        workflows = ["sequential", "parallel", "consensus"]

        return {
            "task": random.choice(tasks),
            "agents": random.sample(agents, random.randint(2, 4)),
            "workflow": random.choice(workflows),
            "constraints": [f"constraint_{i}" for i in range(random.randint(0, 2))]
        }

class ChaosTestExecutor:
    """Executes chaos tests against API endpoints"""

    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.results: List[ChaosTestResult] = []
        self.session = None

    async def __aenter__(self):
        self.session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=30))
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    async def make_request(self, endpoint: str, method: str, payload: Dict[str, Any],
                          test_id: str, scenario: str, seed: int, parallel_group: int) -> ChaosTestResult:
        """Make a single API request and measure performance"""
        start_time = time.time()
        url = f"{self.base_url}{endpoint}"
        payload_size = len(json.dumps(payload))

        try:
            if method.upper() == "GET":
                async with self.session.get(url) as response:
                    await response.text()  # Consume response
                    status_code = response.status
                    error = None
            else:  # POST
                async with self.session.post(url, json=payload) as response:
                    await response.text()  # Consume response
                    status_code = response.status
                    error = None

        except Exception as e:
            status_code = 0
            error = str(e)

        latency_ms = (time.time() - start_time) * 1000

        return ChaosTestResult(
            test_id=test_id,
            timestamp=datetime.now(timezone.utc).isoformat(),
            endpoint=endpoint,
            method=method,
            payload_size=payload_size,
            status_code=status_code,
            latency_ms=latency_ms,
            error=error,
            parallel_group=parallel_group,
            test_scenario=scenario,
            seed=seed
        )

    async def run_parallel_tests(self, endpoints: List[Dict[str, Any]],
                                num_parallel: int = 10, scenario: str = "random") -> List[ChaosTestResult]:
        """Run tests in parallel batches"""
        logger.info(f"Running parallel tests: {len(endpoints)} requests, {num_parallel} concurrent")

        tasks = []
        for i, endpoint_config in enumerate(endpoints):
            test_id = f"test_{i}_{scenario}"
            parallel_group = i // num_parallel
            seed = hash(f"{test_id}_{scenario}") % (2**31)

            task = self.make_request(
                endpoint=endpoint_config["endpoint"],
                method=endpoint_config["method"],
                payload=endpoint_config.get("payload", {}),
                test_id=test_id,
                scenario=scenario,
                seed=seed,
                parallel_group=parallel_group
            )
            tasks.append(task)

        # Execute in batches to control parallelism
        results = []
        for i in range(0, len(tasks), num_parallel):
            batch = tasks[i:i + num_parallel]
            batch_results = await asyncio.gather(*batch, return_exceptions=True)

            for result in batch_results:
                if isinstance(result, Exception):
                    logger.error(f"Task failed: {result}")
                else:
                    results.append(result)

        return results

class SLOMonitor:
    """Service Level Objective monitoring and calculation"""

    @staticmethod
    def calculate_metrics(results: List[ChaosTestResult]) -> SLOMetrics:
        """Calculate SLO metrics from test results"""
        if not results:
            return SLOMetrics(0, 0, 0, 1.0, 0, 0, 0, 0)

        latencies = [r.latency_ms for r in results if r.status_code == 200]
        successful = len([r for r in results if r.status_code == 200])
        failed = len([r for r in results if r.status_code != 200])
        total = len(results)

        if latencies:
            p95_latency = np.percentile(latencies, 95)
            p99_latency = np.percentile(latencies, 99)
            mean_latency = statistics.mean(latencies)
        else:
            p95_latency = p99_latency = mean_latency = float('inf')

        error_rate = failed / total if total > 0 else 1.0

        # Calculate stability score (0..1)
        stability_score = SLOMonitor.calculate_stability_score(
            p95_latency, error_rate, successful, total
        )

        return SLOMetrics(
            p95_latency_ms=p95_latency,
            p99_latency_ms=p99_latency,
            mean_latency_ms=mean_latency,
            error_rate=error_rate,
            total_requests=total,
            successful_requests=successful,
            failed_requests=failed,
            stability_score=stability_score
        )

    @staticmethod
    def calculate_stability_score(p95_latency: float, error_rate: float,
                               successful: int, total: int) -> float:
        """Calculate composite stability score from 0 to 1"""

        # Latency component (target: <500ms for p95)
        if p95_latency == float('inf'):
            latency_score = 0.0
        else:
            latency_score = max(0, 1 - (p95_latency / 1000))  # 1000ms as max acceptable

        # Error rate component (target: <5%)
        error_score = max(0, 1 - (error_rate * 10))  # 10% error rate = 0 score

        # Success rate component
        success_score = successful / total if total > 0 else 0

        # Consistency component (based on variance in recent performance)
        consistency_score = 0.8  # Placeholder for now

        # Weighted composite score
        stability_score = (
            0.3 * latency_score +
            0.3 * error_score +
            0.2 * success_score +
            0.2 * consistency_score
        )

        return min(1.0, max(0.0, stability_score))

class ChaosTestSuite:
    """Main chaos test suite orchestrator"""

    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.executor = ChaosTestExecutor(base_url)

    def generate_test_endpoints(self, num_requests: int, scenarios: List[str]) -> List[Dict[str, Any]]:
        """Generate test endpoint configurations"""
        endpoints = []

        for i in range(num_requests):
            scenario = random.choice(scenarios)
            seed = hash(f"endpoint_{i}_{scenario}") % (2**31)

            # Mix of different endpoints
            endpoint_choices = [
                {
                    "endpoint": "/v1/converse/run",
                    "method": "POST",
                    "payload": ChaosTestScenarios.create_conversation_payload(seed, scenario)
                },
                {
                    "endpoint": "/v1/converse/collaborate",
                    "method": "POST",
                    "payload": ChaosTestScenarios.create_collaboration_payload(seed, scenario)
                },
                {
                    "endpoint": "/v1/converse/agents",
                    "method": "GET",
                    "payload": {}
                },
                {
                    "endpoint": "/v1/converse/status",
                    "method": "GET",
                    "payload": {}
                },
                {
                    "endpoint": "/v1/converse/health",
                    "method": "GET",
                    "payload": {}
                }
            ]

            endpoints.append(random.choice(endpoint_choices))

        return endpoints

    async def run_chaos_tests(self, num_requests: int = 250,
                            parallel_concurrency: int = 20) -> Tuple[List[ChaosTestResult], SLOMetrics]:
        """Run comprehensive chaos tests"""
        logger.info(f"Starting chaos test suite: {num_requests} requests, {parallel_concurrency} parallel")

        scenarios = ["random", "collaboration", "debugging", "planning", "stress"]

        # Generate test endpoints
        endpoints = self.generate_test_endpoints(num_requests, scenarios)

        # Run tests
        async with self.executor as executor:
            results = await executor.run_parallel_tests(
                endpoints, parallel_concurrency, "chaos_comprehensive"
            )

        # Calculate metrics
        metrics = SLOMonitor.calculate_metrics(results)

        logger.info(f"Chaos tests completed: {metrics.total_requests} requests, "
                   f"stability score: {metrics.stability_score:.3f}")

        return results, metrics

    def save_results(self, results: List[ChaosTestResult], metrics: SLOMetrics):
        """Save test results to required output files"""

        # Save stability report
        stability_data = {
            "test_timestamp": datetime.now(timezone.utc).isoformat(),
            "test_configuration": {
                "total_requests": metrics.total_requests,
                "api_base_url": self.base_url,
                "test_type": "chaos_engineering"
            },
            "slo_metrics": asdict(metrics),
            "stability_analysis": {
                "score_interpretation": self._interpret_stability_score(metrics.stability_score),
                "performance_grade": self._calculate_grade(metrics),
                "recommendations": self._generate_recommendations(metrics)
            }
        }

        with open("data/reports/converse_stability.json", "w") as f:
            json.dump(stability_data, f, indent=2)

        # Save detailed run data
        with open("data/ablation/chaos_runs.csv", "w", newline="") as f:
            fieldnames = ["test_id", "timestamp", "endpoint", "method", "payload_size",
                         "status_code", "latency_ms", "error", "parallel_group",
                         "test_scenario", "seed"]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()

            for result in results:
                writer.writerow(asdict(result))

        logger.info("Results saved to data/reports/converse_stability.json and data/ablation/chaos_runs.csv")

    def _interpret_stability_score(self, score: float) -> str:
        """Interpret stability score"""
        if score >= 0.9:
            return "Excellent - highly stable system"
        elif score >= 0.8:
            return "Good - stable with minor issues"
        elif score >= 0.7:
            return "Fair - some stability concerns"
        elif score >= 0.5:
            return "Poor - significant stability issues"
        else:
            return "Critical - major stability problems"

    def _calculate_grade(self, metrics: SLOMetrics) -> str:
        """Calculate performance grade"""
        score = metrics.stability_score

        if score >= 0.9:
            return "A"
        elif score >= 0.8:
            return "B"
        elif score >= 0.7:
            return "C"
        elif score >= 0.6:
            return "D"
        else:
            return "F"

    def _generate_recommendations(self, metrics: SLOMetrics) -> List[str]:
        """Generate performance recommendations"""
        recommendations = []

        if metrics.p95_latency_ms > 500:
            recommendations.append("Consider optimizing for latency - p95 > 500ms")

        if metrics.error_rate > 0.05:
            recommendations.append("High error rate detected - investigate error handling")

        if metrics.stability_score < 0.8:
            recommendations.append("Overall stability needs improvement")

        if metrics.failed_requests > 0:
            recommendations.append(f"Analyze {metrics.failed_requests} failed requests")

        return recommendations

async def main():
    """Main chaos test execution"""
    # Ensure data directories exist
    import os
    os.makedirs("data/reports", exist_ok=True)
    os.makedirs("data/ablation", exist_ok=True)

    # Run chaos tests
    test_suite = ChaosTestSuite()
    results, metrics = await test_suite.run_chaos_tests(num_requests=250, parallel_concurrency=20)

    # Save results
    test_suite.save_results(results, metrics)

    # Print summary
    print(f"\n{'='*60}")
    print("CHAOS TEST SUMMARY")
    print(f"{'='*60}")
    print(f"Total Requests: {metrics.total_requests}")
    print(f"Successful: {metrics.successful_requests}")
    print(f"Failed: {metrics.failed_requests}")
    print(f"Error Rate: {metrics.error_rate:.2%}")
    print(f"p95 Latency: {metrics.p95_latency_ms:.2f}ms")
    print(f"Mean Latency: {metrics.mean_latency_ms:.2f}ms")
    print(f"Stability Score: {metrics.stability_score:.3f}")
    print(f"Grade: {test_suite._calculate_grade(metrics)}")
    print(f"{'='*60}")

if __name__ == "__main__":
    asyncio.run(main())