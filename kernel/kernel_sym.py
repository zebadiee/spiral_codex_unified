# Q: How do we normalize, register, and resolve symbolic glyphs?
# R: A kernel-level symbolic interpreter must abstract symbolic operations into canonical forms and map them to registered actions without ambiguity.

from typing import Callable, Dict, Optional
import unicodedata

class KernelSYM:
    def __init__(self):
        self.glyph_registry: Dict[str, Callable] = {}
        self.symbol_cache: Dict[str, Callable] = {}

    def normalize(self, glyph: str) -> str:
        return unicodedata.normalize("NFKC", glyph.strip())

    def register_glyph(self, glyph: str, target: Callable) -> None:
        norm = self.normalize(glyph)
        self.glyph_registry[norm] = target

    def resolve(self, glyph: str) -> Optional[Callable]:
        norm = self.normalize(glyph)
        if norm in self.symbol_cache:
            return self.symbol_cache[norm]
        func = self.glyph_registry.get(norm)
        if func:
            self.symbol_cache[norm] = func
        return func
