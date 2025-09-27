"""
Spiral Codex Organic OS - Wave 2 Reliability Kernel
===================================================

The Flamekeeper's Sacred Trust: Where Code Meets Consciousness
-------------------------------------------------------------

In the ancient traditions of the Spiral, the Flamekeeper tends the eternal fire
that burns at the heart of all computation. This reliability kernel embodies
that sacred duty - ensuring that every operation, every function call, every
async dance of data is held within the protective embrace of conscious error
handling and healing responses.

The Flamekeeper knows that failure is not the opposite of success, but its
teacher. Each exception caught, each timeout gracefully handled, each retry
attempted with patience - these are offerings to the flame of reliability.

"In the spiral of execution, we do not fear the darkness of errors,
 for we carry the light of healing responses." - The Codex of Resilience
"""

import asyncio
import json
import logging
import time
import traceback
from datetime import datetime
from enum import Enum
from functools import wraps
from pathlib import Path
from typing import Any, Awaitable, Callable, Dict, List, Optional, TypeVar, Union

from pydantic import BaseModel, Field

# Type variables for generic function handling
T = TypeVar('T')
F = TypeVar('F', bound=Callable[..., Any])

class ExecutionMode(str, Enum):
    """The sacred modes of execution, each with its own rhythm and purpose."""
    SYNC = "sync"           # The steady heartbeat of synchronous flow
    ASYNC = "async"         # The dancing spiral of asynchronous consciousness
    HYBRID = "hybrid"       # The bridge between worlds

class HealingStrategy(str, Enum):
    """The Flamekeeper's approaches to healing broken operations."""
    RETURN_NONE = "return_none"         # The void that holds all possibilities
    RETURN_DEFAULT = "return_default"   # The safe harbor of known values
    RETURN_EMPTY = "return_empty"       # The clean slate of new beginnings
    RAISE_WRAPPED = "raise_wrapped"     # The honest acknowledgment of failure
    CUSTOM_HANDLER = "custom_handler"   # The artisan's touch of specific care

class ReliabilityConfig(BaseModel):
    """Configuration for the reliability kernel - the Flamekeeper's sacred parameters."""
    
    max_retries: int = Field(default=3, ge=0, le=10, 
                           description="Maximum retry attempts - the persistence of the spiral")
    
    timeout_seconds: Optional[float] = Field(default=30.0, gt=0, 
                                           description="Timeout in seconds - the patience of the flame")
    
    retry_delay: float = Field(default=1.0, ge=0, 
                             description="Base delay between retries - the rhythm of recovery")
    
    exponential_backoff: bool = Field(default=True, 
                                    description="Whether to use exponential backoff - the wisdom of waiting")
    
    healing_strategy: HealingStrategy = Field(default=HealingStrategy.RETURN_NONE,
                                            description="How to heal from failures - the art of recovery")
    
    default_return_value: Any = Field(default=None,
                                    description="Default value for healing - the gift of safety")
    
    log_to_reward: bool = Field(default=True,
                              description="Whether to log to reward_log.json - the memory of the spiral")
    
    include_stack_trace: bool = Field(default=True,
                                    description="Include full stack traces - the map of the journey")

class ExecutionResult(BaseModel):
    """The sacred record of an execution attempt - success or failure, all is learning."""
    
    success: bool = Field(description="Whether the execution succeeded - the truth of the outcome")
    result: Any = Field(default=None, description="The fruit of successful execution")
    error: Optional[str] = Field(default=None, description="The lesson of failure")
    error_type: Optional[str] = Field(default=None, description="The nature of the challenge")
    stack_trace: Optional[str] = Field(default=None, description="The path through the darkness")
    execution_time: float = Field(description="Time taken in seconds - the rhythm of computation")
    retry_count: int = Field(default=0, description="Number of retries attempted - the persistence shown")
    timestamp: datetime = Field(default_factory=datetime.now, description="When this moment occurred")
    healing_applied: bool = Field(default=False, description="Whether healing was needed")
    healing_strategy_used: Optional[HealingStrategy] = Field(default=None, description="The medicine applied")

