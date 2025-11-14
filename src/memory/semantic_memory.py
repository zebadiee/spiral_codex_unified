
"""
Semantic Memory System - Stores factual knowledge and relationships using knowledge graphs
"""

import asyncio
import json
import uuid
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
import numpy as np


@dataclass
class Concept:
    """Represents a concept in semantic memory"""
    id: str
    name: str
    description: str
    properties: Dict[str, Any]
    embedding: Optional[List[float]] = None
    created_at: datetime = None
    updated_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now(timezone.utc)
        if self.updated_at is None:
            self.updated_at = datetime.now(timezone.utc)


@dataclass
class Relationship:
    """Represents a relationship between concepts"""
    id: str
    source_concept_id: str
    target_concept_id: str
    relationship_type: str
    properties: Dict[str, Any]
    strength: float  # 0.0 to 1.0
    created_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now(timezone.utc)


class SemanticMemorySystem:
    """
    Manages semantic memories using an in-memory graph structure
    with vector embeddings for similarity search
    
    Note: In production, this would use Neo4j or similar graph database
    """
    
    def __init__(self, persist_directory: str = "./data/semantic_memory"):
        self.persist_directory = persist_directory
        self.concepts: Dict[str, Concept] = {}
        self.relationships: Dict[str, Relationship] = {}
        self.concept_embeddings: Dict[str, List[float]] = {}
        self._load_from_disk()
    
    def _load_from_disk(self):
        """Load semantic memory from disk"""
        try:
            import os
            concepts_file = os.path.join(self.persist_directory, "concepts.json")
            relationships_file = os.path.join(self.persist_directory, "relationships.json")
            
            os.makedirs(self.persist_directory, exist_ok=True)
            
            # Load concepts
            if os.path.exists(concepts_file):
                with open(concepts_file, 'r') as f:
                    concepts_data = json.load(f)
                    for concept_data in concepts_data:
                        concept_data['created_at'] = datetime.fromisoformat(concept_data['created_at'])
                        concept_data['updated_at'] = datetime.fromisoformat(concept_data['updated_at'])
                        concept = Concept(**concept_data)
                        self.concepts[concept.id] = concept
                        if concept.embedding:
                            self.concept_embeddings[concept.id] = concept.embedding
            
            # Load relationships
            if os.path.exists(relationships_file):
                with open(relationships_file, 'r') as f:
                    relationships_data = json.load(f)
                    for rel_data in relationships_data:
                        rel_data['created_at'] = datetime.fromisoformat(rel_data['created_at'])
                        relationship = Relationship(**rel_data)
                        self.relationships[relationship.id] = relationship
                        
        except Exception as e:
            print(f"Error loading semantic memory: {e}")
    
    def _save_to_disk(self):
        """Save semantic memory to disk"""
        try:
            import os
            concepts_file = os.path.join(self.persist_directory, "concepts.json")
            relationships_file = os.path.join(self.persist_directory, "relationships.json")
            
            os.makedirs(self.persist_directory, exist_ok=True)
            
            # Save concepts
            concepts_data = []
            for concept in self.concepts.values():
                concept_dict = asdict(concept)
                concept_dict['created_at'] = concept.created_at.isoformat()
                concept_dict['updated_at'] = concept.updated_at.isoformat()
                concepts_data.append(concept_dict)
            
            with open(concepts_file, 'w') as f:
                json.dump(concepts_data, f, indent=2)
            
            # Save relationships
            relationships_data = []
            for relationship in self.relationships.values():
                rel_dict = asdict(relationship)
                rel_dict['created_at'] = relationship.created_at.isoformat()
                relationships_data.append(rel_dict)
            
            with open(relationships_file, 'w') as f:
                json.dump(relationships_data, f, indent=2)
                
        except Exception as e:
            print(f"Error saving semantic memory: {e}")
    
    async def add_concept(self, concept: Concept) -> str:
        """Add a new concept to semantic memory"""
        try:
            # Generate embedding if not provided
            if concept.embedding is None:
                concept.embedding = await self._generate_concept_embedding(concept)
            
            self.concepts[concept.id] = concept
            self.concept_embeddings[concept.id] = concept.embedding
            
            self._save_to_disk()
            return concept.id
            
        except Exception as e:
            print(f"Error adding concept {concept.id}: {e}")
            raise
    
    async def get_concept(self, concept_id: str) -> Optional[Concept]:
        """Retrieve a concept by ID"""
        return self.concepts.get(concept_id)
    
    async def find_concepts(
        self,
        query: str,
        limit: int = 10,
        similarity_threshold: float = 0.7
    ) -> List[Tuple[Concept, float]]:
        """Find concepts similar to query"""
        try:
            query_embedding = await self._generate_text_embedding(query)
            
            similarities = []
            for concept_id, concept_embedding in self.concept_embeddings.items():
                similarity = self._cosine_similarity(query_embedding, concept_embedding)
                if similarity >= similarity_threshold:
                    concept = self.concepts[concept_id]
                    similarities.append((concept, similarity))
            
            # Sort by similarity and return top results
            similarities.sort(key=lambda x: x[1], reverse=True)
            return similarities[:limit]
            
        except Exception as e:
            print(f"Error finding concepts: {e}")
            return []
    
    async def add_relationship(self, relationship: Relationship) -> str:
        """Add a relationship between concepts"""
        try:
            # Verify that both concepts exist
            if relationship.source_concept_id not in self.concepts:
                raise ValueError(f"Source concept {relationship.source_concept_id} not found")
            if relationship.target_concept_id not in self.concepts:
                raise ValueError(f"Target concept {relationship.target_concept_id} not found")
            
            self.relationships[relationship.id] = relationship
            self._save_to_disk()
            return relationship.id
            
        except Exception as e:
            print(f"Error adding relationship {relationship.id}: {e}")
            raise
    
    async def get_related_concepts(
        self,
        concept_id: str,
        relationship_types: Optional[List[str]] = None,
        max_depth: int = 1
    ) -> List[Tuple[Concept, Relationship, int]]:
        """Get concepts related to a given concept"""
        try:
            related = []
            visited = set()
            
            def _traverse(current_id: str, depth: int):
                if depth > max_depth or current_id in visited:
                    return
                
                visited.add(current_id)
                
                for relationship in self.relationships.values():
                    if relationship.source_concept_id == current_id:
                        if relationship_types is None or relationship.relationship_type in relationship_types:
                            target_concept = self.concepts.get(relationship.target_concept_id)
                            if target_concept:
                                related.append((target_concept, relationship, depth))
                                if depth < max_depth:
                                    _traverse(relationship.target_concept_id, depth + 1)
            
            _traverse(concept_id, 0)
            return related
            
        except Exception as e:
            print(f"Error getting related concepts: {e}")
            return []
    
    async def update_concept(self, concept_id: str, updates: Dict[str, Any]):
        """Update a concept's properties"""
        try:
            if concept_id not in self.concepts:
                raise ValueError(f"Concept {concept_id} not found")
            
            concept = self.concepts[concept_id]
            
            if 'name' in updates:
                concept.name = updates['name']
            if 'description' in updates:
                concept.description = updates['description']
            if 'properties' in updates:
                concept.properties.update(updates['properties'])
            
            concept.updated_at = datetime.now(timezone.utc)
            
            # Regenerate embedding if content changed
            if any(key in updates for key in ['name', 'description']):
                concept.embedding = await self._generate_concept_embedding(concept)
                self.concept_embeddings[concept_id] = concept.embedding
            
            self._save_to_disk()
            
        except Exception as e:
            print(f"Error updating concept {concept_id}: {e}")
            raise
    
    async def delete_concept(self, concept_id: str):
        """Delete a concept and all its relationships"""
        try:
            if concept_id not in self.concepts:
                return
            
            # Remove all relationships involving this concept
            relationships_to_remove = []
            for rel_id, relationship in self.relationships.items():
                if (relationship.source_concept_id == concept_id or 
                    relationship.target_concept_id == concept_id):
                    relationships_to_remove.append(rel_id)
            
            for rel_id in relationships_to_remove:
                del self.relationships[rel_id]
            
            # Remove concept
            del self.concepts[concept_id]
            if concept_id in self.concept_embeddings:
                del self.concept_embeddings[concept_id]
            
            self._save_to_disk()
            
        except Exception as e:
            print(f"Error deleting concept {concept_id}: {e}")
    
    async def get_knowledge_graph_stats(self) -> Dict[str, Any]:
        """Get statistics about the knowledge graph"""
        try:
            relationship_types = {}
            for relationship in self.relationships.values():
                rel_type = relationship.relationship_type
                relationship_types[rel_type] = relationship_types.get(rel_type, 0) + 1
            
            return {
                "total_concepts": len(self.concepts),
                "total_relationships": len(self.relationships),
                "relationship_types": relationship_types,
                "average_connections_per_concept": len(self.relationships) / max(len(self.concepts), 1)
            }
            
        except Exception as e:
            print(f"Error getting knowledge graph stats: {e}")
            return {}
    
    async def _generate_concept_embedding(self, concept: Concept) -> List[float]:
        """Generate embedding for a concept"""
        text = f"{concept.name} {concept.description}"
        return await self._generate_text_embedding(text)
    
    async def _generate_text_embedding(self, text: str) -> List[float]:
        """Generate embedding for text (placeholder implementation)"""
        # Simple hash-based embedding (replace with actual embedding model)
        import hashlib
        hash_obj = hashlib.md5(text.encode())
        hash_hex = hash_obj.hexdigest()
        
        # Convert to float vector (384 dimensions)
        embedding = []
        for i in range(0, len(hash_hex), 2):
            val = int(hash_hex[i:i+2], 16) / 255.0
            embedding.append(val)
        
        # Pad to 384 dimensions
        while len(embedding) < 384:
            embedding.append(0.0)
        
        return embedding[:384]
    
    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors"""
        try:
            vec1_np = np.array(vec1)
            vec2_np = np.array(vec2)
            
            dot_product = np.dot(vec1_np, vec2_np)
            norm1 = np.linalg.norm(vec1_np)
            norm2 = np.linalg.norm(vec2_np)
            
            if norm1 == 0 or norm2 == 0:
                return 0.0
            
            return dot_product / (norm1 * norm2)
            
        except Exception as e:
            print(f"Error calculating cosine similarity: {e}")
            return 0.0


# Factory functions
def create_concept(
    name: str,
    description: str,
    properties: Optional[Dict[str, Any]] = None
) -> Concept:
    """Factory function to create a new concept"""
    return Concept(
        id=str(uuid.uuid4()),
        name=name,
        description=description,
        properties=properties or {}
    )


def create_relationship(
    source_concept_id: str,
    target_concept_id: str,
    relationship_type: str,
    properties: Optional[Dict[str, Any]] = None,
    strength: float = 1.0
) -> Relationship:
    """Factory function to create a new relationship"""
    return Relationship(
        id=str(uuid.uuid4()),
        source_concept_id=source_concept_id,
        target_concept_id=target_concept_id,
        relationship_type=relationship_type,
        properties=properties or {},
        strength=strength
    )
