import pytest
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock

from src.engine.models.emotional_state import (
    EmotionalState, EmotionType, EmotionalMemory
)
from src.engine.processors.emotional_engine import EmotionalEngine
from src.engine.memory.working_memory import WorkingMemory, StructuredInput
from src.engine.engine import MetacognitiveEngine


class TestEmotionalState:
    """Test the EmotionalState class and its methods"""
    
    def test_emotional_state_creation(self):
        """Test creating an EmotionalState with default values"""
        state = EmotionalState()
        assert state.valence == 0.0
        assert state.arousal == 0.5
        assert state.dominance == 0.5
        assert len(state.emotions) == 0
        assert state.confidence == 0.0
    
    def test_add_emotion(self):
        """Test adding emotions to the state"""
        state = EmotionalState()
        state.add_emotion(EmotionType.JOY, 0.8)
        state.add_emotion(EmotionType.EXCITEMENT, 0.6)
        
        assert state.emotions[EmotionType.JOY] == 0.8
        assert state.emotions[EmotionType.EXCITEMENT] == 0.6
    
    def test_add_emotion_invalid_intensity(self):
        """Test that invalid emotion intensities raise ValueError"""
        state = EmotionalState()
        with pytest.raises(ValueError):
            state.add_emotion(EmotionType.JOY, 1.5)
        with pytest.raises(ValueError):
            state.add_emotion(EmotionType.JOY, -0.1)
    
    def test_get_dominant_emotion(self):
        """Test getting the dominant emotion"""
        state = EmotionalState()
        state.add_emotion(EmotionType.JOY, 0.3)
        state.add_emotion(EmotionType.EXCITEMENT, 0.8)
        state.add_emotion(EmotionType.CURIOSITY, 0.5)
        
        assert state.get_dominant_emotion() == EmotionType.EXCITEMENT
    
    def test_get_dominant_emotion_no_emotions(self):
        """Test getting dominant emotion when no emotions are present"""
        state = EmotionalState()
        assert state.get_dominant_emotion() is None
    
    def test_emotional_intensity(self):
        """Test calculating overall emotional intensity"""
        state = EmotionalState()
        assert state.get_emotional_intensity() == 0.0
        
        state.add_emotion(EmotionType.JOY, 0.6)
        state.add_emotion(EmotionType.TRUST, 0.4)
        assert state.get_emotional_intensity() == 0.5  # (0.6 + 0.4) / 2
    
    def test_emotional_properties(self):
        """Test various emotional state properties"""
        # Positive state
        positive_state = EmotionalState(valence=0.5, arousal=0.3, dominance=0.8)
        assert positive_state.is_positive()
        assert not positive_state.is_high_arousal()
        assert positive_state.is_dominant_state()
        
        # Negative, high arousal state
        negative_state = EmotionalState(valence=-0.7, arousal=0.9, dominance=0.2)
        assert not negative_state.is_positive()
        assert negative_state.is_high_arousal()
        assert not negative_state.is_dominant_state()
    
    def test_emotional_quadrants(self):
        """Test emotional quadrant classification"""
        # Excited: positive valence, high arousal
        excited = EmotionalState(valence=0.5, arousal=0.8)
        assert excited.get_emotional_quadrant() == "excited"
        
        # Content: positive valence, low arousal
        content = EmotionalState(valence=0.3, arousal=0.2)
        assert content.get_emotional_quadrant() == "content"
        
        # Distressed: negative valence, high arousal
        distressed = EmotionalState(valence=-0.6, arousal=0.8)
        assert distressed.get_emotional_quadrant() == "distressed"
        
        # Depressed: negative valence, low arousal
        depressed = EmotionalState(valence=-0.4, arousal=0.3)
        assert depressed.get_emotional_quadrant() == "depressed"
    
    def test_blend_emotional_states(self):
        """Test blending two emotional states"""
        state1 = EmotionalState(valence=0.8, arousal=0.6, dominance=0.7)
        state1.add_emotion(EmotionType.JOY, 0.9)
        
        state2 = EmotionalState(valence=-0.2, arousal=0.8, dominance=0.3)
        state2.add_emotion(EmotionType.ANGER, 0.7)
        
        # Blend with 50% weight
        blended = state1.blend_with(state2, 0.5)
        
        assert abs(blended.valence - 0.3) < 0.001  # (0.8 + (-0.2)) / 2
        assert abs(blended.arousal - 0.7) < 0.001  # (0.6 + 0.8) / 2
        assert abs(blended.dominance - 0.5) < 0.001  # (0.7 + 0.3) / 2
        
        # Both emotions should be present but reduced
        assert EmotionType.JOY in blended.emotions
        assert EmotionType.ANGER in blended.emotions
        assert blended.emotions[EmotionType.JOY] < 0.9
        assert blended.emotions[EmotionType.ANGER] < 0.7
    
    def test_to_summary_string(self):
        """Test emotional state summary generation"""
        state = EmotionalState(valence=0.6, arousal=0.8, dominance=0.5)
        state.add_emotion(EmotionType.EXCITEMENT, 0.9)
        
        summary = state.to_summary_string()
        assert "positive" in summary
        assert "high-energy" in summary
        assert "excitement" in summary
        assert "excited" in summary  # quadrant


