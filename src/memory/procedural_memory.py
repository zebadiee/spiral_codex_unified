
"""
Procedural Memory System - Stores learned behaviors and skills
"""

import asyncio
import json
import uuid
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, asdict
from enum import Enum
import numpy as np


class SkillType(Enum):
    """Types of skills that can be stored"""
    COGNITIVE = "cognitive"
    MOTOR = "motor"
    SOCIAL = "social"
    CREATIVE = "creative"
    ANALYTICAL = "analytical"


@dataclass
class SkillExecution:
    """Represents a single execution of a skill"""
    id: str
    skill_id: str
    timestamp: datetime
    context: Dict[str, Any]
    parameters: Dict[str, Any]
    result: Dict[str, Any]
    success: bool
    execution_time: float  # seconds
    performance_score: float  # 0.0 to 1.0


@dataclass
class Skill:
    """Represents a learned skill or behavior pattern"""
    id: str
    name: str
    description: str
    skill_type: SkillType
    parameters_schema: Dict[str, Any]  # JSON schema for parameters
    execution_pattern: Dict[str, Any]  # Pattern for execution
    success_rate: float  # 0.0 to 1.0
    average_performance: float  # 0.0 to 1.0
    usage_count: int
    created_at: datetime
    updated_at: datetime
    prerequisites: List[str]  # IDs of prerequisite skills
    tags: List[str]
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now(timezone.utc)
        if self.updated_at is None:
            self.updated_at = datetime.now(timezone.utc)


