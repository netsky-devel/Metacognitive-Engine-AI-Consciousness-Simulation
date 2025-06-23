from src.engine.memory.long_term_memory import LongTermMemory
from src.engine.memory.working_memory import WorkingMemory
from src.engine.processors.associative_engine import AssociativeEngine
from src.engine.processors.introspection_engine import IntrospectionEngine
from src.engine.processors.response_generator import ResponseGenerator
from src.engine.processors.emotional_engine import EmotionalEngine
from src.engine.processors.attention_engine import AttentionEngine
from src.engine.perception.sensory_cortex import SensoryCortex
from src.engine.models.entry import Entry

class MetacognitiveEngine:
    """
    The core of the metacognitive architecture.
    This class initializes and integrates all cognitive components,
    and orchestrates the complex cognitive cycle through WorkingMemory.
    """
    def __init__(self, enable_emotions: bool = True, enable_attention: bool = True):
        print("Initializing Advanced Metacognitive Engine...")
        
        # Core memory systems
        self.ltm = LongTermMemory()
        self.working_memory = WorkingMemory()
        
        # Cognitive processors
        self.sensory_cortex = SensoryCortex()
        self.associative_engine = AssociativeEngine(self.ltm)
        self.introspection_engine = IntrospectionEngine()
        self.response_generator = ResponseGenerator()
        
        # Advanced processing systems
        self.emotional_engine = EmotionalEngine() if enable_emotions else None
        self.attention_engine = AttentionEngine() if enable_attention else None
        self.emotions_enabled = enable_emotions
        self.attention_enabled = enable_attention
        
        features = []
        if enable_emotions:
            features.append("emotional processing")
        if enable_attention:
            features.append("attention mechanism")
        
        if features:
            print(f"Advanced Engine components initialized with {' and '.join(features)}.")
        else:
            print("Advanced Engine components initialized in basic mode.")

    def add_memory(self, entry: Entry):
        """Adds a new entry directly to long-term memory."""
        self.ltm.add_memory(entry)

    def get_all_memories(self):
        """Retrieves all memories from the LTM."""
        return self.ltm.get_all_memories()

    def clear_all_memories(self):
        """Clears all memories from the LTM."""
        print(f"Clearing all memories from collection '{self.ltm.collection.name}'...")
        self.ltm.clear_all_memories()
        print("Memory cleared. Collection is now empty.")

    def process_thought(self, text: str, max_cycles: int = 3) -> str:
        """
        Advanced cognitive processing with multiple cycles and response generation.
        
        Args:
            text: The input text to process
            max_cycles: Maximum number of cognitive cycles to perform
            
        Returns:
            A synthesized response string
        """
        print(f"\n🧠 === ADVANCED COGNITIVE PROCESSING ===")
        print(f"Input: '{text[:100]}{'...' if len(text) > 100 else ''}'")
        
        # Reset working memory for new processing
        self.working_memory.clear()
        
        # 1. PERCEPTION PHASE
        print(f"\n🔍 PHASE 1: PERCEPTION")
        structured_input = self.sensory_cortex.analyze(text)
        self.working_memory.set_input(structured_input)
        
        # 1.5. EMOTIONAL PROCESSING PHASE (if enabled)
        if self.emotions_enabled and self.emotional_engine:
            print(f"\n💖 PHASE 1.5: EMOTIONAL PROCESSING")
            self.emotional_engine.process_emotional_input(self.working_memory)
            self.working_memory.set_emotional_state(self.emotional_engine.current_emotional_state)
        
        # 2. COGNITIVE CYCLES
        for cycle in range(max_cycles):
            print(f"\n🔄 CYCLE {cycle + 1}/{max_cycles}")
            self.working_memory.update_cognitive_state(cycle_count=cycle + 1)
            
            # Attention allocation phase (NEW)
            if self.attention_enabled and self.attention_engine:
                print("  🎯 Attention Phase")
                self.attention_engine.process(self.working_memory)
            
            # Association phase
            print("  🔗 Association Phase")
            association_success = self.associative_engine.process(self.working_memory)
            
            # Introspection phase  
            print("  🤔 Introspection Phase")
            introspection_success = self.introspection_engine.process(self.working_memory)
            
            # Check if we should stabilize (early termination)
            if self._should_stabilize(cycle, association_success, introspection_success):
                print(f"  ✅ Cognitive process stabilized after {cycle + 1} cycles")
                self.working_memory.update_cognitive_state(is_stable=True)
                break
        
        # 3. LEARNING PHASE - Save new insights to long-term memory
        print(f"\n💾 PHASE 3: LEARNING")
        self._save_insights_to_ltm()
        
        # 4. RESPONSE GENERATION
        print(f"\n💬 PHASE 4: RESPONSE GENERATION")
        response = self.response_generator.generate_response(self.working_memory)
        
        # 5. SUMMARY
        print(f"\n📊 PROCESSING SUMMARY:")
        print(f"  • Cycles completed: {self.working_memory.cognitive_state.cycle_count}")
        print(f"  • Memories retrieved: {len(self.working_memory.retrieved_memories)}")
        print(f"  • Insights generated: {len(self.working_memory.generated_insights)}")
        print(f"  • Confidence score: {self.working_memory.cognitive_state.confidence_score:.2f}")
        print(f"  • Context: {self.working_memory.get_context_summary()}")
        
        return response
    
    def _should_stabilize(self, cycle: int, association_success: bool, introspection_success: bool) -> bool:
        """Determine if the cognitive process should stabilize."""
        # Stabilize if no new information was processed
        if not association_success and not introspection_success:
            return True
        
        # Stabilize if confidence is high
        if self.working_memory.cognitive_state.confidence_score > 0.8:
            return True
        
        # Continue processing otherwise
        return False
    
    def _save_insights_to_ltm(self):
        """Save generated insights to long-term memory."""
        insights_saved = 0
        for insight in self.working_memory.generated_insights:
            self.add_memory(insight)
            insights_saved += 1
        
        if insights_saved > 0:
            print(f"  💾 Saved {insights_saved} insights to long-term memory")
        else:
            print(f"  💾 No new insights to save")

    def analyze_new_thought(self, text: str):
        """
        Legacy method for backward compatibility.
        Processes a new piece of text through the full cognitive cycle.
        """
        print("\n--- Legacy Cognitive Cycle ---")

        # 1. Perception
        print("Perception: Analyzing input text...")
        perception_result = self.sensory_cortex.analyze(text)
        print(f"Perception result: Intent={perception_result.intent}, Sentiment={perception_result.sentiment}")
        
        # 2. Association (legacy mode)
        print("Processing: Finding associations in LTM...")
        associations = self.associative_engine.find_associations(text)
        
        if associations:
            print(f"Association Engine found {len(associations)} relevant memories:")
            # For brevity, let's just show the top one.
            top_association, top_score = associations[0]
            similarity = 1 - top_score
            print(f"  - [Similarity: {similarity:.4f}] '{top_association['content'][:50]}...' (Distance: {top_score:.4f})")
        else:
            print("Association Engine found no relevant memories.")

        # 3. Introspection (legacy mode)
        print("Introspection: Reflecting on new information...")
        new_entry = self.introspection_engine.analyze(text, associations)

        # 4. Learning
        if new_entry:
            self.add_memory(new_entry)
            print(f"Generated and saved: {new_entry.entry_type.name} - {new_entry.content}")
        else:
            print("No new insights generated")

        print("--- Legacy Cognitive Cycle Finished ---")
        
        # Return the new insights for API compatibility
        return [new_entry] if new_entry else [] 