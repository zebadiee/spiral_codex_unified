#!/usr/bin/env python3
"""
🧠 CONTEXTUAL REASONING ENGINE
Multi-layered intelligence that understands context, searches files, then generates
Similar to how humans reason: memory → research → creation
"""

import os
import json
import re
from pathlib import Path
from typing import List, Dict, Optional, Tuple, Any
from dataclasses import dataclass
from datetime import datetime
import subprocess

@dataclass
class ReasoningResult:
    """Result of contextual reasoning"""
    answer: str
    confidence: float
    source: str  # 'context', 'filesystem', 'ai', 'unknown'
    evidence: List[str]
    search_performed: bool
    files_consulted: List[Path]

@dataclass
class ConversationContext:
    """Current conversation context"""
    recent_messages: List[Dict[str, str]]
    mentioned_files: List[Path]
    mentioned_topics: List[str]
    current_task: Optional[str]
    working_directory: Path

class ContextualReasoningEngine:
    """
    Intelligent reasoning engine that:
    1. Analyzes conversation history for context
    2. Searches filesystem if context insufficient
    3. Uses AI as last resort
    """
    
    def __init__(self, conversation_history: Optional[List[Dict]] = None):
        self.conversation_history = conversation_history or []
        self.context = ConversationContext(
            recent_messages=[],
            mentioned_files=[],
            mentioned_topics=[],
            current_task=None,
            working_directory=Path.cwd()
        )
        
        # Knowledge extraction patterns
        self.entity_patterns = {
            'file': r'(?:file|document|pdf|xlsx?|csv|json)\s+(?:named|called)?\s*["\']?([^\s"\']+)["\']?',
            'path': r'([~\/][\w\/\.\-]+)',
            'project': r'(?:project|application|app)\s+(?:named|called)?\s*["\']?([^\s"\']+)["\']?',
            'template': r'template\s+(?:id=)?["\']?(\w+)["\']?',
            'certificate': r'(?:eicr|certificate|cert)\s+(?:for|at)?\s*["\']?([^\s"\']+)["\']?',
        }
        
        # Search domains - where to look for different types of info
        self.search_domains = {
            'eicr': [
                Path.home() / "Downloads",
                Path.home() / "Documents",
                Path.home() / "Documents/Obsidian",
            ],
            'template': [
                Path.cwd() / "templates",
                Path.home() / "Documents/spiral_codex_unified/templates",
            ],
            'code': [
                Path.cwd(),
                Path.home() / "Documents",
            ],
            'config': [
                Path.cwd() / "config",
                Path.home() / ".config",
                Path.home() / "Documents/config",
            ]
        }
    
    def reason(self, user_query: str, ai_fallback_fn=None) -> ReasoningResult:
        """
        Main reasoning pipeline:
        1. Extract context from conversation
        2. Try to answer from context
        3. Search filesystem if needed
        4. Use AI fallback if still uncertain
        """
        
        # Step 1: Update context with new query
        self._update_context(user_query)
        
        # Step 2: Try to answer from existing context
        context_answer = self._answer_from_context(user_query)
        if context_answer.confidence > 0.7:
            return context_answer
        
        # Step 3: Search filesystem for answer
        print("🔍 Context insufficient, searching filesystem...")
        filesystem_answer = self._answer_from_filesystem(user_query)
        if filesystem_answer.confidence > 0.6:
            return filesystem_answer
        
        # Step 4: AI fallback
        if ai_fallback_fn:
            print("🤖 Filesystem search incomplete, using AI reasoning...")
            ai_response = ai_fallback_fn(user_query, self.context)
            return ReasoningResult(
                answer=ai_response,
                confidence=0.8,
                source='ai',
                evidence=['AI generation'],
                search_performed=True,
                files_consulted=[]
            )
        
        return ReasoningResult(
            answer="I don't have enough information to answer that confidently.",
            confidence=0.3,
            source='unknown',
            evidence=[],
            search_performed=True,
            files_consulted=[]
        )
    
    def _update_context(self, user_query: str):
        """Extract and update context from user query"""
        # Extract entities
        for entity_type, pattern in self.entity_patterns.items():
            matches = re.findall(pattern, user_query, re.IGNORECASE)
            for match in matches:
                if entity_type == 'file' or entity_type == 'path':
                    path = Path(match).expanduser()
                    if path not in self.context.mentioned_files:
                        self.context.mentioned_files.append(path)
                elif entity_type == 'project':
                    if match not in self.context.mentioned_topics:
                        self.context.mentioned_topics.append(f"project:{match}")
        
        # Detect task type
        task_keywords = {
            'create': ['create', 'make', 'generate', 'build'],
            'read': ['show', 'display', 'read', 'view', 'what is', 'tell me'],
            'modify': ['change', 'update', 'modify', 'edit'],
            'analyze': ['analyze', 'check', 'validate', 'inspect'],
            'find': ['find', 'locate', 'search', 'look for'],
        }
        
        query_lower = user_query.lower()
        for task, keywords in task_keywords.items():
            if any(kw in query_lower for kw in keywords):
                self.context.current_task = task
                break
        
        # Add to recent messages
        self.context.recent_messages.append({
            'timestamp': datetime.now().isoformat(),
            'content': user_query
        })
        if len(self.context.recent_messages) > 10:
            self.context.recent_messages.pop(0)
    
    def _answer_from_context(self, query: str) -> ReasoningResult:
        """Try to answer from conversation context"""
        evidence = []
        confidence = 0.0
        
        query_lower = query.lower()
        
        # Check if referring to recently mentioned files
        if any(word in query_lower for word in ['it', 'that', 'this', 'the file', 'the template']):
            if self.context.mentioned_files:
                last_file = self.context.mentioned_files[-1]
                if last_file.exists():
                    evidence.append(f"Recently mentioned: {last_file}")
                    confidence = 0.9
                    
                    # Read file content if possible
                    try:
                        if last_file.suffix == '.json':
                            content = json.loads(last_file.read_text())
                            return ReasoningResult(
                                answer=f"The file is: {last_file}\n\n{json.dumps(content, indent=2)[:500]}...",
                                confidence=0.95,
                                source='context',
                                evidence=evidence,
                                search_performed=False,
                                files_consulted=[last_file]
                            )
                        elif last_file.suffix in ['.txt', '.md']:
                            content = last_file.read_text()[:500]
                            return ReasoningResult(
                                answer=f"The file is: {last_file}\n\n{content}...",
                                confidence=0.95,
                                source='context',
                                evidence=evidence,
                                search_performed=False,
                                files_consulted=[last_file]
                            )
                    except Exception as e:
                        pass
        
        # Check if question about current task
        if self.context.current_task:
            task_answers = {
                'create': "We're in creation mode. I can help you build files, projects, or certificates.",
                'find': "We're searching for something. Let me look in the filesystem.",
                'analyze': "We're analyzing data. I'll examine the relevant files.",
            }
            if self.context.current_task in task_answers:
                evidence.append(f"Current task: {self.context.current_task}")
                confidence = 0.6
        
        return ReasoningResult(
            answer="",
            confidence=confidence,
            source='context',
            evidence=evidence,
            search_performed=False,
            files_consulted=[]
        )
    
    def _answer_from_filesystem(self, query: str) -> ReasoningResult:
        """Search filesystem for answer"""
        query_lower = query.lower()
        files_found = []
        evidence = []
        
        # Determine what we're looking for
        search_type = self._detect_search_type(query_lower)
        search_paths = self.search_domains.get(search_type, [Path.cwd()])
        
        # Perform filesystem search
        for search_path in search_paths:
            if not search_path.exists():
                continue
            
            # Smart search based on query
            if 'eicr' in query_lower or 'certificate' in query_lower:
                found = self._search_files(search_path, ['.pdf', '.xlsx'], ['eicr', 'certificate', 'electrical'])
                files_found.extend(found)
            
            elif 'template' in query_lower:
                found = self._search_files(search_path, ['.json', '.yaml'], ['template'])
                files_found.extend(found)
            
            elif 'config' in query_lower or 'setting' in query_lower:
                found = self._search_files(search_path, ['.json', '.yaml', '.conf', '.ini'], ['config', 'settings'])
                files_found.extend(found)
            
            else:
                # Generic search - look for keywords from query
                keywords = [w for w in query_lower.split() if len(w) > 3]
                found = self._search_files(search_path, None, keywords[:3])
                files_found.extend(found)
        
        if files_found:
            # Analyze found files
            file_summaries = []
            for file_path in files_found[:5]:  # Top 5 results
                summary = self._summarize_file(file_path)
                if summary:
                    file_summaries.append(f"📄 {file_path.name}:\n  {summary}")
                    evidence.append(str(file_path))
            
            if file_summaries:
                answer = "🔍 Found relevant files:\n\n" + "\n\n".join(file_summaries)
                return ReasoningResult(
                    answer=answer,
                    confidence=0.8,
                    source='filesystem',
                    evidence=evidence,
                    search_performed=True,
                    files_consulted=files_found[:5]
                )
        
        return ReasoningResult(
            answer="",
            confidence=0.3,
            source='filesystem',
            evidence=evidence,
            search_performed=True,
            files_consulted=[]
        )
    
    def _detect_search_type(self, query: str) -> str:
        """Detect what type of thing to search for"""
        type_keywords = {
            'eicr': ['eicr', 'certificate', 'electrical', 'inspection'],
            'template': ['template', 'schema', 'format'],
            'code': ['script', 'code', 'program', 'function'],
            'config': ['config', 'setting', 'configuration', 'setup'],
        }
        
        for search_type, keywords in type_keywords.items():
            if any(kw in query for kw in keywords):
                return search_type
        
        return 'code'  # default
    
    def _search_files(self, base_path: Path, extensions: Optional[List[str]], keywords: List[str], max_depth: int = 3) -> List[Path]:
        """Search for files matching criteria"""
        matches = []
        
        try:
            for item in self._walk_limited(base_path, max_depth):
                if not item.is_file():
                    continue
                
                # Check extension
                if extensions and item.suffix.lower() not in extensions:
                    continue
                
                # Check keywords in filename
                filename_lower = item.name.lower()
                if keywords:
                    if not any(kw in filename_lower for kw in keywords):
                        continue
                
                matches.append(item)
                
                if len(matches) >= 20:  # Limit results
                    break
        except PermissionError:
            pass
        
        return matches
    
    def _walk_limited(self, path: Path, max_depth: int, current_depth: int = 0):
        """Limited depth directory walk"""
        skip_dirs = {'.git', '__pycache__', 'node_modules', '.venv', 'venv', 'build', 'dist'}
        
        if current_depth > max_depth:
            return
        
        try:
            for item in path.iterdir():
                if item.name.startswith('.') and item.name not in {'.env', '.config'}:
                    continue
                
                if item.is_dir():
                    if item.name not in skip_dirs:
                        yield item
                        yield from self._walk_limited(item, max_depth, current_depth + 1)
                else:
                    yield item
        except PermissionError:
            pass
    
    def _summarize_file(self, file_path: Path) -> Optional[str]:
        """Generate quick summary of file"""
        try:
            if file_path.suffix == '.json':
                data = json.loads(file_path.read_text())
                if isinstance(data, dict):
                    keys = list(data.keys())[:5]
                    return f"JSON with keys: {', '.join(keys)}"
                elif isinstance(data, list):
                    return f"JSON array with {len(data)} items"
            
            elif file_path.suffix in ['.txt', '.md']:
                lines = file_path.read_text().splitlines()
                if lines:
                    return f"{lines[0][:80]}..."
            
            elif file_path.suffix == '.pdf':
                stat = file_path.stat()
                return f"PDF document ({stat.st_size // 1024}KB)"
            
            elif file_path.suffix in ['.xlsx', '.xls']:
                stat = file_path.stat()
                return f"Excel workbook ({stat.st_size // 1024}KB)"
            
            return f"{file_path.suffix[1:].upper()} file"
        
        except Exception:
            return None
    
    def explain_reasoning(self, result: ReasoningResult) -> str:
        """Generate explanation of reasoning process"""
        explanation = [
            f"🧠 Reasoning Process:",
            f"  Confidence: {result.confidence*100:.0f}%",
            f"  Source: {result.source}",
        ]
        
        if result.search_performed:
            explanation.append(f"  Filesystem searched: Yes")
        
        if result.evidence:
            explanation.append(f"  Evidence: {len(result.evidence)} item(s)")
            for ev in result.evidence[:3]:
                explanation.append(f"    • {ev}")
        
        if result.files_consulted:
            explanation.append(f"  Files consulted: {len(result.files_consulted)}")
        
        return "\n".join(explanation)


def create_reasoning_engine(conversation_history: Optional[List[Dict]] = None) -> ContextualReasoningEngine:
    """Factory function to create reasoning engine"""
    return ContextualReasoningEngine(conversation_history)


if __name__ == "__main__":
    # Demo
    print("🧠 CONTEXTUAL REASONING ENGINE DEMO\n")
    
    engine = ContextualReasoningEngine()
    
    test_queries = [
        "find my EICR files",
        "what templates do I have?",
        "show me the configuration",
        "populate that template",
    ]
    
    for query in test_queries:
        print(f"\n{'='*60}")
        print(f"Query: {query}")
        print('='*60)
        result = engine.reason(query)
        print(result.answer)
        print()
        print(engine.explain_reasoning(result))
