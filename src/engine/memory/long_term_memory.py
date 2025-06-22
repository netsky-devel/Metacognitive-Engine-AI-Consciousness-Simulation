import chromadb
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Any
import uuid

from ..models.entry import ConsciousnessEntry, EntryType


class LongTermMemory:
    """
    Handles the storage and retrieval of consciousness entries using a vector database
    for semantic search capabilities.
    """

    def __init__(self, db_path: str = "data/chroma_db"):
        self._model = SentenceTransformer('all-MiniLM-L6-v2')
        self._client = chromadb.PersistentClient(path=db_path)
        self._collection = self._client.get_or_create_collection(name="consciousness_memories")
        print(f"LongTermMemory initialized. Collection '{self._collection.name}' has {self._collection.count()} entries.")

    def add_memory(self, entry: ConsciousnessEntry):
        """
        Adds a new consciousness entry to the long-term memory.
        The entry's content is converted into a vector embedding for storage.
        """
        embedding = self._model.encode([entry.content])[0].tolist()
        
        metadata = {
            "content": entry.content,
            "context": entry.context,
            "entry_type": entry.entry_type.name,
            "timestamp": entry.timestamp.isoformat()
        }

        self._collection.add(
            embeddings=[embedding],
            documents=[entry.content],  # The document is the content itself
            metadatas=[metadata],
            ids=[str(entry.id)]
        )
        print(f"Added memory to LTM: {entry}")

    def search_memories(self, query_text: str, n_results: int = 5) -> List[Dict[str, Any]]:
        """
        Searches for memories semantically similar to the query text.
        
        Returns a list of dictionaries, where each dictionary contains
        the memory's metadata and its distance (similarity score).
        """
        query_embedding = self._model.encode([query_text])[0].tolist()
        
        results = self._collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results
        )

        # The result from chromadb is a dictionary of lists. Let's reformat it.
        memories = []
        if results['ids'][0]:
            for i in range(len(results['ids'][0])):
                memory = {
                    "id": results['ids'][0][i],
                    "distance": results['distances'][0][i],
                    "metadata": results['metadatas'][0][i]
                }
                memories.append(memory)

        return memories 