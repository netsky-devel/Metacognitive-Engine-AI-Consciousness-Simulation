#!/usr/bin/env python3
"""
Simple Demo of Metacognitive AI Framework

A basic demonstration showing how to use the framework.
"""

import asyncio
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from metacognitive_ai.core.engine import MetacognitiveEngine


async def simple_demo():
    """Simple demonstration of the metacognitive framework"""
    print("🧠 Metacognitive AI Framework - Simple Demo")
    print("=" * 45)
    print()
    
    # Create engine
    engine = MetacognitiveEngine(
        introspection_level="medium",
        enable_real_time=False
    )
    
    print("✅ Engine initialized")
    
    # Start session
    session_id = await engine.start_session("Analyze a simple problem")
    print(f"🚀 Started session: {session_id[:8]}...")
    
    # Add some thoughts
    await engine.add_thought_step(
        "Let me think about this problem",
        step_type="analysis",
        confidence=0.8
    )
    
    await engine.add_thought_step(
        "I need to consider multiple approaches",
        step_type="reasoning",
        confidence=0.7
    )
    
    await engine.add_thought_step(
        "The best approach seems to be systematic analysis",
        step_type="decision",
        confidence=0.9
    )
    
    print("💭 Added 3 thought steps")
    
    # Generate introspection
    report = await engine.generate_introspection()
    print("🔍 Generated introspection report")
    
    # End session
    session = await engine.end_session("Problem analyzed successfully")
    print("🏁 Session completed")
    
    # Show results
    print("\n📊 Results:")
    print(f"   Steps: {len(session.cognitive_steps)}")
    print(f"   Duration: {session.performance_metrics.get('session_duration', 0):.2f}s")
    print(f"   Avg Confidence: {session.performance_metrics.get('average_confidence', 0):.1%}")
    
    return session


if __name__ == "__main__":
    asyncio.run(simple_demo())
