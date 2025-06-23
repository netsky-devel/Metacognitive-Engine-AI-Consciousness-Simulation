"""
Tests for the MCP server endpoints
"""

import pytest
import tempfile
import shutil
import os
from fastapi.testclient import TestClient
from unittest.mock import patch, Mock

from src.mcp_server import app
from src.engine.models.entry import EntryType


class TestMCPServer:
    """Test the MCP server endpoints"""
    
    @pytest.fixture
    def client(self):
        """Create a test client for the FastAPI app"""
        return TestClient(app)
    
    @pytest.fixture
    def temp_db_setup(self):
        """Setup temporary database for testing"""
        temp_dir = tempfile.mkdtemp()
        test_db_path = os.path.join(temp_dir, "test_chroma_db")
        
        # Patch the engine initialization to use temp DB
        with patch('src.mcp_server.engine') as mock_engine:
            yield mock_engine, test_db_path
        
        # Cleanup
        shutil.rmtree(temp_dir)
    
    def test_add_memory_endpoint(self, client, temp_db_setup):
        """Test the /add endpoint"""
        mock_engine, _ = temp_db_setup
        
        # Mock engine behavior
        mock_entry = Mock()
        mock_entry.id = "test_id"
        mock_entry.timestamp.isoformat.return_value = "2025-01-01T00:00:00"
        mock_entry.entry_type.name = "INSIGHT"
        mock_entry.content = "Test content"
        
        mock_engine.add_memory.return_value = None
        
        # Test request
        response = client.post("/add", json={
            "content": "Test content",
            "entry_type": "insight"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert "content" in data
        assert "type" in data
    
    def test_query_memories_endpoint(self, client, temp_db_setup):
        """Test the /query endpoint"""
        mock_engine, _ = temp_db_setup
        
        # Mock engine behavior
        mock_entry = Mock()
        mock_entry.id = "test_id"
        mock_entry.timestamp.isoformat.return_value = "2025-01-01T00:00:00"
        mock_entry.entry_type.name = "INSIGHT"
        mock_entry.content = "Test content"
        
        mock_engine.ltm.query.return_value = [mock_entry]
        
        # Test request
        response = client.post("/query", json={
            "content": "test query",
            "n_results": 3
        })
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_reflect_endpoint(self, client, temp_db_setup):
        """Test the /reflect endpoint"""
        mock_engine, _ = temp_db_setup
        
        # Mock engine behavior
        mock_entry = Mock()
        mock_entry.id = "test_id"
        mock_entry.timestamp.isoformat.return_value = "2025-01-01T00:00:00"
        mock_entry.entry_type.name = "INSIGHT"
        mock_entry.content = "Generated insight"
        
        mock_engine.analyze_new_thought.return_value = [mock_entry]
        
        # Test request
        response = client.post("/reflect", json={
            "content": "test thought"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_process_endpoint(self, client, temp_db_setup):
        """Test the /process endpoint"""
        mock_engine, _ = temp_db_setup
        
        # Mock engine behavior
        mock_engine.process_thought.return_value = "Generated response"
        
        # Test request
        response = client.post("/process", json={
            "content": "test thought"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert "response" in data
        assert "status" in data
        assert data["status"] == "success"
    
    def test_list_memories_endpoint(self, client, temp_db_setup):
        """Test the /list endpoint"""
        mock_engine, _ = temp_db_setup
        
        # Mock engine behavior
        mock_collection = Mock()
        mock_collection.get.return_value = {
            "ids": ["test_id"],
            "metadatas": [{
                "content": "Test content",
                "entry_type": "insight",
                "timestamp": "2025-01-01T00:00:00"
            }]
        }
        mock_engine.ltm.collection = mock_collection
        
        # Test request
        response = client.get("/list")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_clear_memories_endpoint(self, client, temp_db_setup):
        """Test the /clear endpoint"""
        mock_engine, _ = temp_db_setup
        
        # Mock engine behavior
        mock_engine.clear_all_memories.return_value = None
        
        # Test request
        response = client.post("/clear")
        
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
    
    def test_invalid_entry_type(self, client, temp_db_setup):
        """Test /add endpoint with invalid entry type"""
        mock_engine, _ = temp_db_setup
        
        # Test request with invalid entry type
        response = client.post("/add", json={
            "content": "Test content",
            "entry_type": "invalid_type"
        })
        
        assert response.status_code == 400
    
    def test_error_handling(self, client, temp_db_setup):
        """Test error handling in endpoints"""
        mock_engine, _ = temp_db_setup
        
        # Mock engine to raise an exception
        mock_engine.add_memory.side_effect = Exception("Test error")
        
        # Test request that should fail
        response = client.post("/add", json={
            "content": "Test content",
            "entry_type": "insight"
        })
        
        assert response.status_code == 400


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 