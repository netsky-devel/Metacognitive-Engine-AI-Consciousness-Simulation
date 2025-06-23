"""
Shared pytest fixtures for all tests
"""

import pytest
import tempfile
import shutil
import os
import time


@pytest.fixture
def temp_db_path():
    """
    Create a temporary database path for testing with proper cleanup.
    Handles Windows file locking issues with retries.
    """
    temp_dir = tempfile.mkdtemp()
    db_path = os.path.join(temp_dir, "test_chroma_db")
    
    yield db_path
    
    # Cleanup with retry for Windows file locking issues
    for attempt in range(3):
        try:
            shutil.rmtree(temp_dir)
            break
        except (PermissionError, OSError) as e:
            if attempt < 2:  # Not the last attempt
                time.sleep(0.5)
            else:  # Last attempt, ignore errors
                try:
                    shutil.rmtree(temp_dir, ignore_errors=True)
                except:
                    pass  # Ignore all cleanup errors on final attempt 