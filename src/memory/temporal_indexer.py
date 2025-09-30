
"""
Temporal Indexer - Provides time-aware indexing and retrieval for memory systems
"""

import asyncio
import json
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
import bisect


class TimeGranularity(Enum):
    """Time granularity levels for indexing"""
    SECOND = "second"
    MINUTE = "minute"
    HOUR = "hour"
    DAY = "day"
    WEEK = "week"
    MONTH = "month"
    YEAR = "year"


@dataclass
class TemporalIndex:
    """Represents a temporal index entry"""
    timestamp: datetime
    memory_id: str
    memory_type: str  # 'episodic', 'semantic', 'procedural'
    importance_score: float
    tags: List[str]
    metadata: Dict[str, Any]


@dataclass
class TimeRange:
    """Represents a time range for queries"""
    start: datetime
    end: datetime
    granularity: TimeGranularity


class TemporalIndexer:
    """
    Provides time-aware indexing and retrieval capabilities for memory systems
    Supports multiple time granularities and efficient temporal queries
    """
    
    def __init__(self, persist_directory: str = "./data/temporal_index"):
        self.persist_directory = persist_directory
        
        # Multi-level temporal indexes
        self.indexes: Dict[TimeGranularity, Dict[str, List[TemporalIndex]]] = {
            granularity: {} for granularity in TimeGranularity
        }
        
        # Memory ID to index mapping for fast updates
        self.memory_to_indexes: Dict[str, List[Tuple[TimeGranularity, str]]] = {}
        
        self._load_from_disk()
    
    def _load_from_disk(self):
        """Load temporal indexes from disk"""
        try:
            import os
            index_file = os.path.join(self.persist_directory, "temporal_indexes.json")
            
            os.makedirs(self.persist_directory, exist_ok=True)
            
            if os.path.exists(index_file):
                with open(index_file, 'r') as f:
                    data = json.load(f)
                    
                    for granularity_str, time_buckets in data.get('indexes', {}).items():
                        granularity = TimeGranularity(granularity_str)
                        
                        for time_key, entries in time_buckets.items():
                            index_entries = []
                            for entry_data in entries:
                                entry_data['timestamp'] = datetime.fromisoformat(entry_data['timestamp'])
                                index_entries.append(TemporalIndex(**entry_data))
                            
                            self.indexes[granularity][time_key] = index_entries
                    
                    # Rebuild memory to indexes mapping
                    self._rebuild_memory_mapping()
                    
        except Exception as e:
            print(f"Error loading temporal indexes: {e}")
    
    def _save_to_disk(self):
        """Save temporal indexes to disk"""
        try:
            import os
            index_file = os.path.join(self.persist_directory, "temporal_indexes.json")
            
            os.makedirs(self.persist_directory, exist_ok=True)
            
            # Convert to serializable format
            data = {'indexes': {}}
            
            for granularity, time_buckets in self.indexes.items():
                data['indexes'][granularity.value] = {}
                
                for time_key, entries in time_buckets.items():
                    serializable_entries = []
                    for entry in entries:
                        entry_dict = {
                            'timestamp': entry.timestamp.isoformat(),
                            'memory_id': entry.memory_id,
                            'memory_type': entry.memory_type,
                            'importance_score': entry.importance_score,
                            'tags': entry.tags,
                            'metadata': entry.metadata
                        }
                        serializable_entries.append(entry_dict)
                    
                    data['indexes'][granularity.value][time_key] = serializable_entries
            
            with open(index_file, 'w') as f:
                json.dump(data, f, indent=2)
                
        except Exception as e:
            print(f"Error saving temporal indexes: {e}")
    
    def _rebuild_memory_mapping(self):
        """Rebuild the memory ID to indexes mapping"""
        self.memory_to_indexes.clear()
        
        for granularity, time_buckets in self.indexes.items():
            for time_key, entries in time_buckets.items():
                for entry in entries:
                    if entry.memory_id not in self.memory_to_indexes:
                        self.memory_to_indexes[entry.memory_id] = []
                    self.memory_to_indexes[entry.memory_id].append((granularity, time_key))
    
    async def add_memory_index(
        self,
        memory_id: str,
        memory_type: str,
        timestamp: datetime,
        importance_score: float = 0.5,
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Add a memory to the temporal index"""
        try:
            index_entry = TemporalIndex(
                timestamp=timestamp,
                memory_id=memory_id,
                memory_type=memory_type,
                importance_score=importance_score,
                tags=tags or [],
                metadata=metadata or {}
            )
            
            # Add to all granularity levels
            for granularity in TimeGranularity:
                time_key = self._get_time_key(timestamp, granularity)
                
                if time_key not in self.indexes[granularity]:
                    self.indexes[granularity][time_key] = []
                
                # Insert in chronological order
                entries = self.indexes[granularity][time_key]
                bisect.insort(entries, index_entry, key=lambda x: x.timestamp)
                
                # Update memory mapping
                if memory_id not in self.memory_to_indexes:
                    self.memory_to_indexes[memory_id] = []
                self.memory_to_indexes[memory_id].append((granularity, time_key))
            
            self._save_to_disk()
            
        except Exception as e:
            print(f"Error adding memory index: {e}")
            raise
    
    async def query_by_time_range(
        self,
        time_range: TimeRange,
        memory_types: Optional[List[str]] = None,
        min_importance: float = 0.0,
        tags: Optional[List[str]] = None,
        limit: Optional[int] = None
    ) -> List[TemporalIndex]:
        """Query memories within a time range"""
        try:
            results = []
            
            # Determine optimal granularity for the query
            optimal_granularity = self._determine_optimal_granularity(time_range)
            
            # Get all time keys that overlap with the range
            time_keys = self._get_overlapping_time_keys(time_range, optimal_granularity)
            
            for time_key in time_keys:
                if time_key in self.indexes[optimal_granularity]:
                    for entry in self.indexes[optimal_granularity][time_key]:
                        # Check if entry falls within the exact time range
                        if not (time_range.start <= entry.timestamp <= time_range.end):
                            continue
                        
                        # Apply filters
                        if memory_types and entry.memory_type not in memory_types:
                            continue
                        
                        if entry.importance_score < min_importance:
                            continue
                        
                        if tags and not any(tag in entry.tags for tag in tags):
                            continue
                        
                        results.append(entry)
            
            # Sort by timestamp (most recent first)
            results.sort(key=lambda x: x.timestamp, reverse=True)
            
            # Apply limit
            if limit:
                results = results[:limit]
            
            return results
            
        except Exception as e:
            print(f"Error querying by time range: {e}")
            return []
    
    async def query_recent_memories(
        self,
        duration: timedelta,
        memory_types: Optional[List[str]] = None,
        min_importance: float = 0.0,
        limit: Optional[int] = None
    ) -> List[TemporalIndex]:
        """Query recent memories within a duration"""
        try:
            end_time = datetime.now(timezone.utc)
            start_time = end_time - duration
            
            time_range = TimeRange(
                start=start_time,
                end=end_time,
                granularity=self._determine_granularity_for_duration(duration)
            )
            
            return await self.query_by_time_range(
                time_range=time_range,
                memory_types=memory_types,
                min_importance=min_importance,
                limit=limit
            )
            
        except Exception as e:
            print(f"Error querying recent memories: {e}")
            return []
    
    async def get_memory_timeline(
        self,
        memory_id: str
    ) -> List[TemporalIndex]:
        """Get the timeline of a specific memory across all granularities"""
        try:
            timeline = []
            
            if memory_id in self.memory_to_indexes:
                for granularity, time_key in self.memory_to_indexes[memory_id]:
                    if time_key in self.indexes[granularity]:
                        for entry in self.indexes[granularity][time_key]:
                            if entry.memory_id == memory_id:
                                timeline.append(entry)
            
            # Remove duplicates and sort by timestamp
            unique_timeline = list({entry.timestamp: entry for entry in timeline}.values())
            unique_timeline.sort(key=lambda x: x.timestamp)
            
            return unique_timeline
            
        except Exception as e:
            print(f"Error getting memory timeline: {e}")
            return []
    
    async def update_memory_importance(
        self,
        memory_id: str,
        new_importance: float
    ):
        """Update the importance score of a memory across all indexes"""
        try:
            if memory_id in self.memory_to_indexes:
                for granularity, time_key in self.memory_to_indexes[memory_id]:
                    if time_key in self.indexes[granularity]:
                        for entry in self.indexes[granularity][time_key]:
                            if entry.memory_id == memory_id:
                                entry.importance_score = new_importance
                
                self._save_to_disk()
                
        except Exception as e:
            print(f"Error updating memory importance: {e}")
    
    async def remove_memory_index(self, memory_id: str):
        """Remove a memory from all temporal indexes"""
        try:
            if memory_id in self.memory_to_indexes:
                for granularity, time_key in self.memory_to_indexes[memory_id]:
                    if time_key in self.indexes[granularity]:
                        self.indexes[granularity][time_key] = [
                            entry for entry in self.indexes[granularity][time_key]
                            if entry.memory_id != memory_id
                        ]
                        
                        # Remove empty time buckets
                        if not self.indexes[granularity][time_key]:
                            del self.indexes[granularity][time_key]
                
                del self.memory_to_indexes[memory_id]
                self._save_to_disk()
                
        except Exception as e:
            print(f"Error removing memory index: {e}")
    
    async def get_temporal_patterns(
        self,
        granularity: TimeGranularity,
        memory_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """Analyze temporal patterns in memory creation"""
        try:
            patterns = {
                'activity_by_time': {},
                'peak_periods': [],
                'average_importance_by_time': {},
                'memory_type_distribution': {}
            }
            
            time_buckets = self.indexes[granularity]
            
            for time_key, entries in time_buckets.items():
                if memory_type:
                    entries = [e for e in entries if e.memory_type == memory_type]
                
                if entries:
                    patterns['activity_by_time'][time_key] = len(entries)
                    patterns['average_importance_by_time'][time_key] = (
                        sum(e.importance_score for e in entries) / len(entries)
                    )
                    
                    # Count memory types
                    for entry in entries:
                        mem_type = entry.memory_type
                        if mem_type not in patterns['memory_type_distribution']:
                            patterns['memory_type_distribution'][mem_type] = 0
                        patterns['memory_type_distribution'][mem_type] += 1
            
            # Find peak periods (top 5 most active time periods)
            activity_items = list(patterns['activity_by_time'].items())
            activity_items.sort(key=lambda x: x[1], reverse=True)
            patterns['peak_periods'] = activity_items[:5]
            
            return patterns
            
        except Exception as e:
            print(f"Error analyzing temporal patterns: {e}")
            return {}
    
    def _get_time_key(self, timestamp: datetime, granularity: TimeGranularity) -> str:
        """Generate a time key for a given timestamp and granularity"""
        if granularity == TimeGranularity.SECOND:
            return timestamp.strftime("%Y-%m-%d_%H:%M:%S")
        elif granularity == TimeGranularity.MINUTE:
            return timestamp.strftime("%Y-%m-%d_%H:%M")
        elif granularity == TimeGranularity.HOUR:
            return timestamp.strftime("%Y-%m-%d_%H")
        elif granularity == TimeGranularity.DAY:
            return timestamp.strftime("%Y-%m-%d")
        elif granularity == TimeGranularity.WEEK:
            year, week, _ = timestamp.isocalendar()
            return f"{year}-W{week:02d}"
        elif granularity == TimeGranularity.MONTH:
            return timestamp.strftime("%Y-%m")
        elif granularity == TimeGranularity.YEAR:
            return timestamp.strftime("%Y")
        else:
            return timestamp.isoformat()
    
    def _determine_optimal_granularity(self, time_range: TimeRange) -> TimeGranularity:
        """Determine the optimal granularity for a time range query"""
        duration = time_range.end - time_range.start
        
        if duration <= timedelta(minutes=1):
            return TimeGranularity.SECOND
        elif duration <= timedelta(hours=1):
            return TimeGranularity.MINUTE
        elif duration <= timedelta(days=1):
            return TimeGranularity.HOUR
        elif duration <= timedelta(weeks=1):
            return TimeGranularity.DAY
        elif duration <= timedelta(days=30):
            return TimeGranularity.WEEK
        elif duration <= timedelta(days=365):
            return TimeGranularity.MONTH
        else:
            return TimeGranularity.YEAR
    
    def _determine_granularity_for_duration(self, duration: timedelta) -> TimeGranularity:
        """Determine appropriate granularity for a duration"""
        if duration <= timedelta(minutes=5):
            return TimeGranularity.SECOND
        elif duration <= timedelta(hours=2):
            return TimeGranularity.MINUTE
        elif duration <= timedelta(days=2):
            return TimeGranularity.HOUR
        elif duration <= timedelta(weeks=2):
            return TimeGranularity.DAY
        elif duration <= timedelta(days=60):
            return TimeGranularity.WEEK
        elif duration <= timedelta(days=730):
            return TimeGranularity.MONTH
        else:
            return TimeGranularity.YEAR
    
    def _get_overlapping_time_keys(
        self,
        time_range: TimeRange,
        granularity: TimeGranularity
    ) -> List[str]:
        """Get all time keys that overlap with a time range"""
        time_keys = []
        
        # Generate time keys for the entire range
        current = time_range.start
        
        while current <= time_range.end:
            time_key = self._get_time_key(current, granularity)
            if time_key not in time_keys:
                time_keys.append(time_key)
            
            # Increment by granularity
            if granularity == TimeGranularity.SECOND:
                current += timedelta(seconds=1)
            elif granularity == TimeGranularity.MINUTE:
                current += timedelta(minutes=1)
            elif granularity == TimeGranularity.HOUR:
                current += timedelta(hours=1)
            elif granularity == TimeGranularity.DAY:
                current += timedelta(days=1)
            elif granularity == TimeGranularity.WEEK:
                current += timedelta(weeks=1)
            elif granularity == TimeGranularity.MONTH:
                # Approximate month increment
                current += timedelta(days=30)
            elif granularity == TimeGranularity.YEAR:
                current += timedelta(days=365)
        
        return time_keys
    
    async def get_index_stats(self) -> Dict[str, Any]:
        """Get statistics about the temporal index"""
        try:
            stats = {
                'total_indexed_memories': len(self.memory_to_indexes),
                'indexes_by_granularity': {},
                'memory_types': {},
                'oldest_memory': None,
                'newest_memory': None
            }
            
            all_timestamps = []
            
            for granularity, time_buckets in self.indexes.items():
                total_entries = 0
                memory_types = {}
                
                for entries in time_buckets.values():
                    total_entries += len(entries)
                    
                    for entry in entries:
                        all_timestamps.append(entry.timestamp)
                        
                        mem_type = entry.memory_type
                        if mem_type not in memory_types:
                            memory_types[mem_type] = 0
                        memory_types[mem_type] += 1
                
                stats['indexes_by_granularity'][granularity.value] = {
                    'total_entries': total_entries,
                    'time_buckets': len(time_buckets),
                    'memory_types': memory_types
                }
            
            # Overall memory type distribution
            for granularity_stats in stats['indexes_by_granularity'].values():
                for mem_type, count in granularity_stats['memory_types'].items():
                    if mem_type not in stats['memory_types']:
                        stats['memory_types'][mem_type] = 0
                    stats['memory_types'][mem_type] += count
            
            # Oldest and newest memories
            if all_timestamps:
                stats['oldest_memory'] = min(all_timestamps).isoformat()
                stats['newest_memory'] = max(all_timestamps).isoformat()
            
            return stats
            
        except Exception as e:
            print(f"Error getting index stats: {e}")
            return {}
