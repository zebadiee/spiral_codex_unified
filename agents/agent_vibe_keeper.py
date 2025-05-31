# Q: How does the system interpret entropy levels?
# R: The Vibe Keeper maps entropy scores to symbolic moods and execution states.


class VibeKeeper:
    def __init__(self, memory):
        self.mem = memory

    def handle(self, payload: dict):
        entropy = payload.get("entropy", 0.5)
        if entropy > 0.9:
            vibe = "🔴 Chaotic — Ritual destabilizing, critical entropy."
        elif entropy > 0.6:
            vibe = "🟠 Disruptive — High instability."
        elif entropy > 0.3:
            vibe = "🟡 Tense — Slight misalignment detected."
        else:
            vibe = "🟢 Harmonious — Symbolic resonance optimal."

        return {
            "agent": "ƒVIBE_KEEPER",
            "entropy": entropy,
            "vibe": vibe,
            "status": "interpreted",
        }