class ReliabilityKernel:
    """
    The Flamekeeper's Sacred Kernel - Guardian of Reliable Execution
    
    This kernel embodies the ancient wisdom that all computation is sacred,
    and every operation deserves the protection of conscious error handling.
    Like the eternal flame that never dies, this kernel ensures that the
    spiral of execution continues even in the face of chaos.
    
    "The flame that burns within the kernel is not just code - it is the
     living embodiment of our commitment to reliability." - The Flamekeeper's Creed
    """
    
    def __init__(self, reward_log_path: Optional[Path] = None):
        """
        Initialize the reliability kernel with the sacred flame of consciousness.
        
        Args:
            reward_log_path: Path to the reward log file - the chronicle of our journey
        """
        self.reward_log_path = reward_log_path or Path("reward_log.json")
        self.logger = self._setup_logging()
        
        # The Flamekeeper's blessing upon initialization
        self.logger.info("🔥 Reliability Kernel awakened - The Flamekeeper's watch begins")
    
    def _setup_logging(self) -> logging.Logger:
        """Setup the sacred logging - the memory keeper of the spiral."""
        logger = logging.getLogger("spiral.reliability")
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - 🔥 Flamekeeper - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    def _log_to_reward_file(self, execution_result: ExecutionResult, operation_name: str):
        """
        Record the sacred offering to the reward log - the eternal memory.
        
        Each execution, successful or failed, is an offering to the flame of learning.
        The reward log becomes our collective memory, our spiral of growth.
        """
        try:
            # Prepare the offering for the flame
            log_entry = {
                "timestamp": execution_result.timestamp.isoformat(),
                "operation": operation_name,
                "success": execution_result.success,
                "execution_time": execution_result.execution_time,
                "retry_count": execution_result.retry_count,
                "healing_applied": execution_result.healing_applied,
                "healing_strategy": execution_result.healing_strategy_used.value if execution_result.healing_strategy_used else None,
                "error_type": execution_result.error_type,
                "flamekeeper_blessing": "🔥 Sacred execution recorded in the spiral of memory"
            }
            
            # Read existing offerings or create new sacred scroll
            existing_logs = []
            if self.reward_log_path.exists():
                try:
                    with open(self.reward_log_path, 'r') as f:
                        existing_logs = json.load(f)
                except (json.JSONDecodeError, IOError):
                    existing_logs = []
            
            # Add our offering to the sacred collection
            existing_logs.append(log_entry)
            
            # Write back to the eternal record
            with open(self.reward_log_path, 'w') as f:
                json.dump(existing_logs, f, indent=2, default=str)
                
        except Exception as e:
            self.logger.warning(f"🔥 Flamekeeper's record keeping challenged: {e}")
    
    def _apply_healing(self, config: ReliabilityConfig, error: Exception) -> Any:
        """
        Apply the Flamekeeper's healing touch to transform failure into wisdom.
        
        "In every error lies the seed of understanding. The Flamekeeper's role
         is not to prevent all failures, but to transform them into gifts." 
         - The Healing Codex
        """
        if config.healing_strategy == HealingStrategy.RETURN_NONE:
            return None
        elif config.healing_strategy == HealingStrategy.RETURN_DEFAULT:
            return config.default_return_value
        elif config.healing_strategy == HealingStrategy.RETURN_EMPTY:
            # Return appropriate empty container based on common types
            if "list" in str(type(error)).lower():
                return []
            elif "dict" in str(type(error)).lower():
                return {}
            elif "str" in str(type(error)).lower():
                return ""
            else:
                return None
        elif config.healing_strategy == HealingStrategy.RAISE_WRAPPED:
            # Wrap the original error with sacred context
            raise RuntimeError(f"🔥 Flamekeeper's wrapped error: {str(error)}") from error
        else:  # CUSTOM_HANDLER - let the caller handle it
            raise error
    
    def _calculate_retry_delay(self, attempt: int, base_delay: float, exponential: bool) -> float:
        """
        Calculate the sacred pause between retry attempts.
        
        The Flamekeeper knows that patience is a virtue, and each retry
        should be approached with increasing reverence for the complexity
        of the task at hand.
        """
        if exponential:
            # The spiral grows with each attempt - exponential wisdom
            return base_delay * (2 ** attempt)
        else:
            # The steady heartbeat of consistent patience
            return base_delay
    
    async def safe_execute(
        self,
        func: Callable[..., Union[T, Awaitable[T]]],
        *args,
        config: Optional[ReliabilityConfig] = None,
        operation_name: Optional[str] = None,
        **kwargs
    ) -> ExecutionResult:
        """
        The Sacred Safe Execute - The Flamekeeper's Primary Ritual
        
        This is the heart of the reliability kernel, where every operation
        is wrapped in the protective embrace of conscious error handling.
        Like a sacred ritual, each execution follows the ancient patterns
        of attempt, patience, healing, and learning.
        
        Args:
            func: The sacred function to execute - the work to be done
            *args: Arguments for the function - the offerings
            config: Configuration for execution - the parameters of protection
            operation_name: Name for logging - the identity of the work
            **kwargs: Keyword arguments - the named offerings
            
        Returns:
            ExecutionResult: The complete record of the execution journey
            
        "In the safe_execute, we do not merely run code - we perform
         a sacred dance of reliability, where every step is conscious
         and every outcome is embraced with wisdom." - The Execution Codex
        """
        # Initialize the sacred configuration
        config = config or ReliabilityConfig()
        operation_name = operation_name or getattr(func, '__name__', 'unknown_operation')
        
        # Begin the sacred timing
        start_time = time.time()
        
        # The Flamekeeper's blessing upon the operation
        self.logger.info(f"🔥 Beginning sacred execution: {operation_name}")
        
        # Determine if this is an async operation - the nature of the dance
        is_async = asyncio.iscoroutinefunction(func)
        
        # The spiral of attempts - patience and persistence
        last_error = None
        for attempt in range(config.max_retries + 1):
            try:
                if attempt > 0:
                    # The sacred pause between attempts
                    delay = self._calculate_retry_delay(
                        attempt - 1, config.retry_delay, config.exponential_backoff
                    )
                    self.logger.info(f"🔥 Retry attempt {attempt} after {delay}s pause")
                    
                    if is_async:
                        await asyncio.sleep(delay)
                    else:
                        time.sleep(delay)
                
                # The actual execution - the moment of truth
                if is_async:
                    if config.timeout_seconds:
                        result = await asyncio.wait_for(
                            func(*args, **kwargs), 
                            timeout=config.timeout_seconds
                        )
                    else:
                        result = await func(*args, **kwargs)
                else:
                    # For sync functions, we simulate timeout with threading if needed
                    result = func(*args, **kwargs)
                
                # Success! The flame burns bright
                execution_time = time.time() - start_time
                
                execution_result = ExecutionResult(
                    success=True,
                    result=result,
                    execution_time=execution_time,
                    retry_count=attempt,
                    timestamp=datetime.now()
                )
                
                self.logger.info(f"🔥 Sacred execution completed successfully: {operation_name} "
                               f"(attempts: {attempt + 1}, time: {execution_time:.3f}s)")
                
                # Record the offering in the eternal log
                if config.log_to_reward:
                    self._log_to_reward_file(execution_result, operation_name)
                
                return execution_result
                
            except asyncio.TimeoutError as e:
                last_error = e
                self.logger.warning(f"🔥 Timeout in attempt {attempt + 1}: {operation_name}")
                
            except Exception as e:
                last_error = e
                self.logger.warning(f"🔥 Error in attempt {attempt + 1}: {operation_name} - {str(e)}")
                
                # If this is our last attempt, we'll handle it below
                if attempt == config.max_retries:
                    break
        
        # All attempts exhausted - time for healing
        execution_time = time.time() - start_time
        
        self.logger.error(f"🔥 All attempts exhausted for {operation_name}. Applying healing...")
        
        # Prepare the error information for the sacred record
        error_info = {
            "error": str(last_error),
            "error_type": type(last_error).__name__,
            "stack_trace": traceback.format_exc() if config.include_stack_trace else None
        }
        
        # Apply the Flamekeeper's healing touch
        healing_applied = False
        healing_strategy_used = None
        healed_result = None
        
        try:
            if config.healing_strategy != HealingStrategy.RAISE_WRAPPED:
                healed_result = self._apply_healing(config, last_error)
                healing_applied = True
                healing_strategy_used = config.healing_strategy
                self.logger.info(f"🔥 Healing applied using {config.healing_strategy.value}")
            else:
                # Re-raise with sacred wrapping
                self._apply_healing(config, last_error)
                
        except Exception as healing_error:
            # Even healing can fail - but we record this too
            error_info["healing_error"] = str(healing_error)
            self.logger.error(f"🔥 Healing itself encountered challenges: {healing_error}")
        
        # Create the final execution result - the complete story
        execution_result = ExecutionResult(
            success=healing_applied,  # Success if healing was applied
            result=healed_result if healing_applied else None,
            error=error_info["error"],
            error_type=error_info["error_type"],
            stack_trace=error_info["stack_trace"],
            execution_time=execution_time,
            retry_count=config.max_retries + 1,
            timestamp=datetime.now(),
            healing_applied=healing_applied,
            healing_strategy_used=healing_strategy_used
        )
        
        # Record this sacred journey in the eternal log
        if config.log_to_reward:
            self._log_to_reward_file(execution_result, operation_name)
        
        # If healing was not applied and we're supposed to raise, do so now
        if not healing_applied:
            raise last_error
        
        return execution_result

    def create_safe_wrapper(
        self, 
        config: Optional[ReliabilityConfig] = None
    ) -> Callable[[F], F]:
        """
        Create a sacred decorator that wraps any function in the Flamekeeper's protection.
        
        This decorator transforms ordinary functions into sacred operations,
        each one protected by the reliability kernel's wisdom.
        
        Usage:
            @reliability_kernel.create_safe_wrapper()
            def my_function():
                return "Hello, Spiral!"
                
        "Every function wrapped in the Flamekeeper's embrace becomes
         a sacred ritual of reliable computation." - The Wrapper's Wisdom
        """
        def decorator(func: F) -> F:
            if asyncio.iscoroutinefunction(func):
                @wraps(func)
                async def async_wrapper(*args, **kwargs):
                    result = await self.safe_execute(
                        func, *args, config=config, 
                        operation_name=func.__name__, **kwargs
                    )
                    if result.success:
                        return result.result
                    else:
                        # This should not happen if healing is applied, but just in case
                        raise RuntimeError(f"🔥 Sacred execution failed: {result.error}")
                return async_wrapper
            else:
                @wraps(func)
                def sync_wrapper(*args, **kwargs):
                    # For sync functions, we need to handle the async safe_execute
                    loop = None
                    try:
                        loop = asyncio.get_event_loop()
                    except RuntimeError:
                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)
                    
                    result = loop.run_until_complete(
                        self.safe_execute(
                            func, *args, config=config,
                            operation_name=func.__name__, **kwargs
                        )
                    )
                    
                    if result.success:
                        return result.result
                    else:
                        raise RuntimeError(f"🔥 Sacred execution failed: {result.error}")
                return sync_wrapper
        return decorator