class TestEmotionalMemory:
    """Test the EmotionalMemory class"""
    
    def test_emotional_memory_creation(self):
        """Test creating an emotional memory"""
        emotional_state = EmotionalState(valence=0.7, arousal=0.6)
        emotional_state.add_emotion(EmotionType.JOY, 0.8)
        
        memory = EmotionalMemory(
            content="Had a great conversation about AI",
            emotional_state=emotional_state,
            trigger_patterns=["AI", "conversation", "great"]
        )
        
        assert memory.content == "Had a great conversation about AI"
        assert memory.emotional_state.valence == 0.7
        assert "AI" in memory.trigger_patterns
        assert memory.strength == 1.0
    
    def test_emotional_memory_relevance(self):
        """Test emotional memory relevance calculation"""
        memory = EmotionalMemory(
            content="Discussed machine learning",
            emotional_state=EmotionalState(),
            trigger_patterns=["machine learning", "AI", "neural networks"]
        )
        
        # High relevance for exact match
        assert memory.is_relevant("I want to learn about machine learning") > 0.7
        
        # Medium relevance for partial match
        assert memory.is_relevant("What is AI about?") > 0.3
        
        # Low relevance for no match
        assert memory.is_relevant("Tell me about cooking") < 0.1
    
    def test_emotional_memory_decay(self):
        """Test emotional memory strength decay over time"""
        old_timestamp = datetime.now() - timedelta(days=10)
        memory = EmotionalMemory(
            content="Old memory",
            emotional_state=EmotionalState(),
            timestamp=old_timestamp,
            decay_rate=0.1  # High decay rate for testing
        )
        
        current_strength = memory.get_current_strength()
        assert current_strength < 1.0  # Should have decayed
        assert current_strength > 0.0  # But not completely gone


