#!/usr/bin/env python3
"""
Demo script for the Emotional Processing System
Demonstrates the new emotional capabilities of the Metacognitive Engine.
"""

import os
import sys
from datetime import datetime

# Add the src directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.engine.engine import MetacognitiveEngine
from src.engine.models.emotional_state import EmotionType


def print_separator(title: str):
    """Print a nice separator with title"""
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)


def print_emotional_state(engine):
    """Print current emotional state summary"""
    if engine.emotional_engine:
        state_summary = engine.emotional_engine.get_emotional_state_summary()
        print(f"\n🧠 Current Emotional State:")
        print(f"   State: {state_summary['current_state']}")
        print(f"   Valence: {state_summary['valence']:.2f} (negative ← → positive)")
        print(f"   Arousal: {state_summary['arousal']:.2f} (calm ← → excited)")
        print(f"   Dominance: {state_summary['dominance']:.2f} (submissive ← → dominant)")
        if state_summary['dominant_emotion']:
            print(f"   Dominant Emotion: {state_summary['dominant_emotion']}")
        print(f"   Emotional Memories: {state_summary['emotional_memories_count']}")
        print(f"   Last Update: {state_summary['last_update']}")


def demo_emotional_responses():
    """Demonstrate emotional processing with various inputs"""
    
    print_separator("🚀 EMOTIONAL PROCESSING SYSTEM DEMO")
    print("This demo shows how the Metacognitive Engine processes emotions.")
    
    # Initialize engine with emotions enabled
    print("\n🔧 Initializing Metacognitive Engine with Emotional Processing...")
    engine = MetacognitiveEngine(enable_emotions=True)
    
    # Test scenarios with different emotional content
    test_scenarios = [
        {
            "input": "I'm so excited about this new AI project! It's going to be amazing!",
            "description": "High positive valence, high arousal (excitement)"
        },
        {
            "input": "I'm feeling quite confused and frustrated with this problem. It seems impossible to solve.",
            "description": "Negative valence, mixed emotions (confusion + frustration)"
        },
        {
            "input": "This is a peaceful evening. I feel calm and content with my progress today.",
            "description": "Positive valence, low arousal (contentment)"
        },
        {
            "input": "I'm worried about the future of AI. What if we lose control?",
            "description": "Negative valence, anxiety and fear"
        },
        {
            "input": "Tell me about machine learning algorithms in a technical context.",
            "description": "Neutral emotional content, technical inquiry"
        }
    ]
    
    for i, scenario in enumerate(test_scenarios, 1):
        print_separator(f"SCENARIO {i}: {scenario['description']}")
        print(f"📝 Input: \"{scenario['input']}\"")
        
        # Process the input
        response = engine.process_thought(scenario['input'])
        
        # Show emotional state
        print_emotional_state(engine)
        
        # Show response
        print(f"\n💬 Response:")
        print(f"   {response}")
        
        print(f"\n⏱️  Processing completed at: {datetime.now().strftime('%H:%M:%S')}")
        
        # Pause between scenarios
        if i < len(test_scenarios):
            input("\n👆 Press Enter to continue to next scenario...")
    
    print_separator("🧪 EMOTIONAL MEMORY DEMONSTRATION")
    
    # Test emotional memory retrieval
    print("Now testing how emotional memories influence responses...")
    
    memory_test_inputs = [
        "Let's talk about AI projects again. I have some new ideas!",
        "I'm still struggling with that same problem from before.",
        "How do you feel about machine learning now?"
    ]
    
    for i, test_input in enumerate(memory_test_inputs, 1):
        print(f"\n🔍 Memory Test {i}: \"{test_input}\"")
        response = engine.process_thought(test_input)
        print(f"💬 Response: {response}")
        print_emotional_state(engine)
        
        if i < len(memory_test_inputs):
            input("\n👆 Press Enter for next memory test...")
    
    print_separator("📊 FINAL EMOTIONAL SYSTEM STATISTICS")
    
    if engine.emotional_engine:
        state_summary = engine.emotional_engine.get_emotional_state_summary()
        print(f"🧠 Final Emotional State: {state_summary['current_state']}")
        print(f"💾 Total Emotional Memories Created: {state_summary['emotional_memories_count']}")
        print(f"📈 Emotional History Entries: {state_summary['emotional_history_count']}")
        
        # Show some emotional memories
        if engine.emotional_engine.emotional_memories:
            print(f"\n🔍 Sample Emotional Memories:")
            for i, memory in enumerate(engine.emotional_engine.emotional_memories[:3], 1):
                print(f"   {i}. \"{memory.content[:50]}...\"")
                print(f"      Emotional State: {memory.emotional_state.to_summary_string()}")
                print(f"      Strength: {memory.get_current_strength():.2f}")
                print(f"      Trigger Patterns: {memory.trigger_patterns}")
    
    print(f"\n✅ Demo completed successfully!")
    print(f"🎯 The emotional system is now integrated and working with the cognitive engine.")


