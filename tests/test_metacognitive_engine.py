"""
Tests for MetacognitiveEngine

Test suite for core metacognitive functionality.
"""

import pytest
import asyncio
import time
from unittest.mock import AsyncMock, MagicMock

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from metacognitive_ai.core.engine import (
    MetacognitiveEngine, 
    CognitiveStep, 
    MetacognitiveSession,
    CognitiveState
)


class TestMetacognitiveEngine:
    """Test suite for MetacognitiveEngine class"""
    
    @pytest.fixture
    def engine(self):
        """Create a MetacognitiveEngine instance for testing"""
        return MetacognitiveEngine(
            introspection_level="medium",
            enable_real_time=False  # Disable for testing
        )
    
    @pytest.fixture
    def sample_session(self):
        """Create a sample metacognitive session"""
        session = MetacognitiveSession(
            initial_prompt="Test prompt",
            start_time=time.time()
        )
        
        # Add some sample cognitive steps
        steps = [
            CognitiveStep(
                content="Initial analysis",
                step_type="analysis",
                confidence=0.7
            ),
            CognitiveStep(
                content="Consider alternatives",
                step_type="reasoning",
                confidence=0.6
            ),
            CognitiveStep(
                content="Make decision",
                step_type="decision",
                confidence=0.8
            )
        ]
        
        session.cognitive_steps = steps
        return session
    
    def test_engine_initialization(self, engine):
        """Test that engine initializes correctly"""
        assert engine.introspection_level == "medium"
        assert engine.enable_real_time == False
        assert engine.current_session is None
        assert engine.session_history == []
        assert engine.cognitive_state == CognitiveState.IDLE
    
    @pytest.mark.asyncio
    async def test_start_session(self, engine):
        """Test starting a new session"""
        prompt = "What is consciousness?"
        session_id = await engine.start_session(prompt)
        
        assert session_id is not None
        assert engine.current_session is not None
        assert engine.current_session.initial_prompt == prompt
        assert engine.cognitive_state == CognitiveState.THINKING
    
    @pytest.mark.asyncio
    async def test_add_thought_step(self, engine):
        """Test adding thought steps to session"""
        await engine.start_session("Test prompt")
        
        step_id = await engine.add_thought_step(
            content="This is a test thought",
            step_type="analysis",
            confidence=0.75
        )
        
        assert step_id is not None
        assert len(engine.current_session.cognitive_steps) == 1
        
        step = engine.current_session.cognitive_steps[0]
        assert step.content == "This is a test thought"
        assert step.step_type == "analysis"
        assert step.confidence == 0.75
    
    @pytest.mark.asyncio
    async def test_add_thought_step_without_session(self, engine):
        """Test that adding thought step without session raises error"""
        with pytest.raises(ValueError, match="No active session"):
            await engine.add_thought_step("Test thought")
    
    @pytest.mark.asyncio
    async def test_generate_introspection(self, engine):
        """Test generating introspection report"""
        await engine.start_session("Test prompt")
        await engine.add_thought_step("Step 1", "analysis", 0.8)
        await engine.add_thought_step("Step 2", "reasoning", 0.6)
        
        report = await engine.generate_introspection()
        
        assert "session_id" in report
        assert "total_steps" in report
        assert report["total_steps"] == 2
        assert "thinking_patterns" in report
        assert "confidence_analysis" in report
    
    @pytest.mark.asyncio
    async def test_end_session(self, engine):
        """Test ending a session"""
        # Start session and add steps
        await engine.start_session("Test prompt")
        await engine.add_thought_step("Test step", "analysis", 0.7)
        
        # End session
        final_response = "This is the final response"
        completed_session = await engine.end_session(final_response)
        
        assert completed_session is not None
        assert completed_session.final_response == final_response
        assert completed_session.end_time is not None
        assert engine.current_session is None
        assert engine.cognitive_state == CognitiveState.IDLE
        assert len(engine.session_history) == 1
    
    @pytest.mark.asyncio
    async def test_end_session_without_active_session(self, engine):
        """Test that ending session without active session raises error"""
        with pytest.raises(ValueError, match="No active session"):
            await engine.end_session()
    
    def test_get_session_summary_current(self, engine, sample_session):
        """Test getting summary of current session"""
        engine.current_session = sample_session
        
        summary = engine.get_session_summary()
        
        assert "id" in summary
        assert "duration" in summary
        assert "step_count" in summary
        assert summary["step_count"] == 3
    
    def test_get_session_summary_historical(self, engine, sample_session):
        """Test getting summary of historical session"""
        sample_session.end_time = time.time()
        engine.session_history.append(sample_session)
        
        summary = engine.get_session_summary(sample_session.id)
        
        assert "id" in summary
        assert summary["id"] == sample_session.id
        assert "step_count" in summary
        assert summary["step_count"] == 3
    
    def test_get_session_summary_not_found(self, engine):
        """Test getting summary of non-existent session"""
        with pytest.raises(ValueError, match="Session not found"):
            engine.get_session_summary("non-existent-id")
    
    @pytest.mark.asyncio
    async def test_multiple_sessions(self, engine):
        """Test handling multiple sequential sessions"""
        # First session
        session1_id = await engine.start_session("First prompt")
        await engine.add_thought_step("First thought", "analysis", 0.7)
        completed1 = await engine.end_session("First response")
        
        # Second session
        session2_id = await engine.start_session("Second prompt")
        await engine.add_thought_step("Second thought", "reasoning", 0.8)
        completed2 = await engine.end_session("Second response")
        
        assert session1_id != session2_id
        assert len(engine.session_history) == 2
        assert engine.session_history[0].id == completed1.id
        assert engine.session_history[1].id == completed2.id
    
    def test_calculate_average_confidence(self, engine, sample_session):
        """Test confidence calculation"""
        engine.current_session = sample_session
        
        avg_confidence = engine._calculate_average_confidence()
        
        # Sample session has confidences [0.7, 0.6, 0.8]
        expected_avg = (0.7 + 0.6 + 0.8) / 3
        assert abs(avg_confidence - expected_avg) < 0.001
    
    def test_calculate_average_confidence_no_session(self, engine):
        """Test confidence calculation with no session"""
        avg_confidence = engine._calculate_average_confidence()
        assert avg_confidence == 0.0
    
    def test_analyze_thinking_patterns(self, engine, sample_session):
        """Test thinking pattern analysis"""
        engine.current_session = sample_session
        
        patterns = engine._analyze_thinking_patterns()
        
        assert "step_type_distribution" in patterns
        assert "common_sequences" in patterns
        assert "total_transitions" in patterns
        
        # Check step type distribution
        distribution = patterns["step_type_distribution"]
        assert distribution["analysis"] == 1
        assert distribution["reasoning"] == 1
        assert distribution["decision"] == 1
    
    def test_analyze_confidence(self, engine, sample_session):
        """Test confidence analysis"""
        engine.current_session = sample_session
        
        analysis = engine._analyze_confidence()
        
        assert "average" in analysis
        assert "min" in analysis
        assert "max" in analysis
        assert "variance" in analysis
        assert "trend" in analysis
        
        # Check values
        assert analysis["min"] == 0.6
        assert analysis["max"] == 0.8
        assert abs(analysis["average"] - 0.7) < 0.001
    
    def test_generate_insights(self, engine, sample_session):
        """Test insight generation"""
        engine.current_session = sample_session
        
        insights = engine._generate_insights()
        
        assert isinstance(insights, list)
        # Should have some insights for this session
        assert len(insights) > 0
    
    def test_generate_summary(self, engine, sample_session):
        """Test summary generation"""
        engine.current_session = sample_session
        
        summary = engine._generate_summary()
        
        assert isinstance(summary, str)
        assert len(summary) > 0
        assert "3" in summary  # Should mention 3 steps
    
    @pytest.mark.asyncio
    async def test_session_auto_introspection(self, engine):
        """Test that introspection is automatically generated on session end"""
        await engine.start_session("Test prompt")
        await engine.add_thought_step("Test step", "analysis", 0.7)
        
        completed_session = await engine.end_session("Final response")
        
        # Should have automatically generated introspection
        assert completed_session.introspection_report is not None
        assert len(completed_session.introspection_report) > 0
    
    def test_real_time_subscription(self, engine):
        """Test real-time subscription functionality"""
        callback = MagicMock()
        
        # Subscribe
        engine.subscribe_realtime(callback)
        assert callback in engine._real_time_subscribers
        
        # Unsubscribe
        engine.unsubscribe_realtime(callback)
        assert callback not in engine._real_time_subscribers

    @pytest.mark.asyncio
    async def test_complete_workflow(self):
        """Test complete metacognitive workflow"""
        engine = MetacognitiveEngine(enable_real_time=False)
        
        # Start session
        session_id = await engine.start_session("Analyze the nature of consciousness")
        
        # Add thought steps
        await engine.add_thought_step(
            "Consciousness involves self-awareness",
            step_type="analysis",
            confidence=0.8
        )
        
        await engine.add_thought_step(
            "But what constitutes genuine self-awareness?",
            step_type="questioning",
            confidence=0.6
        )
        
        await engine.add_thought_step(
            "Perhaps it's the ability to model one's own mental states",
            step_type="hypothesis",
            confidence=0.7
        )
        
        # Generate introspection
        introspection = await engine.generate_introspection()
        assert introspection["total_steps"] == 3
        
        # End session
        completed_session = await engine.end_session("Consciousness may be recursive self-modeling")
        
        # Verify results
        assert len(completed_session.cognitive_steps) == 3
        assert completed_session.introspection_report is not None
        assert len(engine.session_history) == 1


