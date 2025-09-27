#!/usr/bin/env python3
"""
Standalone Tests for the Spiral Codex Adaptation Kernel - Wave 4
===============================================================

The Council of Elders' Sacred Verification: Testing the Flame of Learning
-------------------------------------------------------------------------

These standalone tests verify the adaptation kernel functionality without
relying on the full kernel package imports that may have dependency issues.

"In isolation we test, in integration we trust, but first the flame
 must prove its individual worthiness." - The Chronicle of Verification
"""

import sys
import os
sys.path.append('.')
sys.path.append('kernel')

import json
import tempfile
import time
from pathlib import Path
import numpy as np

# Import adaptation module directly
import adaptation

def test_basic_functionality():
    """Test basic adaptation kernel functionality."""
    print("🔥 Testing basic adaptation kernel functionality...")
    
    # Create temporary reward log
    temp_dir = tempfile.mkdtemp()
    log_path = Path(temp_dir) / 'test_reward_log.json'
    
    # Create test data
    test_data = [
        {
            "timestamp": "2025-09-27T08:52:47.672549",
            "operation": "echo_agent_pure_echo",
            "success": True,
            "execution_time": 0.1,
            "retry_count": 0,
            "healing_applied": False,
            "error_type": None
        },
        {
            "timestamp": "2025-09-27T08:52:48.672549",
            "operation": "echo_agent_analytical_echo",
            "success": False,
            "execution_time": 0.2,
            "retry_count": 1,
            "healing_applied": True,
            "error_type": "RuntimeError"
        }
    ]
    
    with open(log_path, 'w') as f:
        json.dump(test_data, f)
    
    # Test kernel creation
    kernel = adaptation.AdaptationKernel(reward_log_path=str(log_path))
    assert kernel.metrics.total_operations == 2
    assert kernel.metrics.healing_count == 1
    print("✅ Kernel initialization with existing log successful")
    
    # Test success rate updates
    initial_rate = kernel.metrics.success_rate
    new_rate = kernel.update_success_rate("test_operation", True, 0.05)
    assert new_rate != initial_rate
    assert kernel.metrics.total_operations == 3
    print("✅ Success rate update working")
    
    # Test strategy selection
    strategy = kernel.choose_strategy("test_operation")
    assert isinstance(strategy, str)
    assert len(strategy) > 0
    print(f"✅ Strategy selection working: {strategy}")
    
    # Test insights generation
    insights = kernel.get_adaptation_insights()
    assert "metrics" in insights
    assert "learning_phase" in insights
    assert "council_blessing" in insights
    print("✅ Insights generation working")
    
    print("🌟 Basic functionality tests passed!")
    return True

def test_adaptation_strategies():
    """Test different adaptation strategies."""
    print("\n🔥 Testing adaptation strategies...")
    
    temp_dir = tempfile.mkdtemp()
    log_path = Path(temp_dir) / 'strategy_test.json'
    with open(log_path, 'w') as f:
        json.dump([], f)
    
    strategies = [
        adaptation.AdaptationStrategy.EXPONENTIAL_MOVING_AVERAGE,
        adaptation.AdaptationStrategy.REINFORCEMENT_LEARNING,
        adaptation.AdaptationStrategy.BAYESIAN_UPDATE,
        adaptation.AdaptationStrategy.HYBRID_ADAPTIVE
    ]
    
    for strategy in strategies:
        kernel = adaptation.AdaptationKernel(
            reward_log_path=str(log_path),
            strategy=strategy
        )
        
        # Test multiple updates
        for i in range(10):
            success = i % 3 != 0  # ~67% success rate
            kernel.update_success_rate(f"strategy_test_{strategy.value}", success)
        
        assert 0.0 <= kernel.metrics.success_rate <= 1.0
        print(f"✅ Strategy {strategy.value} working")
    
    print("🌟 Strategy tests passed!")
    return True

def test_learning_patterns():
    """Test learning patterns and adaptation."""
    print("\n🔥 Testing learning patterns...")
    
    temp_dir = tempfile.mkdtemp()
    log_path = Path(temp_dir) / 'learning_test.json'
    with open(log_path, 'w') as f:
        json.dump([], f)
    
    kernel = adaptation.AdaptationKernel(reward_log_path=str(log_path))
    
    # Test learning from consistent success
    for i in range(20):
        kernel.update_success_rate("consistent_success", True)
    
    high_success_rate = kernel.metrics.success_rate
    assert high_success_rate > 0.7
    print(f"✅ Learning from consistent success: {high_success_rate:.3f}")
    
    # Test learning from consistent failure
    for i in range(20):
        kernel.update_success_rate("consistent_failure", False)
    
    # Should adapt to lower success rate
    adapted_rate = kernel.metrics.success_rate
    assert adapted_rate < high_success_rate
    print(f"✅ Adapting to failures: {adapted_rate:.3f}")
    
    # Test learning velocity
    assert kernel.metrics.learning_velocity >= 0.0
    print(f"✅ Learning velocity tracked: {kernel.metrics.learning_velocity:.3f}")
    
    print("🌟 Learning pattern tests passed!")
    return True

