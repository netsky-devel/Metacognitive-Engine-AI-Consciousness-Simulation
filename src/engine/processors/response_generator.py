import os
import json
import google.generativeai as genai
from typing import Dict, Any, Optional
from datetime import datetime

from ..memory.working_memory import WorkingMemory


class ResponseGenerator:
    """
    Generates coherent, context-aware responses by synthesizing all information
    in WorkingMemory (input, retrieved memories, generated insights).
    """
    
    def __init__(self):
        # API-ключ должен быть установлен в переменной окружения GEMINI_API_KEY
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            print("WARNING: GEMINI_API_KEY environment variable not set. ResponseGenerator will be disabled.")
            self.model = None
        else:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-1.5-flash-latest')
        print("ResponseGenerator initialized for Gemini.")

    def _create_synthesis_prompt(self, working_memory: WorkingMemory) -> str:
        """Create a prompt for response synthesis based on working memory content."""
        
        content = working_memory.get_all_content()
        
        # Extract key information
        input_data = content['input']
        memories = content['memories']
        insights = content['insights']
        associations = content['associations']
        context_tags = content['context_tags']
        cognitive_state = content['cognitive_state']
        
        prompt_parts = [
            "You are a metacognitive AI system generating a thoughtful response.",
            "You have processed user input through multiple cognitive stages.",
            "",
            f"USER INPUT:",
            f"Text: \"{input_data.raw_text if input_data else 'No input'}\"",
            f"Intent: {input_data.intent if input_data else 'Unknown'}",
            f"Sentiment: {input_data.sentiment if input_data else 'Unknown'}",
            f"Tone: {input_data.tone if input_data else 'Unknown'}",
            "",
        ]
        
        if memories:
            prompt_parts.extend([
                "RETRIEVED MEMORIES:",
                *[f"- {memory.content} ({memory.entry_type.name})" for memory in memories[:3]],
                "",
            ])
        
        if insights:
            prompt_parts.extend([
                "GENERATED INSIGHTS:",
                *[f"- {insight.content} ({insight.entry_type.name})" for insight in insights],
                "",
            ])
        
        if context_tags:
            prompt_parts.extend([
                f"CONTEXT TAGS: {', '.join(context_tags)}",
                "",
            ])
        
        # Add emotional context if available
        if hasattr(cognitive_state, 'emotional_state') and cognitive_state.emotional_state:
            emotional_state = cognitive_state.emotional_state
            prompt_parts.extend([
                "EMOTIONAL CONTEXT:",
                f"- Emotional state: {emotional_state.to_summary_string()}",
                f"- Emotional quadrant: {emotional_state.get_emotional_quadrant()}",
                f"- Dominant emotion: {emotional_state.get_dominant_emotion().value if emotional_state.get_dominant_emotion() else 'None'}",
                f"- Emotional intensity: {emotional_state.get_emotional_intensity():.2f}",
                f"- Valence: {emotional_state.valence:.2f} (positive/negative)",
                f"- Arousal: {emotional_state.arousal:.2f} (calm/excited)",
                "",
            ])
        
        prompt_parts.extend([
            "COGNITIVE STATE:",
            f"- Cycles completed: {cognitive_state.cycle_count}",
            f"- Confidence level: {cognitive_state.confidence_score:.2f}",
            f"- Active insights: {len(cognitive_state.active_insights)}",
            "",
            "TASK:",
            "Synthesize all this information into a coherent, thoughtful response.",
            "Consider the user's intent, relevant memories, and new insights.",
            "Match the tone and sentiment appropriately.",
            "Be authentic and show the depth of your processing.",
            "",
            "EMOTIONAL RESPONSE GUIDELINES:",
            "- If emotional context is provided, incorporate it naturally into your response",
            "- Match the user's emotional energy level (high arousal = more energetic response)",
            "- Respond empathetically if the user seems to be in distress or negative emotional state",
            "- Be encouraging if the user seems to need support",
            "- Show emotional understanding and connection when appropriate",
            "- If positive emotions are detected, respond with warmth and engagement",
            "",
            "Your response should be natural and conversational, not a data dump.",
            "Show how the memories, insights, and emotional context influenced your thinking.",
            "Demonstrate emotional intelligence in your response."
        ])
        
        return "\n".join(prompt_parts)

    def _create_simple_response(self, working_memory: WorkingMemory) -> str:
        """Create a simple fallback response when LLM is not available."""
        content = working_memory.get_all_content()
        input_data = content['input']
        
        if not input_data:
            return "I processed your input, but encountered an issue. Please try again."
        
        response_parts = []
        
        # Acknowledge the input
        if input_data.intent == 'QUESTION':
            response_parts.append("I understand you're asking about something.")
        elif input_data.intent == 'COMMAND':
            response_parts.append("I see you'd like me to do something.")
        elif input_data.intent == 'REFLECTION':
            response_parts.append("Thank you for sharing your thoughts.")
        else:
            response_parts.append("I've processed your input.")
        
        # Mention memories if found
        memories = content['memories']
        if memories:
            response_parts.append(f"I found {len(memories)} relevant memories that relate to this.")
        
        # Mention insights if generated
        insights = content['insights']
        if insights:
            response_parts.append(f"This led me to {len(insights)} new insights.")
        
        response_parts.append("My cognitive processing is currently in basic mode.")
        
        return " ".join(response_parts)

    def generate_response(self, working_memory: WorkingMemory) -> str:
        """
        Generate a comprehensive response based on all working memory content.
        
        Args:
            working_memory: The WorkingMemory containing all processed information.
            
        Returns:
            A synthesized response string.
        """
        
        if not working_memory.is_ready_for_response():
            return "I need more information to provide a meaningful response."
        
        if not self.model:
            return self._create_simple_response(working_memory)
        
        try:
            print("\n[ResponseGenerator] Synthesizing final response...")
            
            prompt = self._create_synthesis_prompt(working_memory)
            
            # Generate response with appropriate configuration
            generation_config = genai.types.GenerationConfig(
                temperature=0.7,  # Slightly creative
                max_output_tokens=1000,
                top_p=0.8
            )
            
            response = self.model.generate_content(prompt, generation_config=generation_config)
            
            generated_response = response.text.strip()
            
            print(f"[ResponseGenerator] Generated response ({len(generated_response)} chars)")
            
            return generated_response
            
        except Exception as e:
            print(f"ERROR: ResponseGenerator failed: {e}")
            return self._create_simple_response(working_memory)

    def get_response_metadata(self, working_memory: WorkingMemory) -> Dict[str, Any]:
        """Get metadata about the response generation process."""
        content = working_memory.get_all_content()
        
        return {
            "timestamp": datetime.now().isoformat(),
            "input_intent": content['input'].intent if content['input'] else None,
            "memories_used": len(content['memories']),
            "insights_generated": len(content['insights']),
            "cognitive_cycles": content['cognitive_state'].cycle_count,
            "confidence_score": content['cognitive_state'].confidence_score,
            "context_tags": content['context_tags']
        } 