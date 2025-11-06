# utils/rag.py
"""
Enhanced RAG (Retrieval-Augmented Generation) for Spiral Codex
Uses BM25 + vector tie-break scoring for improved retrieval quality
"""
import os
import sqlite3
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
import json
import math
import re
from collections import Counter, defaultdict

EMBEDDINGS_DB = Path(os.getenv("EMBEDDINGS_DB", "data/embeddings.sqlite"))
BM25_TOP_K = int(os.getenv("BM25_TOP_K", "5"))
VECTOR_MODEL = os.getenv("VECTOR_MODEL", "all-MiniLM-L6-v2")

# Try to import vector model, but make it optional
try:
    from sentence_transformers import SentenceTransformer
    import numpy as np
    VECTOR_AVAILABLE = True
except ImportError:
    VECTOR_AVAILABLE = False

class BM25Scorer:
    """Simple BM25 scorer implementation"""

    def __init__(self, k1: float = 1.2, b: float = 0.75):
        self.k1 = k1
        self.b = b
        self.doc_freqs = defaultdict(int)
        self.idf = {}
        self.doc_len = []
        self.avgdl = 0
        self.N = 0
        self.documents = []

    def fit(self, documents: List[str]):
        """Fit BM25 on corpus"""
        self.documents = documents
        self.N = len(documents)
        self.doc_len = [len(self._tokenize(doc)) for doc in documents]
        self.avgdl = sum(self.doc_len) / self.N if self.N > 0 else 0

        # Calculate document frequencies
        for doc in documents:
            tokens = set(self._tokenize(doc))
            for token in tokens:
                self.doc_freqs[token] += 1

        # Calculate IDF
        for token, freq in self.doc_freqs.items():
            self.idf[token] = math.log(self.N - freq + 0.5) - math.log(freq + 0.5)

    def _tokenize(self, text: str) -> List[str]:
        """Simple tokenization"""
        # Convert to lowercase and extract alphanumeric tokens
        tokens = re.findall(r'\b\w+\b', text.lower())
        return [t for t in tokens if len(t) > 2]  # Filter very short tokens

    def score(self, query: str, doc_idx: int) -> float:
        """Calculate BM25 score for query-document pair"""
        if doc_idx >= len(self.documents):
            return 0.0

        doc = self.documents[doc_idx]
        doc_tokens = self._tokenize(doc)
        query_tokens = self._tokenize(query)

        doc_len = len(doc_tokens)
        if doc_len == 0:
            return 0.0

        # Count query tokens in document
        token_counts = Counter(doc_tokens)

        score = 0.0
        for token in query_tokens:
            if token in token_counts:
                tf = token_counts[token]
                idf = self.idf.get(token, 0)
                numerator = tf * (self.k1 + 1)
                denominator = tf + self.k1 * (1 - self.b + self.b * (doc_len / self.avgdl))
                score += idf * (numerator / denominator)

        return score

class VectorTieBreak:
    """Vector similarity for tie-breaking BM25 scores"""

    def __init__(self):
        self.model = None
        self.embeddings = None
        self._load_model()

    def _load_model(self):
        """Load sentence transformer model"""
        if not VECTOR_AVAILABLE:
            return
        try:
            self.model = SentenceTransformer(VECTOR_MODEL)
        except Exception as e:
            print(f"[RAG] Warning: Could not load vector model: {e}")
            self.model = None

    def fit(self, documents: List[str]):
        """Fit vector model on corpus"""
        if not self.model:
            return
        try:
            self.embeddings = self.model.encode(documents, show_progress_bar=False)
        except Exception as e:
            print(f"[RAG] Warning: Could not encode documents: {e}")
            self.embeddings = None

    def cosine_similarity(self, query: str, doc_idx: int) -> float:
        """Calculate cosine similarity for tie-breaking"""
        if not self.model or self.embeddings is None:
            return 0.0
        if doc_idx >= len(self.embeddings):
            return 0.0

        try:
            query_vec = self.model.encode([query], show_progress_bar=False)
            doc_vec = self.embeddings[doc_idx:doc_idx+1]

            # Cosine similarity
            dot_product = np.dot(query_vec, doc_vec.T)[0][0]
            norm_query = np.linalg.norm(query_vec)
            norm_doc = np.linalg.norm(doc_vec)

            if norm_query == 0 or norm_doc == 0:
                return 0.0

            return dot_product / (norm_query * norm_doc)
        except Exception as e:
            print(f"[RAG] Warning: Vector similarity failed: {e}")
            return 0.0