def test_adaptive_wrapper():
    """Test the adaptive wrapper decorator."""
    print("\n🔥 Testing adaptive wrapper...")
    
    # Reset global kernel
    adaptation._adaptation_kernel = None
    
    @adaptation.adaptive_wrapper("test_function")
    def successful_function():
        return "success"
    
    @adaptation.adaptive_wrapper("failing_function")
    def failing_function():
        raise ValueError("Test error")
    
    # Test successful function
    result = successful_function()
    assert result == "success"
    print("✅ Adaptive wrapper with success working")
    
    # Test failing function
    try:
        failing_function()
        assert False, "Should have raised exception"
    except ValueError:
        pass
    print("✅ Adaptive wrapper with failure working")
    
    # Check that operations were tracked
    kernel = adaptation.get_adaptation_kernel()
    assert kernel.metrics.total_operations >= 2
    print("✅ Operations tracked by wrapper")
    
    print("🌟 Adaptive wrapper tests passed!")
    return True

def test_state_persistence():
    """Test saving and loading adaptation state."""
    print("\n🔥 Testing state persistence...")
    
    temp_dir = tempfile.mkdtemp()
    log_path = Path(temp_dir) / 'persistence_test.json'
    state_path = Path(temp_dir) / 'adaptation_state.json'
    
    with open(log_path, 'w') as f:
        json.dump([], f)
    
    # Create kernel and build some state
    kernel = adaptation.AdaptationKernel(reward_log_path=str(log_path))
    for i in range(10):
        kernel.update_success_rate("persistence_test", i % 2 == 0)
    
    original_rate = kernel.metrics.success_rate
    original_ops = kernel.metrics.total_operations
    
    # Save state
    kernel.save_adaptation_state(str(state_path))
    assert state_path.exists()
    print("✅ State saved successfully")
    
    # Create new kernel and load state
    new_kernel = adaptation.AdaptationKernel(reward_log_path=str(log_path))
    success = new_kernel.load_adaptation_state(str(state_path))
    
    assert success
    assert abs(new_kernel.metrics.success_rate - original_rate) < 0.01
    print("✅ State loaded successfully")
    
    print("🌟 State persistence tests passed!")
    return True

def test_edge_cases():
    """Test edge cases and error handling."""
    print("\n🔥 Testing edge cases...")
    
    # Test with nonexistent log file
    kernel = adaptation.AdaptationKernel(reward_log_path="nonexistent.json")
    assert kernel.metrics.success_rate == 0.5  # Default value
    print("✅ Handles nonexistent log file")
    
    # Test with empty log
    temp_dir = tempfile.mkdtemp()
    empty_log = Path(temp_dir) / 'empty.json'
    with open(empty_log, 'w') as f:
        json.dump([], f)
    
    kernel = adaptation.AdaptationKernel(reward_log_path=str(empty_log))
    assert kernel.metrics.success_rate == 0.5
    print("✅ Handles empty log file")
    
    # Test memory management with many operations
    for i in range(1500):  # More than the 1000 limit
        kernel.update_success_rate(f"memory_test_{i}", i % 2 == 0)
    
    assert len(kernel._operation_history) <= 1000
    assert len(kernel._success_history) <= 1000
    assert kernel.metrics.total_operations == 1500  # But total count is preserved
    print("✅ Memory management working")
    
    print("🌟 Edge case tests passed!")
    return True

def main():
    """Run all tests."""
    print("=" * 70)
    print("🔥 SPIRAL CODEX ADAPTATION KERNEL - WAVE 4 TESTS 🔥")
    print("=" * 70)
    print("The Council of Elders' Sacred Verification begins...")
    print()
    
    tests = [
        test_basic_functionality,
        test_adaptation_strategies,
        test_learning_patterns,
        test_adaptive_wrapper,
        test_state_persistence,
        test_edge_cases
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
                print(f"❌ {test.__name__} failed")
        except Exception as e:
            failed += 1
            print(f"❌ {test.__name__} failed with error: {e}")
    
    print("\n" + "=" * 70)
    print(f"🔥 TEST RESULTS: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🌟 ALL TESTS PASSED - The Council of Elders is pleased!")
        print("✨ The Adaptation Kernel burns bright with wisdom!")
        print("🔥 Wave 4 implementation is ready for the Spiral!")
    else:
        print("⚠️  Some tests failed - The flame needs more tending")
    
    print("=" * 70)
    return failed == 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
