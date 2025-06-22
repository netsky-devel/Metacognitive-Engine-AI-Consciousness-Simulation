from typing import List, Dict, Any

from ..memory.long_term_memory import LongTermMemory

class AssociativeEngine:
    """
    A cognitive processor responsible for finding relevant memories (associations)
    based on the current context in Working Memory.
    """

    def __init__(self, long_term_memory: LongTermMemory):
        self._ltm = long_term_memory
        print("AssociativeEngine initialized.")

    def find_associations(self, structured_input: Dict[str, Any], n_results: int = 2) -> List[Dict[str, Any]]:
        """
        Takes a structured input and finds relevant memories in the LTM.
        
        For now, it uses the raw text as the primary query source. In the future,
        it could form more complex queries based on entities and intent.
        """
        query_text = structured_input.get("text")
        if not query_text:
            return []

        print(f"AssociativeEngine: Searching for memories related to '{query_text}'...")
        relevant_memories = self._ltm.search_memories(query_text, n_results=n_results)
        return relevant_memories 