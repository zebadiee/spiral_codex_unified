
"""
Sensor Integration Module - Handles IoT sensor data, environmental monitoring, and biometric data
"""

import asyncio
import json
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass, asdict
from enum import Enum
import numpy as np


class SensorType(Enum):
    """Types of sensors supported"""
    TEMPERATURE = "temperature"
    HUMIDITY = "humidity"
    PRESSURE = "pressure"
    LIGHT = "light"
    MOTION = "motion"
    SOUND_LEVEL = "sound_level"
    AIR_QUALITY = "air_quality"
    HEART_RATE = "heart_rate"
    ACCELEROMETER = "accelerometer"
    GYROSCOPE = "gyroscope"
    GPS = "gps"
    PROXIMITY = "proximity"
    MAGNETIC_FIELD = "magnetic_field"
    CAMERA = "camera"
    MICROPHONE = "microphone"


@dataclass
class SensorReading:
    """Represents a single sensor reading"""
    sensor_id: str
    sensor_type: SensorType
    value: Union[float, int, str, Dict[str, Any]]
    unit: str
    timestamp: datetime
    location: Optional[Dict[str, float]] = None  # lat, lon, alt
    metadata: Optional[Dict[str, Any]] = None
    quality_score: float = 1.0  # 0.0 to 1.0


@dataclass
class SensorDevice:
    """Represents a sensor device"""
    device_id: str
    device_name: str
    sensor_types: List[SensorType]
    location: Optional[Dict[str, float]] = None
    status: str = "active"
    last_seen: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class EnvironmentalConditions:
    """Represents environmental conditions from multiple sensors"""
    temperature: Optional[float] = None
    humidity: Optional[float] = None
    pressure: Optional[float] = None
    light_level: Optional[float] = None
    air_quality_index: Optional[float] = None
    sound_level: Optional[float] = None
    timestamp: datetime = None
    location: Optional[Dict[str, float]] = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now(timezone.utc)


