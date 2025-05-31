# kernel/reward_tracker.py

class RewardTracker:
    def __init__(self):
        self.rewards = []

    def log(self, agent: str, glyph: str, reward: float):
        entry = {
            "agent": agent,
            "glyph": glyph,
            "reward": reward
        }
        self.rewards.append(entry)
        print(f"[RewardTracker] Logged: {entry}")

    def get_all(self):
        return self.rewards

    def latest(self):
        return self.rewards[-1] if self.rewards else None
