#!/usr/bin/env python3
"""
🧠 AUTONOMOUS INTELLIGENCE MODULE
Gives SPIRAL commonsense file discovery and autonomous task execution
Similar to GitHub Copilot CLI's intelligent behavior
"""

import os
import json
import re
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
import mimetypes

@dataclass
class FileDiscovery:
    """Result of autonomous file discovery"""
    path: Path
    file_type: str
    confidence: float
    reason: str

@dataclass
class TaskPlan:
    """Autonomous task execution plan"""
    task_description: str
    steps: List[Dict]
    files_needed: List[Path]
    estimated_complexity: str
    confidence: float

class AutonomousIntelligence:
    """
    Provides autonomous intelligence for file discovery and task execution.
    Makes SPIRAL smart enough to explore, locate, and process without hand-holding.
    """
    
    def __init__(self, base_paths: Optional[List[str]] = None):
        self.base_paths = base_paths or [
            str(Path.home() / "Documents"),
            str(Path.home() / "Downloads"),
            str(Path.cwd())
        ]
        
        # File type patterns for intelligent recognition
        self.file_patterns = {
            'eicr': {
                'extensions': ['.pdf', '.xlsx', '.xls', '.docx'],
                'keywords': ['eicr', 'electrical', 'installation', 'condition', 'report', 'certificate'],
                'patterns': [r'eicr', r'electrical.*cert', r'test.*result', r'inspection']
            },
            'certificate': {
                'extensions': ['.pdf', '.xlsx', '.docx'],
                'keywords': ['certificate', 'cert', 'inspection', 'test'],
                'patterns': [r'cert', r'inspection', r'test.*report']
            },
            'circuit_data': {
                'extensions': ['.xlsx', '.xls', '.csv'],
                'keywords': ['circuit', 'schedule', 'breaker', 'mcb', 'rcd'],
                'patterns': [r'circuit', r'schedule', r'distribution.*board']
            },
            'template': {
                'extensions': ['.json', '.yaml', '.yml'],
                'keywords': ['template', 'schema'],
                'patterns': [r'\.template\.', r'schema']
            }
        }
        
        # Task understanding patterns
        self.task_patterns = {
            'populate_template': {
                'triggers': ['populate', 'fill', 'complete', 'build'],
                'requires': ['template', 'source_data'],
                'complexity': 'medium'
            },
            'scan_document': {
                'triggers': ['scan', 'read', 'extract', 'analyze'],
                'requires': ['document'],
                'complexity': 'low'
            },
            'create_certificate': {
                'triggers': ['create', 'generate', 'build', 'make'],
                'requires': ['template', 'data'],
                'complexity': 'high'
            },
            'find_files': {
                'triggers': ['find', 'locate', 'search', 'look for'],
                'requires': [],
                'complexity': 'low'
            }
        }
    
    def understand_request(self, user_input: str) -> TaskPlan:
        """
        Autonomous understanding of user intent.
        Similar to how Copilot CLI understands natural language commands.
        """
        user_lower = user_input.lower()
        
        # Detect task type
        detected_task = None
        for task_type, config in self.task_patterns.items():
            if any(trigger in user_lower for trigger in config['triggers']):
                detected_task = task_type
                break
        
        if not detected_task:
            detected_task = 'general'
        
        # Extract file references from input
        file_hints = self._extract_file_hints(user_input)
        
        # Build execution plan
        steps = self._generate_task_steps(detected_task, file_hints, user_input)
        files_needed = self._identify_needed_files(detected_task, file_hints)
        
        return TaskPlan(
            task_description=detected_task,
            steps=steps,
            files_needed=files_needed,
            estimated_complexity=self.task_patterns.get(detected_task, {}).get('complexity', 'medium'),
            confidence=0.85 if detected_task != 'general' else 0.5
        )
    
    def autonomous_file_search(self, file_type: str, search_paths: Optional[List[str]] = None) -> List[FileDiscovery]:
        """
        Intelligently search for files without explicit paths.
        Like Copilot CLI's ability to "just know" where things are.
        """
        search_paths = search_paths or self.base_paths
        discoveries = []
        
        for base_path in search_paths:
            base = Path(base_path).expanduser()
            if not base.exists():
                continue
            
            # Smart recursive search with depth limit
            for item in self._smart_walk(base, max_depth=3):
                if item.is_file():
                    match_result = self._match_file_type(item, file_type)
                    if match_result:
                        discoveries.append(match_result)
        
        # Sort by confidence
        discoveries.sort(key=lambda x: x.confidence, reverse=True)
        return discoveries[:10]  # Top 10 results
    
    def _smart_walk(self, path: Path, max_depth: int = 3, current_depth: int = 0):
        """Smart directory walk that avoids common noise directories"""
        skip_dirs = {
            'node_modules', '.git', '__pycache__', '.venv', 'venv',
            '.cache', 'build', 'dist', '.pytest_cache', '.mypy_cache'
        }
        
        if current_depth > max_depth:
            return
        
        try:
            for item in path.iterdir():
                if item.name.startswith('.') and item.name not in {'.env', '.config'}:
                    continue
                
                if item.is_dir():
                    if item.name not in skip_dirs:
                        yield item
                        yield from self._smart_walk(item, max_depth, current_depth + 1)
                else:
                    yield item
        except PermissionError:
            pass
    
    def _match_file_type(self, file_path: Path, target_type: str) -> Optional[FileDiscovery]:
        """Match file against type patterns with confidence scoring"""
        if target_type not in self.file_patterns:
            return None
        
        config = self.file_patterns[target_type]
        confidence = 0.0
        reasons = []
        
        # Check extension
        if file_path.suffix.lower() in config['extensions']:
            confidence += 0.3
            reasons.append(f"extension: {file_path.suffix}")
        
        # Check filename keywords
        filename_lower = file_path.name.lower()
        keyword_matches = [kw for kw in config['keywords'] if kw in filename_lower]
        if keyword_matches:
            confidence += 0.4 * (len(keyword_matches) / len(config['keywords']))
            reasons.append(f"keywords: {', '.join(keyword_matches)}")
        
        # Check regex patterns
        for pattern in config['patterns']:
            if re.search(pattern, filename_lower):
                confidence += 0.3
                reasons.append(f"pattern: {pattern}")
                break
        
        # Require minimum confidence
        if confidence < 0.3:
            return None
        
        return FileDiscovery(
            path=file_path,
            file_type=target_type,
            confidence=min(1.0, confidence),
            reason=" | ".join(reasons)
        )
    
    def _extract_file_hints(self, user_input: str) -> Dict[str, List[str]]:
        """Extract file-related hints from natural language"""
        hints = {
            'paths': [],
            'types': [],
            'keywords': []
        }
        
        # Extract explicit paths
        path_pattern = r'([~\/][\w\/\.\-]+)'
        hints['paths'] = re.findall(path_pattern, user_input)
        
        # Extract file type hints
        for file_type in self.file_patterns.keys():
            if file_type in user_input.lower():
                hints['types'].append(file_type)
        
        # Extract extension hints
        ext_pattern = r'\.(pdf|xlsx?|csv|docx?|json|ya?ml)'
        hints['keywords'].extend(re.findall(ext_pattern, user_input.lower()))
        
        return hints
    
    def _identify_needed_files(self, task_type: str, file_hints: Dict) -> List[Path]:
        """Autonomously identify files needed for task"""
        needed = []
        
        # If explicit paths given, use them
        for path_str in file_hints.get('paths', []):
            path = Path(path_str).expanduser()
            if path.exists():
                needed.append(path)
        
        # Auto-discover based on task requirements
        if task_type in self.task_patterns:
            requirements = self.task_patterns[task_type]['requires']
            for req in requirements:
                if req in file_hints.get('types', []):
                    continue  # Already have explicit hint
                
                # Auto-search
                discoveries = self.autonomous_file_search(req)
                if discoveries:
                    needed.append(discoveries[0].path)  # Best match
        
        return needed
    
    def _generate_task_steps(self, task_type: str, file_hints: Dict, user_input: str) -> List[Dict]:
        """Generate autonomous execution steps"""
        
        steps_map = {
            'populate_template': [
                {'action': 'locate_template', 'description': 'Find or verify template file'},
                {'action': 'locate_source_data', 'description': 'Find source data (PDF/Excel)'},
                {'action': 'extract_data', 'description': 'Extract data from source'},
                {'action': 'map_fields', 'description': 'Map source fields to template'},
                {'action': 'validate', 'description': 'Validate populated template'},
                {'action': 'output', 'description': 'Generate final output'}
            ],
            'scan_document': [
                {'action': 'locate_document', 'description': 'Find document to scan'},
                {'action': 'analyze_structure', 'description': 'Analyze document structure'},
                {'action': 'extract_data', 'description': 'Extract relevant data'},
                {'action': 'format_output', 'description': 'Format extracted data'}
            ],
            'create_certificate': [
                {'action': 'load_template', 'description': 'Load certificate template'},
                {'action': 'gather_data', 'description': 'Gather required data'},
                {'action': 'populate_fields', 'description': 'Populate certificate fields'},
                {'action': 'validate_bs7671', 'description': 'Validate against BS7671 standards'},
                {'action': 'generate_output', 'description': 'Generate certificate PDF/document'}
            ],
            'find_files': [
                {'action': 'analyze_search_criteria', 'description': 'Understand what to find'},
                {'action': 'search_filesystem', 'description': 'Search filesystem intelligently'},
                {'action': 'rank_results', 'description': 'Rank results by relevance'},
                {'action': 'present_findings', 'description': 'Present discovered files'}
            ]
        }
        
        return steps_map.get(task_type, [
            {'action': 'analyze', 'description': 'Analyze user request'},
            {'action': 'execute', 'description': 'Execute appropriate action'},
            {'action': 'respond', 'description': 'Provide response'}
        ])
    
    def explain_plan(self, plan: TaskPlan) -> str:
        """Generate human-readable explanation of autonomous plan"""
        explanation = [
            f"🧠 Autonomous Analysis:",
            f"  Task: {plan.task_description}",
            f"  Complexity: {plan.estimated_complexity}",
            f"  Confidence: {plan.confidence*100:.0f}%",
            "",
            f"📋 Execution Plan ({len(plan.steps)} steps):"
        ]
        
        for i, step in enumerate(plan.steps, 1):
            explanation.append(f"  {i}. {step['description']}")
        
        if plan.files_needed:
            explanation.append("")
            explanation.append("📁 Files Identified:")
            for file in plan.files_needed:
                explanation.append(f"  • {file}")
        
        return "\n".join(explanation)
    
    def locate_eicr_files(self, search_hint: Optional[str] = None) -> List[FileDiscovery]:
        """Convenience method: autonomously locate EICR files"""
        print("🔍 Autonomously searching for EICR files...")
        
        # Expand search if hint provided
        search_paths = self.base_paths.copy()
        if search_hint:
            hint_path = Path(search_hint).expanduser()
            if hint_path.exists():
                search_paths.insert(0, str(hint_path))
        
        discoveries = self.autonomous_file_search('eicr', search_paths)
        
        if discoveries:
            print(f"✅ Found {len(discoveries)} potential EICR files:")
            for i, disc in enumerate(discoveries[:5], 1):
                print(f"  {i}. {disc.path.name} ({disc.confidence*100:.0f}% confidence)")
                print(f"     Location: {disc.path.parent}")
                print(f"     Reason: {disc.reason}")
        else:
            print("❌ No EICR files found in accessible locations")
        
        return discoveries


# Singleton instance
_autonomous_intelligence = None

def get_autonomous_intelligence() -> AutonomousIntelligence:
    """Get or create singleton autonomous intelligence instance"""
    global _autonomous_intelligence
    if _autonomous_intelligence is None:
        _autonomous_intelligence = AutonomousIntelligence()
    return _autonomous_intelligence


if __name__ == "__main__":
    # Demo autonomous intelligence
    ai = AutonomousIntelligence()
    
    print("🧠 AUTONOMOUS INTELLIGENCE DEMO\n")
    
    # Test 1: Understand request
    test_requests = [
        "I want to populate the EICR template",
        "Find all EICR files in Downloads",
        "Create a certificate from the template",
        "Scan that PDF and extract the circuit data"
    ]
    
    for request in test_requests:
        print(f"\n{'='*60}")
        print(f"Request: {request}")
        print('='*60)
        plan = ai.understand_request(request)
        print(ai.explain_plan(plan))
    
    # Test 2: Autonomous file discovery
    print(f"\n\n{'='*60}")
    print("AUTONOMOUS FILE DISCOVERY TEST")
    print('='*60)
    eicr_files = ai.locate_eicr_files()
