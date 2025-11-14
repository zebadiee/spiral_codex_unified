
"""
Cross-Modal Fusion Module - Handles fusion and synthesis across different modalities
"""

import asyncio
import json
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
import numpy as np


class FusionMethod(Enum):
    """Methods for cross-modal fusion"""
    WEIGHTED_AVERAGE = "weighted_average"
    ATTENTION_BASED = "attention_based"
    NEURAL_FUSION = "neural_fusion"
    CONFIDENCE_WEIGHTED = "confidence_weighted"
    HIERARCHICAL = "hierarchical"
    CONSENSUS_BASED = "consensus_based"


@dataclass
class ModalityFeatures:
    """Features extracted from a single modality"""
    modality: str
    features: List[float]
    confidence: float
    metadata: Dict[str, Any]
    timestamp: datetime


@dataclass
class FusionResult:
    """Result of cross-modal fusion"""
    fused_features: List[float]
    fusion_method: FusionMethod
    modalities_used: List[str]
    fusion_confidence: float
    individual_contributions: Dict[str, float]
    fusion_metadata: Dict[str, Any]
    timestamp: datetime


class CrossModalFusion:
    """
    Handles fusion and synthesis across different modalities
    Implements various fusion strategies for combining vision, audio, text, and sensor data
    """
    
    def __init__(self, default_fusion_method: FusionMethod = FusionMethod.CONFIDENCE_WEIGHTED):
        self.default_fusion_method = default_fusion_method
        self.fusion_methods = {
            FusionMethod.WEIGHTED_AVERAGE: self._weighted_average_fusion,
            FusionMethod.ATTENTION_BASED: self._attention_based_fusion,
            FusionMethod.NEURAL_FUSION: self._neural_fusion,
            FusionMethod.CONFIDENCE_WEIGHTED: self._confidence_weighted_fusion,
            FusionMethod.HIERARCHICAL: self._hierarchical_fusion,
            FusionMethod.CONSENSUS_BASED: self._consensus_based_fusion
        }
        
        # Modality weights (can be learned or configured)
        self.modality_weights = {
            'vision': 0.4,
            'audio': 0.3,
            'text': 0.2,
            'sensors': 0.1
        }
        
        # Feature dimension for fusion (standardized)
        self.fusion_dimension = 384
    
    async def fuse_features(
        self,
        modality_features: List[ModalityFeatures],
        fusion_method: Optional[FusionMethod] = None,
        parameters: Optional[Dict[str, Any]] = None
    ) -> FusionResult:
        """Fuse features from multiple modalities"""
        try:
            if not modality_features:
                raise ValueError("No modality features provided for fusion")
            
            fusion_method = fusion_method or self.default_fusion_method
            parameters = parameters or {}
            
            # Normalize features to same dimension
            normalized_features = await self._normalize_features(modality_features)
            
            # Apply fusion method
            if fusion_method in self.fusion_methods:
                fused_features, fusion_confidence, contributions = await self.fusion_methods[fusion_method](
                    normalized_features, parameters
                )
            else:
                raise ValueError(f"Unsupported fusion method: {fusion_method}")
            
            return FusionResult(
                fused_features=fused_features,
                fusion_method=fusion_method,
                modalities_used=[mf.modality for mf in modality_features],
                fusion_confidence=fusion_confidence,
                individual_contributions=contributions,
                fusion_metadata={
                    'original_dimensions': {mf.modality: len(mf.features) for mf in modality_features},
                    'fusion_parameters': parameters
                },
                timestamp=datetime.now(timezone.utc)
            )
            
        except Exception as e:
            raise Exception(f"Feature fusion failed: {e}")
    
    async def fuse_scene_understanding(
        self,
        individual_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Fuse scene understanding results from multiple modalities"""
        try:
            fusion_insights = {
                'cross_modal_consistency': 0.0,
                'complementary_information': [],
                'confidence_boost': 0.0,
                'unified_scene_description': ''
            }
            
            # Extract key information from each modality
            scene_elements = {}
            
            if 'vision' in individual_results and individual_results['vision'].success:
                vision_result = individual_results['vision'].result
                scene_elements['visual'] = {
                    'scene_type': vision_result.get('scene_type', ''),
                    'objects': vision_result.get('objects', []),
                    'mood': vision_result.get('mood', ''),
                    'lighting': vision_result.get('lighting', '')
                }
            
            if 'audio' in individual_results and individual_results['audio'].success:
                audio_result = individual_results['audio'].result
                scene_elements['audio'] = {
                    'environment_type': audio_result.get('environment_type', ''),
                    'noise_level': audio_result.get('noise_level_db', 0),
                    'detected_sounds': audio_result.get('detected_sounds', [])
                }
            
            if 'sensors' in individual_results:
                sensor_result = individual_results['sensors']['result']
                scene_elements['sensors'] = {
                    'temperature': sensor_result.get('temperature'),
                    'humidity': sensor_result.get('humidity'),
                    'light_level': sensor_result.get('light_level')
                }
            
            # Analyze cross-modal consistency
            consistency_score = await self._analyze_scene_consistency(scene_elements)
            fusion_insights['cross_modal_consistency'] = consistency_score
            
            # Identify complementary information
            complementary_info = await self._identify_complementary_scene_info(scene_elements)
            fusion_insights['complementary_information'] = complementary_info
            
            # Calculate confidence boost from fusion
            individual_confidences = []
            for modality, result in individual_results.items():
                if hasattr(result, 'confidence'):
                    individual_confidences.append(result.confidence)
                elif isinstance(result, dict) and 'result' in result:
                    individual_confidences.append(result['result'].get('confidence', 0.5))
            
            if individual_confidences:
                avg_confidence = np.mean(individual_confidences)
                # Fusion typically boosts confidence when modalities agree
                fusion_insights['confidence_boost'] = min(0.2, consistency_score * 0.2)
            
            # Create unified scene description
            unified_description = await self._create_unified_scene_description(scene_elements)
            fusion_insights['unified_scene_description'] = unified_description
            
            return fusion_insights
            
        except Exception as e:
            print(f"Error in scene understanding fusion: {e}")
            return {'error': str(e)}
    
    async def fuse_activity_recognition(
        self,
        individual_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Fuse activity recognition results from multiple modalities"""
        try:
            activities = []
            confidence_scores = []
            
            # Extract activities from each modality
            if 'vision' in individual_results and individual_results['vision'].success:
                vision_objects = individual_results['vision'].result.get('objects', [])
                for obj in vision_objects:
                    activities.append({
                        'modality': 'vision',
                        'activity': f"object_interaction_{obj['label']}",
                        'confidence': obj['confidence']
                    })
                    confidence_scores.append(obj['confidence'])
            
            if 'audio' in individual_results and individual_results['audio'].success:
                audio_sounds = individual_results['audio'].result.get('classifications', [])
                for sound in audio_sounds:
                    activities.append({
                        'modality': 'audio',
                        'activity': f"sound_activity_{sound['label']}",
                        'confidence': sound['confidence']
                    })
                    confidence_scores.append(sound['confidence'])
            
            if 'sensors' in individual_results:
                sensor_activity = individual_results['sensors']['result'].get('activity_level', 'unknown')
                activities.append({
                    'modality': 'sensors',
                    'activity': f"motion_activity_{sensor_activity}",
                    'confidence': 0.75
                })
                confidence_scores.append(0.75)
            
            # Fuse activities using consensus
            fused_activity = await self._consensus_activity_fusion(activities)
            
            return {
                'fused_activity': fused_activity,
                'individual_activities': activities,
                'fusion_confidence': np.mean(confidence_scores) if confidence_scores else 0.0,
                'activity_agreement': self._calculate_activity_agreement(activities)
            }
            
        except Exception as e:
            print(f"Error in activity recognition fusion: {e}")
            return {'error': str(e)}
    
    async def fuse_emotion_analysis(
        self,
        individual_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Fuse emotion analysis results from multiple modalities"""
        try:
            emotions = {}
            confidence_scores = []
            
            # Extract emotions from each modality
            if 'vision' in individual_results and individual_results['vision'].success:
                faces = individual_results['vision'].result.get('faces', [])
                if faces:
                    face_emotion = faces[0].get('attributes', {}).get('emotion', 'neutral')
                    emotions['visual'] = face_emotion
                    confidence_scores.append(faces[0].get('confidence', 0.5))
            
            if 'audio' in individual_results and individual_results['audio'].success:
                audio_emotion = individual_results['audio'].result.get('primary_emotion', 'neutral')
                emotions['audio'] = audio_emotion
                confidence_scores.append(individual_results['audio'].confidence)
            
            if 'text' in individual_results and individual_results['text'].success:
                text_sentiment = individual_results['text']['result'].get('sentiment', 'neutral')
                emotions['text'] = text_sentiment
                confidence_scores.append(individual_results['text']['result'].get('confidence', 0.5))
            
            # Fuse emotions using weighted voting
            fused_emotion = await self._weighted_emotion_fusion(emotions, confidence_scores)
            
            # Calculate emotion consistency across modalities
            emotion_consistency = self._calculate_emotion_consistency(emotions)
            
            return {
                'fused_emotion': fused_emotion,
                'individual_emotions': emotions,
                'emotion_consistency': emotion_consistency,
                'fusion_confidence': np.mean(confidence_scores) if confidence_scores else 0.0,
                'cross_modal_agreement': emotion_consistency > 0.7
            }
            
        except Exception as e:
            print(f"Error in emotion analysis fusion: {e}")
            return {'error': str(e)}
    
    async def _normalize_features(
        self,
        modality_features: List[ModalityFeatures]
    ) -> List[ModalityFeatures]:
        """Normalize features from different modalities to same dimension"""
        try:
            normalized_features = []
            
            for mf in modality_features:
                # Normalize feature vector to fusion dimension
                if len(mf.features) == self.fusion_dimension:
                    normalized_vector = mf.features
                elif len(mf.features) > self.fusion_dimension:
                    # Truncate or pool
                    normalized_vector = mf.features[:self.fusion_dimension]
                else:
                    # Pad with zeros
                    normalized_vector = mf.features + [0.0] * (self.fusion_dimension - len(mf.features))
                
                # L2 normalize
                norm = np.linalg.norm(normalized_vector)
                if norm > 0:
                    normalized_vector = (np.array(normalized_vector) / norm).tolist()
                
                normalized_features.append(ModalityFeatures(
                    modality=mf.modality,
                    features=normalized_vector,
                    confidence=mf.confidence,
                    metadata=mf.metadata,
                    timestamp=mf.timestamp
                ))
            
            return normalized_features
            
        except Exception as e:
            raise Exception(f"Feature normalization failed: {e}")
    
    async def _weighted_average_fusion(
        self,
        features: List[ModalityFeatures],
        parameters: Dict[str, Any]
    ) -> Tuple[List[float], float, Dict[str, float]]:
        """Weighted average fusion of features"""
        try:
            # Get weights for each modality
            weights = {}
            total_weight = 0.0
            
            for mf in features:
                weight = parameters.get('weights', {}).get(mf.modality, self.modality_weights.get(mf.modality, 1.0))
                weights[mf.modality] = weight
                total_weight += weight
            
            # Normalize weights
            for modality in weights:
                weights[modality] /= total_weight
            
            # Compute weighted average
            fused_features = np.zeros(self.fusion_dimension)
            fusion_confidence = 0.0
            
            for mf in features:
                weight = weights[mf.modality]
                fused_features += weight * np.array(mf.features)
                fusion_confidence += weight * mf.confidence
            
            return fused_features.tolist(), fusion_confidence, weights
            
        except Exception as e:
            raise Exception(f"Weighted average fusion failed: {e}")
    
    async def _attention_based_fusion(
        self,
        features: List[ModalityFeatures],
        parameters: Dict[str, Any]
    ) -> Tuple[List[float], float, Dict[str, float]]:
        """Attention-based fusion of features"""
        try:
            # Simple attention mechanism based on confidence scores
            attention_weights = {}
            total_attention = 0.0
            
            # Calculate attention weights based on confidence
            for mf in features:
                # Softmax-like attention based on confidence
                attention = np.exp(mf.confidence * 2)  # Scale confidence
                attention_weights[mf.modality] = attention
                total_attention += attention
            
            # Normalize attention weights
            for modality in attention_weights:
                attention_weights[modality] /= total_attention
            
            # Apply attention to features
            fused_features = np.zeros(self.fusion_dimension)
            fusion_confidence = 0.0
            
            for mf in features:
                attention = attention_weights[mf.modality]
                fused_features += attention * np.array(mf.features)
                fusion_confidence += attention * mf.confidence
            
            return fused_features.tolist(), fusion_confidence, attention_weights
            
        except Exception as e:
            raise Exception(f"Attention-based fusion failed: {e}")
    
    async def _neural_fusion(
        self,
        features: List[ModalityFeatures],
        parameters: Dict[str, Any]
    ) -> Tuple[List[float], float, Dict[str, float]]:
        """Neural network-based fusion (mock implementation)"""
        try:
            # Mock neural fusion - in reality would use trained neural network
            # For now, use a combination of weighted average and non-linear transformation
            
            # First, get weighted average
            weighted_features, weighted_confidence, weights = await self._weighted_average_fusion(
                features, parameters
            )
            
            # Apply mock non-linear transformation
            fused_features = np.array(weighted_features)
            
            # Simple non-linear transformation (tanh activation)
            fused_features = np.tanh(fused_features * 1.5)
            
            # Boost confidence slightly for neural fusion
            fusion_confidence = min(1.0, weighted_confidence * 1.1)
            
            return fused_features.tolist(), fusion_confidence, weights
            
        except Exception as e:
            raise Exception(f"Neural fusion failed: {e}")
    
    async def _confidence_weighted_fusion(
        self,
        features: List[ModalityFeatures],
        parameters: Dict[str, Any]
    ) -> Tuple[List[float], float, Dict[str, float]]:
        """Confidence-weighted fusion of features"""
        try:
            # Use confidence scores as weights
            confidence_weights = {}
            total_confidence = 0.0
            
            for mf in features:
                confidence_weights[mf.modality] = mf.confidence
                total_confidence += mf.confidence
            
            # Normalize confidence weights
            if total_confidence > 0:
                for modality in confidence_weights:
                    confidence_weights[modality] /= total_confidence
            else:
                # Equal weights if no confidence
                equal_weight = 1.0 / len(features)
                for modality in confidence_weights:
                    confidence_weights[modality] = equal_weight
            
            # Apply confidence weights
            fused_features = np.zeros(self.fusion_dimension)
            fusion_confidence = 0.0
            
            for mf in features:
                weight = confidence_weights[mf.modality]
                fused_features += weight * np.array(mf.features)
                fusion_confidence += weight * mf.confidence
            
            return fused_features.tolist(), fusion_confidence, confidence_weights
            
        except Exception as e:
            raise Exception(f"Confidence-weighted fusion failed: {e}")
    
    async def _hierarchical_fusion(
        self,
        features: List[ModalityFeatures],
        parameters: Dict[str, Any]
    ) -> Tuple[List[float], float, Dict[str, float]]:
        """Hierarchical fusion of features"""
        try:
            # Group modalities by hierarchy level
            hierarchy = parameters.get('hierarchy', {
                'primary': ['vision', 'audio'],
                'secondary': ['text', 'sensors']
            })
            
            # First fuse primary modalities
            primary_features = [mf for mf in features if mf.modality in hierarchy.get('primary', [])]
            secondary_features = [mf for mf in features if mf.modality in hierarchy.get('secondary', [])]
            
            fused_features = np.zeros(self.fusion_dimension)
            fusion_confidence = 0.0
            contributions = {}
            
            # Fuse primary modalities first
            if primary_features:
                primary_fused, primary_conf, primary_contrib = await self._confidence_weighted_fusion(
                    primary_features, parameters
                )
                fused_features += 0.7 * np.array(primary_fused)  # 70% weight to primary
                fusion_confidence += 0.7 * primary_conf
                
                for modality, contrib in primary_contrib.items():
                    contributions[modality] = 0.7 * contrib
            
            # Then incorporate secondary modalities
            if secondary_features:
                secondary_fused, secondary_conf, secondary_contrib = await self._confidence_weighted_fusion(
                    secondary_features, parameters
                )
                fused_features += 0.3 * np.array(secondary_fused)  # 30% weight to secondary
                fusion_confidence += 0.3 * secondary_conf
                
                for modality, contrib in secondary_contrib.items():
                    contributions[modality] = 0.3 * contrib
            
            return fused_features.tolist(), fusion_confidence, contributions
            
        except Exception as e:
            raise Exception(f"Hierarchical fusion failed: {e}")
    
    async def _consensus_based_fusion(
        self,
        features: List[ModalityFeatures],
        parameters: Dict[str, Any]
    ) -> Tuple[List[float], float, Dict[str, float]]:
        """Consensus-based fusion of features"""
        try:
            # Calculate pairwise similarities between modalities
            similarities = {}
            
            for i, mf1 in enumerate(features):
                for j, mf2 in enumerate(features[i+1:], i+1):
                    similarity = self._cosine_similarity(mf1.features, mf2.features)
                    similarities[(mf1.modality, mf2.modality)] = similarity
            
            # Weight modalities based on consensus (how well they agree with others)
            consensus_weights = {}
            
            for mf in features:
                consensus_score = 0.0
                count = 0
                
                for (mod1, mod2), sim in similarities.items():
                    if mod1 == mf.modality or mod2 == mf.modality:
                        consensus_score += sim
                        count += 1
                
                consensus_weights[mf.modality] = consensus_score / count if count > 0 else 0.5
            
            # Normalize consensus weights
            total_consensus = sum(consensus_weights.values())
            if total_consensus > 0:
                for modality in consensus_weights:
                    consensus_weights[modality] /= total_consensus
            
            # Apply consensus weights
            fused_features = np.zeros(self.fusion_dimension)
            fusion_confidence = 0.0
            
            for mf in features:
                weight = consensus_weights[mf.modality]
                fused_features += weight * np.array(mf.features)
                fusion_confidence += weight * mf.confidence
            
            return fused_features.tolist(), fusion_confidence, consensus_weights
            
        except Exception as e:
            raise Exception(f"Consensus-based fusion failed: {e}")
    
    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors"""
        try:
            v1 = np.array(vec1)
            v2 = np.array(vec2)
            
            dot_product = np.dot(v1, v2)
            norm1 = np.linalg.norm(v1)
            norm2 = np.linalg.norm(v2)
            
            if norm1 == 0 or norm2 == 0:
                return 0.0
            
            return dot_product / (norm1 * norm2)
            
        except Exception as e:
            print(f"Error calculating cosine similarity: {e}")
            return 0.0
    
    async def _analyze_scene_consistency(self, scene_elements: Dict[str, Any]) -> float:
        """Analyze consistency across modalities for scene understanding"""
        try:
            consistency_score = 0.0
            comparisons = 0
            
            # Check visual-audio consistency
            if 'visual' in scene_elements and 'audio' in scene_elements:
                visual_scene = scene_elements['visual'].get('scene_type', '').lower()
                audio_env = scene_elements['audio'].get('environment_type', '').lower()
                
                # Simple keyword matching for consistency
                if any(word in audio_env for word in visual_scene.split('_')):
                    consistency_score += 1.0
                comparisons += 1
            
            # Check visual-sensor consistency
            if 'visual' in scene_elements and 'sensors' in scene_elements:
                visual_lighting = scene_elements['visual'].get('lighting', '').lower()
                sensor_light = scene_elements['sensors'].get('light_level', 0)
                
                # Check if lighting description matches sensor reading
                if 'bright' in visual_lighting and sensor_light > 500:
                    consistency_score += 1.0
                elif 'dim' in visual_lighting and sensor_light < 200:
                    consistency_score += 1.0
                elif 'normal' in visual_lighting and 200 <= sensor_light <= 500:
                    consistency_score += 1.0
                
                comparisons += 1
            
            return consistency_score / comparisons if comparisons > 0 else 0.5
            
        except Exception as e:
            print(f"Error analyzing scene consistency: {e}")
            return 0.0
    
    async def _identify_complementary_scene_info(self, scene_elements: Dict[str, Any]) -> List[str]:
        """Identify complementary information across modalities"""
        try:
            complementary_info = []
            
            # Visual provides spatial information
            if 'visual' in scene_elements:
                objects = scene_elements['visual'].get('objects', [])
                if objects:
                    complementary_info.append(f"Visual: {len(objects)} objects detected providing spatial context")
            
            # Audio provides temporal and ambient information
            if 'audio' in scene_elements:
                sounds = scene_elements['audio'].get('detected_sounds', [])
                if sounds:
                    complementary_info.append(f"Audio: {len(sounds)} ambient sounds providing temporal context")
            
            # Sensors provide quantitative environmental data
            if 'sensors' in scene_elements:
                sensor_data = scene_elements['sensors']
                quantitative_measures = [k for k, v in sensor_data.items() if isinstance(v, (int, float)) and v is not None]
                if quantitative_measures:
                    complementary_info.append(f"Sensors: {len(quantitative_measures)} quantitative measurements")
            
            return complementary_info
            
        except Exception as e:
            print(f"Error identifying complementary info: {e}")
            return []
    
    async def _create_unified_scene_description(self, scene_elements: Dict[str, Any]) -> str:
        """Create a unified scene description from all modalities"""
        try:
            description_parts = []
            
            # Add visual description
            if 'visual' in scene_elements:
                visual = scene_elements['visual']
                scene_type = visual.get('scene_type', '')
                mood = visual.get('mood', '')
                lighting = visual.get('lighting', '')
                
                if scene_type:
                    description_parts.append(f"a {scene_type} scene")
                if mood:
                    description_parts.append(f"with a {mood} atmosphere")
                if lighting:
                    description_parts.append(f"under {lighting} lighting")
            
            # Add audio description
            if 'audio' in scene_elements:
                audio = scene_elements['audio']
                env_type = audio.get('environment_type', '')
                noise_level = audio.get('noise_level', 0)
                
                if env_type:
                    description_parts.append(f"in an {env_type} environment")
                if noise_level:
                    noise_desc = "quiet" if noise_level < 40 else "moderate" if noise_level < 60 else "noisy"
                    description_parts.append(f"with {noise_desc} ambient sound")
            
            # Add sensor description
            if 'sensors' in scene_elements:
                sensors = scene_elements['sensors']
                temp = sensors.get('temperature')
                humidity = sensors.get('humidity')
                
                if temp:
                    temp_desc = "cool" if temp < 18 else "warm" if temp > 25 else "comfortable"
                    description_parts.append(f"at a {temp_desc} temperature")
                if humidity:
                    humidity_desc = "dry" if humidity < 40 else "humid" if humidity > 70 else "moderate humidity"
                    description_parts.append(f"with {humidity_desc}")
            
            return "This appears to be " + ", ".join(description_parts) + "."
            
        except Exception as e:
            print(f"Error creating unified description: {e}")
            return "Unable to create unified scene description."
    
    async def _consensus_activity_fusion(self, activities: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Fuse activities using consensus approach"""
        try:
            # Group activities by type
            activity_votes = {}
            
            for activity in activities:
                activity_type = activity['activity']
                confidence = activity['confidence']
                
                if activity_type not in activity_votes:
                    activity_votes[activity_type] = []
                activity_votes[activity_type].append(confidence)
            
            # Find consensus activity (highest average confidence)
            best_activity = None
            best_score = 0.0
            
            for activity_type, confidences in activity_votes.items():
                avg_confidence = np.mean(confidences)
                if avg_confidence > best_score:
                    best_score = avg_confidence
                    best_activity = activity_type
            
            return {
                'activity': best_activity,
                'confidence': best_score,
                'supporting_modalities': len([a for a in activities if a['activity'] == best_activity])
            }
            
        except Exception as e:
            print(f"Error in consensus activity fusion: {e}")
            return {'activity': 'unknown', 'confidence': 0.0}
    
    def _calculate_activity_agreement(self, activities: List[Dict[str, Any]]) -> float:
        """Calculate agreement level between activity predictions"""
        try:
            if len(activities) < 2:
                return 1.0
            
            # Simple agreement based on activity similarity
            activity_types = [a['activity'] for a in activities]
            unique_activities = set(activity_types)
            
            # Agreement is higher when fewer unique activities are detected
            agreement = 1.0 - (len(unique_activities) - 1) / len(activities)
            return max(0.0, agreement)
            
        except Exception as e:
            print(f"Error calculating activity agreement: {e}")
            return 0.0
    
    async def _weighted_emotion_fusion(self, emotions: Dict[str, str], confidences: List[float]) -> str:
        """Fuse emotions using weighted voting"""
        try:
            # Map emotions to numerical values for fusion
            emotion_mapping = {
                'happy': 1.0, 'joy': 1.0, 'positive': 1.0,
                'sad': -1.0, 'negative': -1.0,
                'angry': -0.8, 'fear': -0.6,
                'surprise': 0.2, 'neutral': 0.0
            }
            
            weighted_sum = 0.0
            total_weight = 0.0
            
            modalities = list(emotions.keys())
            for i, (modality, emotion) in enumerate(emotions.items()):
                emotion_value = emotion_mapping.get(emotion.lower(), 0.0)
                weight = confidences[i] if i < len(confidences) else 0.5
                
                weighted_sum += emotion_value * weight
                total_weight += weight
            
            # Convert back to emotion category
            if total_weight > 0:
                avg_emotion_value = weighted_sum / total_weight
                
                if avg_emotion_value > 0.5:
                    return 'positive'
                elif avg_emotion_value < -0.5:
                    return 'negative'
                else:
                    return 'neutral'
            
            return 'neutral'
            
        except Exception as e:
            print(f"Error in weighted emotion fusion: {e}")
            return 'neutral'
    
    def _calculate_emotion_consistency(self, emotions: Dict[str, str]) -> float:
        """Calculate consistency between emotion predictions"""
        try:
            if len(emotions) < 2:
                return 1.0
            
            # Group similar emotions
            positive_emotions = {'happy', 'joy', 'positive', 'excited'}
            negative_emotions = {'sad', 'angry', 'fear', 'negative'}
            neutral_emotions = {'neutral', 'calm'}
            
            emotion_categories = []
            for emotion in emotions.values():
                emotion_lower = emotion.lower()
                if emotion_lower in positive_emotions:
                    emotion_categories.append('positive')
                elif emotion_lower in negative_emotions:
                    emotion_categories.append('negative')
                else:
                    emotion_categories.append('neutral')
            
            # Calculate consistency as proportion of same category
            most_common_category = max(set(emotion_categories), key=emotion_categories.count)
            consistency = emotion_categories.count(most_common_category) / len(emotion_categories)
            
            return consistency
            
        except Exception as e:
            print(f"Error calculating emotion consistency: {e}")
            return 0.0
    
    async def get_fusion_info(self) -> Dict[str, Any]:
        """Get information about the cross-modal fusion system"""
        return {
            'supported_fusion_methods': [method.value for method in FusionMethod],
            'default_fusion_method': self.default_fusion_method.value,
            'fusion_dimension': self.fusion_dimension,
            'modality_weights': self.modality_weights,
            'specialized_fusion_tasks': [
                'scene_understanding',
                'activity_recognition',
                'emotion_analysis'
            ]
        }
