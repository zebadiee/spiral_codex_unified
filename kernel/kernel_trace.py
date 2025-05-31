# Q: How do we trace symbolic operations in execution?
# R: A trace log buffers meaningful state changes for introspection, debugging, and learning purposes.

from typing import List
from datetime import datetime

class KernelTRACE:
    def __init__(self):
        self.buffer: List[str] = []

    def log(self, msg: str):
        self.buffer.append(f"[{self._now()}] {msg}")

    def dump(self) -> List[str]:
        return self.buffer

    def _now(self) -> str:
        return datetime.utcnow().isoformat(timespec='seconds') + "Z"