class ProceduralMemorySystem:
    """
    Manages procedural memories - learned behaviors and skills
    with hierarchical skill trees and execution pattern recognition
    """
    
    def __init__(self, persist_directory: str = "./data/procedural_memory"):
        self.persist_directory = persist_directory
        self.skills: Dict[str, Skill] = {}
        self.executions: Dict[str, List[SkillExecution]] = {}
        self.skill_hierarchy: Dict[str, List[str]] = {}  # parent -> children
        self._load_from_disk()
    
    def _load_from_disk(self):
        """Load procedural memory from disk"""
        try:
            import os
            skills_file = os.path.join(self.persist_directory, "skills.json")
            executions_file = os.path.join(self.persist_directory, "executions.json")
            hierarchy_file = os.path.join(self.persist_directory, "hierarchy.json")
            
            os.makedirs(self.persist_directory, exist_ok=True)
            
            # Load skills
            if os.path.exists(skills_file):
                with open(skills_file, 'r') as f:
                    skills_data = json.load(f)
                    for skill_data in skills_data:
                        skill_data['skill_type'] = SkillType(skill_data['skill_type'])
                        skill_data['created_at'] = datetime.fromisoformat(skill_data['created_at'])
                        skill_data['updated_at'] = datetime.fromisoformat(skill_data['updated_at'])
                        skill = Skill(**skill_data)
                        self.skills[skill.id] = skill
            
            # Load executions
            if os.path.exists(executions_file):
                with open(executions_file, 'r') as f:
                    executions_data = json.load(f)
                    for skill_id, skill_executions in executions_data.items():
                        self.executions[skill_id] = []
                        for exec_data in skill_executions:
                            exec_data['timestamp'] = datetime.fromisoformat(exec_data['timestamp'])
                            execution = SkillExecution(**exec_data)
                            self.executions[skill_id].append(execution)
            
            # Load hierarchy
            if os.path.exists(hierarchy_file):
                with open(hierarchy_file, 'r') as f:
                    self.skill_hierarchy = json.load(f)
                    
        except Exception as e:
            print(f"Error loading procedural memory: {e}")
    
    def _save_to_disk(self):
        """Save procedural memory to disk"""
        try:
            import os
            skills_file = os.path.join(self.persist_directory, "skills.json")
            executions_file = os.path.join(self.persist_directory, "executions.json")
            hierarchy_file = os.path.join(self.persist_directory, "hierarchy.json")
            
            os.makedirs(self.persist_directory, exist_ok=True)
            
            # Save skills
            skills_data = []
            for skill in self.skills.values():
                skill_dict = asdict(skill)
                skill_dict['skill_type'] = skill.skill_type.value
                skill_dict['created_at'] = skill.created_at.isoformat()
                skill_dict['updated_at'] = skill.updated_at.isoformat()
                skills_data.append(skill_dict)
            
            with open(skills_file, 'w') as f:
                json.dump(skills_data, f, indent=2)
            
            # Save executions
            executions_data = {}
            for skill_id, skill_executions in self.executions.items():
                executions_data[skill_id] = []
                for execution in skill_executions:
                    exec_dict = asdict(execution)
                    exec_dict['timestamp'] = execution.timestamp.isoformat()
                    executions_data[skill_id].append(exec_dict)
            
            with open(executions_file, 'w') as f:
                json.dump(executions_data, f, indent=2)
            
            # Save hierarchy
            with open(hierarchy_file, 'w') as f:
                json.dump(self.skill_hierarchy, f, indent=2)
                
        except Exception as e:
            print(f"Error saving procedural memory: {e}")
    
    async def add_skill(self, skill: Skill) -> str:
        """Add a new skill to procedural memory"""
        try:
            self.skills[skill.id] = skill
            self.executions[skill.id] = []
            
            # Update hierarchy if prerequisites exist
            for prereq_id in skill.prerequisites:
                if prereq_id in self.skill_hierarchy:
                    self.skill_hierarchy[prereq_id].append(skill.id)
                else:
                    self.skill_hierarchy[prereq_id] = [skill.id]
            
            self._save_to_disk()
            return skill.id
            
        except Exception as e:
            print(f"Error adding skill {skill.id}: {e}")
            raise
    
    async def get_skill(self, skill_id: str) -> Optional[Skill]:
        """Retrieve a skill by ID"""
        return self.skills.get(skill_id)
    
    async def find_skills(
        self,
        skill_type: Optional[SkillType] = None,
        tags: Optional[List[str]] = None,
        min_success_rate: float = 0.0,
        limit: int = 10
    ) -> List[Skill]:
        """Find skills matching criteria"""
        try:
            matching_skills = []
            
            for skill in self.skills.values():
                # Filter by skill type
                if skill_type and skill.skill_type != skill_type:
                    continue
                
                # Filter by tags
                if tags and not any(tag in skill.tags for tag in tags):
                    continue
                
                # Filter by success rate
                if skill.success_rate < min_success_rate:
                    continue
                
                matching_skills.append(skill)
            
            # Sort by performance and usage
            matching_skills.sort(
                key=lambda s: (s.average_performance, s.usage_count),
                reverse=True
            )
            
            return matching_skills[:limit]
            
        except Exception as e:
            print(f"Error finding skills: {e}")
            return []
    
    async def execute_skill(
        self,
        skill_id: str,
        context: Dict[str, Any],
        parameters: Dict[str, Any]
    ) -> SkillExecution:
        """Execute a skill and record the execution"""
        try:
            skill = self.skills.get(skill_id)
            if not skill:
                raise ValueError(f"Skill {skill_id} not found")
            
            # Validate parameters against schema (simplified)
            if not self._validate_parameters(parameters, skill.parameters_schema):
                raise ValueError("Invalid parameters for skill execution")
            
            # Create execution record
            execution = SkillExecution(
                id=str(uuid.uuid4()),
                skill_id=skill_id,
                timestamp=datetime.now(timezone.utc),
                context=context,
                parameters=parameters,
                result={},  # Will be filled by actual execution
                success=False,  # Will be updated
                execution_time=0.0,  # Will be measured
                performance_score=0.0  # Will be calculated
            )
            
            # Simulate skill execution (in real implementation, this would call actual skill logic)
            start_time = datetime.now(timezone.utc)
            
            try:
                # Execute the skill pattern
                result = await self._execute_skill_pattern(skill, context, parameters)
                execution.result = result
                execution.success = True
                execution.performance_score = self._calculate_performance_score(skill, result)
                
            except Exception as e:
                execution.result = {"error": str(e)}
                execution.success = False
                execution.performance_score = 0.0
            
            end_time = datetime.now(timezone.utc)
            execution.execution_time = (end_time - start_time).total_seconds()
            
            # Record execution
            if skill_id not in self.executions:
                self.executions[skill_id] = []
            self.executions[skill_id].append(execution)
            
            # Update skill statistics
            await self._update_skill_stats(skill_id)
            
            self._save_to_disk()
            return execution
            
        except Exception as e:
            print(f"Error executing skill {skill_id}: {e}")
            raise
    
    async def get_skill_executions(
        self,
        skill_id: str,
        limit: int = 10,
        successful_only: bool = False
    ) -> List[SkillExecution]:
        """Get execution history for a skill"""
        try:
            executions = self.executions.get(skill_id, [])
            
            if successful_only:
                executions = [e for e in executions if e.success]
            
            # Sort by timestamp (most recent first)
            executions.sort(key=lambda e: e.timestamp, reverse=True)
            
            return executions[:limit]
            
        except Exception as e:
            print(f"Error getting skill executions: {e}")
            return []
    
    async def get_skill_hierarchy(self, skill_id: str) -> Dict[str, Any]:
        """Get the hierarchical relationships for a skill"""
        try:
            skill = self.skills.get(skill_id)
            if not skill:
                return {}
            
            # Get prerequisites (parents)
            prerequisites = []
            for prereq_id in skill.prerequisites:
                prereq_skill = self.skills.get(prereq_id)
                if prereq_skill:
                    prerequisites.append({
                        "id": prereq_id,
                        "name": prereq_skill.name,
                        "success_rate": prereq_skill.success_rate
                    })
            
            # Get dependent skills (children)
            dependents = []
            for dependent_id in self.skill_hierarchy.get(skill_id, []):
                dependent_skill = self.skills.get(dependent_id)
                if dependent_skill:
                    dependents.append({
                        "id": dependent_id,
                        "name": dependent_skill.name,
                        "success_rate": dependent_skill.success_rate
                    })
            
            return {
                "skill": {
                    "id": skill_id,
                    "name": skill.name,
                    "success_rate": skill.success_rate
                },
                "prerequisites": prerequisites,
                "dependents": dependents
            }
            
        except Exception as e:
            print(f"Error getting skill hierarchy: {e}")
            return {}
    
    async def optimize_skill(self, skill_id: str) -> Dict[str, Any]:
        """Optimize a skill based on execution history"""
        try:
            skill = self.skills.get(skill_id)
            executions = self.executions.get(skill_id, [])
            
            if not skill or not executions:
                return {"status": "no_data"}
            
            # Analyze successful executions
            successful_executions = [e for e in executions if e.success]
            if not successful_executions:
                return {"status": "no_successful_executions"}
            
            # Find optimal parameters
            optimal_params = self._find_optimal_parameters(successful_executions)
            
            # Update skill pattern
            if optimal_params:
                skill.execution_pattern.update(optimal_params)
                skill.updated_at = datetime.now(timezone.utc)
                self._save_to_disk()
            
            return {
                "status": "optimized",
                "optimal_parameters": optimal_params,
                "improvement_potential": self._calculate_improvement_potential(executions)
            }
            
        except Exception as e:
            print(f"Error optimizing skill {skill_id}: {e}")
            return {"status": "error", "message": str(e)}
    
    async def get_procedural_stats(self) -> Dict[str, Any]:
        """Get statistics about the procedural memory system"""
        try:
            skill_types = {}
            total_executions = 0
            successful_executions = 0
            
            for skill in self.skills.values():
                skill_type = skill.skill_type.value
                skill_types[skill_type] = skill_types.get(skill_type, 0) + 1
            
            for executions in self.executions.values():
                total_executions += len(executions)
                successful_executions += sum(1 for e in executions if e.success)
            
            overall_success_rate = (
                successful_executions / total_executions 
                if total_executions > 0 else 0.0
            )
            
            return {
                "total_skills": len(self.skills),
                "skill_types": skill_types,
                "total_executions": total_executions,
                "successful_executions": successful_executions,
                "overall_success_rate": overall_success_rate,
                "average_skill_performance": np.mean([s.average_performance for s in self.skills.values()]) if self.skills else 0.0
            }
            
        except Exception as e:
            print(f"Error getting procedural stats: {e}")
            return {}
    
    def _validate_parameters(self, parameters: Dict[str, Any], schema: Dict[str, Any]) -> bool:
        """Validate parameters against schema (simplified implementation)"""
        # In a real implementation, this would use jsonschema
        required_params = schema.get("required", [])
        return all(param in parameters for param in required_params)
    
    async def _execute_skill_pattern(
        self,
        skill: Skill,
        context: Dict[str, Any],
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute the skill pattern (placeholder implementation)"""
        # This would contain the actual skill execution logic
        # For now, simulate based on skill success rate
        import random
        
        success_probability = skill.success_rate
        if random.random() < success_probability:
            return {
                "status": "success",
                "output": f"Skill {skill.name} executed successfully",
                "context_used": context,
                "parameters_used": parameters
            }
        else:
            raise Exception(f"Skill {skill.name} execution failed")
    
    def _calculate_performance_score(self, skill: Skill, result: Dict[str, Any]) -> float:
        """Calculate performance score for an execution"""
        # Simplified scoring based on result
        if result.get("status") == "success":
            return min(1.0, skill.average_performance + 0.1)
        return 0.0
    
    async def _update_skill_stats(self, skill_id: str):
        """Update skill statistics based on execution history"""
        try:
            skill = self.skills[skill_id]
            executions = self.executions[skill_id]
            
            if not executions:
                return
            
            # Update usage count
            skill.usage_count = len(executions)
            
            # Update success rate
            successful = sum(1 for e in executions if e.success)
            skill.success_rate = successful / len(executions)
            
            # Update average performance
            performance_scores = [e.performance_score for e in executions if e.success]
            if performance_scores:
                skill.average_performance = np.mean(performance_scores)
            
            skill.updated_at = datetime.now(timezone.utc)
            
        except Exception as e:
            print(f"Error updating skill stats: {e}")
    
    def _find_optimal_parameters(self, executions: List[SkillExecution]) -> Dict[str, Any]:
        """Find optimal parameters from successful executions"""
        # Simplified implementation - in reality would use more sophisticated analysis
        if not executions:
            return {}
        
        # Find the execution with highest performance score
        best_execution = max(executions, key=lambda e: e.performance_score)
        return best_execution.parameters
    
    def _calculate_improvement_potential(self, executions: List[SkillExecution]) -> float:
        """Calculate potential for improvement based on execution variance"""
        if len(executions) < 2:
            return 0.0
        
        performance_scores = [e.performance_score for e in executions]
        variance = np.var(performance_scores)
        
        # Higher variance suggests more room for improvement
        return min(1.0, variance * 2)


# Factory function
def create_skill(
    name: str,
    description: str,
    skill_type: SkillType,
    parameters_schema: Dict[str, Any],
    execution_pattern: Optional[Dict[str, Any]] = None,
    prerequisites: Optional[List[str]] = None,
    tags: Optional[List[str]] = None
) -> Skill:
    """Factory function to create a new skill"""
    return Skill(
        id=str(uuid.uuid4()),
        name=name,
        description=description,
        skill_type=skill_type,
        parameters_schema=parameters_schema,
        execution_pattern=execution_pattern or {},
        success_rate=0.0,
        average_performance=0.0,
        usage_count=0,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
        prerequisites=prerequisites or [],
        tags=tags or []
    )
