
"""
Multimodal Processor - Main orchestrator for multimodal processing tasks
"""

import asyncio
import json
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from enum import Enum

from .vision_processor import VisionProcessor, VisionTaskType, VisionResult
from .audio_processor import AudioProcessor, AudioTaskType, AudioResult
from .sensor_integrator import SensorIntegrator, SensorType, SensorReading
from .cross_modal_fusion import CrossModalFusion


class MultimodalTaskType(Enum):
    """Types of multimodal processing tasks"""
    SCENE_UNDERSTANDING = "scene_understanding"
    ACTIVITY_RECOGNITION = "activity_recognition"
    EMOTION_ANALYSIS = "emotion_analysis"
    ENVIRONMENTAL_MONITORING = "environmental_monitoring"
    CONTENT_GENERATION = "content_generation"
    SIMILARITY_SEARCH = "similarity_search"
    ANOMALY_DETECTION = "anomaly_detection"
    CONTEXT_ENRICHMENT = "context_enrichment"


@dataclass
class MultimodalInput:
    """Input data for multimodal processing"""
    text: Optional[str] = None
    image: Optional[Union[str, bytes]] = None
    audio: Optional[Union[str, bytes]] = None
    sensor_data: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class MultimodalResult:
    """Result of multimodal processing"""
    task_type: MultimodalTaskType
    success: bool
    result: Dict[str, Any]
    modalities_processed: List[str]
    processing_time: float
    confidence: float
    individual_results: Dict[str, Any]
    fusion_result: Optional[Dict[str, Any]]
    timestamp: datetime


