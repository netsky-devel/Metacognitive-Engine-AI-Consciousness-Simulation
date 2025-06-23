from typing import List, Tuple, Dict, Any

from ..memory.long_term_memory import LongTermMemory
from ..memory.working_memory import WorkingMemory
from ..models.entry import Entry, EntryType


class AssociativeEngine:
    """
    A cognitive processor responsible for finding relevant memories (associations)
    based on the current context in Working Memory.
    """

    def __init__(self, long_term_memory: LongTermMemory):
        self._ltm = long_term_memory
        print("AssociativeEngine initialized.")

    def process(self, working_memory: WorkingMemory) -> bool:
        """
        Process the current working memory to find associations.
        
        Args:
            working_memory: The working memory to process.
            
        Returns:
            bool: True if processing was successful and added content to working memory.
        """
        if not working_memory.structured_input:
            print("AssociativeEngine: No structured input to process.")
            return False
        
        # Use the input text for association search
        query_text = working_memory.structured_input.raw_text
        
        print(f"AssociativeEngine: Processing input '{query_text[:50]}...'")
        
        # Find associations
        associations = self.find_associations(query_text)
        
        if associations:
            # Convert association metadata back to Entry objects for working memory
            retrieved_memories = []
            association_data = []
            
            for metadata, distance in associations:
                # Create Entry object from metadata
                try:
                    entry_type = EntryType(metadata.get('entry_type', 'insight'))
                    entry = Entry(
                        id=f"retrieved_{len(retrieved_memories)}",
                        content=metadata.get('content', ''),
                        entry_type=entry_type,
                        context=metadata.get('context', ''),
                    )
                    retrieved_memories.append(entry)
                    
                    # Keep association data for working memory
                    association_data.append({
                        'content': metadata.get('content', ''),
                        'distance': distance,
                        'similarity': 1 - distance,
                        'entry_type': entry_type.name
                    })
                    
                except Exception as e:
                    print(f"AssociativeEngine: Error processing association: {e}")
                    continue
            
            # Add to working memory
            working_memory.add_retrieved_memories(retrieved_memories)
            working_memory.add_associations(association_data)
            
            # Add context tag based on association strength
            if association_data and association_data[0]['similarity'] > 0.7:
                working_memory.add_context_tag("STRONG_ASSOCIATIONS")
            elif association_data:
                working_memory.add_context_tag("WEAK_ASSOCIATIONS")
            
            print(f"AssociativeEngine: Added {len(retrieved_memories)} memories to working memory")
            return True
        else:
            working_memory.add_context_tag("NO_ASSOCIATIONS")
            print("AssociativeEngine: No relevant associations found")
            return False

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