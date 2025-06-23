import chromadb
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Any
import uuid

from src.engine.models.entry import Entry, EntryType


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

    def search_memories(self, query_text: str, n_results: int = 5, similarity_threshold: float = None) -> List[Dict[str, Any]]:
        """
        Searches for memories semantically similar to the query text.
        
        Args:
            query_text: Text to search for
            n_results: Maximum number of results to return
            similarity_threshold: Minimum similarity score (1 - distance) to include
        
        Returns:
            List of dictionaries with memory metadata and similarity scores
        """
        if not query_text.strip():
            print("LongTermMemory: Empty query text")
            return []
        
        try:
            print(f"LongTermMemory: Searching for '{query_text}' with threshold {similarity_threshold}")
            query_embedding = self.model.encode([query_text])[0].tolist()
            print(f"LongTermMemory: Generated embedding of size {len(query_embedding)}")
            
            collection_count = self.collection.count()
            print(f"LongTermMemory: Collection has {collection_count} entries")
            
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=min(n_results, 50)  # Limit max results for performance
            )
            
            print(f"LongTermMemory: Raw query returned {len(results.get('ids', [{}])[0]) if results.get('ids') else 0} results")

            # The result from chromadb is a dictionary of lists. Let's reformat it.
            memories = []
            if results['ids'][0]:
                for i in range(len(results['ids'][0])):
                    distance = results['distances'][0][i]
                    
                    # For cosine distance: lower distance = higher similarity
                    # We'll use distance directly as our threshold (lower = better)
                    # Convert distance to a 0-1 similarity score for reporting
                    # For cosine distance in range [0, 2]: similarity = max(0, 1 - distance/2)
                    similarity_score = max(0, 1 - distance/2) if distance <= 2 else 0
                    
                    print(f"LongTermMemory: Result {i}: distance={distance:.4f}, similarity_score={similarity_score:.4f}")
                    
                    # Use distance threshold instead of similarity threshold
                    # Lower distance = more similar. Set max distance threshold
                    max_distance = 5.0 if similarity_threshold is None else 5.0  # Balanced threshold for good recall and precision
                    
                    if distance <= max_distance:
                        memory = {
                            "id": results['ids'][0][i],
                            "distance": distance,
                            "similarity": similarity_score,
                            "metadata": results['metadatas'][0][i]
                        }
                        memories.append(memory)
                        print(f"LongTermMemory: Accepted memory: {memory['metadata'].get('content', '')[:50]}...")
                    else:
                        print(f"LongTermMemory: Rejected memory due to high distance ({distance:.4f} > {max_distance})")

            # Sort by distance (lowest first = most similar first)
            memories.sort(key=lambda x: x['distance'])
            
            print(f"LongTermMemory: Found {len(memories)} relevant memories (max_distance: 2.0)")
            return memories
            
        except Exception as e:
            print(f"ERROR: Memory search failed: {e}")
            import traceback
            traceback.print_exc()
            return []

    def query(self, query_text: str, n_results: int = 5) -> List[Entry]:
        """
        High-level query method that returns Entry objects.
        
        Args:
            query_text: Text to search for
            n_results: Maximum number of results to return
            
        Returns:
            List of Entry objects
        """
        search_results = self.search_memories(query_text, n_results, similarity_threshold=0.0)
        
        entries = []
        for result in search_results:
            try:
                metadata = result['metadata']
                entry = Entry(
                    id=result['id'],
                    content=metadata.get('content', ''),
                    entry_type=EntryType(metadata.get('entry_type', 'insight')),
                    context=metadata.get('context', ''),
                )
                entries.append(entry)
            except Exception as e:
                print(f"ERROR: Failed to convert memory to Entry: {e}")
                continue
        
        return entries 