class SensorIntegrator:
    """
    Integrates data from various IoT sensors, environmental monitors, and biometric devices
    Provides unified interface for sensor data collection, processing, and analysis
    """
    
    def __init__(self, data_directory: str = "./data/sensors"):
        self.data_directory = data_directory
        self.devices: Dict[str, SensorDevice] = {}
        self.readings_buffer: Dict[str, List[SensorReading]] = {}
        self.buffer_size = 1000  # Maximum readings per sensor to keep in memory
        self.connection_handlers = {}
        self._initialize_storage()
    
    def _initialize_storage(self):
        """Initialize sensor data storage"""
        try:
            import os
            os.makedirs(self.data_directory, exist_ok=True)
            
            # Load existing devices
            devices_file = os.path.join(self.data_directory, "devices.json")
            if os.path.exists(devices_file):
                with open(devices_file, 'r') as f:
                    devices_data = json.load(f)
                    for device_data in devices_data:
                        device_data['sensor_types'] = [SensorType(st) for st in device_data['sensor_types']]
                        if device_data.get('last_seen'):
                            device_data['last_seen'] = datetime.fromisoformat(device_data['last_seen'])
                        device = SensorDevice(**device_data)
                        self.devices[device.device_id] = device
                        self.readings_buffer[device.device_id] = []
            
            print("Sensor integration system initialized")
            
        except Exception as e:
            print(f"Error initializing sensor storage: {e}")
    
    def _save_devices(self):
        """Save device configurations to disk"""
        try:
            import os
            devices_file = os.path.join(self.data_directory, "devices.json")
            
            devices_data = []
            for device in self.devices.values():
                device_dict = asdict(device)
                device_dict['sensor_types'] = [st.value for st in device.sensor_types]
                if device.last_seen:
                    device_dict['last_seen'] = device.last_seen.isoformat()
                devices_data.append(device_dict)
            
            with open(devices_file, 'w') as f:
                json.dump(devices_data, f, indent=2)
                
        except Exception as e:
            print(f"Error saving devices: {e}")
    
    async def register_device(self, device: SensorDevice) -> bool:
        """Register a new sensor device"""
        try:
            self.devices[device.device_id] = device
            self.readings_buffer[device.device_id] = []
            device.last_seen = datetime.now(timezone.utc)
            
            self._save_devices()
            
            print(f"Registered sensor device: {device.device_name} ({device.device_id})")
            return True
            
        except Exception as e:
            print(f"Error registering device {device.device_id}: {e}")
            return False
    
    async def unregister_device(self, device_id: str) -> bool:
        """Unregister a sensor device"""
        try:
            if device_id in self.devices:
                del self.devices[device_id]
                if device_id in self.readings_buffer:
                    del self.readings_buffer[device_id]
                
                self._save_devices()
                print(f"Unregistered sensor device: {device_id}")
                return True
            else:
                print(f"Device {device_id} not found")
                return False
                
        except Exception as e:
            print(f"Error unregistering device {device_id}: {e}")
            return False
    
    async def add_reading(self, reading: SensorReading) -> bool:
        """Add a sensor reading"""
        try:
            device_id = reading.sensor_id
            
            # Check if device is registered
            if device_id not in self.devices:
                print(f"Device {device_id} not registered, auto-registering...")
                device = SensorDevice(
                    device_id=device_id,
                    device_name=f"Auto-registered {device_id}",
                    sensor_types=[reading.sensor_type]
                )
                await self.register_device(device)
            
            # Add reading to buffer
            if device_id not in self.readings_buffer:
                self.readings_buffer[device_id] = []
            
            self.readings_buffer[device_id].append(reading)
            
            # Maintain buffer size
            if len(self.readings_buffer[device_id]) > self.buffer_size:
                self.readings_buffer[device_id] = self.readings_buffer[device_id][-self.buffer_size:]
            
            # Update device last seen
            self.devices[device_id].last_seen = reading.timestamp
            
            # Trigger any registered handlers
            await self._trigger_reading_handlers(reading)
            
            return True
            
        except Exception as e:
            print(f"Error adding reading: {e}")
            return False
    
    async def add_batch_readings(self, readings: List[SensorReading]) -> int:
        """Add multiple sensor readings in batch"""
        try:
            successful_count = 0
            
            for reading in readings:
                if await self.add_reading(reading):
                    successful_count += 1
            
            return successful_count
            
        except Exception as e:
            print(f"Error adding batch readings: {e}")
            return 0
    
    async def get_latest_reading(
        self,
        device_id: str,
        sensor_type: Optional[SensorType] = None
    ) -> Optional[SensorReading]:
        """Get the latest reading from a device"""
        try:
            if device_id not in self.readings_buffer:
                return None
            
            readings = self.readings_buffer[device_id]
            
            if sensor_type:
                readings = [r for r in readings if r.sensor_type == sensor_type]
            
            if not readings:
                return None
            
            # Return most recent reading
            return max(readings, key=lambda r: r.timestamp)
            
        except Exception as e:
            print(f"Error getting latest reading: {e}")
            return None
    
    async def get_readings_in_range(
        self,
        device_id: str,
        start_time: datetime,
        end_time: datetime,
        sensor_type: Optional[SensorType] = None
    ) -> List[SensorReading]:
        """Get readings within a time range"""
        try:
            if device_id not in self.readings_buffer:
                return []
            
            readings = self.readings_buffer[device_id]
            
            # Filter by time range
            filtered_readings = [
                r for r in readings
                if start_time <= r.timestamp <= end_time
            ]
            
            # Filter by sensor type if specified
            if sensor_type:
                filtered_readings = [
                    r for r in filtered_readings
                    if r.sensor_type == sensor_type
                ]
            
            # Sort by timestamp
            filtered_readings.sort(key=lambda r: r.timestamp)
            
            return filtered_readings
            
        except Exception as e:
            print(f"Error getting readings in range: {e}")
            return []
    
    async def get_environmental_conditions(
        self,
        location: Optional[Dict[str, float]] = None,
        radius_km: float = 1.0
    ) -> EnvironmentalConditions:
        """Get current environmental conditions from available sensors"""
        try:
            conditions = EnvironmentalConditions()
            
            # Get latest readings from all devices
            for device_id, device in self.devices.items():
                if location and device.location:
                    # Check if device is within radius
                    distance = self._calculate_distance(location, device.location)
                    if distance > radius_km:
                        continue
                
                # Get latest readings for environmental sensors
                for sensor_type in device.sensor_types:
                    latest_reading = await self.get_latest_reading(device_id, sensor_type)
                    
                    if latest_reading and isinstance(latest_reading.value, (int, float)):
                        if sensor_type == SensorType.TEMPERATURE:
                            conditions.temperature = latest_reading.value
                        elif sensor_type == SensorType.HUMIDITY:
                            conditions.humidity = latest_reading.value
                        elif sensor_type == SensorType.PRESSURE:
                            conditions.pressure = latest_reading.value
                        elif sensor_type == SensorType.LIGHT:
                            conditions.light_level = latest_reading.value
                        elif sensor_type == SensorType.AIR_QUALITY:
                            conditions.air_quality_index = latest_reading.value
                        elif sensor_type == SensorType.SOUND_LEVEL:
                            conditions.sound_level = latest_reading.value
            
            conditions.location = location
            return conditions
            
        except Exception as e:
            print(f"Error getting environmental conditions: {e}")
            return EnvironmentalConditions()
    
    async def analyze_sensor_patterns(
        self,
        device_id: str,
        sensor_type: SensorType,
        analysis_period: timedelta = timedelta(hours=24)
    ) -> Dict[str, Any]:
        """Analyze patterns in sensor data"""
        try:
            end_time = datetime.now(timezone.utc)
            start_time = end_time - analysis_period
            
            readings = await self.get_readings_in_range(
                device_id, start_time, end_time, sensor_type
            )
            
            if not readings:
                return {'status': 'no_data'}
            
            # Extract numeric values
            values = []
            timestamps = []
            
            for reading in readings:
                if isinstance(reading.value, (int, float)):
                    values.append(reading.value)
                    timestamps.append(reading.timestamp)
            
            if not values:
                return {'status': 'no_numeric_data'}
            
            # Calculate statistics
            values_array = np.array(values)
            
            analysis = {
                'status': 'success',
                'period_hours': analysis_period.total_seconds() / 3600,
                'reading_count': len(values),
                'statistics': {
                    'mean': float(np.mean(values_array)),
                    'median': float(np.median(values_array)),
                    'std': float(np.std(values_array)),
                    'min': float(np.min(values_array)),
                    'max': float(np.max(values_array)),
                    'range': float(np.max(values_array) - np.min(values_array))
                },
                'trends': self._analyze_trends(values, timestamps),
                'anomalies': self._detect_anomalies(values_array),
                'patterns': self._detect_patterns(values, timestamps)
            }
            
            return analysis
            
        except Exception as e:
            print(f"Error analyzing sensor patterns: {e}")
            return {'status': 'error', 'message': str(e)}
    
    async def get_device_status(self, device_id: str) -> Dict[str, Any]:
        """Get status information for a device"""
        try:
            if device_id not in self.devices:
                return {'status': 'not_found'}
            
            device = self.devices[device_id]
            
            # Check recent activity
            now = datetime.now(timezone.utc)
            if device.last_seen:
                time_since_last_seen = now - device.last_seen
                is_active = time_since_last_seen < timedelta(minutes=5)
            else:
                is_active = False
                time_since_last_seen = None
            
            # Get reading counts
            reading_counts = {}
            if device_id in self.readings_buffer:
                for reading in self.readings_buffer[device_id]:
                    sensor_type = reading.sensor_type.value
                    reading_counts[sensor_type] = reading_counts.get(sensor_type, 0) + 1
            
            return {
                'status': 'active' if is_active else 'inactive',
                'device_name': device.device_name,
                'sensor_types': [st.value for st in device.sensor_types],
                'location': device.location,
                'last_seen': device.last_seen.isoformat() if device.last_seen else None,
                'time_since_last_seen_seconds': time_since_last_seen.total_seconds() if time_since_last_seen else None,
                'reading_counts': reading_counts,
                'total_readings': sum(reading_counts.values())
            }
            
        except Exception as e:
            print(f"Error getting device status: {e}")
            return {'status': 'error', 'message': str(e)}
    
    async def get_all_devices_status(self) -> Dict[str, Dict[str, Any]]:
        """Get status for all registered devices"""
        try:
            status_dict = {}
            
            for device_id in self.devices:
                status_dict[device_id] = await self.get_device_status(device_id)
            
            return status_dict
            
        except Exception as e:
            print(f"Error getting all devices status: {e}")
            return {}
    
    async def register_reading_handler(self, handler_name: str, handler_func):
        """Register a handler function to be called when new readings arrive"""
        self.connection_handlers[handler_name] = handler_func
    
    async def unregister_reading_handler(self, handler_name: str):
        """Unregister a reading handler"""
        if handler_name in self.connection_handlers:
            del self.connection_handlers[handler_name]
    
    async def _trigger_reading_handlers(self, reading: SensorReading):
        """Trigger all registered reading handlers"""
        try:
            for handler_name, handler_func in self.connection_handlers.items():
                try:
                    if asyncio.iscoroutinefunction(handler_func):
                        await handler_func(reading)
                    else:
                        handler_func(reading)
                except Exception as e:
                    print(f"Error in reading handler {handler_name}: {e}")
                    
        except Exception as e:
            print(f"Error triggering reading handlers: {e}")
    
    def _calculate_distance(self, loc1: Dict[str, float], loc2: Dict[str, float]) -> float:
        """Calculate distance between two locations in kilometers"""
        try:
            # Simple Euclidean distance (for more accuracy, use Haversine formula)
            lat_diff = loc1.get('lat', 0) - loc2.get('lat', 0)
            lon_diff = loc1.get('lon', 0) - loc2.get('lon', 0)
            
            # Approximate conversion to km (rough estimate)
            distance = np.sqrt(lat_diff**2 + lon_diff**2) * 111  # 1 degree ≈ 111 km
            
            return distance
            
        except Exception as e:
            print(f"Error calculating distance: {e}")
            return float('inf')
    
    def _analyze_trends(self, values: List[float], timestamps: List[datetime]) -> Dict[str, Any]:
        """Analyze trends in sensor data"""
        try:
            if len(values) < 2:
                return {'trend': 'insufficient_data'}
            
            # Simple linear trend analysis
            x = np.arange(len(values))
            y = np.array(values)
            
            # Calculate slope
            slope = np.polyfit(x, y, 1)[0]
            
            # Determine trend direction
            if abs(slope) < 0.01:  # Threshold for "stable"
                trend = 'stable'
            elif slope > 0:
                trend = 'increasing'
            else:
                trend = 'decreasing'
            
            return {
                'trend': trend,
                'slope': float(slope),
                'trend_strength': abs(float(slope))
            }
            
        except Exception as e:
            print(f"Error analyzing trends: {e}")
            return {'trend': 'error'}
    
    def _detect_anomalies(self, values: np.ndarray) -> Dict[str, Any]:
        """Detect anomalies in sensor data using simple statistical methods"""
        try:
            if len(values) < 10:
                return {'anomalies': [], 'anomaly_count': 0}
            
            # Use z-score method for anomaly detection
            mean = np.mean(values)
            std = np.std(values)
            
            if std == 0:
                return {'anomalies': [], 'anomaly_count': 0}
            
            z_scores = np.abs((values - mean) / std)
            anomaly_threshold = 2.5  # Values beyond 2.5 standard deviations
            
            anomaly_indices = np.where(z_scores > anomaly_threshold)[0]
            
            anomalies = [
                {
                    'index': int(idx),
                    'value': float(values[idx]),
                    'z_score': float(z_scores[idx])
                }
                for idx in anomaly_indices
            ]
            
            return {
                'anomalies': anomalies,
                'anomaly_count': len(anomalies),
                'anomaly_rate': len(anomalies) / len(values)
            }
            
        except Exception as e:
            print(f"Error detecting anomalies: {e}")
            return {'anomalies': [], 'anomaly_count': 0}
    
    def _detect_patterns(self, values: List[float], timestamps: List[datetime]) -> Dict[str, Any]:
        """Detect patterns in sensor data"""
        try:
            if len(values) < 10:
                return {'patterns': []}
            
            patterns = []
            
            # Detect periodic patterns (simplified)
            values_array = np.array(values)
            
            # Check for daily patterns (if we have enough data)
            if len(values) > 24:
                # Simple autocorrelation check
                autocorr = np.correlate(values_array, values_array, mode='full')
                autocorr = autocorr[autocorr.size // 2:]
                
                # Look for peaks that might indicate periodicity
                if len(autocorr) > 24:
                    daily_corr = autocorr[24] if len(autocorr) > 24 else 0
                    if daily_corr > 0.5:
                        patterns.append({
                            'type': 'daily_cycle',
                            'strength': float(daily_corr),
                            'period_hours': 24
                        })
            
            # Detect step changes
            if len(values) > 5:
                diffs = np.diff(values_array)
                large_changes = np.where(np.abs(diffs) > 2 * np.std(diffs))[0]
                
                if len(large_changes) > 0:
                    patterns.append({
                        'type': 'step_changes',
                        'count': len(large_changes),
                        'average_magnitude': float(np.mean(np.abs(diffs[large_changes])))
                    })
            
            return {'patterns': patterns}
            
        except Exception as e:
            print(f"Error detecting patterns: {e}")
            return {'patterns': []}
    
    async def simulate_sensor_data(
        self,
        device_id: str,
        sensor_type: SensorType,
        duration_minutes: int = 60,
        interval_seconds: int = 30
    ) -> int:
        """Simulate sensor data for testing purposes"""
        try:
            readings_added = 0
            start_time = datetime.now(timezone.utc)
            
            for i in range(0, duration_minutes * 60, interval_seconds):
                timestamp = start_time + timedelta(seconds=i)
                
                # Generate mock sensor value based on type
                if sensor_type == SensorType.TEMPERATURE:
                    value = 20 + 5 * np.sin(i / 3600) + np.random.normal(0, 1)
                    unit = "°C"
                elif sensor_type == SensorType.HUMIDITY:
                    value = 50 + 20 * np.sin(i / 1800) + np.random.normal(0, 5)
                    unit = "%"
                elif sensor_type == SensorType.PRESSURE:
                    value = 1013 + np.random.normal(0, 2)
                    unit = "hPa"
                elif sensor_type == SensorType.LIGHT:
                    value = max(0, 500 + 400 * np.sin(i / 7200) + np.random.normal(0, 50))
                    unit = "lux"
                else:
                    value = np.random.normal(50, 10)
                    unit = "units"
                
                reading = SensorReading(
                    sensor_id=device_id,
                    sensor_type=sensor_type,
                    value=value,
                    unit=unit,
                    timestamp=timestamp,
                    quality_score=0.9 + np.random.normal(0, 0.05)
                )
                
                if await self.add_reading(reading):
                    readings_added += 1
            
            return readings_added
            
        except Exception as e:
            print(f"Error simulating sensor data: {e}")
            return 0


# Factory functions
def create_sensor_device(
    device_id: str,
    device_name: str,
    sensor_types: List[SensorType],
    location: Optional[Dict[str, float]] = None,
    metadata: Optional[Dict[str, Any]] = None
) -> SensorDevice:
    """Factory function to create a sensor device"""
    return SensorDevice(
        device_id=device_id,
        device_name=device_name,
        sensor_types=sensor_types,
        location=location,
        metadata=metadata or {}
    )


def create_sensor_reading(
    sensor_id: str,
    sensor_type: SensorType,
    value: Union[float, int, str, Dict[str, Any]],
    unit: str,
    location: Optional[Dict[str, float]] = None,
    metadata: Optional[Dict[str, Any]] = None,
    quality_score: float = 1.0
) -> SensorReading:
    """Factory function to create a sensor reading"""
    return SensorReading(
        sensor_id=sensor_id,
        sensor_type=sensor_type,
        value=value,
        unit=unit,
        timestamp=datetime.now(timezone.utc),
        location=location,
        metadata=metadata,
        quality_score=quality_score
    )
