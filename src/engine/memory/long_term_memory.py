import chromadb
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Any
import uuid

from src.engine.models.entry import Entry


class LongTermMemory:
    """
    Handles the storage and retrieval of consciousness entries using a vector database
    for semantic search capabilities.
    """

    def __init__(self, db_path: str = "data/chroma_db"):
        self.client = chromadb.PersistentClient(path=db_path)
        
        # Заменяем модель на многоязычную
        model_name = "paraphrase-multilingual-mpnet-base-v2"
        self.model = SentenceTransformer(model_name)
        
        self.collection = self.client.get_or_create_collection(
            name="consciousness_stream_v2",
            metadata={"hnsw:space": "cosine"}
        )
        print(f"LongTermMemory initialized. Collection '{self.collection.name}' has {self.collection.count()} entries.")

    def clear_all_memories(self):
        """
        Deletes and recreates the entire collection, effectively clearing all memories.
        """
        print(f"Clearing all memories from collection '{self.collection.name}'...")
        self.client.delete_collection(name=self.collection.name)
        self.collection = self.client.get_or_create_collection(name=self.collection.name)
        print("Memory cleared. Collection is now empty.")

    def add_memory(self, entry: Entry):
        """
        Adds a new memory entry to the vector database.
        The entry's content is converted into a vector embedding for storage.
        """
        embedding = self.model.encode([entry.content])[0].tolist()
        
        metadata = {
            "content": entry.content,
            "context": entry.context or "",
            "entry_type": entry.entry_type.value,
            "timestamp": entry.timestamp.isoformat()
        }

        self.collection.add(
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
        query_embedding = self.model.encode([query_text])[0].tolist()
        
        results = self.collection.query(
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