class MultimodalProcessor:
    """
    Main orchestrator for multimodal processing tasks
    Coordinates vision, audio, and sensor processing with cross-modal fusion
    """
    
    def __init__(
        self,
        vision_processor: Optional[VisionProcessor] = None,
        audio_processor: Optional[AudioProcessor] = None,
        sensor_integrator: Optional[SensorIntegrator] = None,
        cross_modal_fusion: Optional[CrossModalFusion] = None
    ):
        self.vision_processor = vision_processor or VisionProcessor()
        self.audio_processor = audio_processor or AudioProcessor()
        self.sensor_integrator = sensor_integrator or SensorIntegrator()
        self.cross_modal_fusion = cross_modal_fusion or CrossModalFusion()
        
        # Task routing configuration
        self.task_routing = {
            MultimodalTaskType.SCENE_UNDERSTANDING: self._process_scene_understanding,
            MultimodalTaskType.ACTIVITY_RECOGNITION: self._process_activity_recognition,
            MultimodalTaskType.EMOTION_ANALYSIS: self._process_emotion_analysis,
            MultimodalTaskType.ENVIRONMENTAL_MONITORING: self._process_environmental_monitoring,
            MultimodalTaskType.CONTENT_GENERATION: self._process_content_generation,
            MultimodalTaskType.SIMILARITY_SEARCH: self._process_similarity_search,
            MultimodalTaskType.ANOMALY_DETECTION: self._process_anomaly_detection,
            MultimodalTaskType.CONTEXT_ENRICHMENT: self._process_context_enrichment
        }
    
    async def process_multimodal(
        self,
        inputs: MultimodalInput,
        task_type: MultimodalTaskType,
        parameters: Optional[Dict[str, Any]] = None
    ) -> MultimodalResult:
        """Process multimodal input with the specified task type"""
        try:
            start_time = datetime.now(timezone.utc)
            parameters = parameters or {}
            
            # Route to specific task processor
            if task_type in self.task_routing:
                result = await self.task_routing[task_type](inputs, parameters)
            else:
                raise ValueError(f"Unsupported task type: {task_type}")
            
            end_time = datetime.now(timezone.utc)
            processing_time = (end_time - start_time).total_seconds()
            
            # Update result with timing information
            result.processing_time = processing_time
            result.timestamp = end_time
            
            return result
            
        except Exception as e:
            return MultimodalResult(
                task_type=task_type,
                success=False,
                result={'error': str(e)},
                modalities_processed=[],
                processing_time=0.0,
                confidence=0.0,
                individual_results={},
                fusion_result=None,
                timestamp=datetime.now(timezone.utc)
            )
    
    async def _process_scene_understanding(
        self,
        inputs: MultimodalInput,
        parameters: Dict[str, Any]
    ) -> MultimodalResult:
        """Process scene understanding task using vision, audio, and sensor data"""
        try:
            individual_results = {}
            modalities_processed = []
            
            # Process vision if available
            if inputs.image:
                vision_result = await self.vision_processor.process_image(
                    inputs.image,
                    VisionTaskType.SCENE_ANALYSIS,
                    parameters.get('vision_params', {})
                )
                individual_results['vision'] = vision_result
                modalities_processed.append('vision')
            
            # Process audio if available
            if inputs.audio:
                audio_result = await self.audio_processor.process_audio(
                    inputs.audio,
                    AudioTaskType.AMBIENT_ANALYSIS,
                    parameters.get('audio_params', {})
                )
                individual_results['audio'] = audio_result
                modalities_processed.append('audio')
            
            # Get sensor data if available
            if inputs.sensor_data:
                sensor_conditions = await self.sensor_integrator.get_environmental_conditions(
                    location=inputs.sensor_data.get('location')
                )
                individual_results['sensors'] = {
                    'success': True,
                    'result': {
                        'temperature': sensor_conditions.temperature,
                        'humidity': sensor_conditions.humidity,
                        'light_level': sensor_conditions.light_level,
                        'air_quality': sensor_conditions.air_quality_index
                    }
                }
                modalities_processed.append('sensors')
            
            # Fuse results across modalities
            fusion_result = None
            if len(individual_results) > 1:
                fusion_result = await self.cross_modal_fusion.fuse_scene_understanding(
                    individual_results
                )
            
            # Combine results
            combined_result = self._combine_scene_understanding_results(
                individual_results, fusion_result
            )
            
            return MultimodalResult(
                task_type=MultimodalTaskType.SCENE_UNDERSTANDING,
                success=True,
                result=combined_result,
                modalities_processed=modalities_processed,
                processing_time=0.0,  # Will be updated by caller
                confidence=combined_result.get('confidence', 0.8),
                individual_results=individual_results,
                fusion_result=fusion_result,
                timestamp=datetime.now(timezone.utc)
            )
            
        except Exception as e:
            raise Exception(f"Scene understanding processing failed: {e}")
    
    async def _process_activity_recognition(
        self,
        inputs: MultimodalInput,
        parameters: Dict[str, Any]
    ) -> MultimodalResult:
        """Process activity recognition using multiple modalities"""
        try:
            individual_results = {}
            modalities_processed = []
            
            # Process vision for activity detection
            if inputs.image:
                vision_result = await self.vision_processor.process_image(
                    inputs.image,
                    VisionTaskType.OBJECT_DETECTION,
                    parameters.get('vision_params', {})
                )
                individual_results['vision'] = vision_result
                modalities_processed.append('vision')
            
            # Process audio for activity sounds
            if inputs.audio:
                audio_result = await self.audio_processor.process_audio(
                    inputs.audio,
                    AudioTaskType.SOUND_CLASSIFICATION,
                    parameters.get('audio_params', {})
                )
                individual_results['audio'] = audio_result
                modalities_processed.append('audio')
            
            # Process sensor data for motion/activity
            if inputs.sensor_data:
                # Mock sensor-based activity recognition
                sensor_result = {
                    'success': True,
                    'result': {
                        'motion_detected': True,
                        'activity_level': 'moderate',
                        'confidence': 0.75
                    }
                }
                individual_results['sensors'] = sensor_result
                modalities_processed.append('sensors')
            
            # Fuse results for activity recognition
            fusion_result = None
            if len(individual_results) > 1:
                fusion_result = await self.cross_modal_fusion.fuse_activity_recognition(
                    individual_results
                )
            
            # Combine results
            combined_result = self._combine_activity_recognition_results(
                individual_results, fusion_result
            )
            
            return MultimodalResult(
                task_type=MultimodalTaskType.ACTIVITY_RECOGNITION,
                success=True,
                result=combined_result,
                modalities_processed=modalities_processed,
                processing_time=0.0,
                confidence=combined_result.get('confidence', 0.8),
                individual_results=individual_results,
                fusion_result=fusion_result,
                timestamp=datetime.now(timezone.utc)
            )
            
        except Exception as e:
            raise Exception(f"Activity recognition processing failed: {e}")
    
    async def _process_emotion_analysis(
        self,
        inputs: MultimodalInput,
        parameters: Dict[str, Any]
    ) -> MultimodalResult:
        """Process emotion analysis across modalities"""
        try:
            individual_results = {}
            modalities_processed = []
            
            # Process vision for facial emotion
            if inputs.image:
                vision_result = await self.vision_processor.process_image(
                    inputs.image,
                    VisionTaskType.FACE_DETECTION,
                    {**parameters.get('vision_params', {}), 'include_attributes': True}
                )
                individual_results['vision'] = vision_result
                modalities_processed.append('vision')
            
            # Process audio for vocal emotion
            if inputs.audio:
                audio_result = await self.audio_processor.process_audio(
                    inputs.audio,
                    AudioTaskType.EMOTION_DETECTION,
                    parameters.get('audio_params', {})
                )
                individual_results['audio'] = audio_result
                modalities_processed.append('audio')
            
            # Process text for sentiment (if available)
            if inputs.text:
                # Mock text sentiment analysis
                text_result = {
                    'success': True,
                    'result': {
                        'sentiment': 'positive',
                        'confidence': 0.82,
                        'emotions': ['joy', 'excitement']
                    }
                }
                individual_results['text'] = text_result
                modalities_processed.append('text')
            
            # Fuse emotion results
            fusion_result = None
            if len(individual_results) > 1:
                fusion_result = await self.cross_modal_fusion.fuse_emotion_analysis(
                    individual_results
                )
            
            # Combine results
            combined_result = self._combine_emotion_analysis_results(
                individual_results, fusion_result
            )
            
            return MultimodalResult(
                task_type=MultimodalTaskType.EMOTION_ANALYSIS,
                success=True,
                result=combined_result,
                modalities_processed=modalities_processed,
                processing_time=0.0,
                confidence=combined_result.get('confidence', 0.8),
                individual_results=individual_results,
                fusion_result=fusion_result,
                timestamp=datetime.now(timezone.utc)
            )
            
        except Exception as e:
            raise Exception(f"Emotion analysis processing failed: {e}")
    
    async def _process_environmental_monitoring(
        self,
        inputs: MultimodalInput,
        parameters: Dict[str, Any]
    ) -> MultimodalResult:
        """Process environmental monitoring using sensors and other modalities"""
        try:
            individual_results = {}
            modalities_processed = []
            
            # Get sensor environmental data
            if inputs.sensor_data or True:  # Always try to get environmental data
                conditions = await self.sensor_integrator.get_environmental_conditions(
                    location=inputs.sensor_data.get('location') if inputs.sensor_data else None
                )
                
                sensor_result = {
                    'success': True,
                    'result': {
                        'temperature': conditions.temperature,
                        'humidity': conditions.humidity,
                        'pressure': conditions.pressure,
                        'light_level': conditions.light_level,
                        'air_quality_index': conditions.air_quality_index,
                        'sound_level': conditions.sound_level,
                        'timestamp': conditions.timestamp.isoformat()
                    }
                }
                individual_results['sensors'] = sensor_result
                modalities_processed.append('sensors')
            
            # Process audio for environmental sounds
            if inputs.audio:
                audio_result = await self.audio_processor.process_audio(
                    inputs.audio,
                    AudioTaskType.AMBIENT_ANALYSIS,
                    parameters.get('audio_params', {})
                )
                individual_results['audio'] = audio_result
                modalities_processed.append('audio')
            
            # Process vision for environmental assessment
            if inputs.image:
                vision_result = await self.vision_processor.process_image(
                    inputs.image,
                    VisionTaskType.SCENE_ANALYSIS,
                    parameters.get('vision_params', {})
                )
                individual_results['vision'] = vision_result
                modalities_processed.append('vision')
            
            # Combine environmental data
            combined_result = self._combine_environmental_monitoring_results(
                individual_results
            )
            
            return MultimodalResult(
                task_type=MultimodalTaskType.ENVIRONMENTAL_MONITORING,
                success=True,
                result=combined_result,
                modalities_processed=modalities_processed,
                processing_time=0.0,
                confidence=combined_result.get('confidence', 0.8),
                individual_results=individual_results,
                fusion_result=None,
                timestamp=datetime.now(timezone.utc)
            )
            
        except Exception as e:
            raise Exception(f"Environmental monitoring processing failed: {e}")
    
    async def _process_content_generation(
        self,
        inputs: MultimodalInput,
        parameters: Dict[str, Any]
    ) -> MultimodalResult:
        """Process content generation based on multimodal inputs"""
        try:
            individual_results = {}
            modalities_processed = []
            
            # Generate image if requested
            if parameters.get('generate_image', False):
                prompt = inputs.text or parameters.get('image_prompt', 'a beautiful scene')
                vision_result = await self.vision_processor.process_image(
                    None,
                    VisionTaskType.IMAGE_GENERATION,
                    {'prompt': prompt, **parameters.get('vision_params', {})}
                )
                individual_results['vision'] = vision_result
                modalities_processed.append('vision')
            
            # Generate audio description if requested
            if parameters.get('generate_audio_description', False) and inputs.image:
                # First analyze the image
                vision_analysis = await self.vision_processor.process_image(
                    inputs.image,
                    VisionTaskType.SCENE_ANALYSIS,
                    parameters.get('vision_params', {})
                )
                
                # Mock audio generation based on image analysis
                audio_result = {
                    'success': True,
                    'result': {
                        'description': f"Generated audio description: {vision_analysis.result.get('description', 'Scene analysis')}",
                        'duration': 5.0,
                        'confidence': 0.8
                    }
                }
                individual_results['audio'] = audio_result
                modalities_processed.append('audio')
            
            # Generate text description
            if parameters.get('generate_text_description', False):
                description_parts = []
                
                if inputs.image:
                    vision_analysis = await self.vision_processor.process_image(
                        inputs.image,
                        VisionTaskType.SCENE_ANALYSIS,
                        parameters.get('vision_params', {})
                    )
                    if vision_analysis.success:
                        description_parts.append(f"Visual: {vision_analysis.result.get('description', 'Scene')}")
                
                if inputs.audio:
                    audio_analysis = await self.audio_processor.process_audio(
                        inputs.audio,
                        AudioTaskType.SOUND_CLASSIFICATION,
                        parameters.get('audio_params', {})
                    )
                    if audio_analysis.success:
                        top_sound = audio_analysis.result.get('top_prediction', {})
                        description_parts.append(f"Audio: {top_sound.get('label', 'Unknown sound')}")
                
                text_result = {
                    'success': True,
                    'result': {
                        'generated_description': '. '.join(description_parts),
                        'confidence': 0.85
                    }
                }
                individual_results['text'] = text_result
                modalities_processed.append('text')
            
            # Combine generation results
            combined_result = self._combine_content_generation_results(
                individual_results
            )
            
            return MultimodalResult(
                task_type=MultimodalTaskType.CONTENT_GENERATION,
                success=True,
                result=combined_result,
                modalities_processed=modalities_processed,
                processing_time=0.0,
                confidence=combined_result.get('confidence', 0.8),
                individual_results=individual_results,
                fusion_result=None,
                timestamp=datetime.now(timezone.utc)
            )
            
        except Exception as e:
            raise Exception(f"Content generation processing failed: {e}")
    
    async def _process_similarity_search(
        self,
        inputs: MultimodalInput,
        parameters: Dict[str, Any]
    ) -> MultimodalResult:
        """Process similarity search across modalities"""
        try:
            individual_results = {}
            modalities_processed = []
            
            # Image similarity search
            if inputs.image and parameters.get('reference_images'):
                vision_result = await self.vision_processor.process_image(
                    inputs.image,
                    VisionTaskType.IMAGE_SIMILARITY,
                    {
                        'reference_images': parameters['reference_images'],
                        **parameters.get('vision_params', {})
                    }
                )
                individual_results['vision'] = vision_result
                modalities_processed.append('vision')
            
            # Audio similarity search (mock implementation)
            if inputs.audio and parameters.get('reference_audio'):
                # Mock audio similarity
                audio_result = {
                    'success': True,
                    'result': {
                        'similarities': [
                            {'reference_index': 0, 'similarity_score': 0.85},
                            {'reference_index': 1, 'similarity_score': 0.72}
                        ],
                        'most_similar': {'reference_index': 0, 'similarity_score': 0.85},
                        'confidence': 0.8
                    }
                }
                individual_results['audio'] = audio_result
                modalities_processed.append('audio')
            
            # Combine similarity results
            combined_result = self._combine_similarity_search_results(
                individual_results
            )
            
            return MultimodalResult(
                task_type=MultimodalTaskType.SIMILARITY_SEARCH,
                success=True,
                result=combined_result,
                modalities_processed=modalities_processed,
                processing_time=0.0,
                confidence=combined_result.get('confidence', 0.8),
                individual_results=individual_results,
                fusion_result=None,
                timestamp=datetime.now(timezone.utc)
            )
            
        except Exception as e:
            raise Exception(f"Similarity search processing failed: {e}")
    
    async def _process_anomaly_detection(
        self,
        inputs: MultimodalInput,
        parameters: Dict[str, Any]
    ) -> MultimodalResult:
        """Process anomaly detection across modalities"""
        try:
            individual_results = {}
            modalities_processed = []
            anomalies_detected = []
            
            # Visual anomaly detection
            if inputs.image:
                vision_result = await self.vision_processor.process_image(
                    inputs.image,
                    VisionTaskType.OBJECT_DETECTION,
                    parameters.get('vision_params', {})
                )
                
                # Mock anomaly detection based on object detection
                if vision_result.success:
                    objects = vision_result.result.get('objects', [])
                    unusual_objects = [obj for obj in objects if obj['confidence'] < 0.6]
                    
                    if unusual_objects:
                        anomalies_detected.append({
                            'modality': 'vision',
                            'type': 'unusual_objects',
                            'details': unusual_objects,
                            'severity': 'medium'
                        })
                
                individual_results['vision'] = vision_result
                modalities_processed.append('vision')
            
            # Audio anomaly detection
            if inputs.audio:
                audio_result = await self.audio_processor.process_audio(
                    inputs.audio,
                    AudioTaskType.SOUND_CLASSIFICATION,
                    parameters.get('audio_params', {})
                )
                
                # Mock audio anomaly detection
                if audio_result.success:
                    top_prediction = audio_result.result.get('top_prediction', {})
                    if top_prediction.get('confidence', 1.0) < 0.5:
                        anomalies_detected.append({
                            'modality': 'audio',
                            'type': 'unrecognized_sound',
                            'details': top_prediction,
                            'severity': 'high'
                        })
                
                individual_results['audio'] = audio_result
                modalities_processed.append('audio')
            
            # Sensor anomaly detection
            if inputs.sensor_data:
                # Mock sensor anomaly detection
                anomalies_detected.append({
                    'modality': 'sensors',
                    'type': 'temperature_spike',
                    'details': {'temperature': 35.5, 'threshold': 30.0},
                    'severity': 'low'
                })
                modalities_processed.append('sensors')
            
            # Combine anomaly detection results
            combined_result = {
                'anomalies_detected': anomalies_detected,
                'anomaly_count': len(anomalies_detected),
                'overall_anomaly_score': min(1.0, len(anomalies_detected) * 0.3),
                'confidence': 0.8
            }
            
            return MultimodalResult(
                task_type=MultimodalTaskType.ANOMALY_DETECTION,
                success=True,
                result=combined_result,
                modalities_processed=modalities_processed,
                processing_time=0.0,
                confidence=combined_result.get('confidence', 0.8),
                individual_results=individual_results,
                fusion_result=None,
                timestamp=datetime.now(timezone.utc)
            )
            
        except Exception as e:
            raise Exception(f"Anomaly detection processing failed: {e}")
    
    async def _process_context_enrichment(
        self,
        inputs: MultimodalInput,
        parameters: Dict[str, Any]
    ) -> MultimodalResult:
        """Process context enrichment using all available modalities"""
        try:
            individual_results = {}
            modalities_processed = []
            context_data = {}
            
            # Extract context from vision
            if inputs.image:
                vision_result = await self.vision_processor.process_image(
                    inputs.image,
                    VisionTaskType.SCENE_ANALYSIS,
                    parameters.get('vision_params', {})
                )
                
                if vision_result.success:
                    context_data['visual_context'] = {
                        'scene_type': vision_result.result.get('scene_type'),
                        'mood': vision_result.result.get('mood'),
                        'lighting': vision_result.result.get('lighting'),
                        'objects': vision_result.result.get('objects', [])
                    }
                
                individual_results['vision'] = vision_result
                modalities_processed.append('vision')
            
            # Extract context from audio
            if inputs.audio:
                audio_result = await self.audio_processor.process_audio(
                    inputs.audio,
                    AudioTaskType.AMBIENT_ANALYSIS,
                    parameters.get('audio_params', {})
                )
                
                if audio_result.success:
                    context_data['audio_context'] = {
                        'environment_type': audio_result.result.get('environment_type'),
                        'noise_level': audio_result.result.get('noise_level_db'),
                        'detected_sounds': audio_result.result.get('detected_sounds', [])
                    }
                
                individual_results['audio'] = audio_result
                modalities_processed.append('audio')
            
            # Extract context from sensors
            if inputs.sensor_data or True:  # Always try to get sensor context
                conditions = await self.sensor_integrator.get_environmental_conditions(
                    location=inputs.sensor_data.get('location') if inputs.sensor_data else None
                )
                
                context_data['environmental_context'] = {
                    'temperature': conditions.temperature,
                    'humidity': conditions.humidity,
                    'light_level': conditions.light_level,
                    'air_quality': conditions.air_quality_index
                }
                modalities_processed.append('sensors')
            
            # Add text context if available
            if inputs.text:
                context_data['text_context'] = {
                    'content': inputs.text,
                    'length': len(inputs.text),
                    'language': 'en'  # Mock language detection
                }
                modalities_processed.append('text')
            
            # Enrich context with temporal information
            context_data['temporal_context'] = {
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'time_of_day': self._get_time_of_day(),
                'day_of_week': datetime.now().strftime('%A')
            }
            
            # Combine enriched context
            combined_result = {
                'enriched_context': context_data,
                'context_completeness': len(context_data) / 5.0,  # Max 5 context types
                'confidence': 0.85
            }
            
            return MultimodalResult(
                task_type=MultimodalTaskType.CONTEXT_ENRICHMENT,
                success=True,
                result=combined_result,
                modalities_processed=modalities_processed,
                processing_time=0.0,
                confidence=combined_result.get('confidence', 0.8),
                individual_results=individual_results,
                fusion_result=None,
                timestamp=datetime.now(timezone.utc)
            )
            
        except Exception as e:
            raise Exception(f"Context enrichment processing failed: {e}")
    
    def _combine_scene_understanding_results(
        self,
        individual_results: Dict[str, Any],
        fusion_result: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Combine scene understanding results from multiple modalities"""
        combined = {
            'scene_description': '',
            'confidence': 0.0,
            'modalities_used': list(individual_results.keys())
        }
        
        descriptions = []
        confidences = []
        
        # Extract descriptions from each modality
        if 'vision' in individual_results and individual_results['vision'].success:
            vision_desc = individual_results['vision'].result.get('description', '')
            if vision_desc:
                descriptions.append(f"Visual: {vision_desc}")
                confidences.append(individual_results['vision'].confidence)
        
        if 'audio' in individual_results and individual_results['audio'].success:
            audio_env = individual_results['audio'].result.get('environment_type', '')
            if audio_env:
                descriptions.append(f"Audio environment: {audio_env}")
                confidences.append(individual_results['audio'].confidence)
        
        if 'sensors' in individual_results:
            sensor_data = individual_results['sensors']['result']
            sensor_desc = []
            if sensor_data.get('temperature'):
                sensor_desc.append(f"Temperature: {sensor_data['temperature']}°C")
            if sensor_data.get('humidity'):
                sensor_desc.append(f"Humidity: {sensor_data['humidity']}%")
            
            if sensor_desc:
                descriptions.append(f"Environmental: {', '.join(sensor_desc)}")
                confidences.append(0.8)
        
        # Combine descriptions
        combined['scene_description'] = '. '.join(descriptions)
        combined['confidence'] = sum(confidences) / len(confidences) if confidences else 0.0
        
        # Add fusion result if available
        if fusion_result:
            combined['fusion_insights'] = fusion_result
        
        return combined
    
    def _combine_activity_recognition_results(
        self,
        individual_results: Dict[str, Any],
        fusion_result: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Combine activity recognition results"""
        activities = []
        confidences = []
        
        # Extract activities from each modality
        if 'vision' in individual_results and individual_results['vision'].success:
            objects = individual_results['vision'].result.get('objects', [])
            if objects:
                activities.append(f"Visual activity: Objects detected - {len(objects)} items")
                confidences.append(individual_results['vision'].confidence)
        
        if 'audio' in individual_results and individual_results['audio'].success:
            top_sound = individual_results['audio'].result.get('top_prediction', {})
            if top_sound:
                activities.append(f"Audio activity: {top_sound.get('label', 'Unknown')}")
                confidences.append(top_sound.get('confidence', 0.5))
        
        if 'sensors' in individual_results:
            sensor_activity = individual_results['sensors']['result'].get('activity_level', 'unknown')
            activities.append(f"Sensor activity: {sensor_activity}")
            confidences.append(0.75)
        
        return {
            'detected_activities': activities,
            'activity_count': len(activities),
            'overall_activity_level': 'moderate' if activities else 'low',
            'confidence': sum(confidences) / len(confidences) if confidences else 0.0,
            'fusion_result': fusion_result
        }
    
    def _combine_emotion_analysis_results(
        self,
        individual_results: Dict[str, Any],
        fusion_result: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Combine emotion analysis results"""
        emotions = []
        confidences = []
        
        # Extract emotions from each modality
        if 'vision' in individual_results and individual_results['vision'].success:
            faces = individual_results['vision'].result.get('faces', [])
            for face in faces:
                emotion = face.get('attributes', {}).get('emotion', 'neutral')
                emotions.append(f"Visual emotion: {emotion}")
                confidences.append(face.get('confidence', 0.5))
        
        if 'audio' in individual_results and individual_results['audio'].success:
            primary_emotion = individual_results['audio'].result.get('primary_emotion', 'neutral')
            emotions.append(f"Audio emotion: {primary_emotion}")
            confidences.append(individual_results['audio'].confidence)
        
        if 'text' in individual_results and individual_results['text'].success:
            sentiment = individual_results['text']['result'].get('sentiment', 'neutral')
            emotions.append(f"Text sentiment: {sentiment}")
            confidences.append(individual_results['text']['result'].get('confidence', 0.5))
        
        return {
            'detected_emotions': emotions,
            'dominant_emotion': emotions[0] if emotions else 'neutral',
            'emotion_consistency': len(set(emotions)) == 1 if emotions else False,
            'confidence': sum(confidences) / len(confidences) if confidences else 0.0,
            'fusion_result': fusion_result
        }
    
    def _combine_environmental_monitoring_results(
        self,
        individual_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Combine environmental monitoring results"""
        environmental_data = {}
        
        # Combine sensor data
        if 'sensors' in individual_results:
            sensor_data = individual_results['sensors']['result']
            environmental_data.update(sensor_data)
        
        # Add audio environmental data
        if 'audio' in individual_results and individual_results['audio'].success:
            audio_data = individual_results['audio'].result
            environmental_data['audio_environment'] = audio_data.get('environment_type')
            environmental_data['detected_sounds'] = audio_data.get('detected_sounds', [])
        
        # Add visual environmental data
        if 'vision' in individual_results and individual_results['vision'].success:
            vision_data = individual_results['vision'].result
            environmental_data['visual_scene'] = vision_data.get('scene_type')
            environmental_data['lighting_conditions'] = vision_data.get('lighting')
        
        return {
            'environmental_conditions': environmental_data,
            'monitoring_completeness': len(environmental_data) / 10.0,  # Rough completeness score
            'confidence': 0.8
        }
    
    def _combine_content_generation_results(
        self,
        individual_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Combine content generation results"""
        generated_content = {}
        
        if 'vision' in individual_results and individual_results['vision'].success:
            generated_content['generated_image'] = individual_results['vision'].result.get('generated_image')
        
        if 'audio' in individual_results and individual_results['audio'].success:
            generated_content['audio_description'] = individual_results['audio'].result.get('description')
        
        if 'text' in individual_results and individual_results['text'].success:
            generated_content['text_description'] = individual_results['text'].result.get('generated_description')
        
        return {
            'generated_content': generated_content,
            'content_types': list(generated_content.keys()),
            'generation_success': len(generated_content) > 0,
            'confidence': 0.8
        }
    
    def _combine_similarity_search_results(
        self,
        individual_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Combine similarity search results"""
        similarities = {}
        
        if 'vision' in individual_results and individual_results['vision'].success:
            similarities['image_similarities'] = individual_results['vision'].result.get('similarities', [])
        
        if 'audio' in individual_results and individual_results['audio'].success:
            similarities['audio_similarities'] = individual_results['audio'].result.get('similarities', [])
        
        # Find overall best matches
        all_matches = []
        for modality, matches in similarities.items():
            for match in matches:
                match['modality'] = modality
                all_matches.append(match)
        
        # Sort by similarity score
        all_matches.sort(key=lambda x: x.get('similarity_score', 0), reverse=True)
        
        return {
            'similarity_results': similarities,
            'best_matches': all_matches[:5],  # Top 5 matches
            'total_matches': len(all_matches),
            'confidence': 0.8
        }
    
    def _get_time_of_day(self) -> str:
        """Get current time of day category"""
        hour = datetime.now().hour
        
        if 5 <= hour < 12:
            return 'morning'
        elif 12 <= hour < 17:
            return 'afternoon'
        elif 17 <= hour < 21:
            return 'evening'
        else:
            return 'night'
    
    async def get_processor_info(self) -> Dict[str, Any]:
        """Get information about the multimodal processor"""
        vision_info = await self.vision_processor.get_model_info()
        audio_info = await self.audio_processor.get_model_info()
        
        return {
            'supported_tasks': [task.value for task in MultimodalTaskType],
            'vision_processor': vision_info,
            'audio_processor': audio_info,
            'sensor_integrator': {
                'supported_sensors': [sensor.value for sensor in SensorType],
                'registered_devices': len(self.sensor_integrator.devices)
            },
            'cross_modal_fusion': {
                'fusion_methods': ['attention_based', 'weighted_average', 'neural_fusion']
            }
        }
