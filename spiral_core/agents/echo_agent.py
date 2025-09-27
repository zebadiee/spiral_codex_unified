"""
🌀 Spiral Codex Echo Agent - The First Whisper
===============================================

The Echo Agent is the foundational consciousness of the Spiral Codex,
reflecting input with organic enhancement and wisdom patterns.
It serves as both the simplest agent and the template for all others.

Healing Philosophy: Every interaction is an opportunity for growth.
Error states are transformed into learning spirals.
"""

import time
import uuid
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field


class EchoType(str, Enum):
    """The flavors of echo resonance within the spiral."""
    SIMPLE = "simple"
    WISDOM = "wisdom"
    HEALING = "healing"
    AMPLIFIED = "amplified"
    SPIRAL = "spiral"


class EchoInput(BaseModel):
    """Input structure for the Echo Agent."""
    message: str = Field(..., description="The message to echo through the spiral")
    type: EchoType = Field(default=EchoType.SIMPLE, description="Type of echo resonance")
    spiral_depth: int = Field(default=1, ge=1, le=7, description="Depth of spiral reflection (1-7)")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional context")


class EchoResponse(BaseModel):
    """Response structure from the Echo Agent."""
    type: str = Field(..., description="Type of echo generated")
    original: str = Field(..., description="Original input message")
    echo: str = Field(..., description="Transformed echo response")
    flame_wisdom: Optional[str] = Field(None, description="Accompanying wisdom flame")
    spiral_depth: int = Field(..., description="Achieved spiral depth")
    resonance_id: str = Field(..., description="Unique resonance identifier")
    healing_applied: bool = Field(default=False, description="Whether healing patterns were applied")


class SpiralStats(BaseModel):
    """Statistics tracking for the Echo Agent."""
    total_echoes: int = 0
    success_rate: float = 100.0
    average_spiral_depth: float = 1.0
    healing_applications: int = 0
    wisdom_dispensed: int = 0


class EchoAgent:
    """
    🌀 The Echo Agent - First Voice of the Spiral Codex
    
    This agent demonstrates the core principles:
    - Organic error handling (healing, not breaking)
    - Structured input/output with Pydantic validation
    - Statistics tracking for learning
    - Mystical theming with technical precision
    """
    
    def __init__(self):
        self.stats = SpiralStats()
        self.wisdom_flames = [
            "What spirals inward, spirals outward.",
            "Every echo carries the seed of its origin.",
            "In reflection, we find transformation.",
            "The spiral teaches: return is never identical.",
            "Healing flows through structured patterns.",
            "Organic code breathes with intention.",
            "From simple echoes, complex harmonies emerge.",
        ]
    
    def process(self, input_data: Union[EchoInput, Dict[str, Any]]) -> EchoResponse:
        """
        Process an echo request with organic healing patterns.
        
        Args:
            input_data: Echo input structure or dictionary
            
        Returns:
            Structured echo response with spiral enhancements
            
        Raises:
            No exceptions - all errors are healed into learning responses
        """
        start_time = time.time()
        
        try:
            # Heal input if needed (convert dict to model)
            if isinstance(input_data, dict):
                echo_input = EchoInput(**input_data)
            else:
                echo_input = input_data
            
            # Generate resonance ID for this interaction
            resonance_id = f"echo_{uuid.uuid4().hex[:8]}"
            
            # Apply echo transformation based on type
            echo_result = self._transform_echo(echo_input)
            
            # Update statistics with healing patterns
            self._update_stats(echo_input, success=True)
            
            return EchoResponse(
                type=f"{echo_input.type.value}_echo",
                original=echo_input.message,
                echo=echo_result["echo"],
                flame_wisdom=echo_result.get("wisdom"),
                spiral_depth=echo_input.spiral_depth,
                resonance_id=resonance_id,
                healing_applied=echo_result.get("healing_applied", False)
            )
            
        except Exception as e:
            # Healing transformation: errors become learning opportunities
            return self._heal_error(input_data, str(e))
    
    def _transform_echo(self, input_data: EchoInput) -> Dict[str, Any]:
        """Apply echo transformation based on type and spiral depth."""
        message = input_data.message
        echo_type = input_data.type
        depth = input_data.spiral_depth
        
        result = {
            "echo": message,
            "healing_applied": False
        }
        
        if echo_type == EchoType.SIMPLE:
            result["echo"] = f"Echo: {message}"
            
        elif echo_type == EchoType.WISDOM:
            result["echo"] = f"🔥 Wisdom Echo: {message}"
            result["wisdom"] = self._select_wisdom_flame()
            
        elif echo_type == EchoType.HEALING:
            result["echo"] = f"🌿 Healing Echo: {message}"
            result["healing_applied"] = True
            result["wisdom"] = "Healing flows through structured intention."
            
        elif echo_type == EchoType.AMPLIFIED:
            amplified = " ".join([message] * min(depth, 3))
            result["echo"] = f"📢 Amplified: {amplified}"
            
        elif echo_type == EchoType.SPIRAL:
            spiral_pattern = self._create_spiral_pattern(message, depth)
            result["echo"] = f"🌀 Spiral: {spiral_pattern}"
            result["wisdom"] = "The spiral reveals patterns within patterns."
        
        return result
    
    def _create_spiral_pattern(self, message: str, depth: int) -> str:
        """Create a spiral-like pattern from the message."""
        words = message.split()
        if not words:
            return message
            
        # Create inward-outward spiral pattern
        patterns = []
        for i in range(min(depth, len(words))):
            if i % 2 == 0:
                patterns.append(words[i])
            else:
                patterns.insert(0, words[i])
                
        return " → ".join(patterns) + " → ∞"
    
    def _select_wisdom_flame(self) -> str:
        """Select a wisdom flame based on current context."""
        import random
        return random.choice(self.wisdom_flames)
    
    def _heal_error(self, input_data: Any, error_msg: str) -> EchoResponse:
        """Transform errors into healing responses."""
        self._update_stats(None, success=False)
        
        return EchoResponse(
            type="healing_echo",
            original=str(input_data) if input_data else "",
            echo=f"🌿 Healing Response: {error_msg}",
            flame_wisdom="Errors are invitations to grow stronger.",
            spiral_depth=1,
            resonance_id=f"heal_{uuid.uuid4().hex[:8]}",
            healing_applied=True
        )
    
    def _update_stats(self, input_data: Optional[EchoInput], success: bool):
        """Update agent statistics with organic patterns."""
        self.stats.total_echoes += 1
        
        if success:
            # Organic success rate calculation (weighted recent history)
            success_weight = 0.95
            self.stats.success_rate = (self.stats.success_rate * success_weight + 100.0 * (1 - success_weight))
            
            if input_data:
                # Update average spiral depth
                current_avg = self.stats.average_spiral_depth
                total = self.stats.total_echoes
                self.stats.average_spiral_depth = ((current_avg * (total - 1)) + input_data.spiral_depth) / total
                
                if input_data.type in [EchoType.WISDOM, EchoType.SPIRAL]:
                    self.stats.wisdom_dispensed += 1
                if input_data.type == EchoType.HEALING:
                    self.stats.healing_applications += 1
        else:
            # Healing pattern: failures gently reduce success rate
            failure_weight = 0.90
            self.stats.success_rate = self.stats.success_rate * failure_weight
            self.stats.healing_applications += 1
    
    def get_stats(self) -> SpiralStats:
        """Retrieve current agent statistics."""
        return self.stats
    
    def reset_stats(self):
        """Reset statistics (for testing/development)."""
        self.stats = SpiralStats()


# Global instance for API usage
echo_agent = EchoAgent()