def demo_emotional_states():
    """Demonstrate different emotional state manipulations"""
    
    print_separator("🎭 EMOTIONAL STATES DEMONSTRATION")
    
    from src.engine.models.emotional_state import EmotionalState, EmotionType
    
    # Create different emotional states
    states = [
        {
            "name": "Joyful Excitement",
            "state": EmotionalState(valence=0.8, arousal=0.9, dominance=0.7),
            "emotions": [(EmotionType.JOY, 0.9), (EmotionType.EXCITEMENT, 0.8)]
        },
        {
            "name": "Calm Contentment", 
            "state": EmotionalState(valence=0.6, arousal=0.2, dominance=0.6),
            "emotions": [(EmotionType.CONTENTMENT, 0.8), (EmotionType.TRUST, 0.6)]
        },
        {
            "name": "Anxious Worry",
            "state": EmotionalState(valence=-0.4, arousal=0.8, dominance=0.3),
            "emotions": [(EmotionType.FEAR, 0.7), (EmotionType.SADNESS, 0.4)]
        }
    ]
    
    for state_info in states:
        state = state_info["state"]
        for emotion, intensity in state_info["emotions"]:
            state.add_emotion(emotion, intensity)
        
        print(f"\n🎭 {state_info['name']}:")
        print(f"   Summary: {state.to_summary_string()}")
        print(f"   Quadrant: {state.get_emotional_quadrant()}")
        print(f"   Dominant Emotion: {state.get_dominant_emotion().value if state.get_dominant_emotion() else 'None'}")
        print(f"   Is Positive: {state.is_positive()}")
        print(f"   Is High Arousal: {state.is_high_arousal()}")
        print(f"   Is Dominant: {state.is_dominant_state()}")
    
    # Demonstrate state blending
    print(f"\n🔄 Emotional State Blending:")
    state1 = states[0]["state"]  # Joyful Excitement
    state2 = states[2]["state"]  # Anxious Worry
    
    blended = state1.blend_with(state2, 0.3)  # 30% anxiety, 70% joy
    print(f"   Blending 'Joyful Excitement' (70%) with 'Anxious Worry' (30%):")
    print(f"   Result: {blended.to_summary_string()}")


if __name__ == "__main__":
    try:
        print("🧠 Metacognitive Engine - Emotional Processing Demo")
        print("=" * 60)
        
        # Check if we have AI capabilities
        api_key = os.getenv('GEMINI_API_KEY')
        if api_key:
            print("✅ Gemini AI detected - Full emotional analysis available")
        else:
            print("⚠️  No Gemini AI key - Using pattern-based emotional analysis")
            print("   Set GEMINI_API_KEY environment variable for full AI capabilities")
        
        print("\nChoose demo mode:")
        print("1. Full Emotional Processing Demo (Recommended)")
        print("2. Emotional States Demonstration")
        print("3. Both")
        
        choice = input("\nEnter choice (1-3): ").strip()
        
        if choice in ['1', '3']:
            demo_emotional_responses()
        
        if choice in ['2', '3']:
            demo_emotional_states()
        
        if choice not in ['1', '2', '3']:
            print("Invalid choice. Running full demo...")
            demo_emotional_responses()
    
    except KeyboardInterrupt:
        print("\n\n🛑 Demo interrupted by user.")
    except Exception as e:
        print(f"\n❌ Error during demo: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print("\n👋 Thanks for trying the Emotional Processing System!") 