import spacy
from typing import List, Dict, Any

class SensoryCortex:
    """
    Processes raw text input to extract meaningful structures like
    entities, intent, and sentiment.
    """

    def __init__(self):
        try:
            self._nlp = spacy.load('en_core_web_sm')
            print("SensoryCortex initialized with 'en_core_web_sm' model.")
        except OSError:
            print("Spacy model 'en_core_web_sm' not found.")
            print("Please run: python -m spacy download en_core_web_sm")
            self._nlp = None

    def analyze(self, text: str) -> Dict[str, Any]:
        """
        Analyzes a piece of text and returns a structured representation.
        For now, it only extracts named entities.
        """
        if not self._nlp:
            return {"text": text, "entities": []}

        doc = self._nlp(text)
        
        entities = [
            {"text": ent.text, "label": ent.label_}
            for ent in doc.ents
        ]

        # In the future, we'll add intent and sentiment analysis here
        structured_input = {
            "text": text,
            "entities": entities,
            "intent": None,  # Placeholder
            "sentiment": None, # Placeholder
        }
        
        return structured_input 