class TestEmotionalEngine:
    """Test the EmotionalEngine class"""
    
    def test_emotional_engine_initialization(self):
        """Test initializing the emotional engine"""
        engine = EmotionalEngine()
        assert engine.current_emotional_state is not None
        assert len(engine.emotional_memories) == 0
        assert engine.max_emotional_memories == 1000
    
    def test_pattern_emotional_analysis(self):
        """Test pattern-based emotional analysis (fallback mode)"""
        engine = EmotionalEngine()
        
        # Test positive text
        positive_state = engine._pattern_emotional_analysis("I am very happy and excited!")
        assert positive_state.valence > 0
        assert positive_state.arousal > 0.5  # Exclamation mark increases arousal
        assert EmotionType.JOY in positive_state.emotions
        
        # Test negative text
        negative_state = engine._pattern_emotional_analysis("I am sad and worried about this")
        assert negative_state.valence < 0
        assert EmotionType.SADNESS in negative_state.emotions
    
    @patch('google.generativeai.GenerativeModel')
    def test_ai_emotional_analysis_success(self, mock_genai):
        """Test AI-based emotional analysis when it succeeds"""
        # Mock successful AI response
        mock_response = MagicMock()
        mock_response.text = '''```json
        {
            "valence": 0.7,
            "arousal": 0.6,
            "dominance": 0.8,
            "emotions": {
                "joy": 0.8,
                "excitement": 0.6,
                "trust": 0.4
            },
            "confidence": 0.9,
            "trigger_event": "positive discussion",
            "mood_trend": "rising"
        }
        ```'''
        
        mock_model = MagicMock()
        mock_model.generate_content.return_value = mock_response
        mock_genai.return_value = mock_model
        
        # Create engine with mocked AI
        engine = EmotionalEngine()
        engine.model = mock_model
        engine.ai_available = True
        
        result = engine._ai_emotional_analysis("This is a great conversation!")
        
        assert result.valence == 0.7
        assert result.arousal == 0.6
        assert result.dominance == 0.8
        assert result.confidence == 0.9
        assert EmotionType.JOY in result.emotions
        assert result.emotions[EmotionType.JOY] == 0.8
    
    @patch('google.generativeai.GenerativeModel')
    def test_ai_emotional_analysis_fallback(self, mock_genai):
        """Test AI emotional analysis falls back to pattern matching on error"""
        # Mock AI failure
        mock_model = MagicMock()
        mock_model.generate_content.side_effect = Exception("API Error")
        mock_genai.return_value = mock_model
        
        engine = EmotionalEngine()
        engine.model = mock_model
        engine.ai_available = True
        
        # Should fallback to pattern analysis
        result = engine._ai_emotional_analysis("I am happy!")
        assert result.confidence < 0.9  # Pattern analysis has lower confidence
        assert result.valence > 0  # Should still detect positive emotion
    
    def test_emotional_state_update(self):
        """Test updating emotional state with blending"""
        engine = EmotionalEngine()
        
        # Set initial state
        initial_state = EmotionalState(valence=0.2, arousal=0.4)
        initial_state.add_emotion(EmotionType.CONTENTMENT, 0.5)
        engine.current_emotional_state = initial_state
        
        # Update with new state
        new_state = EmotionalState(valence=0.8, arousal=0.9)
        new_state.add_emotion(EmotionType.EXCITEMENT, 0.9)
        
        engine.update_emotional_state(new_state, blend_weight=0.7)
        
        # Should be blended between initial and new state
        assert engine.current_emotional_state.valence > 0.2
        assert engine.current_emotional_state.valence < 0.8
        assert engine.current_emotional_state.arousal > 0.4
    
    def test_create_emotional_memory(self):
        """Test creating emotional memories"""
        engine = EmotionalEngine()
        
        emotional_state = EmotionalState(valence=0.6, arousal=0.7)
        emotional_state.add_emotion(EmotionType.JOY, 0.8)
        
        memory = engine.create_emotional_memory(
            content="Had a wonderful discussion",
            emotional_state=emotional_state,
            trigger_patterns=["discussion", "wonderful"]
        )
        
        assert len(engine.emotional_memories) == 1
        assert memory.content == "Had a wonderful discussion"
        assert memory.emotional_state.valence == 0.6
    
    def test_retrieve_emotional_memories(self):
        """Test retrieving relevant emotional memories"""
        engine = EmotionalEngine()
        
        # Create some emotional memories
        memory1 = EmotionalMemory(
            content="Discussed AI safety",
            emotional_state=EmotionalState(valence=0.3),
            trigger_patterns=["AI", "safety", "ethics"]
        )
        
        memory2 = EmotionalMemory(
            content="Talked about cooking",
            emotional_state=EmotionalState(valence=0.8),
            trigger_patterns=["cooking", "food", "recipes"]
        )
        
        engine.emotional_memories = [memory1, memory2]
        
        # Retrieve memories relevant to AI discussion
        relevant = engine.retrieve_emotional_memories("Let's discuss AI ethics")
        
        # Should find the AI-related memory
        assert len(relevant) >= 1
        assert any("AI safety" in memory.content for memory in relevant)
    
    def test_process_emotional_input_integration(self):
        """Test emotional input processing with WorkingMemory"""
        engine = EmotionalEngine()
        working_memory = WorkingMemory()
        
        # Set up structured input
        structured_input = StructuredInput(
            raw_text="I'm excited about this new project!",
            language="en",
            entities=[],
            intent="STATEMENT",
            sentiment="POSITIVE",
            tone="ENTHUSIASTIC"
        )
        working_memory.set_input(structured_input)
        
        # Process emotional input
        engine.process_emotional_input(working_memory)
        
        # Check that emotional state was updated
        assert working_memory.cognitive_state.emotional_state is not None
        assert working_memory.cognitive_state.emotional_processing_enabled
        
        # Check that context tags were added
        emotional_tags = [tag for tag in working_memory.context_tags if "emotional" in tag or "emotion" in tag]
        assert len(emotional_tags) > 0


