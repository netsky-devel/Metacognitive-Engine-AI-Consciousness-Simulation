import os
import json
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
import google.generativeai as genai

from ..models.emotional_state import EmotionalState, EmotionType, EmotionalMemory
from ..memory.working_memory import WorkingMemory, StructuredInput
from ..models.entry import Entry, EntryType


class EmotionalEngine:
    """
    Advanced emotional processing engine that:
    1. Analyzes emotional content in text using AI
    2. Manages emotional state transitions over time
    3. Influences memory retrieval based on emotional context
    4. Generates emotionally-aware responses
    """
    
    def __init__(self):
        self.api_key = os.getenv('GEMINI_API_KEY')
        if self.api_key:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-pro')
            self.ai_available = True
            print("EmotionalEngine initialized with Gemini AI support")
        else:
            self.ai_available = False
            print("EmotionalEngine initialized without AI (GEMINI_API_KEY not found)")
        
        # Current emotional state
        self.current_emotional_state = EmotionalState()
        
        # Emotional memory system
        self.emotional_memories: List[EmotionalMemory] = []
        
        # Emotional history for tracking trends
        self.emotional_history: List[Tuple[datetime, EmotionalState]] = []
        
        # Configuration
        self.memory_decay_rate = 0.01  # Per day
        self.max_emotional_memories = 1000
        self.emotional_influence_threshold = 0.3
        
    def analyze_emotional_content(self, text: str, context: Optional[str] = None) -> EmotionalState:
        """
        Analyze the emotional content of text using AI or fallback patterns.
        Returns an EmotionalState object with detailed emotional analysis.
        """
        if self.ai_available:
            return self._ai_emotional_analysis(text, context)
        else:
            return self._pattern_emotional_analysis(text)
    
    def _ai_emotional_analysis(self, text: str, context: Optional[str] = None) -> EmotionalState:
        """Use Gemini AI for sophisticated emotional analysis"""
        try:
            context_part = f"\n\nAdditional context: {context}" if context else ""
            
            prompt = f"""
            Analyze the emotional content of the following text using the PAD (Pleasure-Arousal-Dominance) model and discrete emotions.
            
            Text: "{text}"{context_part}
            
            Please provide a detailed emotional analysis in the following JSON format:
            {{
                "valence": <float between -1.0 and 1.0>,
                "arousal": <float between 0.0 and 1.0>,
                "dominance": <float between 0.0 and 1.0>,
                "emotions": {{
                    "joy": <float between 0.0 and 1.0>,
                    "sadness": <float between 0.0 and 1.0>,
                    "anger": <float between 0.0 and 1.0>,
                    "fear": <float between 0.0 and 1.0>,
                    "surprise": <float between 0.0 and 1.0>,
                    "disgust": <float between 0.0 and 1.0>,
                    "anticipation": <float between 0.0 and 1.0>,
                    "trust": <float between 0.0 and 1.0>,
                    "curiosity": <float between 0.0 and 1.0>,
                    "confusion": <float between 0.0 and 1.0>,
                    "excitement": <float between 0.0 and 1.0>,
                    "contentment": <float between 0.0 and 1.0>,
                    "frustration": <float between 0.0 and 1.0>
                }},
                "confidence": <float between 0.0 and 1.0>,
                "trigger_event": "<brief description of what triggered these emotions>",
                "mood_trend": "<one of: rising, falling, stable, volatile>"
            }}
            
            Guidelines:
            - Valence: -1.0 = very negative, 0.0 = neutral, 1.0 = very positive
            - Arousal: 0.0 = very calm, 1.0 = very excited/activated
            - Dominance: 0.0 = submissive/powerless, 1.0 = dominant/in-control
            - Only include emotions that are actually present (can be 0.0 if not present)
            - Confidence reflects how certain you are about the emotional analysis
            - Consider cultural and contextual factors in emotional interpretation
            """
            
            response = self.model.generate_content(prompt)
            result_text = response.text.strip()
            
            # Extract JSON from response
            if '```json' in result_text:
                json_start = result_text.find('```json') + 7
                json_end = result_text.find('```', json_start)
                result_text = result_text[json_start:json_end].strip()
            elif '{' in result_text and '}' in result_text:
                json_start = result_text.find('{')
                json_end = result_text.rfind('}') + 1
                result_text = result_text[json_start:json_end]
            
            analysis = json.loads(result_text)
            
            # Create EmotionalState from analysis
            emotional_state = EmotionalState(
                valence=analysis.get('valence', 0.0),
                arousal=analysis.get('arousal', 0.5),
                dominance=analysis.get('dominance', 0.5),
                confidence=analysis.get('confidence', 0.0),
                trigger_event=analysis.get('trigger_event'),
                mood_trend=analysis.get('mood_trend', 'stable')
            )
            
            # Add discrete emotions
            emotions = analysis.get('emotions', {})
            for emotion_name, intensity in emotions.items():
                if intensity > 0.01:  # Only add significant emotions
                    try:
                        emotion_type = EmotionType(emotion_name.lower())
                        emotional_state.add_emotion(emotion_type, intensity)
                    except ValueError:
                        # Skip unknown emotion types
                        pass
            
            print(f"AI emotional analysis: {emotional_state.to_summary_string()}")
            return emotional_state
            
        except Exception as e:
            print(f"AI emotional analysis failed: {e}")
            return self._pattern_emotional_analysis(text)
    
    def _pattern_emotional_analysis(self, text: str) -> EmotionalState:
        """Fallback pattern-based emotional analysis"""
        text_lower = text.lower()
        emotional_state = EmotionalState(confidence=0.3)  # Lower confidence for pattern matching
        
        # Basic valence analysis
        positive_words = ['happy', 'joy', 'love', 'excellent', 'great', 'wonderful', 'amazing', 'good']
        negative_words = ['sad', 'angry', 'hate', 'terrible', 'awful', 'bad', 'horrible', 'worried']
        
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        if positive_count > negative_count:
            emotional_state.valence = min(0.8, positive_count * 0.3)
            emotional_state.add_emotion(EmotionType.JOY, min(0.8, positive_count * 0.2))
        elif negative_count > positive_count:
            emotional_state.valence = max(-0.8, -negative_count * 0.3)
            emotional_state.add_emotion(EmotionType.SADNESS, min(0.8, negative_count * 0.2))
        
        # Basic arousal analysis
        high_arousal_words = ['excited', 'thrilled', 'angry', 'scared', 'surprised']
        arousal_count = sum(1 for word in high_arousal_words if word in text_lower)
        emotional_state.arousal = min(1.0, 0.5 + arousal_count * 0.2)
        
        # Question marks and exclamation points
        emotional_state.arousal += min(0.3, text.count('!') * 0.1 + text.count('?') * 0.05)
        
        print(f"Pattern emotional analysis: {emotional_state.to_summary_string()}")
        return emotional_state
    
    def update_emotional_state(self, new_state: EmotionalState, blend_weight: float = 0.7):
        """
        Update the current emotional state by blending with new emotional input.
        Higher blend_weight gives more influence to the new state.
        """
        # Store previous state in history
        self.emotional_history.append((datetime.now(), self.current_emotional_state))
        
        # Keep only recent history (last 24 hours)
        cutoff_time = datetime.now() - timedelta(hours=24)
        self.emotional_history = [
            (timestamp, state) for timestamp, state in self.emotional_history
            if timestamp > cutoff_time
        ]
        
        # Blend current state with new state
        self.current_emotional_state = self.current_emotional_state.blend_with(new_state, blend_weight)
        self.current_emotional_state.timestamp = datetime.now()
        
        print(f"Emotional state updated: {self.current_emotional_state.to_summary_string()}")
    
    def create_emotional_memory(self, content: str, emotional_state: EmotionalState, 
                              trigger_patterns: List[str]) -> EmotionalMemory:
        """Create a new emotional memory that can influence future responses"""
        emotional_memory = EmotionalMemory(
            content=content,
            emotional_state=emotional_state,
            trigger_patterns=trigger_patterns,
            decay_rate=self.memory_decay_rate
        )
        
        self.emotional_memories.append(emotional_memory)
        
        # Limit memory size
        if len(self.emotional_memories) > self.max_emotional_memories:
            # Remove oldest and weakest memories
            self.emotional_memories.sort(key=lambda m: (m.timestamp, m.get_current_strength()))
            self.emotional_memories = self.emotional_memories[-self.max_emotional_memories:]
        
        print(f"Created emotional memory: {content[:50]}...")
        return emotional_memory
    
    def retrieve_emotional_memories(self, context: str, max_memories: int = 5) -> List[EmotionalMemory]:
        """Retrieve relevant emotional memories based on current context"""
        relevant_memories = []
        
        for memory in self.emotional_memories:
            relevance = memory.is_relevant(context)
            if relevance > self.emotional_influence_threshold:
                relevant_memories.append((memory, relevance))
        
        # Sort by relevance and current strength
        relevant_memories.sort(key=lambda x: x[1] * x[0].get_current_strength(), reverse=True)
        
        selected_memories = [memory for memory, _ in relevant_memories[:max_memories]]
        print(f"Retrieved {len(selected_memories)} relevant emotional memories")
        
        return selected_memories
    
    def process_emotional_input(self, working_memory: WorkingMemory):
        """
        Process emotional content from working memory and update emotional state.
        This integrates emotion analysis with the cognitive processing cycle.
        """
        if not working_memory.structured_input:
            return
        
        # Analyze emotional content of input
        input_text = working_memory.structured_input.raw_text
        context = working_memory.get_context_summary()
        
        new_emotional_state = self.analyze_emotional_content(input_text, context)
        
        # Update current emotional state
        self.update_emotional_state(new_emotional_state)
        
        # Retrieve relevant emotional memories
        emotional_memories = self.retrieve_emotional_memories(input_text)
        
        # Influence current emotional state based on memories
        for memory in emotional_memories:
            influence_weight = memory.get_current_strength() * 0.3  # Moderate influence
            self.current_emotional_state = self.current_emotional_state.blend_with(
                memory.emotional_state, influence_weight
            )
        
        # Create emotional memory for this interaction
        if new_emotional_state.get_emotional_intensity() > 0.2:  # Only for significant emotions
            trigger_patterns = [
                input_text[:30],  # First part of input
                working_memory.structured_input.intent,
                working_memory.structured_input.sentiment
            ]
            self.create_emotional_memory(input_text, new_emotional_state, trigger_patterns)
        
        # Add emotional context to working memory
        working_memory.add_context_tag(f"emotional_state:{self.current_emotional_state.get_emotional_quadrant()}")
        if self.current_emotional_state.get_dominant_emotion():
            dominant = self.current_emotional_state.get_dominant_emotion()
            working_memory.add_context_tag(f"dominant_emotion:{dominant.value}")
        
        # Update working memory with current emotional state
        working_memory.set_emotional_state(self.current_emotional_state)
        
        print(f"Processed emotional input - Current state: {self.current_emotional_state.to_summary_string()}")
    
    def generate_emotional_response_guidance(self, working_memory: WorkingMemory) -> Dict[str, Any]:
        """
        Generate guidance for emotionally-aware response generation.
        Returns emotional context that can be used by ResponseGenerator.
        """
        guidance = {
            "current_emotional_state": self.current_emotional_state,
            "emotional_quadrant": self.current_emotional_state.get_emotional_quadrant(),
            "dominant_emotion": self.current_emotional_state.get_dominant_emotion(),
            "emotional_intensity": self.current_emotional_state.get_emotional_intensity(),
            "should_be_empathetic": self.current_emotional_state.valence < -0.3,
            "should_be_encouraging": self.current_emotional_state.valence < 0 and self.current_emotional_state.arousal < 0.5,
            "should_match_energy": self.current_emotional_state.arousal > 0.7,
            "emotional_memories_active": len(self.retrieve_emotional_memories(
                working_memory.get_context_summary() if working_memory else "", 3
            )) > 0
        }
        
        # Add specific emotional guidance
        if self.current_emotional_state.is_positive():
            guidance["tone_suggestion"] = "warm and engaging"
        elif self.current_emotional_state.valence < -0.5:
            guidance["tone_suggestion"] = "supportive and understanding"
        else:
            guidance["tone_suggestion"] = "balanced and thoughtful"
        
        # Add arousal-based guidance
        if self.current_emotional_state.is_high_arousal():
            guidance["energy_suggestion"] = "match the high energy"
        else:
            guidance["energy_suggestion"] = "calm and steady"
        
        return guidance
    
    def get_emotional_state_summary(self) -> Dict[str, Any]:
        """Get a summary of the current emotional state for debugging/monitoring"""
        return {
            "current_state": self.current_emotional_state.to_summary_string(),
            "valence": self.current_emotional_state.valence,
            "arousal": self.current_emotional_state.arousal,
            "dominance": self.current_emotional_state.dominance,
            "dominant_emotion": self.current_emotional_state.get_dominant_emotion().value if self.current_emotional_state.get_dominant_emotion() else None,
            "emotional_memories_count": len(self.emotional_memories),
            "emotional_history_count": len(self.emotional_history),
            "last_update": self.current_emotional_state.timestamp.isoformat()
        } 