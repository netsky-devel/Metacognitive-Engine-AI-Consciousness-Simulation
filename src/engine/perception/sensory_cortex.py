import spacy
from langdetect import detect, lang_detect_exception
import logging
import re
from typing import Dict, List, Tuple

from ..memory.working_memory import StructuredInput

# Настройка логирования для подавления слишком "громких" библиотек
logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

class SensoryCortex:
    """
    Advanced perceptual analysis system that transforms raw text into rich StructuredInput.
    Performs intent recognition, sentiment analysis, tone detection, and entity extraction.
    """
    def __init__(self):
        self.models = {}  # Кэш для загруженных моделей spaCy
        
        # Intent patterns - простая regex-based система для демонстрации
        self.intent_patterns = {
            'QUESTION': [r'\?', r'как\s+', r'что\s+', r'почему', r'зачем', r'когда', r'где', 
                        r'how\s+', r'what\s+', r'why', r'when', r'where'],
            'CHALLENGE_PROPOSAL': [r'попробуй', r'можешь\s+ли', r'давай', r'предлагаю',
                                  r'try\s+', r'can\s+you', r'let\'s', r'i\s+suggest'],
            'REFLECTION': [r'думаю', r'считаю', r'мне\s+кажется', r'по\s+моему',
                          r'i\s+think', r'i\s+believe', r'it\s+seems', r'in\s+my\s+opinion'],
            'COMMAND': [r'сделай', r'создай', r'покажи', r'объясни',
                       r'make', r'create', r'show', r'explain'],
            'FEEDBACK': [r'хорошо', r'плохо', r'неправильно', r'отлично',
                        r'good', r'bad', r'wrong', r'excellent']
        }
        
        # Sentiment patterns
        self.sentiment_patterns = {
            'POSITIVE': [r'хорошо', r'отлично', r'замечательно', r'прекрасно',
                        r'good', r'excellent', r'wonderful', r'great'],
            'NEGATIVE': [r'плохо', r'ужасно', r'неправильно', r'кошмар',
                        r'bad', r'terrible', r'wrong', r'awful'],
            'CURIOUS': [r'интересно', r'любопытно', r'хочу\s+знать',
                       r'interesting', r'curious', r'want\s+to\s+know'],
            'SKEPTICAL': [r'сомневаюсь', r'не\s+уверен', r'вряд\s+ли',
                         r'doubt', r'not\s+sure', r'unlikely']
        }
        
        # Tone patterns  
        self.tone_patterns = {
            'FORMAL': [r'Вы', r'Ваш', r'позвольте', r'благодарю',
                      r'please', r'thank\s+you', r'would\s+you'],
            'CASUAL': [r'ты', r'твой', r'привет', r'пока',
                      r'hey', r'hi', r'bye', r'you\'re'],
            'ENTHUSIASTIC': [r'!', r'вау', r'потрясающе', r'круто',
                           r'wow', r'amazing', r'awesome', r'cool'],
            'SKEPTICAL': [r'серьёзно\?', r'неужели', r'ну\s+да',
                         r'seriously\?', r'really\?', r'sure']
        }

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

    def _detect_intent(self, text: str) -> Tuple[str, float]:
        """Detect user intent using pattern matching."""
        text_lower = text.lower()
        
        for intent, patterns in self.intent_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text_lower):
                    return intent, 0.8  # Simple confidence score
        
        return 'UNKNOWN', 0.1

    def _detect_sentiment(self, text: str) -> Tuple[str, float]:
        """Detect sentiment using pattern matching."""
        text_lower = text.lower()
        
        for sentiment, patterns in self.sentiment_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text_lower):
                    return sentiment, 0.7
        
        return 'NEUTRAL', 0.5

    def _detect_tone(self, text: str) -> Tuple[str, float]:
        """Detect tone using pattern matching."""
        text_lower = text.lower()
        
        for tone, patterns in self.tone_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text_lower):
                    return tone, 0.7
        
        return 'NEUTRAL', 0.5

    def analyze(self, text: str) -> StructuredInput:
        """
        Performs comprehensive perceptual analysis of input text.

        Args:
            text: The input text string.

        Returns:
            A StructuredInput object with rich analysis results.
        """
        # Language detection
        try:
            lang = detect(text)
        except lang_detect_exception.LangDetectException:
            log.warning("Could not detect language. Falling back to 'unknown'.")
            lang = "unknown"

        # Entity extraction
        entities = []
        if lang != "unknown":
            nlp = self._get_model(lang)
            if nlp:
                doc = nlp(text)
                entities = [(ent.text, ent.label_) for ent in doc.ents]

        # Intent, sentiment, and tone detection
        intent, intent_confidence = self._detect_intent(text)
        sentiment, sentiment_confidence = self._detect_sentiment(text)
        tone, tone_confidence = self._detect_tone(text)
        
        # Overall confidence (simple average)
        overall_confidence = (intent_confidence + sentiment_confidence + tone_confidence) / 3

        # Create structured input
        structured_input = StructuredInput(
            raw_text=text,
            language=lang,
            entities=entities,
            intent=intent,
            sentiment=sentiment,
            tone=tone,
            confidence=overall_confidence,
            metadata={
                'intent_confidence': intent_confidence,
                'sentiment_confidence': sentiment_confidence,
                'tone_confidence': tone_confidence,
                'text_length': len(text),
                'word_count': len(text.split())
            }
        )
        
        log.info(f"SensoryCortex analysis: Intent={intent}, Sentiment={sentiment}, Tone={tone}")
        return structured_input 