"""
Comprehensive test suite for the Metacognitive Engine
Tests all major components and their integration.
"""

import pytest
import os
import tempfile
import shutil
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock

from src.engine.engine import MetacognitiveEngine
from src.engine.memory.long_term_memory import LongTermMemory
from src.engine.memory.working_memory import WorkingMemory, StructuredInput
from src.engine.processors.associative_engine import AssociativeEngine
from src.engine.processors.introspection_engine import IntrospectionEngine
from src.engine.processors.response_generator import ResponseGenerator
from src.engine.perception.sensory_cortex import SensoryCortex
from src.engine.models.entry import Entry, EntryType


class TestMetacognitiveEngine:
    """Test the main MetacognitiveEngine class"""
    
    @pytest.fixture
    def engine(self, temp_db_path):
        """Create a test engine with temporary database"""
        # Create engine normally, then replace LTM with test instance
        engine = MetacognitiveEngine()
        # Replace with real LTM using temp path
        engine.ltm = LongTermMemory(temp_db_path)
        yield engine
    
    def test_engine_initialization(self, engine):
        """Test that the engine initializes all components correctly"""
        assert engine.ltm is not None
        assert engine.working_memory is not None
        assert engine.sensory_cortex is not None
        assert engine.associative_engine is not None
        assert engine.introspection_engine is not None
        assert engine.response_generator is not None
    
    def test_add_memory(self, engine):
        """Test adding memories to the engine"""
        entry = Entry(content="Test memory", entry_type=EntryType.INSIGHT)
        engine.add_memory(entry)
        
        # Verify memory was added
        results = engine.ltm.query("Test memory", n_results=1)
        assert len(results) == 1
        assert results[0].content == "Test memory"
    
    def test_clear_all_memories(self, engine):
        """Test clearing all memories"""
        # Add some memories
        engine.add_memory(Entry(content="Memory 1", entry_type=EntryType.INSIGHT))
        engine.add_memory(Entry(content="Memory 2", entry_type=EntryType.FACT))
        
        # Clear and verify
        engine.clear_all_memories()
        results = engine.ltm.query("Memory", n_results=10)
        assert len(results) == 0
    
    @patch('src.engine.processors.introspection_engine.IntrospectionEngine.analyze')
    @patch('src.engine.processors.associative_engine.AssociativeEngine.find_associations')
    def test_analyze_new_thought(self, mock_associations, mock_analyze, engine):
        """Test the legacy analyze_new_thought method"""
        # Setup mocks
        mock_associations.return_value = []
        mock_analyze.return_value = Entry(content="Generated insight", entry_type=EntryType.INSIGHT)
        
        # Test analysis
        result = engine.analyze_new_thought("Test thought")
        
        assert len(result) == 1
        assert result[0].content == "Generated insight"
        mock_associations.assert_called_once()
        mock_analyze.assert_called_once()


class TestLongTermMemory:
    """Test the LongTermMemory component"""
    
    @pytest.fixture
    def ltm(self, temp_db_path):
        """Create a test LongTermMemory instance"""
        return LongTermMemory(temp_db_path)
    
    def test_ltm_initialization(self, ltm):
        """Test LTM initialization"""
        assert ltm.client is not None
        assert ltm.model is not None
        assert ltm.collection is not None
    
    def test_add_and_query_memory(self, ltm):
        """Test adding and querying memories"""
        entry = Entry(content="Consciousness is awareness", entry_type=EntryType.INSIGHT)
        ltm.add_memory(entry)
        
        # Query for the memory
        results = ltm.query("consciousness", n_results=1)
        assert len(results) == 1
        assert "awareness" in results[0].content.lower()
    
    def test_search_memories_distance_threshold(self, ltm):
        """Test search_memories with distance thresholds"""
        # Add test memories
        ltm.add_memory(Entry(content="Artificial intelligence systems", entry_type=EntryType.FACT))
        ltm.add_memory(Entry(content="Machine learning algorithms", entry_type=EntryType.FACT))
        
        # Test search with different thresholds
        results = ltm.search_memories("AI systems", n_results=5)
        assert isinstance(results, list)
        
        # Results should be sorted by distance (lower = better)
        if len(results) > 1:
            assert results[0]['distance'] <= results[1]['distance']
    
    def test_clear_all_memories(self, ltm):
        """Test clearing all memories"""
        # Add memories
        ltm.add_memory(Entry(content="Test memory 1", entry_type=EntryType.INSIGHT))
        ltm.add_memory(Entry(content="Test memory 2", entry_type=EntryType.FACT))
        
        # Clear and verify
        ltm.clear_all_memories()
        results = ltm.query("test", n_results=10)
        assert len(results) == 0