class TestEmotionalEngineIntegration:
    """Test integration of emotional system with the main engine"""
    
    def test_engine_with_emotions_enabled(self):
        """Test that the main engine properly initializes with emotions"""
        engine = MetacognitiveEngine(enable_emotions=True)
        
        assert engine.emotions_enabled
        assert engine.emotional_engine is not None
        assert isinstance(engine.emotional_engine, EmotionalEngine)
    
    def test_engine_with_emotions_disabled(self):
        """Test that the main engine can run without emotions"""
        engine = MetacognitiveEngine(enable_emotions=False)
        
        assert not engine.emotions_enabled
        assert engine.emotional_engine is None
    
    @patch('src.engine.processors.emotional_engine.EmotionalEngine.process_emotional_input')
    def test_emotional_processing_in_cognitive_cycle(self, mock_process):
        """Test that emotional processing is called during cognitive cycle"""
        engine = MetacognitiveEngine(enable_emotions=True)
        
        # Mock other components to focus on emotional processing
        with patch.object(engine.sensory_cortex, 'analyze') as mock_analyze, \
             patch.object(engine.associative_engine, 'process') as mock_assoc, \
             patch.object(engine.introspection_engine, 'process') as mock_intro, \
             patch.object(engine.response_generator, 'generate_response') as mock_response:
            
            mock_analyze.return_value = StructuredInput(
                raw_text="Test input",
                language="en",
                entities=[],
                intent="QUESTION",
                sentiment="NEUTRAL",
                tone="CASUAL"
            )
            mock_assoc.return_value = True
            mock_intro.return_value = True
            mock_response.return_value = "Test response"
            
            # Process thought - should trigger emotional processing
            engine.process_thought("Test input with emotions")
            
            # Verify emotional processing was called
            mock_process.assert_called_once()
    
    def test_emotional_context_in_working_memory(self):
        """Test that emotional context is properly stored in working memory"""
        engine = MetacognitiveEngine(enable_emotions=True)
        working_memory = WorkingMemory()
        
        # Create an emotional state
        emotional_state = EmotionalState(valence=0.7, arousal=0.6)
        emotional_state.add_emotion(EmotionType.JOY, 0.8)
        
        # Set emotional state in working memory
        working_memory.set_emotional_state(emotional_state)
        
        # Get emotional context
        context = working_memory.get_emotional_context()
        
        assert context["emotional_quadrant"] == "excited"
        assert context["dominant_emotion"] == EmotionType.JOY
        assert context["is_positive"] == True
        assert context["valence"] == 0.7
        assert context["arousal"] == 0.6


if __name__ == "__main__":
    pytest.main([__file__]) 