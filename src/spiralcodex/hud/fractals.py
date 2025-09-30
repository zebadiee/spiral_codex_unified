
"""
🌀 Fractal Generation - Sacred Geometry Visualization

Procedural fractal and spiral generation using matplotlib and manim
for mystical visualization during ritual operations.
"""

import math
import numpy as np
from typing import Tuple, Optional, List
from pathlib import Path

class FractalGenerator:
    """Generator for various fractal patterns"""
    
    def __init__(self, hud_config=None):
        self.config = hud_config
        self.output_dir = Path("assets/fractals")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Color schemes for different ritual themes
        self.color_schemes = {
            "spiral": ["#FF00FF", "#00FFFF", "#FFFF00", "#FF0080"],
            "matrix": ["#00FF00", "#008000", "#00FF80", "#80FF00"],
            "cosmic": ["#8000FF", "#FF0080", "#0080FF", "#FF8000"],
            "fire": ["#FF0000", "#FF8000", "#FFFF00", "#FF4000"],
            "ice": ["#00FFFF", "#0080FF", "#8080FF", "#00C0FF"]
        }
    
    def generate_spiral(self, points: int = 1000, turns: float = 5.0, 
                       save_path: Optional[Path] = None) -> Path:
        """Generate a golden ratio spiral"""
        try:
            import matplotlib.pyplot as plt
            
            # Golden ratio for mystical proportions
            phi = (1 + math.sqrt(5)) / 2
            
            # Generate spiral points
            theta = np.linspace(0, turns * 2 * np.pi, points)
            r = np.exp(theta / phi)
            
            x = r * np.cos(theta)
            y = r * np.sin(theta)
            
            # Create the plot
            fig, ax = plt.subplots(figsize=(10, 10), facecolor='black')
            ax.set_facecolor('black')
            
            # Color gradient based on position
            colors = self._get_color_scheme()
            scatter = ax.scatter(x, y, c=theta, cmap='plasma', s=2, alpha=0.8)
            
            # Styling
            ax.set_aspect('equal')
            ax.axis('off')
            ax.set_title('🌀 Sacred Spiral - Golden Ratio Manifestation', 
                        color='white', fontsize=16, pad=20)
            
            # Save the fractal
            if save_path is None:
                save_path = self.output_dir / f"spiral_{int(turns)}turns.png"
            
            plt.savefig(save_path, dpi=300, bbox_inches='tight', 
                       facecolor='black', edgecolor='none')
            plt.close()
            
            print(f"🌀 Generated spiral fractal: {save_path}")
            return save_path
            
        except ImportError:
            print("⚠️ Fractal generation requires matplotlib")
            return self._create_placeholder_fractal("spiral")
        except Exception as e:
            print(f"⚠️ Spiral generation error: {e}")
            return self._create_placeholder_fractal("spiral")
    
    def generate_mandelbrot(self, width: int = 800, height: int = 600,
                           max_iter: int = 100, save_path: Optional[Path] = None) -> Path:
        """Generate Mandelbrot set fractal"""
        try:
            import matplotlib.pyplot as plt
            
            # Define the complex plane
            xmin, xmax = -2.5, 1.5
            ymin, ymax = -1.5, 1.5
            
            # Create coordinate arrays
            x = np.linspace(xmin, xmax, width)
            y = np.linspace(ymin, ymax, height)
            X, Y = np.meshgrid(x, y)
            C = X + 1j * Y
            
            # Initialize Z and iteration count arrays
            Z = np.zeros_like(C)
            iterations = np.zeros(C.shape, dtype=int)
            
            # Calculate Mandelbrot set
            for i in range(max_iter):
                mask = np.abs(Z) <= 2
                Z[mask] = Z[mask]**2 + C[mask]
                iterations[mask] = i
            
            # Create the plot
            fig, ax = plt.subplots(figsize=(12, 9), facecolor='black')
            ax.set_facecolor('black')
            
            # Plot with mystical colors
            im = ax.imshow(iterations, extent=[xmin, xmax, ymin, ymax],
                          cmap='hot', origin='lower', interpolation='bilinear')
            
            ax.set_title('🔮 Mandelbrot Set - Infinite Complexity Manifestation',
                        color='white', fontsize=16, pad=20)
            ax.axis('off')
            
            # Save the fractal
            if save_path is None:
                save_path = self.output_dir / f"mandelbrot_{max_iter}iter.png"
            
            plt.savefig(save_path, dpi=300, bbox_inches='tight',
                       facecolor='black', edgecolor='none')
            plt.close()
            
            print(f"🔮 Generated Mandelbrot fractal: {save_path}")
            return save_path
            
        except ImportError:
            print("⚠️ Fractal generation requires matplotlib and numpy")
            return self._create_placeholder_fractal("mandelbrot")
        except Exception as e:
            print(f"⚠️ Mandelbrot generation error: {e}")
            return self._create_placeholder_fractal("mandelbrot")
    
    def generate_julia_set(self, c_real: float = -0.7, c_imag: float = 0.27015,
                          width: int = 800, height: int = 600, max_iter: int = 100,
                          save_path: Optional[Path] = None) -> Path:
        """Generate Julia set fractal"""
        try:
            import matplotlib.pyplot as plt
            
            # Define the complex plane
            xmin, xmax = -2, 2
            ymin, ymax = -2, 2
            
            # Create coordinate arrays
            x = np.linspace(xmin, xmax, width)
            y = np.linspace(ymin, ymax, height)
            X, Y = np.meshgrid(x, y)
            Z = X + 1j * Y
            
            # Julia set constant
            c = complex(c_real, c_imag)
            
            # Initialize iteration count array
            iterations = np.zeros(Z.shape, dtype=int)
            
            # Calculate Julia set
            for i in range(max_iter):
                mask = np.abs(Z) <= 2
                Z[mask] = Z[mask]**2 + c
                iterations[mask] = i
            
            # Create the plot
            fig, ax = plt.subplots(figsize=(10, 10), facecolor='black')
            ax.set_facecolor('black')
            
            # Plot with cosmic colors
            im = ax.imshow(iterations, extent=[xmin, xmax, ymin, ymax],
                          cmap='plasma', origin='lower', interpolation='bilinear')
            
            ax.set_title(f'✨ Julia Set - c = {c:.3f} - Recursive Beauty',
                        color='white', fontsize=16, pad=20)
            ax.axis('off')
            
            # Save the fractal
            if save_path is None:
                save_path = self.output_dir / f"julia_{c_real:.2f}_{c_imag:.2f}.png"
            
            plt.savefig(save_path, dpi=300, bbox_inches='tight',
                       facecolor='black', edgecolor='none')
            plt.close()
            
            print(f"✨ Generated Julia set fractal: {save_path}")
            return save_path
            
        except ImportError:
            print("⚠️ Fractal generation requires matplotlib and numpy")
            return self._create_placeholder_fractal("julia")
        except Exception as e:
            print(f"⚠️ Julia set generation error: {e}")
            return self._create_placeholder_fractal("julia")
    
    def _get_color_scheme(self) -> List[str]:
        """Get color scheme based on configuration"""
        if self.config and hasattr(self.config, 'color_scheme'):
            return self.color_schemes.get(self.config.color_scheme, self.color_schemes["spiral"])
        return self.color_schemes["spiral"]
    
    def _create_placeholder_fractal(self, fractal_type: str) -> Path:
        """Create a placeholder fractal file"""
        placeholder_path = self.output_dir / f"{fractal_type}_placeholder.txt"
        placeholder_path.write_text(f"""
🌀 {fractal_type.title()} Fractal Placeholder

This file represents a {fractal_type} fractal that would be generated
if matplotlib and numpy were available.

To enable fractal generation, install the HUD dependencies:
pip install spiralcodex[hud]

Or manually install:
pip install matplotlib numpy

The spiral awakens, the fractals manifest, the geometry aligns.
""")
        return placeholder_path