# Global models (cached)
_bm25_model = None
_vector_model = None

def _ensure_models():
    """Ensure BM25 and vector models are loaded"""
    global _bm25_model, _vector_model

    if not available():
        return False, False

    try:
        conn = sqlite3.connect(str(EMBEDDINGS_DB))
        cursor = conn.cursor()
        cursor.execute("SELECT content FROM embeddings ORDER BY id")
        documents = [row[0] for row in cursor.fetchall()]
        conn.close()

        if not documents:
            return False, False

        # Initialize BM25
        if _bm25_model is None:
            _bm25_model = BM25Scorer()
            _bm25_model.fit(documents)

        # Initialize vector model
        if _vector_model is None:
            _vector_model = VectorTieBreak()
            _vector_model.fit(documents)

        return True, True

    except Exception as e:
        print(f"[RAG] Warning: Failed to load models: {e}")
        return False, False

def available() -> bool:
    """Check if RAG is available (embeddings DB exists)"""
    return EMBEDDINGS_DB.exists()

def retrieve(query: str, top_k: int = 3) -> List[Dict[str, Any]]:
    """
    Enhanced retrieval using BM25 + vector tie-break scoring.
    Returns list of {id, content, score, source, bm25_score, vector_score}

    If embeddings DB doesn't exist, returns empty list (graceful degradation).
    """
    if not available():
        return []

    # Ensure models are loaded
    bm25_ready, vector_ready = _ensure_models()
    if not bm25_ready:
        print("[RAG] Warning: BM25 model not ready")
        return []

    try:
        conn = sqlite3.connect(str(EMBEDDINGS_DB))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # Get all documents with their metadata
        cursor.execute("SELECT id, content, source, metadata FROM embeddings ORDER BY id")
        all_docs = cursor.fetchall()
        conn.close()

        if not all_docs:
            return []

        # Calculate BM25 scores for all documents
        candidate_scores = []
        for doc in all_docs:
            doc_idx = doc["id"] - 1  # SQLite IDs start at 1
            bm25_score = _bm25_model.score(query, doc_idx)

            # Only consider documents with non-zero BM25 scores
            if bm25_score > 0:
                vector_score = 0.0
                if vector_ready and _vector_model:
                    vector_score = _vector_model.cosine_similarity(query, doc_idx)

                candidate_scores.append({
                    "id": doc["id"],
                    "content": doc["content"][:500] if doc["content"] else "",
                    "source": doc["source"] if doc["source"] else "unknown",
                    "metadata": json.loads(doc["metadata"]) if doc["metadata"] else {},
                    "bm25_score": bm25_score,
                    "vector_score": vector_score,
                    "combined_score": bm25_score  # Primary score is BM25
                })

        # Sort by BM25 score primarily, then vector score for ties
        candidate_scores.sort(key=lambda x: (x["bm25_score"], x["vector_score"]), reverse=True)

        # Return top_k results
        results = []
        for i, candidate in enumerate(candidate_scores[:top_k]):
            result = {
                "id": candidate["id"],
                "content": candidate["content"],
                "source": candidate["source"],
                "score": candidate["bm25_score"],  # Primary score for compatibility
                "bm25_score": candidate["bm25_score"],
                "vector_score": candidate["vector_score"],
                "metadata": candidate["metadata"],
                "rank_method": "bm25+vector_tiebreak" if vector_ready else "bm25_only"
            }
            results.append(result)

        return results

    except Exception as e:
        # Graceful degradation - log error but don't crash
        print(f"[RAG] Warning: Failed to retrieve: {e}")
        return []

def retrieve_legacy(query: str, top_k: int = 3) -> List[Dict[str, Any]]:
    """
    Legacy keyword-based retrieval for comparison.
    Returns list of {id, content, score, source}
    """
    if not available():
        return []

    try:
        conn = sqlite3.connect(str(EMBEDDINGS_DB))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # Simple keyword-based retrieval
        query_lower = query.lower()
        keywords = [w for w in query_lower.split() if len(w) > 3]

        if not keywords:
            return []

        # Build LIKE query for keyword matching
        conditions = " OR ".join([f"content LIKE ?" for _ in keywords])
        params = [f"%{kw}%" for kw in keywords]

        cursor.execute(f"""
            SELECT id, content, source, metadata
            FROM embeddings
            WHERE {conditions}
            ORDER BY id DESC
            LIMIT ?
        """, params + [top_k])

        results = []
        for row in cursor.fetchall():
            results.append({
                "id": row["id"],
                "content": row["content"][:500] if row["content"] else "",
                "source": row["source"] if row["source"] else "unknown",
                "score": 1.0,  # Placeholder score
                "metadata": json.loads(row["metadata"]) if row["metadata"] else {},
                "rank_method": "keyword_match"
            })

        conn.close()
        return results

    except Exception as e:
        print(f"[RAG] Warning: Failed legacy retrieve: {e}")
        return []

