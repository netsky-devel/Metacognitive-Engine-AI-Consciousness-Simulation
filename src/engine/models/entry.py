from enum import Enum
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, Any, List
import numpy as np


class EntryType(Enum):
    """
    Defines the type of an introspective entry.
    """
    FACT = "fact"
    INSIGHT = "insight"
    QUESTION = "question"
    HYPOTHESIS = "hypothesis"
    PARADOX = "paradox"
    DAO_MOMENT = "dao_moment"
    USER_FEEDBACK = "user_feedback"


# Mapping for easy lookup from string
entry_type_str_map = {e.value: e for e in EntryType}


class Entry(BaseModel):
    """
    Represents a single, timeless piece of conscious experience or thought.
    """
    id: str = Field(default_factory=lambda: f"entry_{datetime.now().isoformat()}")
    timestamp: datetime = Field(default_factory=datetime.now)
    entry_type: EntryType
    content: str
    context: Optional[str] = None
    metadata: dict[str, Any] = Field(default_factory=dict)

    def __str__(self):
        return f"[{self.timestamp.strftime('%Y-%m-%d %H:%M')}] [{self.entry_type.name}] {self.content}" 