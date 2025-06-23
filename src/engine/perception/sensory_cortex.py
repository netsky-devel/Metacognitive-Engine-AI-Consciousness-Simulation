import spacy
import os
import json
import google.generativeai as genai
from langdetect import detect, lang_detect_exception
import logging
from typing import Dict, List, Tuple

from ..memory.working_memory import StructuredInput

# Настройка логирования
logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

class SensoryCortex:
    """
    AI-powered perceptual analysis system that transforms raw text into rich StructuredInput.
    Uses LLM for intent recognition, sentiment analysis, tone detection, and spaCy for entity extraction.
    """
    def __init__(self):
        self.models = {}  # Кэш для загруженных моделей spaCy
        
        # Initialize LLM for advanced analysis
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            log.warning("GEMINI_API_KEY not set. Using fallback analysis.")
            self.llm = None
        else:
            genai.configure(api_key=api_key)
            self.llm = genai.GenerativeModel('gemini-1.5-flash-latest')
        
        log.info("SensoryCortex initialized with AI-powered analysis.")

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

    def _create_analysis_prompt(self, text: str, language: str) -> str:
        """Create prompt for comprehensive text analysis."""
        return f"""
Analyze the following text for intent, sentiment, and tone. Provide a structured JSON response.

TEXT: "{text}"
LANGUAGE: {language}

Classify the text according to these categories:

INTENT (choose one):
- QUESTION: User is asking for information or clarification
- COMMAND: User is giving instructions or requesting actions
- REFLECTION: User is sharing thoughts, opinions, or personal insights
- CHALLENGE_PROPOSAL: User is proposing a test, challenge, or experiment
- FEEDBACK: User is providing evaluation or response to something
- GREETING: User is saying hello or starting conversation
- FAREWELL: User is ending conversation
- UNKNOWN: Intent unclear

SENTIMENT (choose one):
- POSITIVE: Expressing satisfaction, happiness, or approval
- NEGATIVE: Expressing dissatisfaction, sadness, or disapproval
- NEUTRAL: No clear emotional valence
- CURIOUS: Expressing interest or desire to learn
- SKEPTICAL: Expressing doubt or questioning
- ENTHUSIASTIC: Expressing excitement or strong positive emotion
- FRUSTRATED: Expressing annoyance or impatience

TONE (choose one):
- FORMAL: Professional, polite, structured language
- CASUAL: Informal, relaxed, conversational
- ENTHUSIASTIC: Energetic, excited, passionate
- SKEPTICAL: Doubtful, questioning, critical
- RESPECTFUL: Polite, considerate, deferential  
- URGENT: Demanding immediate attention or action
- NEUTRAL: No particular tone markers

Provide confidence scores (0.0-1.0) for each classification.

Response format (JSON only):
{{
    "intent": "INTENT_NAME",
    "intent_confidence": 0.0,
    "sentiment": "SENTIMENT_NAME", 
    "sentiment_confidence": 0.0,
    "tone": "TONE_NAME",
    "tone_confidence": 0.0,
    "reasoning": "Brief explanation of the analysis"
}}
"""

    def _analyze_with_ai(self, text: str, language: str) -> Dict[str, any]:
        """Perform AI-powered analysis of text."""
        if not self.llm:
            return self._fallback_analysis(text, language)
        
        try:
            prompt = self._create_analysis_prompt(text, language)
            
            generation_config = genai.types.GenerationConfig(
                response_mime_type="application/json",
                temperature=0.1,  # Low temperature for consistent analysis
                max_output_tokens=500
            )
            
            response = self.llm.generate_content(prompt, generation_config=generation_config)
            result = json.loads(response.text)
            
            log.info(f"AI analysis: {result.get('intent', 'UNKNOWN')} | {result.get('sentiment', 'NEUTRAL')} | {result.get('tone', 'NEUTRAL')}")
            
            return result
            
        except Exception as e:
            log.error(f"AI analysis failed: {e}")
            return self._fallback_analysis(text, language)
    
    def _fallback_analysis(self, text: str, language: str) -> Dict[str, any]:
        """Simple fallback analysis when AI is not available."""
        text_lower = text.lower()
        
        # Simple heuristics for intent
        intent = "UNKNOWN"
        intent_confidence = 0.3
        
        if '?' in text or any(word in text_lower for word in ['what', 'how', 'why', 'when', 'where', 'who', 'что', 'как', 'почему', 'когда', 'где']):
            intent = "QUESTION"
            intent_confidence = 0.7
        elif any(word in text_lower for word in ['please', 'can you', 'could you', 'make', 'create', 'show', 'explain', 'сделай', 'покажи', 'объясни', 'можешь']):
            intent = "COMMAND"
            intent_confidence = 0.6
        elif any(word in text_lower for word in ['i think', 'i believe', 'in my opinion', 'я думаю', 'я считаю', 'по-моему']):
            intent = "REFLECTION"
            intent_confidence = 0.6
        elif any(word in text_lower for word in ['hello', 'hi', 'hey', 'привет', 'здравствуй']):
            intent = "GREETING"
            intent_confidence = 0.8
        
        # Simple sentiment analysis
        sentiment = "NEUTRAL"
        sentiment_confidence = 0.5
        
        positive_words = ['good', 'great', 'excellent', 'wonderful', 'amazing', 'хорошо', 'отлично', 'замечательно', 'прекрасно']
        negative_words = ['bad', 'terrible', 'awful', 'horrible', 'плохо', 'ужасно', 'кошмар', 'неправильно']
        
        if any(word in text_lower for word in positive_words):
            sentiment = "POSITIVE"
            sentiment_confidence = 0.7
        elif any(word in text_lower for word in negative_words):
            sentiment = "NEGATIVE"
            sentiment_confidence = 0.7
        elif any(word in text_lower for word in ['interesting', 'curious', 'wonder', 'интересно', 'любопытно']):
            sentiment = "CURIOUS"
            sentiment_confidence = 0.6
        
        # Simple tone analysis
        tone = "NEUTRAL"
        tone_confidence = 0.5
        
        if '!' in text:
            tone = "ENTHUSIASTIC"
            tone_confidence = 0.6
        elif any(word in text_lower for word in ['please', 'thank you', 'thanks', 'спасибо', 'пожалуйста']):
            tone = "RESPECTFUL"
            tone_confidence = 0.7
        elif language in ['ru', 'russian'] and any(word in text for word in ['Вы', 'Ваш', 'Вам']):
            tone = "FORMAL"
            tone_confidence = 0.8
        elif any(word in text_lower for word in ['hey', 'hi', 'yeah', 'ok', 'привет', 'да', 'ок']):
            tone = "CASUAL"
            tone_confidence = 0.7
        
        return {
            "intent": intent,
            "intent_confidence": intent_confidence,
            "sentiment": sentiment,
            "sentiment_confidence": sentiment_confidence,
            "tone": tone,
            "tone_confidence": tone_confidence,
            "reasoning": "Fallback heuristic analysis"
        }

    def analyze(self, text: str) -> StructuredInput:
        """
        Performs comprehensive AI-powered perceptual analysis of input text.

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

        # Entity extraction using spaCy
        entities = []
        if lang != "unknown":
            nlp = self._get_model(lang)
            if nlp:
                doc = nlp(text)
                entities = [(ent.text, ent.label_) for ent in doc.ents]

        # AI-powered intent, sentiment, and tone analysis
        log.info(f"Analyzing text with AI: '{text[:50]}{'...' if len(text) > 50 else ''}'")
        analysis_result = self._analyze_with_ai(text, lang)
        
        # Extract results
        intent = analysis_result.get('intent', 'UNKNOWN')
        sentiment = analysis_result.get('sentiment', 'NEUTRAL')
        tone = analysis_result.get('tone', 'NEUTRAL')
        
        # Calculate overall confidence
        intent_confidence = analysis_result.get('intent_confidence', 0.1)
        sentiment_confidence = analysis_result.get('sentiment_confidence', 0.5)
        tone_confidence = analysis_result.get('tone_confidence', 0.5)
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
                'word_count': len(text.split()),
                'analysis_method': 'AI' if self.llm else 'fallback',
                'reasoning': analysis_result.get('reasoning', 'No reasoning provided')
            }
        )
        
        log.info(f"SensoryCortex analysis complete: Intent={intent} ({intent_confidence:.2f}), Sentiment={sentiment} ({sentiment_confidence:.2f}), Tone={tone} ({tone_confidence:.2f})")
        return structured_input 