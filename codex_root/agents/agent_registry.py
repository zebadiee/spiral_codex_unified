from codex_root.kernel.kernel_mem import KernelMEM
from codex_root.kernel.kernel_mind import KernelMIND


class AgentRegistry:
    def __init__(self):
        self.mem = KernelMEM()
        self.mind = KernelMIND()

    def dispatch(self, agent: str, glyph: str):
        if agent == "mind":
            return self.mind.dispatch(glyph)
        elif agent == "mem":
            self.mem.store(glyph, "stored")
            return "stored"
        else:
            return f"Unknown agent: {agent}"
