from src.engine.memory.long_term_memory import LongTermMemory
from src.engine.processors.associative_engine import AssociativeEngine
from src.engine.processors.introspection_engine import IntrospectionEngine
from src.engine.perception.sensory_cortex import SensoryCortex
from src.engine.models.entry import Entry

class MetacognitiveEngine:
    """
    The core of the metacognitive architecture.
    This class initializes and integrates all cognitive components,
    and orchestrates the process of analyzing new information.
    """
    def __init__(self):
        print("Initializing Metacognitive Engine...")
        self.ltm = LongTermMemory()
        self.associative_engine = AssociativeEngine(self.ltm)
        self.introspection_engine = IntrospectionEngine()
        self.sensory_cortex = SensoryCortex()
        print("Engine components initialized.")

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

    def analyze_new_thought(self, text: str):
        """
        Processes a new piece of text through the full cognitive cycle.
        Perception -> Association -> Introspection -> Learning.
        """
        print("\n--- Starting Cognitive Cycle ---")

        # 1. Perception
        print("Perception: Analyzing input text...")
        perception_result = self.sensory_cortex.analyze(text)
        print(f"Perception result: {perception_result}")
        
        # 2. Association
        print("Processing: Finding associations in LTM...")
        associations = self.associative_engine.find_associations(text)
        
        if associations:
            print(f"Association Engine found {len(associations)} relevant memories:")
            # For brevity, let's just show the top one.
            top_association, top_score = associations[0]
            similarity = 1 - top_score
            print(f"  - [Similarity: {similarity:.4f}] '{top_association['content']}' (Distance: {top_score:.4f})")
        else:
            print("Association Engine found no relevant memories.")

        # 3. Introspection
        print("Introspection: Reflecting on new information...")
        new_entry = self.introspection_engine.analyze(text, associations)

        # 4. Learning
        if new_entry:
            self.add_memory(new_entry)

        print("--- Cognitive Cycle Finished ---") 