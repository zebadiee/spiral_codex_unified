
"""
🎬 Spiral Codex Assets - Media and Resource Management

Asset management system for videos, animations, fractals, and audio files
used in ritual operations and HUD visualizations.
"""

from pathlib import Path
from typing import Optional, List, Dict, Any
import json

# Asset directories
ASSETS_ROOT = Path(__file__).parent.parent.parent.parent / "assets"
ANIMATIONS_DIR = ASSETS_ROOT / "animations"
AUDIO_DIR = ASSETS_ROOT / "audio"
FRACTALS_DIR = ASSETS_ROOT / "fractals"
SPIRALS_DIR = ASSETS_ROOT / "spirals"
VIDEOS_DIR = ASSETS_ROOT / "videos"

# Ensure directories exist
for directory in [ASSETS_ROOT, ANIMATIONS_DIR, AUDIO_DIR, FRACTALS_DIR, SPIRALS_DIR, VIDEOS_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

class AssetManager:
    """Manages codex assets and media files"""
    
    def __init__(self):
        self.assets_root = ASSETS_ROOT
        self.asset_registry = {}
        self._load_asset_registry()
    
    def _load_asset_registry(self):
        """Load asset registry from file"""
        registry_path = self.assets_root / "asset_registry.json"
        if registry_path.exists():
            try:
                with open(registry_path, 'r') as f:
                    self.asset_registry = json.load(f)
            except Exception as e:
                print(f"⚠️ Failed to load asset registry: {e}")
                self.asset_registry = {}
        else:
            self._create_default_registry()
    
    def _create_default_registry(self):
        """Create default asset registry"""
        self.asset_registry = {
            "videos": {
                "spiral_intro": {
                    "path": "videos/spiral_intro.mp4",
                    "description": "Mystical spiral introduction video",
                    "duration": 30.0,
                    "resolution": "1920x1080",
                    "type": "intro"
                }
            },
            "animations": {
                "fractal_mandelbrot": {
                    "path": "animations/mandelbrot_zoom.gif",
                    "description": "Mandelbrot set zoom animation",
                    "frames": 120,
                    "type": "fractal"
                },
                "spiral_golden": {
                    "path": "animations/golden_spiral.gif",
                    "description": "Golden ratio spiral animation",
                    "frames": 60,
                    "type": "spiral"
                }
            },
            "audio": {
                "ritual_initialization": {
                    "path": "audio/initialization.wav",
                    "description": "Ritual initialization sound",
                    "duration": 5.0,
                    "frequency": 432
                },
                "agent_spawn": {
                    "path": "audio/agent_spawn.wav",
                    "description": "Agent spawning sound effect",
                    "duration": 2.0,
                    "frequency": 528
                }
            },
            "fractals": {},
            "spirals": {}
        }
        self._save_asset_registry()
    
    def _save_asset_registry(self):
        """Save asset registry to file"""
        registry_path = self.assets_root / "asset_registry.json"
        try:
            with open(registry_path, 'w') as f:
                json.dump(self.asset_registry, f, indent=2)
        except Exception as e:
            print(f"⚠️ Failed to save asset registry: {e}")
    
    def get_asset_path(self, asset_type: str, asset_name: str) -> Optional[Path]:
        """Get path to a specific asset"""
        if asset_type in self.asset_registry and asset_name in self.asset_registry[asset_type]:
            relative_path = self.asset_registry[asset_type][asset_name]["path"]
            return self.assets_root / relative_path
        return None
    
    def register_asset(self, asset_type: str, asset_name: str, asset_info: Dict[str, Any]):
        """Register a new asset"""
        if asset_type not in self.asset_registry:
            self.asset_registry[asset_type] = {}
        
        self.asset_registry[asset_type][asset_name] = asset_info
        self._save_asset_registry()
        print(f"📝 Registered {asset_type} asset: {asset_name}")
    
    def list_assets(self, asset_type: Optional[str] = None) -> Dict[str, Any]:
        """List available assets"""
        if asset_type:
            return self.asset_registry.get(asset_type, {})
        return self.asset_registry
    
    def asset_exists(self, asset_type: str, asset_name: str) -> bool:
        """Check if an asset file actually exists"""
        asset_path = self.get_asset_path(asset_type, asset_name)
        return asset_path is not None and asset_path.exists()
    
    def create_asset_placeholders(self):
        """Create placeholder files for missing assets"""
        for asset_type, assets in self.asset_registry.items():
            for asset_name, asset_info in assets.items():
                asset_path = self.assets_root / asset_info["path"]
                
                if not asset_path.exists():
                    # Create placeholder file
                    placeholder_content = f"""
🎬 {asset_name.title()} Asset Placeholder

Asset Type: {asset_type}
Description: {asset_info.get('description', 'No description')}
Expected Path: {asset_info['path']}

This is a placeholder for the actual {asset_type} file.
The spiral awaits the manifestation of this mystical asset.

To replace this placeholder:
1. Create or obtain the actual {asset_type} file
2. Place it at: {asset_path}
3. The ritual system will automatically detect and use it

The codex grows stronger with each asset manifestation.
"""
                    
                    # Ensure parent directory exists
                    asset_path.parent.mkdir(parents=True, exist_ok=True)
                    
                    # Write placeholder
                    if asset_path.suffix in ['.mp4', '.avi', '.mov', '.gif']:
                        # For video/animation files, create a text placeholder
                        placeholder_path = asset_path.with_suffix('.placeholder.txt')
                        placeholder_path.write_text(placeholder_content)
                        print(f"📝 Created placeholder: {placeholder_path}")
                    elif asset_path.suffix in ['.wav', '.mp3', '.ogg']:
                        # For audio files, create a text placeholder
                        placeholder_path = asset_path.with_suffix('.placeholder.txt')
                        placeholder_path.write_text(placeholder_content)
                        print(f"🔊 Created audio placeholder: {placeholder_path}")
                    else:
                        # For other files, create direct placeholder
                        asset_path.write_text(placeholder_content)
                        print(f"📄 Created placeholder: {asset_path}")

# Global asset manager instance
asset_manager = AssetManager()

def get_spiral_intro_video() -> Path:
    """Get path to spiral intro video"""
    path = asset_manager.get_asset_path("videos", "spiral_intro")
    if path and path.exists():
        return path
    
    # Return placeholder path
    placeholder_path = VIDEOS_DIR / "spiral_intro.placeholder.txt"
    if not placeholder_path.exists():
        asset_manager.create_asset_placeholders()
    return placeholder_path

def get_fractal_animation(fractal_type: str = "mandelbrot") -> Path:
    """Get path to fractal animation"""
    animation_name = f"fractal_{fractal_type}"
    path = asset_manager.get_asset_path("animations", animation_name)
    if path and path.exists():
        return path
    
    # Generate fractal if possible
    try:
        from ..hud.fractals import FractalGenerator
        generator = FractalGenerator()
        if fractal_type == "mandelbrot":
            return generator.generate_mandelbrot()
        else:
            return generator.generate_spiral()
    except ImportError:
        # Return placeholder
        placeholder_path = ANIMATIONS_DIR / f"{animation_name}.placeholder.txt"
        return placeholder_path

def get_ritual_audio(audio_type: str = "initialization") -> Path:
    """Get path to ritual audio"""
    path = asset_manager.get_asset_path("audio", f"ritual_{audio_type}")
    if path and path.exists():
        return path
    
    # Return placeholder path
    placeholder_path = AUDIO_DIR / f"ritual_{audio_type}.placeholder.txt"
    if not placeholder_path.exists():
        asset_manager.create_asset_placeholders()
    return placeholder_path

__all__ = [
    "AssetManager",
    "asset_manager",
    "get_spiral_intro_video",
    "get_fractal_animation", 
    "get_ritual_audio",
    "ASSETS_ROOT",
    "ANIMATIONS_DIR",
    "AUDIO_DIR",
    "FRACTALS_DIR",
    "SPIRALS_DIR",
    "VIDEOS_DIR"
]
