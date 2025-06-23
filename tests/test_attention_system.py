"""
Tests for the Attention System

This module contains comprehensive tests for the attention mechanism,
including attention allocation, focus management, and integration with
the cognitive processing pipeline.
"""

import pytest
import time
from datetime import datetime, timedelta
from unittest.mock import Mock, patch

from src.engine.models.attention_state import (
    AttentionState, AttentionFocus, AttentionType, AttentionPriority
)
from src.engine.processors.attention_engine import AttentionEngine
from src.engine.memory.working_memory import WorkingMemory, StructuredInput


class TestAttentionFocus:
    """Test the AttentionFocus model"""
    
    def test_attention_focus_creation(self):
        """Test basic attention focus creation"""
        focus = AttentionFocus(
            attention_type=AttentionType.MEMORY_SEARCH,
            target="test_target",
            weight=0.7,
            priority=AttentionPriority.HIGH
        )
        
        assert focus.attention_type == AttentionType.MEMORY_SEARCH
        assert focus.target == "test_target"
        assert focus.weight == 0.7
        assert focus.priority == AttentionPriority.HIGH
        assert focus.duration == 0.0
        assert focus.focus_id is not None
    
    def test_attention_focus_weight_validation(self):
        """Test attention weight validation"""
        focus = AttentionFocus()
        
        # Test valid weight updates
        focus.update_weight(0.8)
        assert focus.weight == 0.8
        
        # Test boundary validation
        focus.update_weight(1.5)  # Should clamp to 1.0
        assert focus.weight == 1.0
        
        focus.update_weight(-0.5)  # Should clamp to 0.0
        assert focus.weight == 0.0
    
    def test_attention_focus_duration_tracking(self):
        """Test duration tracking"""
        focus = AttentionFocus()
        
        focus.increase_duration(5.0)
        assert focus.duration == 5.0
        
        focus.increase_duration(3.0)
        assert focus.duration == 8.0
    
    def test_attention_focus_expiration(self):
        """Test focus expiration logic"""
        focus = AttentionFocus()
        
        # Not expired initially
        assert not focus.is_expired(300.0)
        
        # Expire after duration
        focus.increase_duration(350.0)
        assert focus.is_expired(300.0)
    
    def test_relevance_score_calculation(self):
        """Test relevance score calculation"""
        focus = AttentionFocus(
            weight=0.8,
            priority=AttentionPriority.HIGH
        )
        
        relevance = focus.get_relevance_score()
        assert 0.0 <= relevance <= 1.0
        
        # High priority and weight should give high relevance
        assert relevance > 0.5
        
        # Test low priority focus
        low_focus = AttentionFocus(
            weight=0.2,
            priority=AttentionPriority.MINIMAL
        )
        low_relevance = low_focus.get_relevance_score()
        assert low_relevance < relevance


class TestAttentionState:
    """Test the AttentionState model"""
    
    def test_attention_state_creation(self):
        """Test attention state initialization"""
        state = AttentionState()
        
        assert state.total_attention_capacity == 1.0
        assert state.current_attention_usage == 0.0
        assert len(state.current_focuses) == 0
        assert len(state.attention_history) == 0
    
    def test_add_focus(self):
        """Test adding attention focuses"""
        state = AttentionState()
        focus = AttentionFocus(weight=0.5)
        
        success = state.add_focus(focus)
        assert success
        assert len(state.current_focuses) == 1
        assert state.current_attention_usage == 0.5
    
    def test_remove_focus(self):
        """Test removing attention focuses"""
        state = AttentionState()
        focus = AttentionFocus(weight=0.5)
        state.add_focus(focus)
        
        success = state.remove_focus(focus.focus_id)
        assert success
        assert len(state.current_focuses) == 0
        assert state.current_attention_usage == 0.0
        assert len(state.attention_history) == 1
    
    def test_capacity_management(self):
        """Test attention capacity management"""
        state = AttentionState(total_attention_capacity=1.0)
        
        # Add focuses that exceed capacity
        focus1 = AttentionFocus(weight=0.6)
        focus2 = AttentionFocus(weight=0.7)
        
        state.add_focus(focus1)
        state.add_focus(focus2)  # Should trigger rebalancing
        
        # Total usage should not exceed capacity
        assert state.current_attention_usage <= state.total_attention_capacity
    
    def test_max_concurrent_focuses(self):
        """Test maximum concurrent focuses limit"""
        state = AttentionState(max_concurrent_focuses=2)
        
        # Add focuses up to limit
        for i in range(3):
            focus = AttentionFocus(weight=0.2, priority=AttentionPriority.MEDIUM)
            state.add_focus(focus)
        
        # Should not exceed maximum
        assert len(state.current_focuses) <= 2
    
    def test_get_dominant_focus(self):
        """Test dominant focus identification"""
        state = AttentionState()
        
        # No focuses initially
        assert state.get_dominant_focus() is None
        
        # Add focuses with different relevance
        high_focus = AttentionFocus(weight=0.8, priority=AttentionPriority.HIGH)
        low_focus = AttentionFocus(weight=0.3, priority=AttentionPriority.LOW)
        
        state.add_focus(low_focus)
        state.add_focus(high_focus)
        
        dominant = state.get_dominant_focus()
        assert dominant == high_focus
    
    def test_cleanup_expired_focuses(self):
        """Test cleanup of expired focuses"""
        state = AttentionState()
        
        # Add focus and make it expire
        focus = AttentionFocus(weight=0.5)
        focus.increase_duration(350.0)  # Exceed default 300s limit
        state.add_focus(focus)
        
        expired_count = state.cleanup_expired_focuses(300.0)
        assert expired_count == 1
        assert len(state.current_focuses) == 0
    
    def test_attention_summary(self):
        """Test attention state summary generation"""
        state = AttentionState()
        
        # Add various focuses
        memory_focus = AttentionFocus(
            attention_type=AttentionType.MEMORY_SEARCH,
            weight=0.4
        )
        insight_focus = AttentionFocus(
            attention_type=AttentionType.INSIGHT_GENERATION,
            weight=0.3
        )
        
        state.add_focus(memory_focus)
        state.add_focus(insight_focus)
        
        summary = state.get_attention_summary()
        
        assert summary["total_focuses"] == 2
        assert "memory_search" in summary["focus_distribution"]
        assert "insight_generation" in summary["focus_distribution"]
        assert summary["dominant_focus"] is not None


