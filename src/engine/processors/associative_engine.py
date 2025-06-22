from typing import List, Tuple, Dict, Any

from ..memory.long_term_memory import LongTermMemory

class AssociativeEngine:
    """
    A cognitive processor responsible for finding relevant memories (associations)
    based on the current context in Working Memory.
    """

    def __init__(self, long_term_memory: LongTermMemory):
        self._ltm = long_term_memory
        print("AssociativeEngine initialized.")

    def find_associations(self, query_text: str, top_n: int = 3) -> List[Tuple[Dict[str, Any], float]]:
        """
        Finds the most relevant memories for a given query text.

        Args:
            query_text: The text to find associations for.
            top_n: The number of most relevant memories to return.

        Returns:
            A list of tuples, where each tuple contains the memory's metadata
            and its similarity score (distance).
        """
        print(f"AssociativeEngine: Searching for memories related to '{query_text}'...")
        search_results = self._ltm.search_memories(query_text, n_results=top_n)
        
        # Преобразуем формат данных для удобства
        associations = []
        for res in search_results:
            associations.append((res['metadata'], res['distance']))
            
        return associations 