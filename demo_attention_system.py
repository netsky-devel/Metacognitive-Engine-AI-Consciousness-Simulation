#!/usr/bin/env python3
"""
Interactive Demo: Attention System

This demo showcases the attention mechanism in the Metacognitive Engine,
demonstrating how attention allocation affects cognitive processing.
"""

import os
import sys
import time
from typing import Dict, Any

# Add the src directory to the path so we can import our modules
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.engine.engine import MetacognitiveEngine
from src.engine.processors.attention_engine import AttentionEngine
from src.engine.models.attention_state import AttentionType, AttentionPriority
from src.engine.memory.working_memory import WorkingMemory, StructuredInput


def print_header(title: str):
    """Print a formatted header"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")


def print_section(title: str):
    """Print a formatted section header"""
    print(f"\n{'-'*40}")
    print(f"  {title}")
    print(f"{'-'*40}")


def display_attention_state(attention_engine: AttentionEngine):
    """Display current attention state in a readable format"""
    context = attention_engine.get_attention_context()
    summary = context["attention_summary"]
    dominant = context["dominant_focus"]
    guidance = context["attention_guidance"]
    
    print(f"📊 Attention Summary:")
    print(f"  • Total Focuses: {summary['total_focuses']}")
    print(f"  • Attention Usage: {summary['usage_percentage']}")
    print(f"  • Strategy: {context['current_strategy']}")
    
    if dominant["target"]:
        print(f"  • Dominant Focus: {dominant['target']} ({dominant['type']})")
        print(f"    Weight: {dominant['weight']:.2f}, Priority: {dominant['priority']}")
    
    if summary["focus_distribution"]:
        print(f"  • Focus Distribution:")
        for focus_type, data in summary["focus_distribution"].items():
            print(f"    - {focus_type}: {data['count']} focuses, {data['total_weight']:.2f} weight")
    
    if guidance["processing_recommendations"]:
        print(f"  • Processing Recommendations:")
        for rec in guidance["processing_recommendations"]:
            print(f"    - {rec}")


def demo_attention_strategies():
    """Demonstrate different attention strategies"""
    print_header("🎯 ATTENTION STRATEGIES DEMO")
    
    print("This demo shows how different attention strategies affect cognitive processing.")
    print("We'll process the same question with three different strategies:\n")
    
    question = "How does attention mechanism improve AI reasoning?"
    strategies = ["balanced", "focused", "exploratory"]
    
    for strategy in strategies:
        print_section(f"Strategy: {strategy.upper()}")
        
        # Create engine with attention enabled
        engine = MetacognitiveEngine(enable_emotions=False, enable_attention=True)
        engine.attention_engine.current_strategy = strategy
        
        print(f"🤔 Question: {question}")
        print(f"🎯 Strategy: {strategy}")
        
        # Process the question
        start_time = time.time()
        response = engine.process_thought(question)
        processing_time = time.time() - start_time
        
        print(f"\n📋 Results:")
        print(f"  • Processing Time: {processing_time:.2f} seconds")
        print(f"  • Response Length: {len(response)} characters")
        
        # Display attention state
        display_attention_state(engine.attention_engine)
        
        print(f"\n💬 Response Preview: {response[:100]}...")
        
        input("\nPress Enter to continue to next strategy...")


def demo_manual_attention_control():
    """Demonstrate manual attention control"""
    print_header("🎮 MANUAL ATTENTION CONTROL DEMO")
    
    print("This demo shows how to manually control attention allocation.")
    print("We'll allocate attention to specific cognitive processes.\n")
    
    # Create attention engine
    attention_engine = AttentionEngine(total_capacity=1.0, max_concurrent_focuses=5)
    
    print("Starting with empty attention state:")
    display_attention_state(attention_engine)
    
    # Manual attention allocations
    allocations = [
        (AttentionType.MEMORY_SEARCH, "finding relevant memories", 0.4, AttentionPriority.HIGH),
        (AttentionType.INSIGHT_GENERATION, "generating new insights", 0.3, AttentionPriority.MEDIUM),
        (AttentionType.EMOTIONAL_PROCESSING, "analyzing emotions", 0.2, AttentionPriority.LOW),
        (AttentionType.META_COGNITION, "self-reflection", 0.1, AttentionPriority.MINIMAL)
    ]
    
    for attention_type, target, weight, priority in allocations:
        print(f"\n🎯 Allocating {weight} attention to {target}...")
        focus_id = attention_engine.allocate_attention(
            attention_type=attention_type,
            target=target,
            weight=weight,
            priority=priority
        )
        
        if focus_id:
            print(f"  ✅ Successfully allocated attention (ID: {focus_id[:8]}...)")
            display_attention_state(attention_engine)
        else:
            print(f"  ❌ Failed to allocate attention")
        
        input("Press Enter to continue...")


def demo_attention_strategies_comparison():
    """Compare attention strategies side by side"""
    print_header("⚖️ ATTENTION STRATEGIES COMPARISON")
    
    print("This demo compares all attention strategies processing the same input.")
    print("We'll analyze how each strategy affects the cognitive process.\n")
    
    test_input = "How can AI systems develop better reasoning capabilities?"
    
    print(f"🤔 Test Input: {test_input}\n")
    
    strategies = ["balanced", "focused", "exploratory"]
    results = {}
    
    for strategy in strategies:
        print(f"🎯 Testing {strategy.upper()} strategy...")
        
        # Create engine
        engine = MetacognitiveEngine(enable_emotions=False, enable_attention=True)
        engine.attention_engine.current_strategy = strategy
        
        # Measure processing
        start_time = time.time()
        response = engine.process_thought(test_input)
        processing_time = time.time() - start_time
        
        # Collect metrics
        attention_context = engine.working_memory.get_context_data("attention_context")
        results[strategy] = {
            "processing_time": processing_time,
            "response_length": len(response),
            "total_focuses": attention_context["attention_summary"]["total_focuses"],
            "attention_usage": attention_context["attention_summary"]["usage_percentage"],
            "dominant_focus": attention_context["dominant_focus"]["type"],
            "distribution": attention_context["attention_guidance"]["attention_distribution"]
        }
        
        print(f"  ✅ Completed in {processing_time:.2f}s")
    
    # Display comparison
    print_section("📊 STRATEGY COMPARISON RESULTS")
    
    print(f"{'Strategy':<12} {'Time':<8} {'Focuses':<8} {'Usage':<8} {'Dominant Focus':<15}")
    print("-" * 60)
    
    for strategy, data in results.items():
        print(f"{strategy:<12} {data['processing_time']:<8.2f} "
              f"{data['total_focuses']:<8} {data['attention_usage']:<8} "
              f"{data['dominant_focus']:<15}")
    
    print(f"\n📈 Detailed Analysis:")
    for strategy, data in results.items():
        print(f"\n{strategy.upper()} Strategy:")
        print(f"  • Response Length: {data['response_length']} characters")
        print(f"  • Attention Distribution:")
        for focus_type, weight in data['distribution'].items():
            print(f"    - {focus_type}: {weight:.2f}")


def main():
    """Main demo function"""
    print_header("🎯 ATTENTION SYSTEM DEMONSTRATION")
    
    print("Welcome to the Attention System Demo!")
    print("This demonstration showcases the attention mechanism in the Metacognitive Engine.")
    print("\nThe attention system manages cognitive focus and resource allocation,")
    print("implementing selective attention that can adapt to different processing needs.\n")
    
    demos = [
        ("1", "Attention Strategies Demo", demo_attention_strategies),
        ("2", "Manual Attention Control", demo_manual_attention_control),
        ("3", "Strategy Comparison", demo_attention_strategies_comparison),
        ("4", "Exit", None)
    ]
    
    while True:
        print_section("📋 DEMO MENU")
        for code, title, _ in demos:
            print(f"{code}. {title}")
        
        choice = input("\nSelect a demo (1-4): ").strip()
        
        demo_func = None
        for code, title, func in demos:
            if choice == code:
                demo_func = func
                break
        
        if demo_func is None:
            if choice == "4":
                print("\n👋 Thank you for exploring the Attention System!")
                print("The attention mechanism enhances cognitive processing by:")
                print("• Dynamically allocating cognitive resources")
                print("• Focusing on most relevant information")
                print("• Adapting to different processing strategies")
                print("• Providing context-aware guidance")
                break
            else:
                print("❌ Invalid choice. Please try again.")
                continue
        
        try:
            demo_func()
        except KeyboardInterrupt:
            print("\n\n⏸️ Demo interrupted. Returning to menu...")
        except Exception as e:
            print(f"\n❌ Demo error: {e}")
            print("Returning to menu...")


if __name__ == "__main__":
    main()