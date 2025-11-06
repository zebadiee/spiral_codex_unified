# utils/rag.py
"""
Lightweight RAG (Retrieval-Augmented Generation) for Spiral Codex
Uses local SQLite embeddings (no external services required)
"""
import os
import sqlite3
from pathlib import Path
from typing import List, Dict, Any, Optional
import json

EMBEDDINGS_DB = Path(os.getenv("EMBEDDINGS_DB", "data/embeddings.sqlite"))

def available() -> bool:
    """Check if RAG is available (embeddings DB exists)"""
    return EMBEDDINGS_DB.exists()

def retrieve(query: str, top_k: int = 3) -> List[Dict[str, Any]]:
    """
    Retrieve top-k most relevant snippets for query.
    Returns list of {id, content, score, source}
    
    If embeddings DB doesn't exist, returns empty list (graceful degradation).
    """
    if not available():
        return []
    
    try:
        conn = sqlite3.connect(str(EMBEDDINGS_DB))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Simple keyword-based retrieval for now (can be upgraded to vector search)
        # Normalize query for search
        query_lower = query.lower()
        keywords = [w for w in query_lower.split() if len(w) > 3]
        
        if not keywords:
            return []
        
        # Build LIKE query for keyword matching
        # This is a simple baseline - can be replaced with vector similarity later
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
                "content": row["content"][:500] if row["content"] else "",  # Truncate long content
                "source": row["source"] if row["source"] else "unknown",
                "score": 1.0,  # Placeholder score
                "metadata": json.loads(row["metadata"]) if row["metadata"] else {}
            })
        
        conn.close()
        return results
        
    except Exception as e:
        # Graceful degradation - log error but don't crash
        print(f"[RAG] Warning: Failed to retrieve: {e}")
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
    """Initialize embeddings database with schema (idempotent)"""
    EMBEDDINGS_DB.parent.mkdir(parents=True, exist_ok=True)
    
    conn = sqlite3.connect(str(EMBEDDINGS_DB))
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS embeddings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content TEXT NOT NULL,
            source TEXT,
            metadata TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Create index for faster keyword search
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_content 
        ON embeddings(content)
    """)
    
    conn.commit()
    conn.close()

def add_snippet(content: str, source: str = None, metadata: Dict[str, Any] = None):
    """Add a snippet to the embeddings database"""
    init_db()  # Ensure DB exists
    
    conn = sqlite3.connect(str(EMBEDDINGS_DB))
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO embeddings (content, source, metadata)
        VALUES (?, ?, ?)
    """, (content, source, json.dumps(metadata) if metadata else None))
    
    conn.commit()
    snippet_id = cursor.lastrowid
    conn.close()
    
    return snippet_id
