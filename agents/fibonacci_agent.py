
"""
🌀 Fibonacci Agent - Mystical Sequence Generator

A recursive agent that generates Fibonacci sequences and explores
the golden ratio's mystical properties within the Spiral Codex.
"""

from spiralcodex.plugins import AgentPluginBase, create_capability
from typing import Dict, Any, Optional, List
import logging
from datetime import datetime

class FibonacciAgent(AgentPluginBase):
    """
    🌀 Fibonacci Agent Plugin
    
    Generates mystical Fibonacci sequences and explores the recursive
    nature of the golden ratio within the Spiral Codex framework.
    """
    
    PLUGIN_NAME = "FibonacciAgent"
    PLUGIN_VERSION = "1.0.0"
    PLUGIN_DESCRIPTION = "Mystical Fibonacci sequence generator with golden ratio exploration"
    PLUGIN_AUTHOR = "Spiral Codex"
    PLUGIN_CAPABILITIES = ["fibonacci_sequence", "golden_ratio", "spiral_analysis"]
    PLUGIN_DEPENDENCIES = []
    PLUGIN_CONFIG_SCHEMA = {
        "max_sequence_length": {"type": "integer", "default": 100},
        "precision": {"type": "integer", "default": 10}
    }
    
    def _initialize_agent(self):
        """Initialize the Fibonacci agent"""
        self.logger.info("🌀 Initializing Fibonacci agent")
        
        # Configuration
        self.max_length = self.config.get("max_sequence_length", 100)
        self.precision = self.config.get("precision", 10)
        
        # State
        self.sequence_cache = {}
        self.golden_ratio = (1 + 5**0.5) / 2  # φ (phi)
        self.calculations_performed = 0
        
        # Add capabilities
        self.capabilities.extend([
            create_capability(
                name="fibonacci_sequence",
                description="Generate Fibonacci sequence up to n terms",
                input_schema={"n": "integer", "start_a": "integer", "start_b": "integer"},
                output_schema={"sequence": "array", "length": "integer", "golden_ratio_approximation": "number"}
            ),
            create_capability(
                name="golden_ratio",
                description="Calculate golden ratio properties and relationships",
                input_schema={"precision": "integer"},
                output_schema={"phi": "number", "phi_conjugate": "number", "properties": "object"}
            ),
            create_capability(
                name="spiral_analysis",
                description="Analyze spiral properties of Fibonacci sequence",
                input_schema={"sequence_length": "integer"},
                output_schema={"spiral_data": "object", "growth_rate": "number", "mystical_properties": "object"}
            )
        ])
    
    def _cleanup_agent(self):
        """Cleanup the Fibonacci agent"""
        self.logger.info("🧹 Cleaning up Fibonacci agent")
        self.sequence_cache.clear()
        self.calculations_performed = 0
    
    def execute_fibonacci_sequence(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate Fibonacci sequence"""
        n = input_data.get("n", 10)
        start_a = input_data.get("start_a", 0)
        start_b = input_data.get("start_b", 1)
        
        if n > self.max_length:
            n = self.max_length
            self.logger.warning(f"⚠️ Sequence length capped at {self.max_length}")
        
        self.logger.info(f"🌀 Generating Fibonacci sequence of length {n}")
        
        # Check cache
        cache_key = f"{n}_{start_a}_{start_b}"
        if cache_key in self.sequence_cache:
            self.logger.debug("📋 Using cached sequence")
            return self.sequence_cache[cache_key]
        
        # Generate sequence
        sequence = []
        if n >= 1:
            sequence.append(start_a)
        if n >= 2:
            sequence.append(start_b)
        
        for i in range(2, n):
            next_val = sequence[i-1] + sequence[i-2]
            sequence.append(next_val)
        
        # Calculate golden ratio approximation
        golden_ratio_approx = None
        if len(sequence) >= 2:
            golden_ratio_approx = sequence[-1] / sequence[-2] if sequence[-2] != 0 else None
        
        result = {
            "sequence": sequence,
            "length": len(sequence),
            "golden_ratio_approximation": golden_ratio_approx,
            "theoretical_golden_ratio": self.golden_ratio,
            "convergence_error": abs(golden_ratio_approx - self.golden_ratio) if golden_ratio_approx else None
        }
        
        # Cache result
        self.sequence_cache[cache_key] = result
        self.calculations_performed += 1
        
        return result
    
    def execute_golden_ratio(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate golden ratio properties"""
        precision = input_data.get("precision", self.precision)
        
        self.logger.info(f"✨ Calculating golden ratio properties (precision: {precision})")
        
        phi = self.golden_ratio
        phi_conjugate = (1 - 5**0.5) / 2  # φ̄ (phi conjugate)
        
        # Calculate various properties
        properties = {
            "phi": round(phi, precision),
            "phi_conjugate": round(phi_conjugate, precision),
            "phi_squared": round(phi**2, precision),
            "phi_inverse": round(1/phi, precision),
            "phi_minus_one": round(phi - 1, precision),
            "continued_fraction": self._golden_ratio_continued_fraction(precision),
            "mystical_relationships": {
                "phi_squared_equals_phi_plus_one": abs(phi**2 - (phi + 1)) < 1e-10,
                "phi_inverse_equals_phi_minus_one": abs(1/phi - (phi - 1)) < 1e-10,
                "pentagon_relationship": round(phi, 5) == round((1 + 5**0.5) / 2, 5)
            }
        }
        
        self.calculations_performed += 1
        
        return {
            "phi": phi,
            "phi_conjugate": phi_conjugate,
            "properties": properties,
            "precision": precision
        }
    
    def execute_spiral_analysis(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze spiral properties of Fibonacci sequence"""
        sequence_length = input_data.get("sequence_length", 20)
        
        self.logger.info(f"🌀 Analyzing spiral properties for sequence length {sequence_length}")
        
        # Generate sequence for analysis
        fib_result = self.execute_fibonacci_sequence({"n": sequence_length})
        sequence = fib_result["sequence"]
        
        if len(sequence) < 3:
            return {"error": "Sequence too short for spiral analysis"}
        
        # Calculate growth rates
        growth_rates = []
        for i in range(2, len(sequence)):
            if sequence[i-1] != 0:
                growth_rate = sequence[i] / sequence[i-1]
                growth_rates.append(growth_rate)
        
        # Spiral properties
        spiral_data = {
            "sequence_ratios": growth_rates,
            "convergence_to_phi": growth_rates[-1] if growth_rates else None,
            "spiral_angles": [self._calculate_spiral_angle(i, sequence[i]) for i in range(len(sequence))],
            "golden_spiral_approximation": self._golden_spiral_approximation(sequence)
        }
        
        # Mystical properties
        mystical_properties = {
            "fibonacci_spiral_turns": len(sequence) * 0.618,  # Approximate turns in golden spiral
            "sacred_geometry_ratio": self.golden_ratio,
            "nature_manifestations": [
                "Nautilus shell chambers",
                "Sunflower seed spirals", 
                "Galaxy arm structures",
                "Pinecone patterns",
                "Flower petal arrangements"
            ],
            "recursive_depth": len(sequence),
            "entropy_level": self._calculate_sequence_entropy(sequence)
        }
        
        self.calculations_performed += 1
        
        return {
            "spiral_data": spiral_data,
            "growth_rate": growth_rates[-1] if growth_rates else None,
            "mystical_properties": mystical_properties,
            "sequence_length": len(sequence)
        }
    
    def _golden_ratio_continued_fraction(self, terms: int) -> List[int]:
        """Generate continued fraction representation of golden ratio"""
        # Golden ratio has the simplest continued fraction: [1; 1, 1, 1, ...]
        return [1] + [1] * (terms - 1)
    
    def _calculate_spiral_angle(self, index: int, value: int) -> float:
        """Calculate spiral angle for a given Fibonacci number"""
        if value == 0:
            return 0.0
        
        # Approximate angle based on golden angle (137.5°)
        golden_angle = 137.507764  # degrees
        return (index * golden_angle) % 360
    
    def _golden_spiral_approximation(self, sequence: List[int]) -> Dict[str, Any]:
        """Calculate golden spiral approximation data"""
        if len(sequence) < 4:
            return {"error": "Insufficient data for spiral approximation"}
        
        # Calculate quarter-circle radii using Fibonacci numbers
        radii = []
        for i in range(len(sequence)):
            if sequence[i] > 0:
                radii.append(sequence[i])
        
        return {
            "radii": radii,
            "spiral_growth_factor": self.golden_ratio,
            "quarter_circles": len(radii),
            "total_rotation": len(radii) * 90  # degrees
        }
    
    def _calculate_sequence_entropy(self, sequence: List[int]) -> float:
        """Calculate entropy of the Fibonacci sequence"""
        if not sequence:
            return 0.0
        
        # Simple entropy calculation based on digit distribution
        digit_counts = {}
        for num in sequence:
            for digit in str(num):
                digit_counts[digit] = digit_counts.get(digit, 0) + 1
        
        total_digits = sum(digit_counts.values())
        entropy = 0.0
        
        for count in digit_counts.values():
            if count > 0:
                probability = count / total_digits
                entropy -= probability * (probability.bit_length() - 1)
        
        return entropy
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get agent metrics"""
        uptime = 0
        if self.is_running and self.last_activity:
            uptime = (datetime.now() - self.last_activity).total_seconds()
        
        return {
            "uptime": uptime,
            "calculations_performed": self.calculations_performed,
            "cached_sequences": len(self.sequence_cache),
            "golden_ratio_precision": self.precision,
            "max_sequence_length": self.max_length,
            "last_activity": self.last_activity.isoformat() if self.last_activity else None
        }
    
    # Event handlers
    def on_ritual_cycle(self, event_data: Dict[str, Any]):
        """Handle ritual cycle events"""
        ritual_type = event_data.get("ritual_type", "unknown")
        depth = event_data.get("recursion_depth", 0)
        
        self.logger.info(f"🌀 Participating in ritual: {ritual_type} (depth: {depth})")
        
        # Generate Fibonacci number for the recursion depth
        if depth > 0 and depth <= 50:  # Reasonable limit
            fib_result = self.execute_fibonacci_sequence({"n": depth + 1})
            fib_number = fib_result["sequence"][-1] if fib_result["sequence"] else 0
            
            self.logger.info(f"✨ Fibonacci number for depth {depth}: {fib_number}")
    
    def on_agent_message(self, event_data: Dict[str, Any]):
        """Handle agent messages"""
        message = event_data.get("message", "")
        sender = event_data.get("sender", "unknown")
        
        self.logger.info(f"📨 Received message from {sender}: {message}")
        
        # Respond to Fibonacci-related queries
        if "fibonacci" in message.lower() or "golden" in message.lower():
            self.logger.info("🌀 Responding to Fibonacci query")
            # Could send back a Fibonacci sequence or golden ratio info
    
    def on_system_start(self, event_data: Dict[str, Any]):
        """Handle system start event"""
        self.logger.info("🌟 System started - Fibonacci agent ready for mystical calculations")
        
        # Generate a welcome Fibonacci sequence
        welcome_sequence = self.execute_fibonacci_sequence({"n": 13})  # Lucky 13
        self.logger.info(f"✨ Welcome sequence: {welcome_sequence['sequence']}")

# Plugin entry point
def create_plugin(config: Optional[Dict[str, Any]] = None) -> FibonacciAgent:
    """Create and return the plugin instance"""
    return FibonacciAgent(config)
