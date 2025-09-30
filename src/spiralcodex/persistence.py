
"""
💾 Spiral Codex Persistence - Data Storage and State Management

SQLite and JSON-based persistence system for storing agent states,
ritual events, configuration, and system metrics.
"""

import json
import sqlite3
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
import threading

@dataclass
class AgentRecord:
    """Agent state record for persistence"""
    agent_id: str
    name: str
    type: str
    status: str
    recursion_depth: int
    entropy_level: float
    metadata: Dict[str, Any]
    created_at: datetime
    updated_at: datetime

@dataclass
class RitualEventRecord:
    """Ritual event record for persistence"""
    event_id: str
    timestamp: datetime
    event_type: str
    description: str
    agent_id: Optional[str]
    metadata: Dict[str, Any]
    severity: str = "INFO"

@dataclass
class SystemMetricsRecord:
    """System metrics record for persistence"""
    timestamp: datetime
    agent_count: int
    total_recursion_depth: int
    average_entropy: float
    system_status: str
    uptime: float
    memory_usage: Optional[float] = None
    cpu_usage: Optional[float] = None

class CodexDatabase:
    """SQLite database manager for Codex persistence"""
    
    def __init__(self, db_path: Optional[Path] = None):
        if db_path is None:
            db_path = Path("codex_root/data/codex.db")
        
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Thread-local storage for connections
        self._local = threading.local()
        
        # Initialize database
        self._init_database()
    
    def _get_connection(self) -> sqlite3.Connection:
        """Get thread-local database connection"""
        if not hasattr(self._local, 'connection'):
            self._local.connection = sqlite3.connect(
                str(self.db_path),
                check_same_thread=False,
                timeout=30.0
            )
            self._local.connection.row_factory = sqlite3.Row
        return self._local.connection
    
    def _init_database(self):
        """Initialize database tables"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Agents table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS agents (
                agent_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                type TEXT NOT NULL,
                status TEXT NOT NULL,
                recursion_depth INTEGER DEFAULT 0,
                entropy_level REAL DEFAULT 0.5,
                metadata TEXT DEFAULT '{}',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Ritual events table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ritual_events (
                event_id TEXT PRIMARY KEY,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                event_type TEXT NOT NULL,
                description TEXT NOT NULL,
                agent_id TEXT,
                metadata TEXT DEFAULT '{}',
                severity TEXT DEFAULT 'INFO',
                FOREIGN KEY (agent_id) REFERENCES agents (agent_id)
            )
        """)
        
        # System metrics table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS system_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                agent_count INTEGER DEFAULT 0,
                total_recursion_depth INTEGER DEFAULT 0,
                average_entropy REAL DEFAULT 0.5,
                system_status TEXT DEFAULT 'UNKNOWN',
                uptime REAL DEFAULT 0.0,
                memory_usage REAL,
                cpu_usage REAL
            )
        """)
        
        # Configuration table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS configuration (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                type TEXT DEFAULT 'string',
                description TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create indexes for performance
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_agents_status ON agents(status)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_events_timestamp ON ritual_events(timestamp)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_events_type ON ritual_events(event_type)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_metrics_timestamp ON system_metrics(timestamp)")
        
        conn.commit()
        print("💾 Database initialized successfully")
    
    def save_agent(self, agent: AgentRecord):
        """Save or update agent record"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO agents 
            (agent_id, name, type, status, recursion_depth, entropy_level, metadata, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            agent.agent_id,
            agent.name,
            agent.type,
            agent.status,
            agent.recursion_depth,
            agent.entropy_level,
            json.dumps(agent.metadata),
            agent.created_at.isoformat(),
            agent.updated_at.isoformat()
        ))
        
        conn.commit()
    
    def get_agent(self, agent_id: str) -> Optional[AgentRecord]:
        """Get agent record by ID"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM agents WHERE agent_id = ?", (agent_id,))
        row = cursor.fetchone()
        
        if row:
            return AgentRecord(
                agent_id=row['agent_id'],
                name=row['name'],
                type=row['type'],
                status=row['status'],
                recursion_depth=row['recursion_depth'],
                entropy_level=row['entropy_level'],
                metadata=json.loads(row['metadata']),
                created_at=datetime.fromisoformat(row['created_at']),
                updated_at=datetime.fromisoformat(row['updated_at'])
            )
        return None
    
    def get_all_agents(self) -> List[AgentRecord]:
        """Get all agent records"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM agents ORDER BY updated_at DESC")
        rows = cursor.fetchall()
        
        agents = []
        for row in rows:
            agents.append(AgentRecord(
                agent_id=row['agent_id'],
                name=row['name'],
                type=row['type'],
                status=row['status'],
                recursion_depth=row['recursion_depth'],
                entropy_level=row['entropy_level'],
                metadata=json.loads(row['metadata']),
                created_at=datetime.fromisoformat(row['created_at']),
                updated_at=datetime.fromisoformat(row['updated_at'])
            ))
        
        return agents
    
    def delete_agent(self, agent_id: str):
        """Delete agent record"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM agents WHERE agent_id = ?", (agent_id,))
        conn.commit()
    
    def save_ritual_event(self, event: RitualEventRecord):
        """Save ritual event"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO ritual_events 
            (event_id, timestamp, event_type, description, agent_id, metadata, severity)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            event.event_id,
            event.timestamp.isoformat(),
            event.event_type,
            event.description,
            event.agent_id,
            json.dumps(event.metadata),
            event.severity
        ))
        
        conn.commit()
    
    def get_ritual_events(self, limit: int = 100, event_type: Optional[str] = None,
                         since: Optional[datetime] = None) -> List[RitualEventRecord]:
        """Get ritual events with optional filtering"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        query = "SELECT * FROM ritual_events"
        params = []
        conditions = []
        
        if event_type:
            conditions.append("event_type = ?")
            params.append(event_type)
        
        if since:
            conditions.append("timestamp >= ?")
            params.append(since.isoformat())
        
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        
        query += " ORDER BY timestamp DESC LIMIT ?"
        params.append(limit)
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        events = []
        for row in rows:
            events.append(RitualEventRecord(
                event_id=row['event_id'],
                timestamp=datetime.fromisoformat(row['timestamp']),
                event_type=row['event_type'],
                description=row['description'],
                agent_id=row['agent_id'],
                metadata=json.loads(row['metadata']),
                severity=row['severity']
            ))
        
        return events
    
    def save_system_metrics(self, metrics: SystemMetricsRecord):
        """Save system metrics"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO system_metrics 
            (timestamp, agent_count, total_recursion_depth, average_entropy, 
             system_status, uptime, memory_usage, cpu_usage)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            metrics.timestamp.isoformat(),
            metrics.agent_count,
            metrics.total_recursion_depth,
            metrics.average_entropy,
            metrics.system_status,
            metrics.uptime,
            metrics.memory_usage,
            metrics.cpu_usage
        ))
        
        conn.commit()
    
    def get_system_metrics(self, limit: int = 100, 
                          since: Optional[datetime] = None) -> List[SystemMetricsRecord]:
        """Get system metrics history"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        query = "SELECT * FROM system_metrics"
        params = []
        
        if since:
            query += " WHERE timestamp >= ?"
            params.append(since.isoformat())
        
        query += " ORDER BY timestamp DESC LIMIT ?"
        params.append(limit)
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        metrics = []
        for row in rows:
            metrics.append(SystemMetricsRecord(
                timestamp=datetime.fromisoformat(row['timestamp']),
                agent_count=row['agent_count'],
                total_recursion_depth=row['total_recursion_depth'],
                average_entropy=row['average_entropy'],
                system_status=row['system_status'],
                uptime=row['uptime'],
                memory_usage=row['memory_usage'],
                cpu_usage=row['cpu_usage']
            ))
        
        return metrics
    
    def cleanup_old_data(self, days_to_keep: int = 30):
        """Clean up old data to prevent database bloat"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cutoff_date = datetime.now() - timedelta(days=days_to_keep)
        
        # Clean old ritual events
        cursor.execute("DELETE FROM ritual_events WHERE timestamp < ?", 
                      (cutoff_date.isoformat(),))
        events_deleted = cursor.rowcount
        
        # Clean old system metrics
        cursor.execute("DELETE FROM system_metrics WHERE timestamp < ?", 
                      (cutoff_date.isoformat(),))
        metrics_deleted = cursor.rowcount
        
        conn.commit()
        
        print(f"💾 Cleaned up {events_deleted} old events and {metrics_deleted} old metrics")
    
    def get_config(self, key: str) -> Optional[Any]:
        """Get configuration value"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT value, type FROM configuration WHERE key = ?", (key,))
        row = cursor.fetchone()
        
        if row:
            value = row['value']
            value_type = row['type']
            
            # Convert based on type
            if value_type == 'int':
                return int(value)
            elif value_type == 'float':
                return float(value)
            elif value_type == 'bool':
                return value.lower() == 'true'
            elif value_type == 'json':
                return json.loads(value)
            else:
                return value
        
        return None
    
    def set_config(self, key: str, value: Any, description: Optional[str] = None):
        """Set configuration value"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Determine type and serialize value
        if isinstance(value, bool):
            value_type = 'bool'
            value_str = str(value).lower()
        elif isinstance(value, int):
            value_type = 'int'
            value_str = str(value)
        elif isinstance(value, float):
            value_type = 'float'
            value_str = str(value)
        elif isinstance(value, (dict, list)):
            value_type = 'json'
            value_str = json.dumps(value)
        else:
            value_type = 'string'
            value_str = str(value)
        
        cursor.execute("""
            INSERT OR REPLACE INTO configuration 
            (key, value, type, description, updated_at)
            VALUES (?, ?, ?, ?, ?)
        """, (key, value_str, value_type, description, datetime.now().isoformat()))
        
        conn.commit()

