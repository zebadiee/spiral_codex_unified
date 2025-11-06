#!/usr/bin/env python3
"""Test telemetry logging"""
from agent_orchestrator import AgentOrchestrator
import time

def test_telemetry():
    """Test that telemetry logs are created"""
    orchestrator = AgentOrchestrator()
    orchestrator.initialize_agents()
    
    print("Testing telemetry logging...")
    
    # Test various task types
    tasks = [
        {"task_type": "code_generation", "approx_lines": 50},
        {"task_type": "analysis", "approx_lines": 100},
        {"task_type": "entropy", "approx_lines": 20},
        {"task_type": "archive", "approx_lines": 10},
        {"task_type": "unknown", "approx_lines": 5},
    ]
    
    for task in tasks:
        result = orchestrator.route_task(task)
        print(f"  ✓ {task['task_type']}: {result.get('status', result.get('error', 'ok'))}")
        time.sleep(0.1)  # Small delay for distinct timestamps
    
    # Check telemetry file
    import csv
    from pathlib import Path
    
    csv_path = Path("logs/wean.csv")
    if csv_path.exists():
        with csv_path.open() as f:
            rows = list(csv.DictReader(f))
            print(f"\n📊 Telemetry records: {len(rows)}")
            print("\nSample entries:")
            for row in rows[-5:]:
                print(f"  {row['provider']:10} | {row['task']:15} | {row['latency_ms']:>4}ms | ok={row['ok']}")
    else:
        print("⚠️  No telemetry file found")

if __name__ == "__main__":
    test_telemetry()
