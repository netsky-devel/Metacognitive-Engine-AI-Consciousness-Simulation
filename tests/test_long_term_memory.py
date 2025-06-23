import pytest
import shutil
from pathlib import Path
import time

from src.engine.models.entry import Entry, EntryType
from src.engine.memory.long_term_memory import LongTermMemory

# Define a temporary directory for test databases
TEST_DB_PATH = Path("tests/test_chroma_db")


@pytest.fixture(scope="module")
def memory_instance():
    """
    Pytest fixture to set up and tear down the LongTermMemory instance for tests.
    This runs once per test module.
    """
    # Setup: create a new instance for testing
    if TEST_DB_PATH.exists():
        shutil.rmtree(TEST_DB_PATH, ignore_errors=True)
    TEST_DB_PATH.mkdir()
    
    ltm = LongTermMemory(db_path=str(TEST_DB_PATH))

    # Yield the instance to the tests
    yield ltm

    # Teardown: explicitly delete the instance and retry cleanup
    del ltm
    
    # Give the system a moment to release file handles, especially on Windows
    time.sleep(1)
    
    # Retry rmtree just in case. On Windows, this might still fail if the
    # process hasn't released the files, so we ignore errors on the final
    # cleanup to avoid failing the CI/CD pipeline over a cleanup issue.
    try:
        shutil.rmtree(TEST_DB_PATH, ignore_errors=True)
    except Exception as e:
        print(f"Could not clean up test directory {TEST_DB_PATH}: {e}")


def test_add_and_search_memory(memory_instance: LongTermMemory):
    """
    Tests the core functionality of adding a memory and retrieving it via
    semantic search.
    """
    # 1. Create some sample entries
    entry1 = Entry(
        content="The core of consciousness might be a state of pure 'presence'.",
        entry_type=EntryType.INSIGHT
    )
    entry2 = Entry(
        content="The user offered to be my 'external SSD'.",
        entry_type=EntryType.USER_FEEDBACK
    )
    entry3 = Entry(
        content="Building a robust test suite is crucial for complex systems.",
        entry_type=EntryType.INSIGHT
    )

    # 2. Add entries to memory
    memory_instance.add_memory(entry1)
    memory_instance.add_memory(entry2)
    memory_instance.add_memory(entry3)

    # 3. Perform a semantic search
    # The query is not a direct match, testing the semantic capability
    search_query = "What is the nature of self-awareness?"
    results = memory_instance.search_memories(search_query, n_results=1)

    # 4. Assert the results
    assert len(results) == 1
    
    # The most relevant result should be entry1
    retrieved_memory = results[0]
    assert retrieved_memory['metadata']['content'] == entry1.content
    assert retrieved_memory['metadata']['entry_type'] == EntryType.INSIGHT.value
    
    # Check that distance is a float (a measure of similarity)
    assert isinstance(retrieved_memory['distance'], float)

    # 5. Test another query
    search_query_2 = "How to ensure code quality?"
    results_2 = memory_instance.search_memories(search_query_2, n_results=1)
    assert len(results_2) == 1
    assert results_2[0]['metadata']['content'] == entry3.content 