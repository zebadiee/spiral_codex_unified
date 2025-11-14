
"""
Spiral Codex V2 - Multimodal Integration Module

This module implements multimodal processing capabilities:
- Vision Processing: Image analysis, object detection, scene understanding
- Audio Processing: Speech recognition, music analysis, ambient sound processing
- Sensor Integration: IoT sensor data, environmental monitoring, biometric data
- Cross-Modal Reasoning: Fusion and synthesis across modalities
"""

from .vision_processor import VisionProcessor
from .audio_processor import AudioProcessor
from .sensor_integrator import SensorIntegrator
from .multimodal_processor import MultimodalProcessor
from .cross_modal_fusion import CrossModalFusion

__all__ = [
    'VisionProcessor',
    'AudioProcessor',
    'SensorIntegrator',
    'MultimodalProcessor',
    'CrossModalFusion'
]