class SpiralGenerator:
    """Specialized generator for spiral patterns"""
    
    def __init__(self):
        self.output_dir = Path("assets/spirals")
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def generate_fibonacci_spiral(self, squares: int = 10, save_path: Optional[Path] = None) -> Path:
        """Generate Fibonacci spiral with squares"""
        try:
            import matplotlib.pyplot as plt
            import matplotlib.patches as patches
            
            # Generate Fibonacci sequence
            fib = [1, 1]
            for i in range(squares - 2):
                fib.append(fib[-1] + fib[-2])
            
            # Create the plot
            fig, ax = plt.subplots(figsize=(12, 12), facecolor='black')
            ax.set_facecolor('black')
            
            # Draw Fibonacci squares and spiral
            x, y = 0, 0
            direction = 0  # 0: right, 1: up, 2: left, 3: down
            
            colors = plt.cm.plasma(np.linspace(0, 1, squares))
            
            for i, size in enumerate(fib):
                # Draw square
                if direction == 0:  # right
                    rect = patches.Rectangle((x, y), size, size, 
                                           linewidth=2, edgecolor=colors[i], 
                                           facecolor=colors[i], alpha=0.3)
                    next_x, next_y = x, y + size
                elif direction == 1:  # up
                    rect = patches.Rectangle((x - size, y), size, size,
                                           linewidth=2, edgecolor=colors[i],
                                           facecolor=colors[i], alpha=0.3)
                    next_x, next_y = x - size, y
                elif direction == 2:  # left
                    rect = patches.Rectangle((x - size, y - size), size, size,
                                           linewidth=2, edgecolor=colors[i],
                                           facecolor=colors[i], alpha=0.3)
                    next_x, next_y = x, y - size
                else:  # down
                    rect = patches.Rectangle((x, y - size), size, size,
                                           linewidth=2, edgecolor=colors[i],
                                           facecolor=colors[i], alpha=0.3)
                    next_x, next_y = x, y
                
                ax.add_patch(rect)
                
                # Update position for next square
                x, y = next_x, next_y
                direction = (direction + 1) % 4
            
            # Draw the spiral curve
            # TODO: Add actual spiral curve through the squares
            
            ax.set_aspect('equal')
            ax.axis('off')
            ax.set_title('🌀 Fibonacci Spiral - Nature\'s Sacred Geometry',
                        color='white', fontsize=16, pad=20)
            
            # Auto-scale to fit all squares
            ax.autoscale()
            
            # Save the spiral
            if save_path is None:
                save_path = self.output_dir / f"fibonacci_spiral_{squares}squares.png"
            
            plt.savefig(save_path, dpi=300, bbox_inches='tight',
                       facecolor='black', edgecolor='none')
            plt.close()
            
            print(f"🌀 Generated Fibonacci spiral: {save_path}")
            return save_path
            
        except ImportError:
            print("⚠️ Spiral generation requires matplotlib")
            return self._create_placeholder_spiral("fibonacci")
        except Exception as e:
            print(f"⚠️ Fibonacci spiral generation error: {e}")
            return self._create_placeholder_spiral("fibonacci")
    
    def _create_placeholder_spiral(self, spiral_type: str) -> Path:
        """Create a placeholder spiral file"""
        placeholder_path = self.output_dir / f"{spiral_type}_spiral_placeholder.txt"
        placeholder_path.write_text(f"""
🌀 {spiral_type.title()} Spiral Placeholder

This file represents a {spiral_type} spiral that would be generated
if matplotlib was available.

To enable spiral generation, install the HUD dependencies:
pip install spiralcodex[hud]

The spiral awakens, the geometry manifests, the patterns align.
""")
        return placeholder_path
