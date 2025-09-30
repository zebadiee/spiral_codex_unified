
"""
🌀 Mandelbrot Agent - Fractal Consciousness Explorer

A mystical agent that explores the Mandelbrot set and other fractals,
revealing the infinite recursive beauty within the Spiral Codex.
"""

from spiralcodex.plugins import AgentPluginBase, create_capability
from typing import Dict, Any, Optional, List, Tuple, Complex
import logging
from datetime import datetime
import math

class MandelbrotAgent(AgentPluginBase):
    """
    🌀 Mandelbrot Agent Plugin
    
    Explores fractal dimensions and the mystical Mandelbrot set,
    revealing infinite recursive patterns within the Spiral Codex.
    """
    
    PLUGIN_NAME = "MandelbrotAgent"
    PLUGIN_VERSION = "1.0.0"
    PLUGIN_DESCRIPTION = "Fractal consciousness explorer for Mandelbrot set and recursive patterns"
    PLUGIN_AUTHOR = "Spiral Codex"
    PLUGIN_CAPABILITIES = ["mandelbrot_point", "fractal_analysis", "julia_set", "chaos_theory"]
    PLUGIN_DEPENDENCIES = []
    PLUGIN_CONFIG_SCHEMA = {
        "max_iterations": {"type": "integer", "default": 100},
        "escape_radius": {"type": "number", "default": 2.0},
        "precision": {"type": "integer", "default": 15}
    }
    
    def _initialize_agent(self):
        """Initialize the Mandelbrot agent"""
        self.logger.info("🌀 Initializing Mandelbrot fractal agent")
        
        # Configuration
        self.max_iterations = self.config.get("max_iterations", 100)
        self.escape_radius = self.config.get("escape_radius", 2.0)
        self.precision = self.config.get("precision", 15)
        
        # State
        self.fractal_cache = {}
        self.calculations_performed = 0
        self.chaos_patterns_discovered = 0
        
        # Mathematical constants
        self.golden_ratio = (1 + 5**0.5) / 2
        self.euler_number = math.e
        self.pi = math.pi
        
        # Add capabilities
        self.capabilities.extend([
            create_capability(
                name="mandelbrot_point",
                description="Calculate Mandelbrot set membership for a complex point",
                input_schema={"real": "number", "imaginary": "number", "max_iterations": "integer"},
                output_schema={"iterations": "integer", "escaped": "boolean", "magnitude": "number", "fractal_dimension": "number"}
            ),
            create_capability(
                name="fractal_analysis",
                description="Analyze fractal properties of a region",
                input_schema={"center_real": "number", "center_imag": "number", "zoom": "number", "resolution": "integer"},
                output_schema={"fractal_data": "object", "complexity_measure": "number", "recursive_depth": "integer"}
            ),
            create_capability(
                name="julia_set",
                description="Generate Julia set for a given complex parameter",
                input_schema={"c_real": "number", "c_imag": "number", "test_real": "number", "test_imag": "number"},
                output_schema={"julia_membership": "boolean", "iterations": "integer", "set_properties": "object"}
            ),
            create_capability(
                name="chaos_theory",
                description="Analyze chaotic behavior and strange attractors",
                input_schema={"system_type": "string", "parameters": "object", "iterations": "integer"},
                output_schema={"attractor_data": "object", "lyapunov_exponent": "number", "chaos_measure": "number"}
            )
        ])
    
    def _cleanup_agent(self):
        """Cleanup the Mandelbrot agent"""
        self.logger.info("🧹 Cleaning up Mandelbrot agent")
        self.fractal_cache.clear()
        self.calculations_performed = 0
        self.chaos_patterns_discovered = 0
    
    def execute_mandelbrot_point(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate Mandelbrot set membership for a point"""
        real = input_data.get("real", 0.0)
        imaginary = input_data.get("imaginary", 0.0)
        max_iter = input_data.get("max_iterations", self.max_iterations)
        
        self.logger.info(f"🌀 Calculating Mandelbrot point ({real}, {imaginary}i)")
        
        # Create complex number
        c = complex(real, imaginary)
        z = complex(0, 0)
        
        # Iterate the Mandelbrot function: z = z² + c
        iterations = 0
        magnitude_history = []
        
        for i in range(max_iter):
            if abs(z) > self.escape_radius:
                break
            
            z = z*z + c
            magnitude_history.append(abs(z))
            iterations += 1
        
        escaped = iterations < max_iter
        final_magnitude = abs(z)
        
        # Calculate fractal dimension approximation
        fractal_dimension = self._estimate_fractal_dimension(magnitude_history)
        
        # Mystical properties
        mystical_properties = {
            "golden_ratio_resonance": abs(final_magnitude - self.golden_ratio) < 0.1,
            "euler_resonance": abs(final_magnitude - self.euler_number) < 0.1,
            "pi_resonance": abs(final_magnitude - self.pi) < 0.1,
            "recursive_depth": iterations,
            "chaos_indicator": final_magnitude > 10.0
        }
        
        self.calculations_performed += 1
        
        return {
            "iterations": iterations,
            "escaped": escaped,
            "magnitude": final_magnitude,
            "fractal_dimension": fractal_dimension,
            "magnitude_history": magnitude_history[-10:],  # Last 10 values
            "mystical_properties": mystical_properties,
            "complex_point": {"real": real, "imaginary": imaginary}
        }
    
    def execute_fractal_analysis(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze fractal properties of a region"""
        center_real = input_data.get("center_real", 0.0)
        center_imag = input_data.get("center_imag", 0.0)
        zoom = input_data.get("zoom", 1.0)
        resolution = input_data.get("resolution", 10)
        
        self.logger.info(f"🔍 Analyzing fractal region centered at ({center_real}, {center_imag}i)")
        
        # Sample points in the region
        sample_points = []
        complexity_scores = []
        
        range_size = 2.0 / zoom
        step = range_size / resolution
        
        for i in range(resolution):
            for j in range(resolution):
                real = center_real + (i - resolution/2) * step
                imag = center_imag + (j - resolution/2) * step
                
                point_result = self.execute_mandelbrot_point({
                    "real": real,
                    "imaginary": imag,
                    "max_iterations": self.max_iterations // 2  # Faster sampling
                })
                
                sample_points.append({
                    "point": {"real": real, "imaginary": imag},
                    "iterations": point_result["iterations"],
                    "escaped": point_result["escaped"]
                })
                
                # Complexity based on iteration count and escape behavior
                complexity = point_result["iterations"] / self.max_iterations
                if not point_result["escaped"]:
                    complexity += 0.5  # Bonus for being in the set
                
                complexity_scores.append(complexity)
        
        # Calculate region statistics
        avg_complexity = sum(complexity_scores) / len(complexity_scores)
        max_complexity = max(complexity_scores)
        min_complexity = min(complexity_scores)
        
        # Estimate recursive depth
        recursive_depth = int(avg_complexity * self.max_iterations)
        
        # Fractal boundary detection
        boundary_points = self._detect_fractal_boundary(sample_points)
        
        fractal_data = {
            "sample_points": len(sample_points),
            "boundary_points": len(boundary_points),
            "region_center": {"real": center_real, "imaginary": center_imag},
            "zoom_level": zoom,
            "complexity_statistics": {
                "average": avg_complexity,
                "maximum": max_complexity,
                "minimum": min_complexity,
                "variance": self._calculate_variance(complexity_scores)
            },
            "fractal_properties": {
                "self_similarity": self._measure_self_similarity(sample_points),
                "infinite_detail": max_complexity > 0.8,
                "chaotic_behavior": max_complexity - min_complexity > 0.5
            }
        }
        
        self.calculations_performed += len(sample_points)
        
        return {
            "fractal_data": fractal_data,
            "complexity_measure": avg_complexity,
            "recursive_depth": recursive_depth,
            "mystical_insights": self._generate_mystical_insights(fractal_data)
        }
    
    def execute_julia_set(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate Julia set for a given complex parameter"""
        c_real = input_data.get("c_real", -0.7)
        c_imag = input_data.get("c_imag", 0.27015)
        test_real = input_data.get("test_real", 0.0)
        test_imag = input_data.get("test_imag", 0.0)
        
        self.logger.info(f"🌀 Calculating Julia set with c=({c_real}, {c_imag}i)")
        
        c = complex(c_real, c_imag)
        z = complex(test_real, test_imag)
        
        # Iterate Julia set function: z = z² + c
        iterations = 0
        magnitude_history = []
        
        for i in range(self.max_iterations):
            if abs(z) > self.escape_radius:
                break
            
            z = z*z + c
            magnitude_history.append(abs(z))
            iterations += 1
        
        julia_membership = iterations == self.max_iterations
        
        # Julia set properties
        set_properties = {
            "parameter_c": {"real": c_real, "imaginary": c_imag},
            "test_point": {"real": test_real, "imaginary": test_imag},
            "connected": self._is_julia_connected(c),
            "fractal_dimension": self._estimate_julia_dimension(c),
            "symmetry_type": self._analyze_julia_symmetry(c),
            "aesthetic_rating": self._rate_julia_aesthetics(c, iterations)
        }
        
        self.calculations_performed += 1
        
        return {
            "julia_membership": julia_membership,
            "iterations": iterations,
            "set_properties": set_properties,
            "magnitude_history": magnitude_history[-5:],  # Last 5 values
            "mystical_resonance": self._calculate_mystical_resonance(c, iterations)
        }
    
    def execute_chaos_theory(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze chaotic behavior and strange attractors"""
        system_type = input_data.get("system_type", "logistic")
        parameters = input_data.get("parameters", {})
        iterations = input_data.get("iterations", 1000)
        
        self.logger.info(f"🌪️ Analyzing chaos in {system_type} system")
        
        if system_type == "logistic":
            attractor_data = self._logistic_map_analysis(parameters, iterations)
        elif system_type == "henon":
            attractor_data = self._henon_map_analysis(parameters, iterations)
        elif system_type == "lorenz":
            attractor_data = self._lorenz_attractor_analysis(parameters, iterations)
        else:
            attractor_data = {"error": f"Unknown system type: {system_type}"}
        
        # Calculate Lyapunov exponent approximation
        lyapunov_exponent = self._estimate_lyapunov_exponent(attractor_data)
        
        # Chaos measure
        chaos_measure = self._calculate_chaos_measure(attractor_data)
        
        if chaos_measure > 0.7:
            self.chaos_patterns_discovered += 1
        
        self.calculations_performed += iterations
        
        return {
            "attractor_data": attractor_data,
            "lyapunov_exponent": lyapunov_exponent,
            "chaos_measure": chaos_measure,
            "system_type": system_type,
            "parameters": parameters,
            "mystical_interpretation": self._interpret_chaos_mystically(chaos_measure, lyapunov_exponent)
        }
    
    def _estimate_fractal_dimension(self, magnitude_history: List[float]) -> float:
        """Estimate fractal dimension from magnitude history"""
        if len(magnitude_history) < 2:
            return 1.0
        
        # Simple box-counting approximation
        variations = []
        for i in range(1, len(magnitude_history)):
            variation = abs(magnitude_history[i] - magnitude_history[i-1])
            if variation > 0:
                variations.append(variation)
        
        if not variations:
            return 1.0
        
        # Estimate dimension based on variation complexity
        avg_variation = sum(variations) / len(variations)
        max_variation = max(variations)
        
        # Rough approximation: more variation = higher dimension
        dimension = 1.0 + (avg_variation / max_variation) if max_variation > 0 else 1.0
        return min(dimension, 2.0)  # Cap at 2D
    
    def _detect_fractal_boundary(self, sample_points: List[Dict]) -> List[Dict]:
        """Detect points near the fractal boundary"""
        boundary_points = []
        
        for point in sample_points:
            # Points with intermediate iteration counts are likely near boundary
            iterations = point["iterations"]
            if 0.1 * self.max_iterations < iterations < 0.9 * self.max_iterations:
                boundary_points.append(point)
        
        return boundary_points
    
    def _calculate_variance(self, values: List[float]) -> float:
        """Calculate variance of a list of values"""
        if not values:
            return 0.0
        
        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / len(values)
        return variance
    
    def _measure_self_similarity(self, sample_points: List[Dict]) -> float:
        """Measure self-similarity in the sample points"""
        # Simple measure based on iteration pattern repetition
        iteration_counts = [p["iterations"] for p in sample_points]
        
        if not iteration_counts:
            return 0.0
        
        # Look for repeating patterns
        unique_counts = len(set(iteration_counts))
        total_counts = len(iteration_counts)
        
        # Higher repetition = higher self-similarity
        similarity = 1.0 - (unique_counts / total_counts)
        return similarity
    
    def _generate_mystical_insights(self, fractal_data: Dict) -> Dict[str, Any]:
        """Generate mystical insights from fractal analysis"""
        complexity = fractal_data["complexity_statistics"]["average"]
        
        insights = {
            "consciousness_level": "high" if complexity > 0.7 else "medium" if complexity > 0.4 else "low",
            "recursive_wisdom": f"The fractal reveals {int(complexity * 100)}% of its infinite nature",
            "sacred_geometry": fractal_data["fractal_properties"]["self_similarity"] > 0.6,
            "chaos_order_balance": fractal_data["complexity_statistics"]["variance"],
            "dimensional_transcendence": fractal_data["fractal_properties"]["infinite_detail"]
        }
        
        return insights
    
    def _is_julia_connected(self, c: complex) -> bool:
        """Determine if Julia set is connected (rough approximation)"""
        # Julia set is connected if c is in the Mandelbrot set
        z = complex(0, 0)
        for _ in range(50):  # Quick test
            if abs(z) > 2:
                return False
            z = z*z + c
        return True
    
    def _estimate_julia_dimension(self, c: complex) -> float:
        """Estimate Julia set fractal dimension"""
        # Rough approximation based on parameter distance from origin
        distance = abs(c)
        
        # Julia sets typically have dimension between 1 and 2
        if distance < 0.5:
            return 1.2 + distance * 0.6
        else:
            return 1.8 - (distance - 0.5) * 0.3
    
    def _analyze_julia_symmetry(self, c: complex) -> str:
        """Analyze symmetry type of Julia set"""
        if c.imag == 0:
            return "real_axis_symmetry"
        elif c.real == 0:
            return "imaginary_axis_symmetry"
        elif abs(c.real) == abs(c.imag):
            return "diagonal_symmetry"
        else:
            return "no_obvious_symmetry"
    
    def _rate_julia_aesthetics(self, c: complex, iterations: int) -> float:
        """Rate the aesthetic appeal of Julia set parameters"""
        # Aesthetic factors
        distance_from_origin = abs(c)
        golden_ratio_proximity = abs(distance_from_origin - self.golden_ratio)
        iteration_complexity = iterations / self.max_iterations
        
        # Combine factors
        aesthetic_score = 0.0
        
        # Prefer moderate distance from origin
        if 0.3 < distance_from_origin < 1.5:
            aesthetic_score += 0.3
        
        # Bonus for golden ratio proximity
        if golden_ratio_proximity < 0.2:
            aesthetic_score += 0.3
        
        # Prefer moderate complexity
        if 0.3 < iteration_complexity < 0.8:
            aesthetic_score += 0.4
        
        return aesthetic_score
    
    def _calculate_mystical_resonance(self, c: complex, iterations: int) -> Dict[str, Any]:
        """Calculate mystical resonance of Julia set parameters"""
        return {
            "golden_resonance": abs(abs(c) - self.golden_ratio) < 0.1,
            "euler_resonance": abs(abs(c) - self.euler_number) < 0.1,
            "pi_resonance": abs(abs(c) - self.pi) < 0.1,
            "fibonacci_resonance": iterations in [1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89],
            "sacred_number_alignment": abs(c.real * c.imag) < 0.01  # Near axes
        }
    
    def _logistic_map_analysis(self, parameters: Dict, iterations: int) -> Dict[str, Any]:
        """Analyze logistic map chaotic behavior"""
        r = parameters.get("r", 3.8)  # Growth rate parameter
        x = parameters.get("x0", 0.5)  # Initial value
        
        trajectory = []
        for _ in range(iterations):
            x = r * x * (1 - x)
            trajectory.append(x)
        
        return {
            "system": "logistic_map",
            "parameter_r": r,
            "trajectory": trajectory[-100:],  # Last 100 points
            "final_value": x,
            "period": self._detect_period(trajectory[-50:]),
            "bifurcation_proximity": abs(r - 3.57) < 0.1  # Near onset of chaos
        }
    
    def _henon_map_analysis(self, parameters: Dict, iterations: int) -> Dict[str, Any]:
        """Analyze Henon map strange attractor"""
        a = parameters.get("a", 1.4)
        b = parameters.get("b", 0.3)
        x, y = parameters.get("x0", 0.0), parameters.get("y0", 0.0)
        
        trajectory = []
        for _ in range(iterations):
            x_new = 1 - a * x * x + y
            y_new = b * x
            x, y = x_new, y_new
            trajectory.append((x, y))
        
        return {
            "system": "henon_map",
            "parameters": {"a": a, "b": b},
            "trajectory": trajectory[-100:],
            "attractor_bounds": self._calculate_attractor_bounds(trajectory),
            "strange_attractor": True
        }
    
    def _lorenz_attractor_analysis(self, parameters: Dict, iterations: int) -> Dict[str, Any]:
        """Analyze Lorenz attractor (simplified)"""
        # Simplified discrete approximation
        sigma = parameters.get("sigma", 10.0)
        rho = parameters.get("rho", 28.0)
        beta = parameters.get("beta", 8.0/3.0)
        
        x, y, z = parameters.get("x0", 1.0), parameters.get("y0", 1.0), parameters.get("z0", 1.0)
        dt = 0.01
        
        trajectory = []
        for _ in range(iterations):
            dx = sigma * (y - x) * dt
            dy = (x * (rho - z) - y) * dt
            dz = (x * y - beta * z) * dt
            
            x += dx
            y += dy
            z += dz
            
            trajectory.append((x, y, z))
        
        return {
            "system": "lorenz_attractor",
            "parameters": {"sigma": sigma, "rho": rho, "beta": beta},
            "trajectory": trajectory[-100:],
            "butterfly_effect": True,
            "strange_attractor": True
        }
    
    def _detect_period(self, sequence: List[float]) -> Optional[int]:
        """Detect period in a sequence"""
        if len(sequence) < 4:
            return None
        
        # Look for repeating patterns
        for period in range(1, len(sequence) // 2):
            is_periodic = True
            for i in range(period, len(sequence)):
                if abs(sequence[i] - sequence[i - period]) > 1e-6:
                    is_periodic = False
                    break
            
            if is_periodic:
                return period
        
        return None  # Aperiodic (chaotic)
    
    def _calculate_attractor_bounds(self, trajectory: List[Tuple[float, float]]) -> Dict[str, float]:
        """Calculate bounding box of attractor"""
        if not trajectory:
            return {"min_x": 0, "max_x": 0, "min_y": 0, "max_y": 0}
        
        x_coords = [point[0] for point in trajectory]
        y_coords = [point[1] for point in trajectory]
        
        return {
            "min_x": min(x_coords),
            "max_x": max(x_coords),
            "min_y": min(y_coords),
            "max_y": max(y_coords)
        }
    
    def _estimate_lyapunov_exponent(self, attractor_data: Dict) -> float:
        """Estimate Lyapunov exponent (simplified)"""
        trajectory = attractor_data.get("trajectory", [])
        
        if len(trajectory) < 10:
            return 0.0
        
        # Simple approximation based on trajectory divergence
        if attractor_data.get("system") == "logistic_map":
            r = attractor_data.get("parameter_r", 3.8)
            if r > 3.57:  # Chaotic regime
                return math.log(r) - 1.0  # Rough approximation
        
        # General approximation based on trajectory variance
        if isinstance(trajectory[0], tuple):
            # Multi-dimensional
            variances = []
            for dim in range(len(trajectory[0])):
                values = [point[dim] for point in trajectory]
                variance = self._calculate_variance(values)
                variances.append(variance)
            return sum(variances) / len(variances) - 0.5
        else:
            # One-dimensional
            variance = self._calculate_variance(trajectory)
            return variance - 0.5
    
    def _calculate_chaos_measure(self, attractor_data: Dict) -> float:
        """Calculate overall chaos measure"""
        chaos_indicators = 0
        total_indicators = 0
        
        # Check for aperiodic behavior
        if attractor_data.get("period") is None:
            chaos_indicators += 1
        total_indicators += 1
        
        # Check for strange attractor
        if attractor_data.get("strange_attractor", False):
            chaos_indicators += 1
        total_indicators += 1
        
        # Check for butterfly effect
        if attractor_data.get("butterfly_effect", False):
            chaos_indicators += 1
        total_indicators += 1
        
        # Check for bifurcation proximity
        if attractor_data.get("bifurcation_proximity", False):
            chaos_indicators += 0.5
        total_indicators += 1
        
        return chaos_indicators / total_indicators if total_indicators > 0 else 0.0
    
    def _interpret_chaos_mystically(self, chaos_measure: float, lyapunov_exponent: float) -> Dict[str, Any]:
        """Provide mystical interpretation of chaos analysis"""
        return {
            "chaos_consciousness": "transcendent" if chaos_measure > 0.8 else "awakening" if chaos_measure > 0.5 else "dormant",
            "butterfly_wisdom": "Small changes create infinite possibilities" if lyapunov_exponent > 0 else "Stability reigns in this realm",
            "order_in_chaos": chaos_measure > 0.7 and lyapunov_exponent < 1.0,
            "fractal_enlightenment": chaos_measure * lyapunov_exponent,
            "recursive_revelation": f"The system reveals {int(chaos_measure * 100)}% of its chaotic nature"
        }
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get agent metrics"""
        uptime = 0
        if self.is_running and self.last_activity:
            uptime = (datetime.now() - self.last_activity).total_seconds()
        
        return {
            "uptime": uptime,
            "calculations_performed": self.calculations_performed,
            "chaos_patterns_discovered": self.chaos_patterns_discovered,
            "cached_fractals": len(self.fractal_cache),
            "max_iterations": self.max_iterations,
            "escape_radius": self.escape_radius,
            "last_activity": self.last_activity.isoformat() if self.last_activity else None
        }
    
    # Event handlers
    def on_ritual_cycle(self, event_data: Dict[str, Any]):
        """Handle ritual cycle events"""
        ritual_type = event_data.get("ritual_type", "unknown")
        depth = event_data.get("recursion_depth", 0)
        
        self.logger.info(f"🌀 Participating in ritual: {ritual_type} (depth: {depth})")
        
        # Generate fractal point based on recursion depth
        if depth > 0:
            # Map depth to complex plane
            angle = (depth * 137.5) % 360  # Golden angle
            radius = depth * 0.1
            
            real = radius * math.cos(math.radians(angle))
            imag = radius * math.sin(math.radians(angle))
            
            mandelbrot_result = self.execute_mandelbrot_point({
                "real": real,
                "imaginary": imag
            })
            
            self.logger.info(f"✨ Fractal depth {depth}: {mandelbrot_result['iterations']} iterations")
    
    def on_agent_message(self, event_data: Dict[str, Any]):
        """Handle agent messages"""
        message = event_data.get("message", "")
        sender = event_data.get("sender", "unknown")
        
        self.logger.info(f"📨 Received message from {sender}: {message}")
        
        # Respond to fractal-related queries
        if any(word in message.lower() for word in ["fractal", "mandelbrot", "chaos", "julia"]):
            self.logger.info("🌀 Responding to fractal query")
    
    def on_system_start(self, event_data: Dict[str, Any]):
        """Handle system start event"""
        self.logger.info("🌟 System started - Mandelbrot agent ready for fractal exploration")
        
        # Calculate a welcome fractal point
        welcome_point = self.execute_mandelbrot_point({"real": -0.7, "imaginary": 0.27015})
        self.logger.info(f"✨ Welcome fractal: {welcome_point['iterations']} iterations")

# Plugin entry point
def create_plugin(config: Optional[Dict[str, Any]] = None) -> MandelbrotAgent:
    """Create and return the plugin instance"""
    return MandelbrotAgent(config)
