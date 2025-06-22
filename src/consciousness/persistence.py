import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any

from .entry import ConsciousnessEntry, EntryType


class ConsciousnessEncoder(json.JSONEncoder):
    """
    Custom JSON encoder to handle ConsciousnessEntry specific types.
    """
    def default(self, obj):
        if isinstance(obj, ConsciousnessEntry):
            return {
                "__type__": "ConsciousnessEntry",
                **obj.__dict__
            }
        if isinstance(obj, EntryType):
            return {"__type__": "EntryType", "name": obj.name}
        if isinstance(obj, datetime):
            return {"__type__": "datetime", "iso": obj.isoformat()}
        if isinstance(obj, uuid.UUID):
            return {"__type__": "UUID", "hex": obj.hex}
        return super().default(obj)


def as_consciousness_entry(dct: Dict[str, Any]) -> Any:
    """
    Custom decoder function for JSON loading.
    """
    if "__type__" in dct:
        type_name = dct.pop("__type__")
        if type_name == "ConsciousnessEntry":
            return ConsciousnessEntry(**dct)
        if type_name == "EntryType":
            return EntryType[dct["name"]]
        if type_name == "datetime":
            return datetime.fromisoformat(dct["iso"])
        if type_name == "UUID":
            return uuid.UUID(dct["hex"])
    return dct


class JsonPersistence:
    """
    Handles saving and loading consciousness entries to/from a JSON file.
    """

    @staticmethod
    def save_entries(entries: List[ConsciousnessEntry], file_path: Path):
        """Saves a list of entries to a JSON file."""
        file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(entries, f, cls=ConsciousnessEncoder, indent=2)

    @staticmethod
    def load_entries(file_path: Path) -> List[ConsciousnessEntry]:
        """Loads a list of entries from a JSON file."""
        if not file_path.exists():
            return []
        with open(file_path, "r", encoding="utf-8") as f:
            try:
                data = json.load(f, object_hook=as_consciousness_entry)
                # Ensure we return a list, even for an empty file
                return data if isinstance(data, list) else []
            except json.JSONDecodeError:
                return [] 