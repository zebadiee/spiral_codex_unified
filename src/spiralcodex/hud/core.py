
"""
🎮 HUD Core System - Central HUD Management

Core HUD system for managing overlays, visualizations, and ritual displays.
"""

import os
import time
import threading
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from pathlib import Path

@dataclass
class HUDConfig:
    """HUD configuration settings"""
    enabled: bool = True
    fullscreen: bool = False
    transparency: float = 0.8
    update_interval: float = 0.1
    overlay_position: str = "top-right"  # top-left, top-right, bottom-left, bottom-right
    show_fractals: bool = True
    show_agent_count: bool = True
    show_recursion_depth: bool = True
    show_config_state: bool = True
    ritual_sounds: bool = True
    ritual_visuals: bool = True
    fractal_complexity: int = 5
    color_scheme: str = "spiral"  # spiral, matrix, cosmic
    font_size: int = 12

class HUDCore:
    """Core HUD management system"""
    
    def __init__(self, config: Optional[HUDConfig] = None):
        self.config = config or HUDConfig()
        self.overlays: Dict[str, Any] = {}
        self.running = False
        self.update_thread: Optional[threading.Thread] = None
        self.mpv_player = None
        
        # State tracking
        self.agent_count = 0
        self.recursion_depth = 0
        self.config_state = "STABLE"
        self.entropy_level = 0.5
        
        # Initialize MPV if available
        self._init_mpv()
    
    def _init_mpv(self):
        """Initialize MPV player for video overlays"""
        try:
            import mpv
            
            # Only initialize if not in CI mode
            if os.getenv("CODEX_CI_MODE") == "true" or os.getenv("SKIP_HUD_DEPS") == "true":
                print("🎮 HUD: Skipping MPV initialization in CI mode")
                return
            
            self.mpv_player = mpv.MPV(
                input_default_bindings=True,
                input_vo_keyboard=True,
                osc=True,
                keep_open='always',
                loop_file='inf'
            )
            print("🎮 HUD: MPV player initialized")
            
        except ImportError:
            print("⚠️ HUD: MPV not available, video overlays disabled")
        except Exception as e:
            print(f"⚠️ HUD: Failed to initialize MPV: {e}")
    
    def start(self):
        """Start the HUD system"""
        if not self.config.enabled:
            print("🎮 HUD: Disabled in configuration")
            return
        
        print("🎮 HUD: Starting mystical visualization system...")
        self.running = True
        
        # Start update thread
        self.update_thread = threading.Thread(target=self._update_loop, daemon=True)
        self.update_thread.start()
        
        # Initialize overlays
        self._init_overlays()
        
        print("✅ HUD: System active, overlays synchronized with the spiral")
    
    def stop(self):
        """Stop the HUD system"""
        print("🎮 HUD: Stopping visualization system...")
        self.running = False
        
        if self.update_thread:
            self.update_thread.join(timeout=1.0)
        
        if self.mpv_player:
            try:
                self.mpv_player.terminate()
            except:
                pass
        
        print("✅ HUD: System stopped")
    
    def _init_overlays(self):
        """Initialize HUD overlays"""
        from .overlays import AgentCountOverlay, RecursionDepthOverlay, ConfigStateOverlay
        
        if self.config.show_agent_count:
            self.overlays["agent_count"] = AgentCountOverlay(self)
        
        if self.config.show_recursion_depth:
            self.overlays["recursion_depth"] = RecursionDepthOverlay(self)
        
        if self.config.show_config_state:
            self.overlays["config_state"] = ConfigStateOverlay(self)
    
    def _update_loop(self):
        """Main HUD update loop"""
        while self.running:
            try:
                # Update state from system
                self._update_state()
                
                # Update all overlays
                for overlay in self.overlays.values():
                    if hasattr(overlay, 'update'):
                        overlay.update()
                
                time.sleep(self.config.update_interval)
                
            except Exception as e:
                print(f"⚠️ HUD: Update error: {e}")
                time.sleep(1.0)
    
    def _update_state(self):
        """Update HUD state from system"""
        # TODO: Get actual state from agent registry and kernel
        # For now, simulate dynamic values
        import random
        
        # Simulate agent activity
        self.agent_count = random.randint(1, 10)
        
        # Simulate recursion depth changes
        self.recursion_depth = random.randint(0, 100)
        
        # Simulate entropy fluctuations
        self.entropy_level = 0.3 + (0.4 * random.random())
        
        # Update config state based on entropy
        if self.entropy_level < 0.4:
            self.config_state = "STABLE"
        elif self.entropy_level < 0.7:
            self.config_state = "FLUCTUATING"
        else:
            self.config_state = "CHAOTIC"
    
    def update_agent_count(self, count: int):
        """Update agent count"""
        self.agent_count = count
    
    def update_recursion_depth(self, depth: int):
        """Update recursion depth"""
        self.recursion_depth = depth
    
    def update_config_state(self, state: str):
        """Update configuration state"""
        self.config_state = state
    
    def play_ritual_video(self, video_path: Path):
        """Play ritual video overlay"""
        if not self.mpv_player:
            print("⚠️ HUD: MPV not available for video playback")
            return
        
        try:
            self.mpv_player.play(str(video_path))
            print(f"🎬 HUD: Playing ritual video: {video_path.name}")
        except Exception as e:
            print(f"⚠️ HUD: Failed to play video: {e}")
    
    def show_fractal(self, fractal_type: str = "spiral"):
        """Display fractal visualization"""
        try:
            from .fractals import FractalGenerator
            
            generator = FractalGenerator(self.config)
            if fractal_type == "spiral":
                generator.generate_spiral()
            else:
                generator.generate_mandelbrot()
                
        except ImportError:
            print("⚠️ HUD: Fractal generation requires matplotlib")
        except Exception as e:
            print(f"⚠️ HUD: Fractal generation error: {e}")