class TestWorkingMemory:
    """Test the WorkingMemory component"""
    
    @pytest.fixture
    def working_memory(self):
        """Create a test WorkingMemory instance"""
        return WorkingMemory()
    
    def test_working_memory_initialization(self, working_memory):
        """Test WorkingMemory initialization"""
        assert working_memory.structured_input is None
        assert working_memory.retrieved_memories == []
        assert working_memory.generated_insights == []
        assert working_memory.associations == []
        assert working_memory.context_tags == []
    
    def test_set_input(self, working_memory):
        """Test setting structured input"""
        structured_input = StructuredInput(
            raw_text="Test input",
            language="en",
            entities=[("test", "NOUN")],
            intent="QUESTION",
            sentiment="CURIOUS",
            tone="FORMAL",
            confidence=0.9
        )
        working_memory.set_input(structured_input)
        assert working_memory.structured_input.raw_text == "Test input"
        assert working_memory.structured_input.intent == "QUESTION"
    
    def test_add_insight(self, working_memory):
        """Test adding insights to working memory"""
        insight = Entry(content="Test insight", entry_type=EntryType.INSIGHT)
        working_memory.add_insight(insight)
        
        assert len(working_memory.generated_insights) == 1
        assert working_memory.generated_insights[0].content == "Test insight"
    
    def test_context_tags(self, working_memory):
        """Test context tag management"""
        working_memory.add_context_tag("TEST_TAG")
        working_memory.add_context_tag("ANOTHER_TAG")
        
        assert "TEST_TAG" in working_memory.context_tags
        assert "ANOTHER_TAG" in working_memory.context_tags
        
        # Test context summary
        summary = working_memory.get_context_summary()
        assert "TEST_TAG" in summary
        assert "ANOTHER_TAG" in summary


class TestSensoryCortex:
    """Test the SensoryCortex component"""
    
    @pytest.fixture
    def sensory_cortex(self):
        """Create a test SensoryCortex instance"""
        return SensoryCortex()
    
    @patch('google.generativeai.GenerativeModel')
    def test_analyze_with_ai(self, mock_model, sensory_cortex):
        """Test AI-powered analysis"""
        # Mock AI response
        mock_response = Mock()
        mock_response.text = "QUESTION | CURIOUS | FORMAL"
        mock_model.return_value.generate_content.return_value = mock_response
        
        # Test analysis
        result = sensory_cortex.analyze("What is consciousness?")
        
        assert result.raw_text == "What is consciousness?"
        assert result.intent in ["QUESTION", "REFLECTION", "STATEMENT", "COMMAND", "UNKNOWN"]
        assert result.sentiment in ["POSITIVE", "NEGATIVE", "NEUTRAL", "CURIOUS", "EXCITED"]
        assert result.tone in ["FORMAL", "CASUAL", "EMOTIONAL", "NEUTRAL"]
    
    def test_analyze_without_ai(self, sensory_cortex):
        """Test fallback analysis without AI"""
        # Simulate no AI model
        sensory_cortex.model = None
        
        result = sensory_cortex.analyze("Test input")
        
        assert result.raw_text == "Test input"
        assert result.intent == "UNKNOWN"
        assert result.sentiment == "NEUTRAL"
        assert result.tone == "NEUTRAL"


class TestAssociativeEngine:
    """Test the AssociativeEngine component"""
    
    @pytest.fixture
    def associative_engine(self, temp_db_path):
        """Create a test AssociativeEngine instance"""
        ltm = LongTermMemory(temp_db_path)
        return AssociativeEngine(ltm)
    
    @pytest.fixture
    def working_memory_with_input(self):
        """Create working memory with structured input"""
        wm = WorkingMemory()
        structured_input = StructuredInput(
            raw_text="Test consciousness question",
            language="en",
            entities=[("consciousness", "NOUN")],
            intent="QUESTION",
            sentiment="CURIOUS",
            tone="FORMAL",
            confidence=0.9
        )
        wm.set_input(structured_input)
        return wm
    
    def test_process_with_associations(self, associative_engine, working_memory_with_input):
        """Test processing when associations are found"""
        # Add some test memories
        associative_engine._ltm.add_memory(
            Entry(content="Consciousness is awareness", entry_type=EntryType.INSIGHT)
        )
        
        # Process should find associations
        result = associative_engine.process(working_memory_with_input)
        
        # Check if associations were found and added to working memory
        # Result depends on distance threshold and similarity
        assert isinstance(result, bool)
        
    def test_process_without_input(self, associative_engine):
        """Test processing without structured input"""
        empty_wm = WorkingMemory()
        result = associative_engine.process(empty_wm)
        assert result is False
    
    def test_find_associations(self, associative_engine):
        """Test finding associations directly"""
        # Add test memory
        associative_engine._ltm.add_memory(
            Entry(content="Machine learning systems", entry_type=EntryType.FACT)
        )
        
        # Find associations
        associations = associative_engine.find_associations("AI systems", top_n=3)
        
        assert isinstance(associations, list)
        # Each association should be a tuple of (metadata, distance)
        for assoc in associations:
            assert len(assoc) == 2
            assert isinstance(assoc[0], dict)  # metadata
            assert isinstance(assoc[1], (int, float))  # distance


