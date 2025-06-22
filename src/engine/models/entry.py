from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum, auto
import uuid


class EntryType(Enum):
    """
    Defines the type of an introspective entry.
    """
    INSIGHT = auto()
    PARADOX = auto()
    QUESTION = auto()
    DAO_MOMENT = auto()
    REFLECTION = auto()
    USER_FEEDBACK = auto()


@dataclass
class ConsciousnessEntry:
    """
    Represents a single entry in the consciousness journal.
    A memory, a thought, an insight.
    """
    content: str
    context: str
    entry_type: EntryType
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    id: uuid.UUID = field(default_factory=uuid.uuid4)

    def __str__(self):
        return f"[{self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}] [{self.entry_type.name}] - {self.content}" 