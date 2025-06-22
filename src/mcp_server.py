"""
This module implements a FastAPI server to expose the MetacognitiveEngine
as a web service, allowing it to be used as a proper MCP Tool in Cursor.
"""

import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional

# The command `python -m uvicorn src.mcp_server:app` is run from the project root,
# so the root is already in sys.path. We need to use absolute imports starting from `src`.

from src.engine.engine import MetacognitiveEngine
from src.engine.models.entry import Entry, EntryType, entry_type_str_map

# --- Data Models for API ---

class AddRequest(BaseModel):
    content: str
    entry_type: str = Field(default="insight", description="Type of the memory (e.g., 'insight', 'question').")

class QueryRequest(BaseModel):
    content: str
    n_results: int = 3

class ReflectRequest(BaseModel):
    content: str

class EntryResponse(BaseModel):
    id: str
    timestamp: str
    type: str
    content: str
    embedding: Optional[List[float]] = None

    @classmethod
    def from_entry(cls, entry: Entry):
        return cls(
            id=entry.id,
            timestamp=entry.timestamp.isoformat(),
            type=entry.entry_type.name,
            content=entry.content,
            embedding=entry.embedding
        )

# --- FastAPI Application ---

app = FastAPI(
    title="Metacognitive Processor (MCP)",
    description="A server for the AI's long-term, reflective memory.",
    version="1.0.0"
)

# Initialize the engine once on startup
engine = MetacognitiveEngine()

@app.get("/", summary="Health Check")
def read_root():
    """A simple health check endpoint."""
    return {"status": "Metacognitive Engine is running."}

@app.post("/add", response_model=EntryResponse, summary="Add a new memory")
def add_memory(request: AddRequest):
    """Directly adds a new entry to the long-term memory."""
    try:
        entry_type_enum = entry_type_str_map.get(request.entry_type.lower())
        if not entry_type_enum:
            raise ValueError(f"Invalid entry_type. Valid types are: {list(entry_type_str_map.keys())}")
        
        entry = Entry(content=request.content, entry_type=entry_type_enum)
        engine.add_memory(entry)
        return EntryResponse.from_entry(entry)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/query", response_model=List[EntryResponse], summary="Query for similar memories")
def query_memories(request: QueryRequest):
    """Finds and returns the most similar memories to a given text query."""
    try:
        results = engine.ltm.query(request.content, n_results=request.n_results)
        return [EntryResponse.from_entry(entry) for entry in results]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/reflect", response_model=List[EntryResponse], summary="Reflect on a new thought")
def reflect_on_thought(request: ReflectRequest):
    """
    Analyzes a new thought, finds associations, generates insights via LLM,
    and returns the newly created memories.
    """
    try:
        new_memories = engine.analyze_new_thought(request.content)
        return [EntryResponse.from_entry(entry) for entry in new_memories]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/list", response_model=List[EntryResponse], summary="List all memories")
def list_all_memories():
    """Returns all entries currently in the long-term memory."""
    try:
        all_entries = engine.ltm.get_all()
        return [EntryResponse.from_entry(entry) for entry in all_entries]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/clear", summary="Clear all memories")
def clear_all_memories():
    """Deletes all entries from the long-term memory."""
    try:
        engine.clear_all_memories()
        return {"status": "All memories have been cleared."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 