class TestCognitiveStep:
    """Test suite for CognitiveStep dataclass"""
    
    def test_cognitive_step_creation(self):
        """Test creating a cognitive step"""
        step = CognitiveStep(
            content="Test content",
            step_type="analysis",
            confidence=0.8
        )
        
        assert step.content == "Test content"
        assert step.step_type == "analysis"
        assert step.confidence == 0.8
        assert step.id is not None
        assert step.timestamp > 0
    
    def test_cognitive_step_defaults(self):
        """Test cognitive step with default values"""
        step = CognitiveStep()
        
        assert step.content == ""
        assert step.step_type == "reasoning"
        assert step.confidence == 0.5
        assert step.emotional_state == {}
        assert step.connections == []
        assert step.metadata == {}


class TestMetacognitiveSession:
    """Test suite for MetacognitiveSession dataclass"""
    
    def test_session_creation(self):
        """Test creating a metacognitive session"""
        session = MetacognitiveSession(
            initial_prompt="Test prompt"
        )
        
        assert session.initial_prompt == "Test prompt"
        assert session.id is not None
        assert session.start_time > 0
        assert session.end_time is None
        assert session.cognitive_steps == []
    
    def test_session_with_steps(self):
        """Test session with cognitive steps"""
        session = MetacognitiveSession()
        
        step1 = CognitiveStep(content="Step 1")
        step2 = CognitiveStep(content="Step 2")
        
        session.cognitive_steps = [step1, step2]
        
        assert len(session.cognitive_steps) == 2
        assert session.cognitive_steps[0].content == "Step 1"
        assert session.cognitive_steps[1].content == "Step 2"