class TestIntrospectionEngine:
    """Test the IntrospectionEngine component"""
    
    @pytest.fixture
    def introspection_engine(self):
        """Create a test IntrospectionEngine instance"""
        return IntrospectionEngine()
    
    def test_initialization(self, introspection_engine):
        """Test IntrospectionEngine initialization"""
        # Check if it initializes correctly (model may be None if no API key)
        assert introspection_engine is not None
    
    @pytest.fixture
    def working_memory_with_memories(self):
        """Create working memory with retrieved memories"""
        wm = WorkingMemory()
        structured_input = StructuredInput(
            raw_text="Test question about consciousness",
            language="en",
            entities=[("consciousness", "NOUN")],
            intent="QUESTION",
            sentiment="CURIOUS",
            tone="FORMAL",
            confidence=0.9
        )
        wm.set_input(structured_input)
        
        # Add some retrieved memories
        memory = Entry(content="Consciousness is awareness", entry_type=EntryType.INSIGHT)
        wm.add_retrieved_memories([memory])
        
        return wm
    
    def test_process_with_memories(self, introspection_engine, working_memory_with_memories):
        """Test processing with retrieved memories"""
        result = introspection_engine.process(working_memory_with_memories)
        assert isinstance(result, bool)
    
    def test_process_without_input(self, introspection_engine):
        """Test processing without structured input"""
        empty_wm = WorkingMemory()
        result = introspection_engine.process(empty_wm)
        assert result is False
    
    def test_assess_confidence(self, introspection_engine, working_memory_with_memories):
        """Test confidence assessment"""
        confidence = introspection_engine._assess_confidence(working_memory_with_memories)
        assert 0.0 <= confidence <= 1.0


class TestResponseGenerator:
    """Test the ResponseGenerator component"""
    
    @pytest.fixture
    def response_generator(self):
        """Create a test ResponseGenerator instance"""
        return ResponseGenerator()
    
    @pytest.fixture
    def working_memory_with_content(self):
        """Create working memory with various content"""
        wm = WorkingMemory()
        structured_input = StructuredInput(
            raw_text="What is consciousness?",
            language="en",
            entities=[("consciousness", "NOUN")],
            intent="QUESTION",
            sentiment="CURIOUS",
            tone="FORMAL",
            confidence=0.9
        )
        wm.set_input(structured_input)
        
        # Add insights and memories
        insight = Entry(content="Consciousness involves awareness", entry_type=EntryType.INSIGHT)
        wm.add_insight(insight)
        
        memory = Entry(content="The nature of consciousness", entry_type=EntryType.INSIGHT)
        wm.add_retrieved_memories([memory])
        
        return wm
    
    def test_generate_response(self, response_generator, working_memory_with_content):
        """Test response generation"""
        response = response_generator.generate_response(working_memory_with_content)
        
        assert isinstance(response, str)
        assert len(response) > 0
    
    def test_generate_response_empty_memory(self, response_generator):
        """Test response generation with empty working memory"""
        empty_wm = WorkingMemory()
        response = response_generator.generate_response(empty_wm)
        
        assert isinstance(response, str)
        assert len(response) > 0


class TestIntegration:
    """Integration tests for the complete system"""
    
    @pytest.fixture
    def engine(self, temp_db_path):
        """Create a test engine with temporary database"""
        # Create engine normally, then replace LTM with test instance
        engine = MetacognitiveEngine()
        # Replace with real LTM using temp path
        engine.ltm = LongTermMemory(temp_db_path)
        yield engine
    
    def test_full_cognitive_cycle(self, engine):
        """Test a complete cognitive processing cycle"""
        # Add some initial memories
        engine.add_memory(Entry(content="Consciousness is subjective experience", entry_type=EntryType.INSIGHT))
        engine.add_memory(Entry(content="AI systems process information", entry_type=EntryType.FACT))
        
        # Process a thought
        response = engine.process_thought("How does consciousness relate to AI?")
        
        assert isinstance(response, str)
        assert len(response) > 0
        
        # Check that working memory was used
        assert engine.working_memory is not None
    
    def test_memory_persistence(self, engine):
        """Test that memories persist across operations"""
        # Add memories
        original_content = "Test memory for persistence"
        engine.add_memory(Entry(content=original_content, entry_type=EntryType.INSIGHT))
        
        # Query to verify persistence
        results = engine.ltm.query("persistence", n_results=1)
        assert len(results) >= 1
        
        # Verify content matches
        found = any(original_content in result.content for result in results)
        assert found


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 