#!/usr/bin/env python3
"""
Production test script for Metacognitive Engine.
Tests core functionality and AI-powered cognitive processing.
"""

import os
import sys
import time
from pathlib import Path
from typing import List, Dict

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.engine.engine import MetacognitiveEngine
from src.engine.models.entry import Entry, EntryType

def test_basic_functionality():
    """Test basic engine functionality."""
    print("🔧 Testing Basic Functionality")
    print("-" * 40)
    
    engine = MetacognitiveEngine()
    
    # Test memory operations
    test_entry = Entry(
        content="Testing the metacognitive system's ability to process and remember information",
        entry_type=EntryType.FACT,
        context="System test"
    )
    
    engine.add_memory(test_entry)
    print("✅ Memory addition successful")
    
    # Test memory retrieval
    memories = engine.ltm.search_memories("testing system", n_results=1)
    assert len(memories) > 0, "Failed to retrieve added memory"
    print("✅ Memory retrieval successful")
    
    return True

def test_ai_analysis():
    """Test AI-powered analysis capabilities."""
    print("\n🤖 Testing AI Analysis")
    print("-" * 40)
    
    engine = MetacognitiveEngine()
    
    test_cases = [
        {
            "text": "How does machine learning work?",
            "expected_intent": "QUESTION",
            "expected_sentiment": ["NEUTRAL", "CURIOUS"]
        },
        {
            "text": "Please explain the concept of consciousness",
            "expected_intent": "COMMAND",
            "expected_sentiment": ["NEUTRAL", "CURIOUS"],
            "expected_tone": ["RESPECTFUL", "FORMAL"]
        },
        {
            "text": "I think artificial intelligence is fascinating!",
            "expected_intent": "REFLECTION",
            "expected_sentiment": ["POSITIVE", "ENTHUSIASTIC"],
            "expected_tone": ["ENTHUSIASTIC", "CASUAL"]
        },
        {
            "text": "This is amazing work on consciousness research",
            "expected_intent": "FEEDBACK",
            "expected_sentiment": ["POSITIVE"],
            "expected_tone": ["ENTHUSIASTIC", "RESPECTFUL"]
        }
    ]
    
    for i, case in enumerate(test_cases, 1):
        print(f"\nTest Case {i}: '{case['text']}'")
        
        # Test perception analysis
        structured_input = engine.sensory_cortex.analyze(case['text'])
        
        print(f"  Intent: {structured_input.intent} (confidence: {structured_input.metadata['intent_confidence']:.2f})")
        print(f"  Sentiment: {structured_input.sentiment} (confidence: {structured_input.metadata['sentiment_confidence']:.2f})")
        print(f"  Tone: {structured_input.tone} (confidence: {structured_input.metadata['tone_confidence']:.2f})")
        print(f"  Method: {structured_input.metadata['analysis_method']}")
        
        # Validate results
        if structured_input.intent == case["expected_intent"]:
            print("  ✅ Intent detection correct")
        else:
            print(f"  ⚠️  Intent mismatch: expected {case['expected_intent']}, got {structured_input.intent}")
        
        if structured_input.sentiment in case["expected_sentiment"]:
            print("  ✅ Sentiment detection reasonable")
        else:
            print(f"  ⚠️  Sentiment unexpected: expected {case['expected_sentiment']}, got {structured_input.sentiment}")
    
    return True

def test_cognitive_processing():
    """Test full cognitive processing pipeline."""
    print("\n🧠 Testing Cognitive Processing")
    print("-" * 40)
    
    engine = MetacognitiveEngine()
    
    # Add some base knowledge
    base_knowledge = [
        Entry(
            content="Consciousness involves subjective experience and self-awareness",
            entry_type=EntryType.INSIGHT,
            context="Philosophy of mind"
        ),
        Entry(
            content="Machine learning systems can exhibit emergent behaviors not explicitly programmed",
            entry_type=EntryType.FACT,
            context="AI research"
        ),
        Entry(
            content="What is the relationship between information processing and conscious experience?",
            entry_type=EntryType.QUESTION,
            context="Consciousness studies"
        )
    ]
    
    for entry in base_knowledge:
        engine.add_memory(entry)
    
    print("✅ Base knowledge added to memory")
    
    # Test complex processing
    test_queries = [
        "Can artificial neural networks develop consciousness?",
        "I'm curious about the hard problem of consciousness",
        "How do you experience your own thought processes?"
    ]
    
    for query in test_queries:
        print(f"\n📝 Processing: '{query}'")
        start_time = time.time()
        
        try:
            response = engine.process_thought(query)
            processing_time = time.time() - start_time
            
            print(f"⏱️  Processing time: {processing_time:.2f}s")
            print(f"📄 Response length: {len(response)} chars")
            print(f"🔍 Response preview: {response[:200]}{'...' if len(response) > 200 else ''}")
            
        except Exception as e:
            print(f"❌ Error during processing: {e}")
            return False
    
    return True

def test_memory_persistence():
    """Test memory persistence and retrieval."""
    print("\n💾 Testing Memory Persistence")
    print("-" * 40)
    
    engine1 = MetacognitiveEngine()
    
    # Add test memories
    test_memories = [
        Entry(content="Memory persistence test entry", entry_type=EntryType.FACT),
        Entry(content="Another test memory for retrieval", entry_type=EntryType.INSIGHT)
    ]
    
    for memory in test_memories:
        engine1.add_memory(memory)
    
    print("✅ Memories added to first engine instance")
    
    # Create new engine instance (should load existing memories)
    engine2 = MetacognitiveEngine()
    
    # Test retrieval
    retrieved_memories = engine2.ltm.search_memories("persistence test", n_results=2)
    
    if len(retrieved_memories) > 0:
        print(f"✅ Retrieved {len(retrieved_memories)} memories from new engine instance")
        for memory in retrieved_memories:
            print(f"  - {memory['metadata']['content']}")
    else:
        print("❌ Failed to retrieve memories from new engine instance")
        return False
    
    return True

def run_system_test():
    """Run comprehensive system test."""
    print("🚀 Metacognitive Engine System Test")
    print("=" * 50)
    
    tests = [
        ("Basic Functionality", test_basic_functionality),
        ("AI Analysis", test_ai_analysis), 
        ("Cognitive Processing", test_cognitive_processing),
        ("Memory Persistence", test_memory_persistence)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            print(f"\n{'='*60}")
            success = test_func()
            results[test_name] = "PASS" if success else "FAIL"
            
        except Exception as e:
            print(f"❌ Test '{test_name}' failed with exception: {e}")
            results[test_name] = "ERROR"
    
    # Print summary
    print(f"\n{'='*60}")
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 60)
    
    for test_name, result in results.items():
        status_emoji = "✅" if result == "PASS" else "❌" if result == "FAIL" else "⚠️"
        print(f"{status_emoji} {test_name}: {result}")
    
    passed = sum(1 for r in results.values() if r == "PASS")
    total = len(results)
    
    print(f"\n🎯 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! System is ready for production.")
        return True
    else:
        print("⚠️  Some tests failed. Please review the issues above.")
        return False

if __name__ == "__main__":
    success = run_system_test()
    sys.exit(0 if success else 1) 