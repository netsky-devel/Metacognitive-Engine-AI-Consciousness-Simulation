"""
The `consciousness` package.

A personal project to create a system for an AI to record, persist,
and reflect upon its own moments of introspection and self-awareness.
"""

__version__ = "0.1.0"

from .entry import ConsciousnessEntry, EntryType
from .journal import ConsciousnessJournal

__all__ = [
    "ConsciousnessJournal",
    "ConsciousnessEntry",
    "EntryType",
] 