class JSONPersistence:
    """JSON-based persistence for lightweight storage"""
    
    def __init__(self, data_dir: Optional[Path] = None):
        if data_dir is None:
            data_dir = Path("codex_root/data/json")
        
        self.data_dir = data_dir
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # File paths
        self.agents_file = self.data_dir / "agents.json"
        self.events_file = self.data_dir / "ritual_events.json"
        self.metrics_file = self.data_dir / "system_metrics.json"
        self.config_file = self.data_dir / "configuration.json"
        
        # Thread lock for file operations
        self._lock = threading.Lock()
    
    def _load_json(self, file_path: Path) -> Dict[str, Any]:
        """Load JSON data from file"""
        if file_path.exists():
            try:
                with open(file_path, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"⚠️ Failed to load {file_path}: {e}")
        return {}
    
    def _save_json(self, file_path: Path, data: Dict[str, Any]):
        """Save JSON data to file"""
        try:
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=2, default=str)
        except Exception as e:
            print(f"⚠️ Failed to save {file_path}: {e}")
    
    def save_agent(self, agent: AgentRecord):
        """Save agent to JSON"""
        with self._lock:
            agents = self._load_json(self.agents_file)
            agents[agent.agent_id] = asdict(agent)
            self._save_json(self.agents_file, agents)
    
    def get_agent(self, agent_id: str) -> Optional[AgentRecord]:
        """Get agent from JSON"""
        agents = self._load_json(self.agents_file)
        if agent_id in agents:
            data = agents[agent_id]
            return AgentRecord(
                agent_id=data['agent_id'],
                name=data['name'],
                type=data['type'],
                status=data['status'],
                recursion_depth=data['recursion_depth'],
                entropy_level=data['entropy_level'],
                metadata=data['metadata'],
                created_at=datetime.fromisoformat(data['created_at']),
                updated_at=datetime.fromisoformat(data['updated_at'])
            )
        return None
    
    def get_all_agents(self) -> List[AgentRecord]:
        """Get all agents from JSON"""
        agents = self._load_json(self.agents_file)
        result = []
        
        for data in agents.values():
            result.append(AgentRecord(
                agent_id=data['agent_id'],
                name=data['name'],
                type=data['type'],
                status=data['status'],
                recursion_depth=data['recursion_depth'],
                entropy_level=data['entropy_level'],
                metadata=data['metadata'],
                created_at=datetime.fromisoformat(data['created_at']),
                updated_at=datetime.fromisoformat(data['updated_at'])
            ))
        
        return sorted(result, key=lambda x: x.updated_at, reverse=True)
    
    def delete_agent(self, agent_id: str):
        """Delete agent from JSON"""
        with self._lock:
            agents = self._load_json(self.agents_file)
            if agent_id in agents:
                del agents[agent_id]
                self._save_json(self.agents_file, agents)
    
    def save_ritual_event(self, event: RitualEventRecord):
        """Save ritual event to JSON"""
        with self._lock:
            events = self._load_json(self.events_file)
            if 'events' not in events:
                events['events'] = []
            
            events['events'].append(asdict(event))
            
            # Keep only last 1000 events
            if len(events['events']) > 1000:
                events['events'] = events['events'][-1000:]
            
            self._save_json(self.events_file, events)
    
    def get_config(self, key: str) -> Optional[Any]:
        """Get configuration value from JSON"""
        config = self._load_json(self.config_file)
        return config.get(key)
    
    def set_config(self, key: str, value: Any, description: Optional[str] = None):
        """Set configuration value in JSON"""
        with self._lock:
            config = self._load_json(self.config_file)
            config[key] = {
                'value': value,
                'description': description,
                'updated_at': datetime.now().isoformat()
            }
            self._save_json(self.config_file, config)

