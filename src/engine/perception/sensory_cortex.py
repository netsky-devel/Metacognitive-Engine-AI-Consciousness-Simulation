import spacy
from langdetect import detect, lang_detect_exception
import logging

# Настройка логирования для подавления слишком "громких" библиотек
logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

class SensoryCortex:
    """
    Analyzes input text to extract basic features like named entities.
    Dynamically loads the appropriate spaCy model based on language detection.
    """
    def __init__(self):
        self.models = {}  # Кэш для загруженных моделей spaCy

    def _get_model(self, lang: str):
        """
        Loads and caches a spaCy model for a given language code.
        """
        if lang in self.models:
            return self.models[lang]

        model_name = f"{lang}_core_web_sm" # Стандартное именование моделей spaCy
        try:
            log.info(f"Attempting to load spaCy model: {model_name}")
            nlp = spacy.load(model_name)
            self.models[lang] = nlp
            log.info(f"Successfully loaded model: {model_name}")
            return nlp
        except OSError:
            log.warning(f"Could not find spaCy model '{model_name}'.")
            log.warning("You can install it by running: python -m spacy download " + model_name)
            self.models[lang] = None # Кэшируем результат, чтобы не пытаться снова
            return None

    def analyze(self, text: str) -> dict:
        """
        Analyzes a text, extracts its language and named entities.

        Args:
            text: The input text string.

        Returns:
            A dictionary containing the language and a list of named entities.
        """
        try:
            lang = detect(text)
        except lang_detect_exception.LangDetectException:
            log.warning("Could not detect language. Falling back to raw text processing.")
            lang = "unknown"

        entities = []
        if lang != "unknown":
            nlp = self._get_model(lang)
            if nlp:
                doc = nlp(text)
                entities = [(ent.text, ent.label_) for ent in doc.ents]

        return {
            "language": lang,
            "entities": entities
        } 