class TestAttentionEngine:
    """Test the AttentionEngine processor"""
    
    @pytest.fixture
    def attention_engine(self):
        """Create attention engine for testing"""
        return AttentionEngine(total_capacity=1.0, max_concurrent_focuses=3)
    
    @pytest.fixture
    def working_memory(self):
        """Create working memory for testing"""
        memory = WorkingMemory()
        
        # Add test input
        structured_input = StructuredInput(
            raw_text="Test input for attention",
            language="en",
            entities=[("test", "MISC"), ("attention", "CONCEPT")],
            intent="QUESTION",
            sentiment="CURIOUS",
            tone="CASUAL"
        )
        memory.set_input(structured_input)
        
        return memory
    
    def test_attention_engine_initialization(self, attention_engine):
        """Test attention engine initialization"""
        assert attention_engine.attention_state.total_attention_capacity == 1.0
        assert attention_engine.current_strategy == "balanced"
        assert len(attention_engine.attention_strategies) == 3
    
    def test_manual_attention_allocation(self, attention_engine):
        """Test manual attention allocation"""
        focus_id = attention_engine.allocate_attention(
            attention_type=AttentionType.MEMORY_SEARCH,
            target="test_memory_search",
            weight=0.6,
            priority=AttentionPriority.HIGH
        )
        
        assert focus_id is not None
        assert len(attention_engine.attention_state.current_focuses) == 1
        
        focus = attention_engine.attention_state.current_focuses[0]
        assert focus.target == "test_memory_search"
        assert focus.weight == 0.6
    
    def test_attention_processing_cycle(self, attention_engine, working_memory):
        """Test attention processing during cognitive cycle"""
        success = attention_engine.process(working_memory)
        assert success
        
        # Should have allocated attention based on context
        assert len(attention_engine.attention_state.current_focuses) > 0
        
        # Should have stored attention context in working memory
        attention_context = working_memory.get_context_data("attention_context")
        assert attention_context is not None
        assert "attention_summary" in attention_context
    
    def test_balanced_attention_strategy(self, attention_engine, working_memory):
        """Test balanced attention allocation strategy"""
        attention_engine.current_strategy = "balanced"
        
        success = attention_engine.process(working_memory)
        assert success
        
        context = attention_engine.get_attention_context()
        assert context["current_strategy"] == "balanced"
        
        # Should distribute attention across multiple types
        distribution = context["attention_guidance"]["attention_distribution"]
        assert len(distribution) > 1
    
    def test_focused_attention_strategy(self, attention_engine, working_memory):
        """Test focused attention allocation strategy"""
        attention_engine.current_strategy = "focused"
        
        success = attention_engine.process(working_memory)
        assert success
        
        context = attention_engine.get_attention_context()
        assert context["current_strategy"] == "focused"
        
        # Should have a dominant focus with high weight
        dominant_focus = attention_engine.attention_state.get_dominant_focus()
        assert dominant_focus is not None
        assert dominant_focus.weight > 0.5
    
    def test_attention_context_generation(self, attention_engine, working_memory):
        """Test attention context generation"""
        attention_engine.process(working_memory)
        
        context = attention_engine.get_attention_context()
        
        # Check required context fields
        assert "attention_summary" in context
        assert "dominant_focus" in context
        assert "current_strategy" in context
        assert "attention_guidance" in context
        
        # Check guidance structure
        guidance = context["attention_guidance"]
        assert "primary_focus" in guidance
        assert "attention_distribution" in guidance
        assert "processing_recommendations" in guidance


class TestAttentionIntegration:
    """Test attention system integration with other components"""
    
    def test_working_memory_context_data(self):
        """Test working memory context data storage"""
        memory = WorkingMemory()
        
        test_data = {"test_key": "test_value"}
        memory.set_context_data("attention_context", test_data)
        
        retrieved_data = memory.get_context_data("attention_context")
        assert retrieved_data == test_data
        
        # Test default value
        default_data = memory.get_context_data("nonexistent", "default")
        assert default_data == "default"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])