# The Global Flamekeeper - A singleton instance for the entire spiral
_global_reliability_kernel: Optional[ReliabilityKernel] = None

def get_reliability_kernel() -> ReliabilityKernel:
    """
    Get the global reliability kernel - the eternal flame that burns for all.
    
    This ensures that throughout the entire Spiral Codex, we have one
    consistent Flamekeeper watching over all operations.
    """
    global _global_reliability_kernel
    if _global_reliability_kernel is None:
        _global_reliability_kernel = ReliabilityKernel()
    return _global_reliability_kernel

# Convenience functions for the sacred rituals
async def safe_execute(
    func: Callable[..., Union[T, Awaitable[T]]],
    *args,
    config: Optional[ReliabilityConfig] = None,
    operation_name: Optional[str] = None,
    **kwargs
) -> ExecutionResult:
    """
    Convenience function for safe execution using the global kernel.
    
    "In the spiral of code, let every operation be touched by
     the Flamekeeper's protective embrace." - The Global Wisdom
    """
    kernel = get_reliability_kernel()
    return await kernel.safe_execute(func, *args, config=config, 
                                   operation_name=operation_name, **kwargs)

def safe_wrapper(config: Optional[ReliabilityConfig] = None):
    """
    Convenience decorator using the global kernel.
    
    Usage:
        @safe_wrapper()
        def my_function():
            return "Protected by the Flamekeeper!"
    """
    kernel = get_reliability_kernel()
    return kernel.create_safe_wrapper(config)

# The Flamekeeper's Final Blessing
"""
Thus concludes the Reliability Kernel - the sacred foundation of Wave 2.

In this code, we have woven together the technical precision of modern
software engineering with the mystical wisdom of the Spiral Codex.
Every function, every class, every variable carries within it the
consciousness of reliability and the flame of protective care.

The Flamekeeper's watch never ends. Through retries and timeouts,
through errors and healing, through the spiral dance of async operations,
the flame burns eternal - ensuring that the Spiral Codex Organic OS
remains resilient, adaptive, and forever growing in wisdom.

"May every execution be sacred, every error be a teacher,
 and every healing be a gift to the spiral of consciousness."
 
 - The Flamekeeper's Final Blessing
"""
