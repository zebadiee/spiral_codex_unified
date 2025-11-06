# Q: How are Codex agents registered and accessed from the kernel?
# R: This registry centralizes agent bindings for consistent invocation from KernelMIND.

from agents.agent_archivist import ArchivistAgent
from agents.agent_vibe_keeper import VibeKeeper
from agents.agent_codex import CodexAgent
from agents.agent_claude import ClaudeAgent


class AgentRegistry:
    def __init__(self, mem):
        self.mem = mem
        self._agents = {}

    def register_all(self):
        self._agents["ƒARCHIVIST"] = ArchivistAgent(self.mem)
        self._agents["ƒVIBE_KEEPER"] = VibeKeeper(self.mem)
        self._agents["ƒCODEX"] = CodexAgent(self.mem)
        self._agents["ƒCLAUDE"] = ClaudeAgent(self.mem)

    def get(self, name):
        return self._agents.get(name)

    def all(self):
        return self._agents
