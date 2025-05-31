from kernel.kernel_mem import KernelMEM
from kernel.reward_tracker import RewardTracker


class KernelMIND:
    def __init__(self):
        self.mem = KernelMEM()
        self.agents = {}
        self.reward_tracker = RewardTracker()

    def register_agent(self, name: str, agent):
        self.agents[name] = agent

    def dispatch(self, agent, glyph, inject=None):
        if agent not in self.agents:
            return {
                "agent": agent,
                "status": "not_found",
                "query": glyph,
                "message": "No symbolic memory found for the given glyph.",
            }

        result = self.agents[agent].run(glyph, inject or {})
        self.reward_tracker.log(agent, glyph, 1.0)  # dummy reward
        return result
