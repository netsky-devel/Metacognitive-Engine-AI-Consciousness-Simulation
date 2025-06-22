"""
The `engine` package.

This package contains the core components of the Metacognitive Engine,
a system designed to simulate a thinking process through interacting
cognitive modules.
"""

__version__ = "0.2.0"

# Expose key models and components at the package level
from .models.entry import Entry, EntryType
from .memory.long_term_memory import LongTermMemory
from .main import MetacognitiveEngine

__all__ = [
    "Entry",
    "EntryType",
    "LongTermMemory",
    "MetacognitiveEngine"
]

# This file makes 'engine' a Python package. 