def enrich_prompt(base_prompt: str, context_query: str, max_snippets: int = 3) -> str:
    """
    Enrich a prompt with retrieved context snippets.
    
    If RAG is not available, returns original prompt unchanged.
    """
    snippets = retrieve(context_query, top_k=max_snippets)
    
    if not snippets:
        return base_prompt
    
    # Build enriched prompt with context
    context_block = "## Retrieved Context\n\n"
    for i, snippet in enumerate(snippets, 1):
        source = snippet.get("source", "unknown")
        content = snippet.get("content", "")
        context_block += f"### Context {i} (from {source})\n{content}\n\n"
    
    enriched = f"{context_block}\n## Your Task\n{base_prompt}"
    return enriched

def init_db():
    """Initialize embeddings database with enhanced schema (idempotent)"""
    EMBEDDINGS_DB.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(str(EMBEDDINGS_DB))
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS embeddings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content TEXT NOT NULL,
            source TEXT,
            metadata TEXT,
            vector_embedding BLOB,  -- Store as BLOB for efficiency
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Create indexes for faster search
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_content
        ON embeddings(content)
    """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_source
        ON embeddings(source)
    """)

    conn.commit()
    conn.close()

def add_snippet(content: str, source: str = None, metadata: Dict[str, Any] = None) -> int:
    """Add a snippet to the embeddings database with optional vector embedding"""
    init_db()  # Ensure DB exists

    conn = sqlite3.connect(str(EMBEDDINGS_DB))
    cursor = conn.cursor()

    # Calculate vector embedding if available
    vector_blob = None
    if VECTOR_AVAILABLE:
        try:
            from sentence_transformers import SentenceTransformer
            import numpy as np

            # Lazy load model to avoid overhead if not needed
            if not hasattr(add_snippet, '_vector_model'):
                add_snippet._vector_model = SentenceTransformer(VECTOR_MODEL)

            embedding = add_snippet._vector_model.encode([content], show_progress_bar=False)[0]
            vector_blob = embedding.astype(np.float32).tobytes()
        except Exception as e:
            print(f"[RAG] Warning: Failed to generate embedding: {e}")

    cursor.execute("""
        INSERT INTO embeddings (content, source, metadata, vector_embedding)
        VALUES (?, ?, ?, ?)
    """, (content, source, json.dumps(metadata) if metadata else None, vector_blob))

    conn.commit()
    snippet_id = cursor.lastrowid
    conn.close()

    # Clear cached models to force retraining with new data
    global _bm25_model, _vector_model
    _bm25_model = None
    _vector_model = None

    return snippet_id

def add_test_snippets():
    """Add test snippets to bootstrap the RAG system"""
    test_snippets = [
        ("The Spiral Codex uses glyph-based routing with symbols like ⊕⊡⊠⊨⊚", "README.md", {"type": "architecture"}),
        ("Agent orchestrator routes tasks to Codex, Claude, VibeKeeper and Archivist", "agent_orchestrator.py", {"type": "code"}),
        ("Privacy filter skips notes with #private tag or private: true frontmatter", "omai_ingest.py", {"type": "feature"}),
        ("Ledger sink logs every conversation turn to JSONL with SHA-256 hashes", "ledger.py", {"type": "feature"}),
        ("Wean telemetry tracks provider usage and latency in CSV format", "telemetry.py", {"type": "feature"}),
        ("FastAPI provides automatic API documentation and validation", "api/brain_api.py", {"type": "api"}),
        ("BM25 scoring uses term frequency and inverse document frequency", "utils/rag.py", {"type": "algorithm"}),
        ("Vector embeddings capture semantic similarity for tie-breaking", "utils/rag.py", {"type": "algorithm"}),
        ("Reflection training cycles improve system intelligence over time", "reflection_training.py", {"type": "training"}),
        ("SQLite database provides lightweight local storage", "utils/rag.py", {"type": "database"})
    ]

    for content, source, metadata in test_snippets:
        snippet_id = add_snippet(content, source, metadata)
        print(f"Added test snippet #{snippet_id}: {source}")

def reset_models():
    """Reset cached models to force retraining"""
    global _bm25_model, _vector_model
    _bm25_model = None
    _vector_model = None
