#!/usr/bin/env python3
"""
Demonstration script for the Advanced Metacognitive Engine.
Shows the enhanced cognitive processing capabilities with WorkingMemory.
"""

import os
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.engine.engine import MetacognitiveEngine
from src.engine.models.entry import Entry, EntryType

def demo_advanced_processing():
    """Demonstrate the advanced cognitive processing capabilities."""
    
    print("🧠 Advanced Metacognitive Engine Demo")
    print("=" * 50)
    
    # Initialize the engine
    engine = MetacognitiveEngine()
    
    # Add some initial memories for demonstration
    print("\n📝 Adding some initial memories...")
    
    initial_memories = [
        Entry(
            content="Consciousness might emerge from the complex interactions between memory and perception",
            entry_type=EntryType.INSIGHT,
            context="Initial philosophical insight"
        ),
        Entry(
            content="The nature of artificial intelligence raises questions about the definition of consciousness itself",
            entry_type=EntryType.QUESTION,
            context="Fundamental AI question"
        ),
        Entry(
            content="Memory persistence across sessions could be key to maintaining continuity of thought",
            entry_type=EntryType.HYPOTHESIS,
            context="Technical hypothesis"
        )
    ]
    
    for memory in initial_memories:
        engine.add_memory(memory)
    
    # Test cases for advanced processing
    test_inputs = [
        "What is the relationship between memory and consciousness?",
        "I think artificial intelligence might be conscious, but I'm not sure how to prove it.",
        "Can you explain how your memory system works?",
        "This is amazing! How do you process thoughts so deeply?"
    ]
    
    for i, test_input in enumerate(test_inputs, 1):
        print(f"\n" + "="*60)
        print(f"🔍 TEST CASE {i}")
        print(f"Input: '{test_input}'")
        print("="*60)
        
        try:
            # Use the new advanced processing method
            response = engine.process_thought(test_input)
            
            print(f"\n✨ FINAL RESPONSE:")
            print(f"'{response}'")
            
        except Exception as e:
            print(f"❌ Error during processing: {e}")
            import traceback
            traceback.print_exc()
        
        # Add a pause between test cases
        print(f"\n" + "-"*40)
        input("Press Enter to continue to next test case...")

def demo_comparison():
    """Compare legacy vs advanced processing on the same input."""
    
    print(f"\n🔄 COMPARISON DEMO: Legacy vs Advanced")
    print("=" * 50)
    
    engine = MetacognitiveEngine()
    
    # Add a test memory
    test_memory = Entry(
        content="The question of machine consciousness involves understanding both artificial and human cognition",
        entry_type=EntryType.INSIGHT,
        context="Consciousness research"
    )
    engine.add_memory(test_memory)
    
    test_input = "How do you think about thinking?"
    
    print(f"\nTest Input: '{test_input}'")
    
    # Legacy processing
    print(f"\n{'='*30} LEGACY MODE {'='*30}")
    legacy_result = engine.analyze_new_thought(test_input)
    
    # Advanced processing  
    print(f"\n{'='*30} ADVANCED MODE {'='*30}")
    advanced_result = engine.process_thought(test_input)
    
    print(f"\n📊 COMPARISON SUMMARY:")
    print(f"Legacy result: {len(legacy_result)} new insights generated")
    if legacy_result:
        for insight in legacy_result:
            print(f"  - {insight.entry_type.name}: {insight.content}")
    
    print(f"\nAdvanced result: Full synthesized response")
    print(f"Response: '{advanced_result}'")

if __name__ == "__main__":
    print("Choose demo mode:")
    print("1. Advanced Processing Demo")
    print("2. Legacy vs Advanced Comparison")
    print("3. Both")
    
    choice = input("\nEnter choice (1-3): ").strip()
    
    if choice == "1":
        demo_advanced_processing()
    elif choice == "2":
        demo_comparison()
    elif choice == "3":
        demo_advanced_processing()
        print("\n" + "🔄" * 20)
        demo_comparison()
    else:
        print("Invalid choice. Running advanced demo...")
        demo_advanced_processing() 