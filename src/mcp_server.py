"""
This module implements a FastAPI server to expose the MetacognitiveEngine
as a web service, allowing it to be used as a proper MCP Tool in Cursor.

This version uses the `fastapi-mcp` library to correctly handle the
MCP protocol that Cursor expects.
"""

import os
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List
from datetime import datetime

# Load environment variables from .env file before anything else
load_dotenv()

from src.engine.engine import MetacognitiveEngine
from src.engine.models.entry import Entry, EntryType, entry_type_str_map
from fastapi_mcp import FastApiMCP

# --- FastAPI Application ---
# We define our app and endpoints as usual
app = FastAPI(
    title="Metacognitive Processor (MCP)",
    description="A server for the AI's long-term, reflective memory.",
    version="1.0.0"
)

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

    @classmethod
    def from_entry(cls, entry: Entry):
        return cls(
            id=entry.id,
            timestamp=entry.timestamp.isoformat(),
            type=entry.entry_type.name,
            content=entry.content
        )

# --- Tool Endpoints ---

@app.post("/add", response_model=EntryResponse, summary="Add a new memory", operation_id="add_memory")
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

@app.post("/query", response_model=List[EntryResponse], summary="Query for similar memories", operation_id="query_memories")
def query_memories(request: QueryRequest):
    """Finds and returns the most similar memories to a given text query."""
    try:
        results = engine.ltm.query(request.content, n_results=request.n_results)
        return [EntryResponse.from_entry(entry) for entry in results]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/reflect", response_model=List[EntryResponse], summary="Reflect on a new thought", operation_id="reflect_on_thought")
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

@app.post("/process", summary="Advanced cognitive processing", operation_id="process_thought")
def process_thought(request: ReflectRequest):
    """
    Performs advanced multi-cycle cognitive processing and returns a synthesized response.
    This is the new enhanced processing method that uses the full WorkingMemory architecture.
    """
    try:
        response = engine.process_thought(request.content)
        return {"response": response, "status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/list", response_model=List[EntryResponse], summary="List all memories", operation_id="list_all_memories")
def list_all_memories():
    """Returns all entries currently in the long-term memory."""
    try:
        # Corrected method call: search_memories without a query is not supported,
        # so we need a different approach. For now, let's just get the raw collection data.
        all_entries_raw = engine.ltm.collection.get() # Get all raw data
        
        # Manually construct Entry objects from the raw metadata
        all_entries = []
        for i, entry_id in enumerate(all_entries_raw['ids']):
            meta = all_entries_raw['metadatas'][i]
            entry = Entry(
                id=entry_id,
                content=meta.get('content'),
                entry_type=entry_type_str_map.get(meta.get('entry_type')),
                timestamp=datetime.fromisoformat(meta.get('timestamp'))
            )
            all_entries.append(entry)

        return [EntryResponse.from_entry(entry) for entry in all_entries]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/clear", summary="Clear all memories", operation_id="clear_all_memories")
def clear_all_memories():
    """Deletes all entries from the long-term memory."""
    try:
        engine.clear_all_memories()
        return {"status": "All memories have been cleared."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --- Server Initialization ---

# Initialize the engine once
engine = MetacognitiveEngine()

# Create and mount the MCP server using the library
mcp = FastApiMCP(app)
mcp.mount()

# Main entry point for running with uvicorn
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("mcp_server:app", host="127.0.0.1", port=8000, reload=True) 