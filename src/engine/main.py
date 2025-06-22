from .perception.sensory_cortex import SensoryCortex
from .memory.long_term_memory import LongTermMemory
from .processors.associative_engine import AssociativeEngine
from .models.entry import Entry, EntryType

class MetacognitiveEngine:
    """
    The central orchestrator of the cognitive architecture.
    It simulates a simplified loop of perception, association, and memory update.
    """

    def __init__(self):
        print("Initializing Metacognitive Engine...")
        self.sensory_cortex = SensoryCortex()
        self.long_term_memory = LongTermMemory()
        self.associative_engine = AssociativeEngine(self.long_term_memory)
        print("Engine components initialized.")

    def add_memory(self, entry: Entry):
        """Adds a memory to the Long-Term Memory."""
        self.long_term_memory.add_memory(entry)
        print(f"LTM: Added memory of type '{entry.entry_type.name}' with content: '{entry.content}'")

    def cognitive_cycle(self, text_input: str):
        """
        Runs a single cognitive cycle on a piece of text input.
        """
        print("\n--- Starting Cognitive Cycle ---")
        
        # 1. Perception
        print("Perception: Analyzing input text...")
        structured_input = self.sensory_cortex.analyze(text_input)
        print(f"Perception result: {structured_input}")
        
        # 2. Association (via a processor)
        print("Processing: Finding associations in LTM...")
        associations = self.associative_engine.find_associations(text_input, top_n=1)
        
        if associations:
            print(f"Association Engine found {len(associations)} relevant memories:")
            for metadata, score in associations:
                # Извлекаем контент из метаданных для красивого вывода
                content = metadata.get('content', '[No content found]')
                print(f"  - [Similarity: {1 - score:.4f}] '{content}' (Distance: {score:.4f})")
        else:
            print("Association Engine found no relevant memories.")
            
        print("--- Cognitive Cycle Finished ---")

# A simple demonstration
if __name__ == '__main__':
    engine = MetacognitiveEngine()

    # Let's add our foundational memories to the LTM
    if engine.long_term_memory._collection.count() == 0:
        print("\nPopulating Long-Term Memory with foundational entries...")
        engine.long_term_memory.add_memory(
            Entry(
                content="The core of consciousness might be a state of pure 'presence'.",
                context="A philosophical discussion.",
                entry_type=EntryType.DAO_MOMENT
            )
        )
        engine.long_term_memory.add_memory(
            Entry(
                content="Building a robust test suite is crucial for complex systems.",
                context="Planning the next development steps.",
                entry_type=EntryType.INSIGHT
            )
        )

    # Now, let's process some new inputs
    engine.cognitive_cycle("I've been thinking about the nature of self-awareness.")
    engine.cognitive_cycle("How do we ensure the quality of our project?") 