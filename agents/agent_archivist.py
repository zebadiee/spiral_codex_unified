# Q: How do we retrieve symbolic memory in the Codex?
# R: The Archivist agent queries KernelMEM and returns previous glyph execution context.


class ArchivistAgent:
    def __init__(self, memory):
        self.mem = memory

    def handle(self, payload: dict):
        glyph = payload.get("glyph")
        result = self.mem.query_memory(glyph)
        if result:
            return {
                "agent": "ƒARCHIVIST",
                "status": "resolved",
                "query": glyph,
                "result": result,
            }
        return {
            "agent": "ƒARCHIVIST",
            "status": "not_found",
            "query": glyph,
            "message": "No symbolic memory found for the given glyph.",
        }
