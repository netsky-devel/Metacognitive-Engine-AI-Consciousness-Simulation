import os
import json
import google.generativeai as genai
from typing import List, Tuple, Dict, Any, Optional
from src.engine.models.entry import Entry, EntryType
from ..memory.working_memory import WorkingMemory

class IntrospectionEngine:
    """
    A cognitive processor that reflects on new information in the context of
    existing memories to generate new insights, questions, or identify paradoxes
    by leveraging the Google Gemini API.
    """
    def __init__(self):
        # API-ключ должен быть установлен в переменной окружения GEMINI_API_KEY
        # Вы можете создать файл .env в корне проекта и записать в него:
        # GEMINI_API_KEY="..."
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            print("WARNING: GEMINI_API_KEY environment variable not set. IntrospectionEngine will be disabled.")
            self.model = None
        else:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-1.5-flash-latest')
        print("IntrospectionEngine initialized for Gemini.")

    def process(self, working_memory: WorkingMemory) -> bool:
        """
        Process the working memory to generate introspective insights.
        
        Args:
            working_memory: The working memory to analyze.
            
        Returns:
            bool: True if processing was successful and generated new insights.
        """
        if not working_memory.structured_input:
            print("IntrospectionEngine: No structured input to process.")
            return False
        
        # Perform multiple types of introspective analysis
        insights_generated = 0
        
        print(f"IntrospectionEngine: Retrieved memories count: {len(working_memory.retrieved_memories)}")
        
        # 1. Analyze input against retrieved memories
        if working_memory.retrieved_memories:
            print("IntrospectionEngine: Analyzing with memories...")
            memory_insight = self._analyze_with_memories(working_memory)
            if memory_insight:
                working_memory.add_insight(memory_insight)
                insights_generated += 1
                print(f"IntrospectionEngine: Generated memory insight: {memory_insight.entry_type.name}")
        else:
            print("IntrospectionEngine: No retrieved memories, trying simple analysis...")
            # Generate a simple insight even without memories
            simple_insight = self._generate_simple_insight(working_memory)
            if simple_insight:
                working_memory.add_insight(simple_insight)
                insights_generated += 1
        
        # 2. Detect paradoxes in the current context
        paradox_insight = self._detect_paradoxes(working_memory)
        if paradox_insight:
            working_memory.add_insight(paradox_insight)
            insights_generated += 1
        
        # 3. Assess confidence in current understanding
        confidence_score = self._assess_confidence(working_memory)
        working_memory.update_cognitive_state(confidence_score=confidence_score)
        
        # 4. Add context tags based on analysis
        if insights_generated > 0:
            working_memory.add_context_tag("INSIGHTS_GENERATED")
        
        print(f"IntrospectionEngine: Generated {insights_generated} insights, confidence: {confidence_score:.2f}")
        return insights_generated > 0
    
    def _analyze_with_memories(self, working_memory: WorkingMemory) -> Optional[Entry]:
        """Analyze input in context of retrieved memories."""
        if not self.model or not working_memory.retrieved_memories:
            return self._simple_memory_analysis(working_memory)
        
        original_text = working_memory.structured_input.raw_text
        strongest_memory = working_memory.retrieved_memories[0]
        associated_content = strongest_memory.content
        
        prompt = self._create_memory_analysis_prompt(original_text, associated_content)
        
        try:
            print("\n[IntrospectionEngine] Analyzing input with memories...")
            generation_config = genai.types.GenerationConfig(
                response_mime_type="application/json",
                temperature=0.2
            )
            response = self.model.generate_content(prompt, generation_config=generation_config)
            
            result = json.loads(response.text)
            
            action = result.get("action")
            content = result.get("content")

            print(f"[IntrospectionEngine] Memory analysis result: {action}")

            if not content:
                return None
            
            entry_map = {
                "create_insight": EntryType.INSIGHT,
                "create_paradox": EntryType.PARADOX,
                "create_question": EntryType.QUESTION,
            }

            if action in entry_map:
                return Entry(
                    entry_type=entry_map[action],
                    content=content,
                    context=f"Generated from input analysis with memory: '{strongest_memory.content[:50]}...'"
                )

        except Exception as e:
            print(f"ERROR: Memory analysis failed: {e}")
            return self._simple_memory_analysis(working_memory)
        
        return None
    
    def _detect_paradoxes(self, working_memory: WorkingMemory) -> Optional[Entry]:
        """Detect contradictions or paradoxes in the current context."""
        # Simple paradox detection logic
        memories = working_memory.retrieved_memories
        input_data = working_memory.structured_input
        
        if len(memories) >= 2:
            # Check for contradictory sentiments or contexts
            memory_contents = [m.content.lower() for m in memories[:2]]
            input_lower = input_data.raw_text.lower()
            
            # Simple keyword-based paradox detection
            positive_words = ['good', 'great', 'excellent', 'wonderful', 'хорошо', 'отлично']
            negative_words = ['bad', 'terrible', 'awful', 'wrong', 'плохо', 'ужасно']
            
            has_positive = any(word in input_lower or any(word in mc for mc in memory_contents) for word in positive_words)
            has_negative = any(word in input_lower or any(word in mc for mc in memory_contents) for word in negative_words)
            
            if has_positive and has_negative:
                return Entry(
                    entry_type=EntryType.PARADOX,
                    content=f"Detected contradictory sentiments in current context: positive and negative evaluations present",
                    context="Simple paradox detection based on sentiment analysis"
                )
        
        return None
    
    def _assess_confidence(self, working_memory: WorkingMemory) -> float:
        """Assess confidence in the current cognitive state."""
        confidence_factors = []
        
        # Factor 1: Input analysis confidence
        if working_memory.structured_input:
            confidence_factors.append(working_memory.structured_input.confidence)
        
        # Factor 2: Association strength
        if working_memory.associations:
            avg_similarity = sum(a.get('similarity', 0) for a in working_memory.associations) / len(working_memory.associations)
            confidence_factors.append(avg_similarity)
        
        # Factor 3: Number of insights generated
        insight_count = len(working_memory.generated_insights)
        insight_confidence = min(1.0, insight_count * 0.3)
        confidence_factors.append(insight_confidence)
        
        # Return average confidence
        return sum(confidence_factors) / len(confidence_factors) if confidence_factors else 0.1
    
    def _simple_memory_analysis(self, working_memory: WorkingMemory) -> Optional[Entry]:
        """Simple fallback analysis when LLM is not available."""
        if not working_memory.retrieved_memories:
            return None
        
        input_intent = working_memory.structured_input.intent
        memory_count = len(working_memory.retrieved_memories)
        
        if input_intent == 'QUESTION' and memory_count > 0:
            return Entry(
                entry_type=EntryType.INSIGHT,
                content=f"Found {memory_count} relevant memories that might help answer this question.",
                context="Simple analysis mode"
            )
        elif input_intent == 'REFLECTION' and memory_count > 0:
            return Entry(
                entry_type=EntryType.QUESTION,
                content="How do these past thoughts relate to my current reflection?",
                context="Simple analysis mode"
            )
        
        return None

    def _generate_simple_insight(self, working_memory: WorkingMemory) -> Optional[Entry]:
        """Generate simple insight when no memories are available."""
        input_data = working_memory.structured_input
        
        if not input_data:
            return None
        
        # Generate insight based on input intent and sentiment
        if input_data.intent == 'QUESTION':
            return Entry(
                entry_type=EntryType.INSIGHT,
                content=f"This question about '{input_data.raw_text[:50]}...' explores important aspects that deserve deeper consideration.",
                context="Simple insight generation"
            )
        elif input_data.intent == 'REFLECTION':
            return Entry(
                entry_type=EntryType.QUESTION,
                content=f"What deeper implications might this reflection have for understanding the topic?",
                context="Generated from reflection"
            )
        elif input_data.sentiment == 'CURIOUS':
            return Entry(
                entry_type=EntryType.INSIGHT,
                content=f"This curiosity-driven inquiry opens pathways for exploration and learning.",
                context="Curiosity-based insight"
            )
        
        # Default insight
        return Entry(
            entry_type=EntryType.INSIGHT,
            content=f"This input ({input_data.intent}, {input_data.sentiment}) provides valuable information for processing.",
            context="Default simple insight"
        )

    def _create_memory_analysis_prompt(self, original_text: str, associated_content: str) -> str:
        return f"""
You are a metacognitive introspection engine.
Your task is to analyze a new thought and its strongest associated memory.
Based on this, you must determine if a new insight, paradox, or question arises.

New Thought: "{original_text}"
Associated Memory: "{associated_content}"

Analyze these two statements.
- If they are trivial, only rephrase the same idea, or the connection is weak, respond with: {{"action": "none"}}
- If they reveal a deeper connection or a new layer of understanding, respond with: {{"action": "create_insight", "content": "A concise new insight here."}}
- If they contradict each other, respond with: {{"action": "create_paradox", "content": "A concise statement of the paradox here."}}
- If the new thought raises a new question based on the memory, respond with: {{"action": "create_question", "content": "A concise new question here."}}

Your response MUST be a single, valid JSON object and nothing else.
The JSON must be enclosed in ```json ... ``` tags.
"""

    def analyze(self, original_text: str, associations: List[Tuple[Dict[str, Any], float]]) -> Optional[Entry]:
        """Legacy method for backward compatibility."""
        if not self.model or not associations:
            return None

        strongest_association, _ = associations[0]
        associated_content = strongest_association.get('content', '')
        
        prompt = self._create_memory_analysis_prompt(original_text, associated_content)
        
        try:
            print("\n[IntrospectionEngine] Querying Gemini for insights...")
            # Gemini требует специальной настройки для вывода JSON
            generation_config = genai.types.GenerationConfig(
                response_mime_type="application/json",
                temperature=0.2
            )
            response = self.model.generate_content(prompt, generation_config=generation_config)
            
            result = json.loads(response.text)
            
            action = result.get("action")
            content = result.get("content")

            print(f"[IntrospectionEngine] Gemini LLM Action: {action}")

            if not content:
                return None
            
            entry_map = {
                "create_insight": EntryType.INSIGHT,
                "create_paradox": EntryType.PARADOX,
                "create_question": EntryType.QUESTION,
            }

            if action in entry_map:
                return Entry(
                    entry_type=entry_map[action],
                    content=content,
                    context=f"Generated by Gemini based on thought: '{original_text}'"
                )

        except Exception as e:
            print(f"ERROR: An error occurred while querying Gemini: {e}")
        
        return None 