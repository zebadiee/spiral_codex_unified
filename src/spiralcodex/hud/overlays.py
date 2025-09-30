
"""
🎯 HUD Overlays - Live Information Display

Live overlay system for displaying real-time agent counts, recursion depth,
configuration states, and other mystical metrics.
"""

import time
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

class LiveOverlay(ABC):
    """Base class for live HUD overlays"""
    
    def __init__(self, hud_core, name: str):
        self.hud_core = hud_core
        self.name = name
        self.last_update = 0
        self.visible = True
        self.position = (10, 10)  # x, y coordinates
        self.color = "#00FF00"  # Default green
    
    @abstractmethod
    def render(self) -> str:
        """Render overlay content"""
        pass
    
    def update(self):
        """Update overlay if needed"""
        current_time = time.time()
        if current_time - self.last_update >= self.hud_core.config.update_interval:
            self.last_update = current_time
            if self.visible:
                content = self.render()
                self._display(content)
    
    def _display(self, content: str):
        """Display overlay content (placeholder for actual rendering)"""
        # In a real implementation, this would render to screen
        # For now, we'll just print to console in debug mode
        if hasattr(self.hud_core.config, 'debug') and self.hud_core.config.debug:
            print(f"🎯 {self.name}: {content}")
    
    def show(self):
        """Show overlay"""
        self.visible = True
    
    def hide(self):
        """Hide overlay"""
        self.visible = False

class AgentCountOverlay(LiveOverlay):
    """Overlay showing active agent count"""
    
    def __init__(self, hud_core):
        super().__init__(hud_core, "Agent Count")
        self.color = "#00FFFF"  # Cyan
        self.position = (10, 10)
    
    def render(self) -> str:
        """Render agent count display"""
        count = self.hud_core.agent_count
        
        # Add visual indicators based on count
        if count == 0:
            status = "🔴 DORMANT"
            color = "#FF0000"
        elif count <= 3:
            status = "🟡 ACTIVE"
            color = "#FFFF00"
        elif count <= 7:
            status = "🟢 SYNCHRONIZED"
            color = "#00FF00"
        else:
            status = "🔵 SWARM MODE"
            color = "#0080FF"
        
        self.color = color
        return f"🤖 Agents: {count} {status}"

class RecursionDepthOverlay(LiveOverlay):
    """Overlay showing kernel recursion depth"""
    
    def __init__(self, hud_core):
        super().__init__(hud_core, "Recursion Depth")
        self.color = "#FF00FF"  # Magenta
        self.position = (10, 40)
        self.max_depth_seen = 0
    
    def render(self) -> str:
        """Render recursion depth display"""
        depth = self.hud_core.recursion_depth
        self.max_depth_seen = max(self.max_depth_seen, depth)
        
        # Visual representation of depth
        if depth == 0:
            status = "🌱 SURFACE"
            bar = ""
        elif depth < 10:
            status = "🌿 SHALLOW"
            bar = "▓" * (depth // 2)
        elif depth < 50:
            status = "🌳 DEEP"
            bar = "▓" * 10 + "░" * ((depth - 10) // 4)
        elif depth < 100:
            status = "🌀 SPIRAL"
            bar = "▓" * 15 + "▒" * ((depth - 50) // 5)
        else:
            status = "♾️ INFINITE"
            bar = "█" * 20
        
        return f"🧬 Depth: {depth} {status} [{bar}] Max: {self.max_depth_seen}"

class ConfigStateOverlay(LiveOverlay):
    """Overlay showing configuration and entropy state"""
    
    def __init__(self, hud_core):
        super().__init__(hud_core, "Config State")
        self.color = "#FFFF00"  # Yellow
        self.position = (10, 70)
    
    def render(self) -> str:
        """Render configuration state display"""
        state = self.hud_core.config_state
        entropy = self.hud_core.entropy_level
        
        # State-based coloring and icons
        state_info = {
            "STABLE": ("🟢", "#00FF00", "All systems nominal"),
            "FLUCTUATING": ("🟡", "#FFFF00", "Minor variations detected"),
            "CHAOTIC": ("🔴", "#FF0000", "High entropy - caution advised"),
            "UNKNOWN": ("⚪", "#FFFFFF", "State indeterminate")
        }
        
        icon, color, description = state_info.get(state, state_info["UNKNOWN"])
        self.color = color
        
        # Entropy bar visualization
        entropy_bars = int(entropy * 20)
        entropy_display = "█" * entropy_bars + "░" * (20 - entropy_bars)
        
        return f"⚡ State: {icon} {state} | Entropy: {entropy:.2f} [{entropy_display}]"

class SystemMetricsOverlay(LiveOverlay):
    """Overlay showing system performance metrics"""
    
    def __init__(self, hud_core):
        super().__init__(hud_core, "System Metrics")
        self.color = "#80FF80"  # Light green
        self.position = (10, 100)
    
    def render(self) -> str:
        """Render system metrics"""
        # TODO: Get actual system metrics
        import psutil
        
        try:
            cpu_percent = psutil.cpu_percent(interval=None)
            memory = psutil.virtual_memory()
            
            cpu_bar = "█" * int(cpu_percent / 5) + "░" * (20 - int(cpu_percent / 5))
            mem_bar = "█" * int(memory.percent / 5) + "░" * (20 - int(memory.percent / 5))
            
            return f"💻 CPU: {cpu_percent:5.1f}% [{cpu_bar}] | RAM: {memory.percent:5.1f}% [{mem_bar}]"
            
        except ImportError:
            return "💻 System metrics unavailable (psutil not installed)"
        except Exception as e:
            return f"💻 System metrics error: {e}"

class NetworkStatusOverlay(LiveOverlay):
    """Overlay showing network and connectivity status"""
    
    def __init__(self, hud_core):
        super().__init__(hud_core, "Network Status")
        self.color = "#FF8080"  # Light red
        self.position = (10, 130)
    
    def render(self) -> str:
        """Render network status"""
        # TODO: Implement actual network monitoring
        # For now, simulate network status
        import random
        
        if random.random() > 0.1:  # 90% uptime simulation
            status = "🟢 CONNECTED"
            latency = random.randint(10, 50)
            return f"🌐 Network: {status} | Latency: {latency}ms"
        else:
            return "🔴 Network: DISCONNECTED | Retrying..."
