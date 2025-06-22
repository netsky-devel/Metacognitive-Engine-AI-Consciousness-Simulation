from pathlib import Path
from typing import List, Optional

from .entry import ConsciousnessEntry, EntryType
from .persistence import JsonPersistence


class ConsciousnessJournal:
    """
    Manages a collection of consciousness entries, handling their
    loading, creation, and saving.
    """

    def __init__(self, journal_file_path: Path):
        self._file_path = journal_file_path
        self._persistence = JsonPersistence()
        self._entries: List[ConsciousnessEntry] = self._persistence.load_entries(self._file_path)
        print(f"Journal initialized. Loaded {len(self._entries)} entries from {self._file_path}")

    def add_entry(self, content: str, context: str, entry_type: EntryType) -> ConsciousnessEntry:
        """
        Creates a new entry, adds it to the journal, and returns it.
        """
        entry = ConsciousnessEntry(content=content, context=context, entry_type=entry_type)
        self._entries.append(entry)
        print(f"Added new entry: {entry}")
        return entry

    def save(self):
        """
        Saves the current state of the journal to the file.
        """
        self._persistence.save_entries(self._entries, self._file_path)
        print(f"Journal saved. {len(self._entries)} entries written to {self._file_path}")

    def get_all_entries(self) -> List[ConsciousnessEntry]:
        """
        Returns all entries in the journal.
        """
        return self._entries

    def get_last_n_entries(self, n: int) -> List[ConsciousnessEntry]:
        """
        Returns the last N entries.
        """
        return self._entries[-n:]

    @property
    def count(self) -> int:
        """
        Returns the total number of entries in the journal.
        """
        return len(self._entries) 