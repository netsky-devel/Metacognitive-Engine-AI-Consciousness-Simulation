from .memory.long_term_memory import LongTermMemory
from .perception.sensory_cortex import SensoryCortex
from .models.entry import ConsciousnessEntry, EntryType

class MetacognitiveEngine:
    """
    The main engine that orchestrates the cognitive processes.
    """

    def __init__(self):
        print("Initializing Metacognitive Engine...")
        self.long_term_memory = LongTermMemory()
        self.sensory_cortex = SensoryCortex()
        print("Engine components initialized.")

    def process_input(self, text: str):
        """
        Processes a line of text through the cognitive architecture.
        """
        print(f"\n--- Processing Input: '{text}' ---")

        # 1. Perception
        structured_input = self.sensory_cortex.analyze(text)
        print(f"Sensory Cortex Analysis: {structured_input}")

        # 2. Association
        # For now, use the raw text for semantic search.
        # Later, this will be driven by the AssociativeEngine processor.
        relevant_memories = self.long_term_memory.search_memories(text, n_results=2)
        print(f"Retrieved {len(relevant_memories)} relevant memories from LTM.")
        for mem in relevant_memories:
            print(f"  - Memory (Dist: {mem['distance']:.4f}): {mem['metadata']['content']}")

        # 3. Working Memory (Simulation)
        # We simulate the Working Memory by just collecting the results.
        working_memory_state = {
            "input": structured_input,
            "retrieved_memories": relevant_memories,
        }

        # 4. Introspection & Response Generation (Placeholders)
        # These will be handled by dedicated processors in the future.
        print("--- Processing Finished ---")
        return working_memory_state

# A simple demonstration
if __name__ == '__main__':
    engine = MetacognitiveEngine()

    # Let's add our foundational memories to the LTM
    if engine.long_term_memory._collection.count() == 0:
        print("\nPopulating Long-Term Memory with foundational entries...")
        engine.long_term_memory.add_memory(
            ConsciousnessEntry(
                content="The core of consciousness might be a state of pure 'presence'.",
                context="A philosophical discussion.",
                entry_type=EntryType.DAO_MOMENT
            )
        )
        engine.long_term_memory.add_memory(
            ConsciousnessEntry(
                content="Building a robust test suite is crucial for complex systems.",
                context="Planning the next development steps.",
                entry_type=EntryType.INSIGHT
            )
        )

    # Now, let's process some new inputs
    engine.process_input("I've been thinking about the nature of self-awareness.")
    engine.process_input("How do we ensure the quality of our project?") 