from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum


class EmotionType(Enum):
    """Basic emotion types based on Plutchik's model"""
    JOY = "joy"
    SADNESS = "sadness"
    ANGER = "anger"
    FEAR = "fear"
    SURPRISE = "surprise"
    DISGUST = "disgust"
    ANTICIPATION = "anticipation"
    TRUST = "trust"
    
    # Complex emotions
    CURIOSITY = "curiosity"
    CONFUSION = "confusion"
    EXCITEMENT = "excitement"
    CONTENTMENT = "contentment"
    FRUSTRATION = "frustration"
    PRIDE = "pride"
    GUILT = "guilt"
    SHAME = "shame"


@dataclass
class EmotionalState:
    """
    Represents the emotional state using PAD (Pleasure-Arousal-Dominance) model
    combined with discrete emotion recognition.
    
    The PAD model provides a three-dimensional emotional space:
    - Valence (pleasure): positive/negative emotional value (-1.0 to 1.0)
    - Arousal: calm/excited activation level (0.0 to 1.0)  
    - Dominance: submissive/dominant control feeling (0.0 to 1.0)
    """
    
    # PAD dimensions
    valence: float = 0.0  # -1.0 (negative) to 1.0 (positive)
    arousal: float = 0.5  # 0.0 (calm) to 1.0 (excited)
    dominance: float = 0.5  # 0.0 (submissive) to 1.0 (dominant)
    
    # Discrete emotions with intensity
    emotions: Dict[EmotionType, float] = field(default_factory=dict)
    
    # Contextual information
    timestamp: datetime = field(default_factory=datetime.now)
    trigger_event: Optional[str] = None
    confidence: float = 0.0  # Confidence in emotional analysis
    
    # Memory and persistence
    emotional_memories: List[str] = field(default_factory=list)
    mood_trend: str = "stable"  # "rising", "falling", "stable", "volatile"
    
    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def add_emotion(self, emotion: EmotionType, intensity: float):
        """Add or update an emotion with given intensity (0.0 to 1.0)"""
        if 0.0 <= intensity <= 1.0:
            self.emotions[emotion] = intensity
        else:
            raise ValueError("Emotion intensity must be between 0.0 and 1.0")
    
    def get_dominant_emotion(self) -> Optional[EmotionType]:
        """Get the emotion with highest intensity"""
        if not self.emotions:
            return None
        return max(self.emotions.items(), key=lambda x: x[1])[0]
    
    def get_emotional_intensity(self) -> float:
        """Calculate overall emotional intensity"""
        if not self.emotions:
            return 0.0
        return sum(self.emotions.values()) / len(self.emotions)
    
    def is_positive(self) -> bool:
        """Check if the overall emotional state is positive"""
        return self.valence > 0.0
    
    def is_high_arousal(self) -> bool:
        """Check if arousal level is high"""
        return self.arousal > 0.7
    
    def is_dominant_state(self) -> bool:
        """Check if the state indicates high dominance/control"""
        return self.dominance > 0.7
    
    def get_emotional_quadrant(self) -> str:
        """
        Get emotional quadrant based on valence and arousal:
        - High valence, high arousal: "excited"
        - High valence, low arousal: "content"  
        - Low valence, high arousal: "distressed"
        - Low valence, low arousal: "depressed"
        """
        if self.valence >= 0.0:
            return "excited" if self.arousal >= 0.5 else "content"
        else:
            return "distressed" if self.arousal >= 0.5 else "depressed"
    
    def blend_with(self, other_state: 'EmotionalState', weight: float = 0.5) -> 'EmotionalState':
        """
        Blend this emotional state with another state.
        Weight determines the influence of the other state (0.0 to 1.0).
        """
        blended = EmotionalState()
        
        # Blend PAD dimensions
        blended.valence = self.valence * (1 - weight) + other_state.valence * weight
        blended.arousal = self.arousal * (1 - weight) + other_state.arousal * weight
        blended.dominance = self.dominance * (1 - weight) + other_state.dominance * weight
        
        # Blend emotions
        all_emotions = set(self.emotions.keys()) | set(other_state.emotions.keys())
        for emotion in all_emotions:
            self_intensity = self.emotions.get(emotion, 0.0)
            other_intensity = other_state.emotions.get(emotion, 0.0)
            blended_intensity = self_intensity * (1 - weight) + other_intensity * weight
            if blended_intensity > 0.01:  # Only keep significant emotions
                blended.emotions[emotion] = blended_intensity
        
        # Blend confidence
        blended.confidence = self.confidence * (1 - weight) + other_state.confidence * weight
        
        return blended
    
    def to_summary_string(self) -> str:
        """Get a human-readable summary of the emotional state"""
        summary_parts = []
        
        # Add PAD description
        valence_desc = "positive" if self.valence > 0.1 else "negative" if self.valence < -0.1 else "neutral"
        arousal_desc = "high-energy" if self.arousal > 0.7 else "low-energy" if self.arousal < 0.3 else "moderate-energy"
        summary_parts.append(f"{valence_desc}, {arousal_desc}")
        
        # Add dominant emotion
        dominant = self.get_dominant_emotion()
        if dominant:
            intensity = self.emotions[dominant]
            summary_parts.append(f"primarily {dominant.value} ({intensity:.1f})")
        
        # Add emotional quadrant
        summary_parts.append(f"quadrant: {self.get_emotional_quadrant()}")
        
        return " | ".join(summary_parts)
    
    def __str__(self) -> str:
        return f"EmotionalState(valence={self.valence:.2f}, arousal={self.arousal:.2f}, dominance={self.dominance:.2f})"


@dataclass 
class EmotionalMemory:
    """
    Represents an emotional memory that can influence future emotional responses
    """
    content: str
    emotional_state: EmotionalState
    strength: float = 1.0  # How strongly this memory influences emotions (0.0 to 1.0)
    timestamp: datetime = field(default_factory=datetime.now)
    trigger_patterns: List[str] = field(default_factory=list)  # What patterns trigger this memory
    decay_rate: float = 0.01  # How quickly this memory fades (per day)
    
    def is_relevant(self, current_context: str) -> float:
        """
        Check if this emotional memory is relevant to current context.
        Returns relevance score (0.0 to 1.0).
        """
        if not self.trigger_patterns:
            return 0.0
        
        relevance = 0.0
        context_lower = current_context.lower()
        
        for pattern in self.trigger_patterns:
            if pattern.lower() in context_lower:
                relevance = max(relevance, 0.8)
            elif any(word in context_lower for word in pattern.lower().split()):
                relevance = max(relevance, 0.4)
        
        return relevance * self.strength
    
    def get_current_strength(self) -> float:
        """Get current strength considering decay over time"""
        days_passed = (datetime.now() - self.timestamp).days
        decayed_strength = self.strength * (1 - self.decay_rate) ** days_passed
        return max(0.0, decayed_strength) 