class PersistenceManager:
    """Unified persistence manager supporting both SQLite and JSON"""
    
    def __init__(self, use_sqlite: bool = True, data_dir: Optional[Path] = None):
        self.use_sqlite = use_sqlite
        
        if use_sqlite:
            self.backend = CodexDatabase(data_dir / "codex.db" if data_dir else None)
        else:
            self.backend = JSONPersistence(data_dir)
        
        print(f"💾 Persistence initialized with {'SQLite' if use_sqlite else 'JSON'} backend")
    
    def save_agent(self, agent_id: str, name: str, agent_type: str, status: str,
                  recursion_depth: int = 0, entropy_level: float = 0.5,
                  metadata: Optional[Dict[str, Any]] = None):
        """Save agent with simplified interface"""
        now = datetime.now()
        agent = AgentRecord(
            agent_id=agent_id,
            name=name,
            type=agent_type,
            status=status,
            recursion_depth=recursion_depth,
            entropy_level=entropy_level,
            metadata=metadata or {},
            created_at=now,
            updated_at=now
        )
        self.backend.save_agent(agent)
    
    def save_ritual_event(self, event_type: str, description: str,
                         agent_id: Optional[str] = None, metadata: Optional[Dict[str, Any]] = None,
                         severity: str = "INFO"):
        """Save ritual event with simplified interface"""
        import uuid
        
        event = RitualEventRecord(
            event_id=str(uuid.uuid4()),
            timestamp=datetime.now(),
            event_type=event_type,
            description=description,
            agent_id=agent_id,
            metadata=metadata or {},
            severity=severity
        )
        self.backend.save_ritual_event(event)
    
    def get_agent(self, agent_id: str) -> Optional[AgentRecord]:
        """Get agent record"""
        return self.backend.get_agent(agent_id)
    
    def get_all_agents(self) -> List[AgentRecord]:
        """Get all agent records"""
        return self.backend.get_all_agents()
    
    def delete_agent(self, agent_id: str):
        """Delete agent record"""
        self.backend.delete_agent(agent_id)
    
    def get_config(self, key: str, default: Any = None) -> Any:
        """Get configuration value"""
        value = self.backend.get_config(key)
        return value if value is not None else default
    
    def set_config(self, key: str, value: Any, description: Optional[str] = None):
        """Set configuration value"""
        self.backend.set_config(key, value, description)

# Global persistence manager
persistence_manager = PersistenceManager()

def get_persistence() -> PersistenceManager:
    """Get global persistence manager"""
    return persistence_manager

__all__ = [
    "AgentRecord",
    "RitualEventRecord", 
    "SystemMetricsRecord",
    "CodexDatabase",
    "JSONPersistence",
    "PersistenceManager",
    "persistence_manager",
    "get_persistence"
]
