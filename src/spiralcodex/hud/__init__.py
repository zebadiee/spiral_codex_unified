
"""
🎮 Spiral Codex HUD - Head-Up Display System

Mystical visualization system for monitoring agent states, recursion depth,
and entropy levels with ritual-themed overlays and fractal generation.
"""

from .core import HUDCore, HUDConfig
from .overlays import LiveOverlay, AgentCountOverlay, RecursionDepthOverlay, ConfigStateOverlay
from .fractals import FractalGenerator, SpiralGenerator
from .ritual import RitualVisualizer, RitualAudio

__all__ = [
    "HUDCore",
    "HUDConfig", 
    "LiveOverlay",
    "AgentCountOverlay",
    "RecursionDepthOverlay",
    "ConfigStateOverlay",
    "FractalGenerator",
    "SpiralGenerator",
    "RitualVisualizer",
    "RitualAudio"
]

# HUD availability check
HUD_AVAILABLE = False
MPV_AVAILABLE = False

try:
    import mpv
    MPV_AVAILABLE = True
    HUD_AVAILABLE = True
except ImportError:
    pass

try:
    import matplotlib.pyplot as plt
    import numpy as np
    HUD_AVAILABLE = True
except ImportError:
    pass

def check_hud_dependencies():
    """Check if HUD dependencies are available"""
    missing = []
    
    if not MPV_AVAILABLE:
        missing.append("python-mpv")
    
    try:
        import matplotlib
    except ImportError:
        missing.append("matplotlib")
    
    try:
        import numpy
    except ImportError:
        missing.append("numpy")
    
    return len(missing) == 0, missing
