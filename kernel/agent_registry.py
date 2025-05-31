import sys
from pathlib import Path

# Add codex_root/kernel to the system path
kernel_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(kernel_dir))

# Kernel and agent imports (from same directory)
from kernel.kernel_mem import KernelMEM
from kernel_mind import KernelMIND
from agent_archivist import ArchivistAgent
from agent_vibe_keeper import VibeKeeperAgent

class AgentRegistry:
    def __init__(self):
        self.kernel_mem = KernelMEM()
        self.kernel_mind = KernelMIND()
        self.agents = {
            "archivist": ArchivistAgent(self.kernel_mem),
            "vibe": VibeKeeperAgent(self.kernel_mem),
        }

    def dispatch(self, agent_name, glyph):
        agent = self.agents.get(agent_name.lower())
        if agent:
            return agent.process(glyph)
        return {"error": f"Agent '{agent_name}' not found"}

