
"""
Episodic Memory System - Stores and retrieves specific experiences and events
"""

import asyncio
import json
import uuid
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
import chromadb
from chromadb.config import Settings
import numpy as np


@dataclass
class Episode:
    """Represents a single episodic memory"""
    id: str
    timestamp: datetime
    context: Dict[str, Any]
    action: str
    result: Dict[str, Any]
    emotional_valence: float  # -1.0 to 1.0
    importance_score: float   # 0.0 to 1.0
    tags: List[str]
    embedding: Optional[List[float]] = None


class EpisodicMemorySystem:
    """
    Manages episodic memories using ChromaDB for vector storage
    and temporal indexing for time-aware retrieval
    """
    
    def __init__(self, persist_directory: str = "./data/episodic_memory"):
        self.persist_directory = persist_directory
        self.client = None
        self.collection = None
        self._initialize_storage()
    
    def _initialize_storage(self):
        """Initialize ChromaDB client and collection"""
        try:
            self.client = chromadb.PersistentClient(
                path=self.persist_directory,
                settings=Settings(
                    anonymized_telemetry=False,
                    allow_reset=True
                )
            )
            
            # Create or get collection for episodic memories
            self.collection = self.client.get_or_create_collection(
                name="episodic_memories",
                metadata={"description": "Spiral Codex episodic memory storage"}
            )
            
        except Exception as e:
            print(f"Error initializing episodic memory storage: {e}")
            raise
    
    async def store_episode(self, episode: Episode) -> str:
        """Store a new episodic memory"""
        try:
            # Generate embedding if not provided
            if episode.embedding is None:
                episode.embedding = await self._generate_embedding(episode)
            
            # Prepare metadata
            metadata = {
                "timestamp": episode.timestamp.isoformat(),
                "action": episode.action,
                "emotional_valence": episode.emotional_valence,
                "importance_score": episode.importance_score,
                "tags": json.dumps(episode.tags)
            }
            
            # Create document text for retrieval
            document_text = self._create_document_text(episode)
            
            # Store in ChromaDB
            self.collection.add(
                ids=[episode.id],
                embeddings=[episode.embedding],
                documents=[document_text],
                metadatas=[metadata]
            )
            
            return episode.id
            
        except Exception as e:
            print(f"Error storing episode {episode.id}: {e}")
            raise
    
    async def retrieve_episodes(
        self,
        query: str,
        n_results: int = 10,
        time_range: Optional[tuple] = None,
        importance_threshold: float = 0.0,
        tags: Optional[List[str]] = None
    ) -> List[Episode]:
        """Retrieve episodes based on query and filters"""
        try:
            # Build where clause for filtering
            where_clause = {}
            
            if importance_threshold > 0:
                where_clause["importance_score"] = {"$gte": importance_threshold}
            
            if time_range:
                start_time, end_time = time_range
                where_clause["timestamp"] = {
                    "$gte": start_time.isoformat(),
                    "$lte": end_time.isoformat()
                }
            
            # Query ChromaDB
            results = self.collection.query(
                query_texts=[query],
                n_results=n_results,
                where=where_clause if where_clause else None
            )
            
            # Convert results to Episode objects
            episodes = []
            for i in range(len(results['ids'][0])):
                episode_data = {
                    'id': results['ids'][0][i],
                    'timestamp': datetime.fromisoformat(results['metadatas'][0][i]['timestamp']),
                    'action': results['metadatas'][0][i]['action'],
                    'emotional_valence': results['metadatas'][0][i]['emotional_valence'],
                    'importance_score': results['metadatas'][0][i]['importance_score'],
                    'tags': json.loads(results['metadatas'][0][i]['tags']),
                    'embedding': results['embeddings'][0][i] if results['embeddings'] else None
                }
                
                # Parse context and result from document
                document = results['documents'][0][i]
                context, result = self._parse_document_text(document)
                episode_data['context'] = context
                episode_data['result'] = result
                
                episodes.append(Episode(**episode_data))
            
            return episodes
            
        except Exception as e:
            print(f"Error retrieving episodes: {e}")
            return []
    
    async def get_episode_by_id(self, episode_id: str) -> Optional[Episode]:
        """Retrieve a specific episode by ID"""
        try:
            results = self.collection.get(
                ids=[episode_id],
                include=['embeddings', 'documents', 'metadatas']
            )
            
            if not results['ids']:
                return None
            
            # Convert to Episode object
            metadata = results['metadatas'][0]
            document = results['documents'][0]
            
            context, result = self._parse_document_text(document)
            
            return Episode(
                id=results['ids'][0],
                timestamp=datetime.fromisoformat(metadata['timestamp']),
                context=context,
                action=metadata['action'],
                result=result,
                emotional_valence=metadata['emotional_valence'],
                importance_score=metadata['importance_score'],
                tags=json.loads(metadata['tags']),
                embedding=results['embeddings'][0] if results['embeddings'] else None
            )
            
        except Exception as e:
            print(f"Error retrieving episode {episode_id}: {e}")
            return None
    
    async def update_episode_importance(self, episode_id: str, new_importance: float):
        """Update the importance score of an episode"""
        try:
            self.collection.update(
                ids=[episode_id],
                metadatas=[{"importance_score": new_importance}]
            )
        except Exception as e:
            print(f"Error updating episode importance: {e}")
    
    async def delete_episode(self, episode_id: str):
        """Delete an episode from memory"""
        try:
            self.collection.delete(ids=[episode_id])
        except Exception as e:
            print(f"Error deleting episode {episode_id}: {e}")
    
    async def get_memory_stats(self) -> Dict[str, Any]:
        """Get statistics about the episodic memory system"""
        try:
            count = self.collection.count()
            
            # Get all episodes to calculate stats
            all_episodes = self.collection.get(include=['metadatas'])
            
            if not all_episodes['metadatas']:
                return {
                    "total_episodes": 0,
                    "average_importance": 0.0,
                    "emotional_distribution": {"positive": 0, "neutral": 0, "negative": 0},
                    "oldest_episode": None,
                    "newest_episode": None
                }
            
            importances = [m['importance_score'] for m in all_episodes['metadatas']]
            valences = [m['emotional_valence'] for m in all_episodes['metadatas']]
            timestamps = [datetime.fromisoformat(m['timestamp']) for m in all_episodes['metadatas']]
            
            return {
                "total_episodes": count,
                "average_importance": np.mean(importances),
                "emotional_distribution": {
                    "positive": sum(1 for v in valences if v > 0.1),
                    "neutral": sum(1 for v in valences if -0.1 <= v <= 0.1),
                    "negative": sum(1 for v in valences if v < -0.1)
                },
                "oldest_episode": min(timestamps).isoformat(),
                "newest_episode": max(timestamps).isoformat()
            }
            
        except Exception as e:
            print(f"Error getting memory stats: {e}")
            return {}
    
    async def _generate_embedding(self, episode: Episode) -> List[float]:
        """Generate embedding for an episode (placeholder implementation)"""
        # In a real implementation, this would use a proper embedding model
        # For now, create a simple hash-based embedding
        text = self._create_document_text(episode)
        
        # Simple hash-based embedding (replace with actual embedding model)
        import hashlib
        hash_obj = hashlib.md5(text.encode())
        hash_hex = hash_obj.hexdigest()
        
        # Convert to float vector (384 dimensions for compatibility)
        embedding = []
        for i in range(0, len(hash_hex), 2):
            val = int(hash_hex[i:i+2], 16) / 255.0
            embedding.append(val)
        
        # Pad to 384 dimensions
        while len(embedding) < 384:
            embedding.append(0.0)
        
        return embedding[:384]
    
    def _create_document_text(self, episode: Episode) -> str:
        """Create searchable document text from episode"""
        context_str = json.dumps(episode.context, default=str)
        result_str = json.dumps(episode.result, default=str)
        tags_str = " ".join(episode.tags)
        
        return f"""
        Action: {episode.action}
        Context: {context_str}
        Result: {result_str}
        Tags: {tags_str}
        Timestamp: {episode.timestamp.isoformat()}
        """
    
    def _parse_document_text(self, document: str) -> tuple:
        """Parse context and result from document text"""
        try:
            lines = document.strip().split('\n')
            context_line = next(line for line in lines if line.strip().startswith('Context:'))
            result_line = next(line for line in lines if line.strip().startswith('Result:'))
            
            context_str = context_line.split('Context:', 1)[1].strip()
            result_str = result_line.split('Result:', 1)[1].strip()
            
            context = json.loads(context_str)
            result = json.loads(result_str)
            
            return context, result
            
        except Exception as e:
            print(f"Error parsing document text: {e}")
            return {}, {}


# Factory function for creating episodes
def create_episode(
    context: Dict[str, Any],
    action: str,
    result: Dict[str, Any],
    emotional_valence: float = 0.0,
    importance_score: float = 0.5,
    tags: Optional[List[str]] = None
) -> Episode:
    """Factory function to create a new episode"""
    return Episode(
        id=str(uuid.uuid4()),
        timestamp=datetime.now(timezone.utc),
        context=context,
        action=action,
        result=result,
        emotional_valence=emotional_valence,
        importance_score=importance_score,
        tags=tags or []
    )