# Integration tests
class TestMetacognitiveIntegration:
    """Integration tests for the complete metacognitive workflow"""
    
    @pytest.mark.asyncio
    async def test_complete_workflow(self):
        """Test complete metacognitive workflow"""
        engine = MetacognitiveEngine(enable_real_time=False)
        
        # Start session
        session_id = await engine.start_session("Solve the trolley problem")
        assert session_id is not None
        
        # Add various thought steps
        await engine.add_thought_step(
            "The trolley problem is a classic ethical dilemma",
            step_type="analysis",
            confidence=0.9
        )
        
        await engine.add_thought_step(
            "I need to consider utilitarian vs deontological ethics",
            step_type="reasoning",
            confidence=0.7
        )
        
        await engine.add_thought_step(
            "Utilitarian approach: save the most lives",
            step_type="evaluation",
            confidence=0.8
        )
        
        await engine.add_thought_step(
            "Deontological approach: don't actively harm",
            step_type="evaluation",
            confidence=0.8
        )
        
        await engine.add_thought_step(
            "I lean towards the utilitarian solution",
            step_type="decision",
            confidence=0.6
        )
        
        # Generate introspection mid-session
        introspection = await engine.generate_introspection()
        assert introspection["total_steps"] == 5
        
        # End session
        final_response = "Pull the lever to save more lives, despite moral discomfort"
        completed_session = await engine.end_session(final_response)
        
        # Verify complete session
        assert completed_session.final_response == final_response
        assert len(completed_session.cognitive_steps) == 5
        assert completed_session.performance_metrics["total_steps"] == 5
        assert "session_duration" in completed_session.performance_metrics
        assert "average_confidence" in completed_session.performance_metrics
        
        # Verify introspection quality
        report = completed_session.introspection_report
        assert "thinking_patterns" in report
        assert "confidence_analysis" in report
        assert len(report["insights"]) > 0
        
        # Verify session history
        assert len(engine.session_history) == 1
        assert engine.current_session is None
    
    @pytest.mark.asyncio
    async def test_error_handling(self):
        """Test error handling in various scenarios"""
        engine = MetacognitiveEngine()
        
        # Test operations without active session
        with pytest.raises(ValueError):
            await engine.add_thought_step("Test")
        
        with pytest.raises(ValueError):
            await engine.generate_introspection()
        
        with pytest.raises(ValueError):
            await engine.end_session()
        
        # Test session not found
        with pytest.raises(ValueError):
            engine.get_session_summary("non-existent")


if __name__ == "__main__":
    # Run tests if script is executed directly
    pytest.main([__file__, "-v"]) 