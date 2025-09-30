
"""
Memory Consolidator - Integrates episodic, semantic, and procedural memories
"""

import asyncio
import json
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
import numpy as np

from .episodic_memory import EpisodicMemorySystem, Episode, create_episode
from .semantic_memory import SemanticMemorySystem, Concept, Relationship, create_concept, create_relationship
from .procedural_memory import ProceduralMemorySystem, Skill, SkillType, create_skill


@dataclass
class ConsolidationResult:
    """Result of memory consolidation process"""
    episodic_stored: bool
    semantic_updates: List[str]  # IDs of updated/created concepts
    procedural_patterns: List[str]  # IDs of identified/updated skills
    consolidation_score: float  # 0.0 to 1.0
    insights: List[str]  # Generated insights


class MemoryConsolidator:
    """
    Orchestrates the integration of episodic, semantic, and procedural memories
    Implements memory consolidation algorithms inspired by human memory systems
    """
    
    def __init__(
        self,
        episodic_system: EpisodicMemorySystem,
        semantic_system: SemanticMemorySystem,
        procedural_system: ProceduralMemorySystem,
        consolidation_threshold: float = 0.7
    ):
        self.episodic = episodic_system
        self.semantic = semantic_system
        self.procedural = procedural_system
        self.consolidation_threshold = consolidation_threshold
        
        # Consolidation parameters
        self.importance_decay_rate = 0.1  # How quickly importance decays over time
        self.pattern_recognition_threshold = 0.8
        self.skill_extraction_threshold = 0.6
    
    async def consolidate_experience(
        self,
        context: Dict[str, Any],
        action: str,
        result: Dict[str, Any],
        emotional_valence: float = 0.0,
        importance_score: float = 0.5,
        tags: Optional[List[str]] = None
    ) -> ConsolidationResult:
        """
        Main consolidation method - processes a new experience through all memory systems
        """
        try:
            # Create episodic memory
            episode = create_episode(
                context=context,
                action=action,
                result=result,
                emotional_valence=emotional_valence,
                importance_score=importance_score,
                tags=tags or []
            )
            
            # Store episodic memory
            episode_id = await self.episodic.store_episode(episode)
            episodic_stored = episode_id is not None
            
            # Extract semantic knowledge
            semantic_updates = await self._extract_semantic_knowledge(episode)
            
            # Identify procedural patterns
            procedural_patterns = await self._identify_procedural_patterns(episode)
            
            # Calculate consolidation score
            consolidation_score = await self._calculate_consolidation_score(
                episode, semantic_updates, procedural_patterns
            )
            
            # Generate insights
            insights = await self._generate_insights(
                episode, semantic_updates, procedural_patterns
            )
            
            # Trigger background consolidation if needed
            if consolidation_score > self.consolidation_threshold:
                asyncio.create_task(self._background_consolidation())
            
            return ConsolidationResult(
                episodic_stored=episodic_stored,
                semantic_updates=semantic_updates,
                procedural_patterns=procedural_patterns,
                consolidation_score=consolidation_score,
                insights=insights
            )
            
        except Exception as e:
            print(f"Error in memory consolidation: {e}")
            return ConsolidationResult(
                episodic_stored=False,
                semantic_updates=[],
                procedural_patterns=[],
                consolidation_score=0.0,
                insights=[f"Consolidation failed: {str(e)}"]
            )
    
    async def _extract_semantic_knowledge(self, episode: Episode) -> List[str]:
        """Extract semantic knowledge from an episode"""
        try:
            updated_concepts = []
            
            # Extract entities and concepts from context and result
            entities = self._extract_entities(episode.context, episode.result)
            
            for entity_name, entity_data in entities.items():
                # Check if concept already exists
                existing_concepts = await self.semantic.find_concepts(
                    query=entity_name,
                    limit=1,
                    similarity_threshold=0.9
                )
                
                if existing_concepts:
                    # Update existing concept
                    concept_id = existing_concepts[0][0].id
                    await self._update_concept_from_episode(concept_id, entity_data, episode)
                    updated_concepts.append(concept_id)
                else:
                    # Create new concept
                    concept = create_concept(
                        name=entity_name,
                        description=entity_data.get('description', f'Concept extracted from episode {episode.id}'),
                        properties=entity_data
                    )
                    concept_id = await self.semantic.add_concept(concept)
                    updated_concepts.append(concept_id)
            
            # Extract relationships between entities
            relationships = self._extract_relationships(entities, episode)
            for rel_data in relationships:
                relationship = create_relationship(
                    source_concept_id=rel_data['source'],
                    target_concept_id=rel_data['target'],
                    relationship_type=rel_data['type'],
                    properties=rel_data.get('properties', {}),
                    strength=rel_data.get('strength', 0.8)
                )
                await self.semantic.add_relationship(relationship)
            
            return updated_concepts
            
        except Exception as e:
            print(f"Error extracting semantic knowledge: {e}")
            return []
    
    async def _identify_procedural_patterns(self, episode: Episode) -> List[str]:
        """Identify procedural patterns and skills from an episode"""
        try:
            identified_skills = []
            
            # Analyze action patterns
            action_pattern = self._analyze_action_pattern(episode)
            
            if action_pattern['complexity'] > self.skill_extraction_threshold:
                # Check if similar skill exists
                similar_skills = await self.procedural.find_skills(
                    tags=[episode.action],
                    limit=1
                )
                
                if similar_skills:
                    # Update existing skill with new execution data
                    skill_id = similar_skills[0].id
                    await self._update_skill_from_episode(skill_id, episode)
                    identified_skills.append(skill_id)
                else:
                    # Create new skill
                    skill = create_skill(
                        name=f"Skill: {episode.action}",
                        description=f"Skill extracted from episode {episode.id}",
                        skill_type=self._determine_skill_type(episode),
                        parameters_schema=self._extract_parameters_schema(episode),
                        execution_pattern=action_pattern,
                        tags=[episode.action] + episode.tags
                    )
                    skill_id = await self.procedural.add_skill(skill)
                    identified_skills.append(skill_id)
            
            return identified_skills
            
        except Exception as e:
            print(f"Error identifying procedural patterns: {e}")
            return []
    
    async def _calculate_consolidation_score(
        self,
        episode: Episode,
        semantic_updates: List[str],
        procedural_patterns: List[str]
    ) -> float:
        """Calculate how well the experience was consolidated"""
        try:
            score = 0.0
            
            # Base score from episode importance
            score += episode.importance_score * 0.3
            
            # Bonus for semantic knowledge extraction
            if semantic_updates:
                score += min(0.4, len(semantic_updates) * 0.1)
            
            # Bonus for procedural pattern identification
            if procedural_patterns:
                score += min(0.3, len(procedural_patterns) * 0.15)
            
            # Bonus for emotional significance
            score += abs(episode.emotional_valence) * 0.1
            
            return min(1.0, score)
            
        except Exception as e:
            print(f"Error calculating consolidation score: {e}")
            return 0.0
    
    async def _generate_insights(
        self,
        episode: Episode,
        semantic_updates: List[str],
        procedural_patterns: List[str]
    ) -> List[str]:
        """Generate insights from the consolidation process"""
        try:
            insights = []
            
            # Insight about semantic knowledge
            if semantic_updates:
                insights.append(
                    f"Updated {len(semantic_updates)} concepts in semantic memory"
                )
            
            # Insight about procedural patterns
            if procedural_patterns:
                insights.append(
                    f"Identified {len(procedural_patterns)} procedural patterns"
                )
            
            # Insight about emotional significance
            if abs(episode.emotional_valence) > 0.5:
                valence_type = "positive" if episode.emotional_valence > 0 else "negative"
                insights.append(
                    f"Experience has strong {valence_type} emotional significance"
                )
            
            # Insight about importance
            if episode.importance_score > 0.8:
                insights.append("Experience marked as highly important for future reference")
            
            return insights
            
        except Exception as e:
            print(f"Error generating insights: {e}")
            return []
    
    async def _background_consolidation(self):
        """Perform background memory consolidation tasks"""
        try:
            # Consolidate old episodic memories into semantic knowledge
            await self._consolidate_old_episodes()
            
            # Optimize procedural skills based on usage patterns
            await self._optimize_skills()
            
            # Update importance scores based on time decay
            await self._update_importance_scores()
            
        except Exception as e:
            print(f"Error in background consolidation: {e}")
    
    async def _consolidate_old_episodes(self):
        """Consolidate old episodic memories into semantic knowledge"""
        try:
            # Get episodes older than 30 days with high importance
            cutoff_date = datetime.now(timezone.utc) - timedelta(days=30)
            
            # This would require extending the episodic memory system to support time-based queries
            # For now, we'll skip this implementation
            pass
            
        except Exception as e:
            print(f"Error consolidating old episodes: {e}")
    
    async def _optimize_skills(self):
        """Optimize procedural skills based on usage patterns"""
        try:
            # Get all skills and optimize those with sufficient execution history
            stats = await self.procedural.get_procedural_stats()
            
            # This would iterate through skills and optimize them
            # Implementation depends on the specific optimization algorithms
            pass
            
        except Exception as e:
            print(f"Error optimizing skills: {e}")
    
    async def _update_importance_scores(self):
        """Update importance scores with time-based decay"""
        try:
            # This would implement importance decay over time
            # Requires extending the episodic memory system
            pass
            
        except Exception as e:
            print(f"Error updating importance scores: {e}")
    
    def _extract_entities(self, context: Dict[str, Any], result: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
        """Extract entities from context and result"""
        entities = {}
        
        # Simple entity extraction (in reality would use NLP)
        all_data = {**context, **result}
        
        for key, value in all_data.items():
            if isinstance(value, str) and len(value) > 3:
                entities[key] = {
                    'description': f'Entity from key: {key}',
                    'value': value,
                    'type': 'string'
                }
            elif isinstance(value, (int, float)):
                entities[key] = {
                    'description': f'Numeric entity from key: {key}',
                    'value': value,
                    'type': 'numeric'
                }
        
        return entities
    
    def _extract_relationships(self, entities: Dict[str, Dict[str, Any]], episode: Episode) -> List[Dict[str, Any]]:
        """Extract relationships between entities"""
        relationships = []
        
        # Simple relationship extraction
        entity_ids = list(entities.keys())
        
        for i, source in enumerate(entity_ids):
            for target in entity_ids[i+1:]:
                # Create a generic relationship
                relationships.append({
                    'source': source,
                    'target': target,
                    'type': 'co_occurs_with',
                    'properties': {'episode_id': episode.id},
                    'strength': 0.5
                })
        
        return relationships
    
    def _analyze_action_pattern(self, episode: Episode) -> Dict[str, Any]:
        """Analyze the action pattern in an episode"""
        pattern = {
            'action': episode.action,
            'complexity': len(episode.context) * 0.1 + len(str(episode.result)) * 0.01,
            'success_indicators': [],
            'failure_indicators': []
        }
        
        # Simple pattern analysis
        if 'success' in str(episode.result).lower():
            pattern['success_indicators'].append('success_keyword')
        if 'error' in str(episode.result).lower():
            pattern['failure_indicators'].append('error_keyword')
        
        return pattern
    
    def _determine_skill_type(self, episode: Episode) -> SkillType:
        """Determine the type of skill from an episode"""
        action_lower = episode.action.lower()
        
        if any(word in action_lower for word in ['analyze', 'calculate', 'compute']):
            return SkillType.ANALYTICAL
        elif any(word in action_lower for word in ['create', 'generate', 'design']):
            return SkillType.CREATIVE
        elif any(word in action_lower for word in ['communicate', 'interact', 'collaborate']):
            return SkillType.SOCIAL
        elif any(word in action_lower for word in ['move', 'execute', 'perform']):
            return SkillType.MOTOR
        else:
            return SkillType.COGNITIVE
    
    def _extract_parameters_schema(self, episode: Episode) -> Dict[str, Any]:
        """Extract parameters schema from episode context"""
        schema = {
            "type": "object",
            "properties": {},
            "required": []
        }
        
        for key, value in episode.context.items():
            if isinstance(value, str):
                schema["properties"][key] = {"type": "string"}
            elif isinstance(value, int):
                schema["properties"][key] = {"type": "integer"}
            elif isinstance(value, float):
                schema["properties"][key] = {"type": "number"}
            elif isinstance(value, bool):
                schema["properties"][key] = {"type": "boolean"}
            else:
                schema["properties"][key] = {"type": "object"}
        
        return schema
    
    async def _update_concept_from_episode(self, concept_id: str, entity_data: Dict[str, Any], episode: Episode):
        """Update an existing concept with new information from an episode"""
        try:
            updates = {
                'properties': {
                    f'episode_{episode.id}': entity_data,
                    'last_seen': episode.timestamp.isoformat()
                }
            }
            await self.semantic.update_concept(concept_id, updates)
        except Exception as e:
            print(f"Error updating concept {concept_id}: {e}")
    
    async def _update_skill_from_episode(self, skill_id: str, episode: Episode):
        """Update an existing skill with new execution data from an episode"""
        try:
            # This would create a skill execution record
            # For now, we'll just increment usage
            skill = await self.procedural.get_skill(skill_id)
            if skill:
                skill.usage_count += 1
        except Exception as e:
            print(f"Error updating skill {skill_id}: {e}")
    
    async def get_consolidation_stats(self) -> Dict[str, Any]:
        """Get statistics about the memory consolidation system"""
        try:
            episodic_stats = await self.episodic.get_memory_stats()
            semantic_stats = await self.semantic.get_knowledge_graph_stats()
            procedural_stats = await self.procedural.get_procedural_stats()
            
            return {
                "episodic_memory": episodic_stats,
                "semantic_memory": semantic_stats,
                "procedural_memory": procedural_stats,
                "consolidation_threshold": self.consolidation_threshold,
                "system_health": "operational"
            }
            
        except Exception as e:
            print(f"Error getting consolidation stats: {e}")
            return {"system_health": "error", "error": str(e)}
