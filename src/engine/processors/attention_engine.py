"""
Attention Engine for Metacognitive Engine

This module implements the attention mechanism that manages cognitive focus
and resource allocation across different processing tasks.
"""

import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple

from ..models.attention_state import (
    AttentionState, AttentionFocus, AttentionType, AttentionPriority
)
from ..memory.working_memory import WorkingMemory

logger = logging.getLogger(__name__)


class AttentionEngine:
    """
    Manages attention allocation and focus across cognitive processes.
    
    Implements selective attention mechanism that:
    - Allocates attention resources to different cognitive tasks
    - Maintains focus on most relevant information
    - Tracks attention shifts over time
    - Provides context switching capabilities
    """
    
    def __init__(self, 
                 total_capacity: float = 1.0,
                 max_concurrent_focuses: int = 5,
                 attention_threshold: float = 0.1,
                 focus_decay_rate: float = 0.01):
        """
        Initialize the attention engine.
        
        Args:
            total_capacity: Total attention capacity (0.0-1.0)
            max_concurrent_focuses: Maximum simultaneous attention focuses
            attention_threshold: Minimum attention weight to maintain
            focus_decay_rate: Rate at which unused focuses decay
        """
        self.attention_state = AttentionState(
            total_attention_capacity=total_capacity,
            max_concurrent_focuses=max_concurrent_focuses,
            attention_threshold=attention_threshold
        )
        self.focus_decay_rate = focus_decay_rate
        self.processing_start_time = time.time()
        
        # Attention allocation strategies
        self.attention_strategies = {
            "balanced": self._balanced_attention_strategy,
            "focused": self._focused_attention_strategy,
            "exploratory": self._exploratory_attention_strategy
        }
        self.current_strategy = "balanced"
        
        logger.info(f"AttentionEngine initialized with capacity {total_capacity}")
    
    def process(self, working_memory: WorkingMemory) -> bool:
        """
        Main processing method called during cognitive cycles.
        
        Args:
            working_memory: Current working memory state
            
        Returns:
            bool: True if attention was successfully allocated
        """
        try:
            # Update timing information
            current_time = time.time()
            cycle_duration = current_time - self.processing_start_time
            
            # Clean up expired focuses
            expired_count = self.attention_state.cleanup_expired_focuses()
            if expired_count > 0:
                logger.debug(f"Cleaned up {expired_count} expired attention focuses")
            
            # Analyze current context and determine attention needs
            attention_needs = self._analyze_attention_needs(working_memory)
            
            # Allocate attention based on current strategy
            strategy_func = self.attention_strategies[self.current_strategy]
            allocated_focuses = strategy_func(attention_needs, working_memory)
            
            # Update attention durations
            self._update_focus_durations(cycle_duration)
            
            # Store attention context in working memory
            attention_context = self.get_attention_context()
            working_memory.set_context_data("attention_context", attention_context)
            
            logger.debug(f"Attention allocated: {len(allocated_focuses)} focuses active")
            return True
            
        except Exception as e:
            logger.error(f"Error in attention processing: {e}")
            return False
        finally:
            self.processing_start_time = time.time()
    
    def allocate_attention(self, 
                          attention_type: AttentionType,
                          target: str,
                          weight: float = 0.5,
                          priority: AttentionPriority = AttentionPriority.MEDIUM,
                          metadata: Optional[Dict[str, Any]] = None) -> Optional[str]:
        """
        Manually allocate attention to a specific target.
        
        Args:
            attention_type: Type of attention focus
            target: What to focus attention on
            weight: Attention weight (0.0-1.0)
            priority: Priority level
            metadata: Additional metadata
            
        Returns:
            str: Focus ID if successful, None otherwise
        """
        try:
            focus = AttentionFocus(
                attention_type=attention_type,
                target=target,
                weight=weight,
                priority=priority,
                metadata=metadata or {}
            )
            
            success = self.attention_state.add_focus(focus)
            if success:
                logger.info(f"Attention allocated to {target} ({attention_type.value})")
                return focus.focus_id
            else:
                logger.warning(f"Failed to allocate attention to {target}")
                return None
                
        except Exception as e:
            logger.error(f"Error allocating attention: {e}")
            return None
    
    def get_attention_context(self) -> Dict[str, Any]:
        """
        Get current attention context for other processors.
        
        Returns:
            Dict containing attention context information
        """
        dominant_focus = self.attention_state.get_dominant_focus()
        summary = self.attention_state.get_attention_summary()
        
        context = {
            "attention_summary": summary,
            "dominant_focus": {
                "target": dominant_focus.target if dominant_focus else None,
                "type": dominant_focus.attention_type.value if dominant_focus else None,
                "weight": dominant_focus.weight if dominant_focus else 0.0,
                "priority": dominant_focus.priority.value if dominant_focus else None
            },
            "current_strategy": self.current_strategy,
            "attention_guidance": self._generate_attention_guidance()
        }
        
        return context
    
    def _analyze_attention_needs(self, working_memory: WorkingMemory) -> Dict[AttentionType, float]:
        """
        Analyze current context to determine attention allocation needs.
        
        Args:
            working_memory: Current working memory state
            
        Returns:
            Dict mapping attention types to needed weights
        """
        needs = {}
        
        # Analyze input complexity
        structured_input = working_memory.get_structured_input()
        if structured_input:
            # Higher complexity inputs need more memory search attention
            complexity_score = len(structured_input.entities) * 0.1
            needs[AttentionType.MEMORY_SEARCH] = min(0.8, 0.3 + complexity_score)
            
            # Emotional content needs emotional processing attention
            if hasattr(structured_input, 'sentiment') and structured_input.sentiment in ["EMOTIONAL", "NEGATIVE", "POSITIVE"]:
                needs[AttentionType.EMOTIONAL_PROCESSING] = 0.4
        
        # Analyze memory retrieval needs
        retrieved_memories = working_memory.get_retrieved_memories()
        if retrieved_memories:
            memory_count = len(retrieved_memories)
            # More memories require more insight generation attention
            needs[AttentionType.INSIGHT_GENERATION] = min(0.7, 0.2 + memory_count * 0.1)
        
        # Analyze current insights
        insights = working_memory.get_generated_insights()
        if insights:
            # Many insights require response generation attention
            needs[AttentionType.RESPONSE_GENERATION] = min(0.8, 0.4 + len(insights) * 0.1)
        
        # Always allocate some attention to meta-cognition
        needs[AttentionType.META_COGNITION] = 0.2
        
        return needs
    
    def _balanced_attention_strategy(self, 
                                   attention_needs: Dict[AttentionType, float],
                                   working_memory: WorkingMemory) -> List[AttentionFocus]:
        """
        Balanced attention allocation strategy.
        
        Distributes attention evenly across all identified needs.
        """
        allocated_focuses = []
        
        if not attention_needs:
            return allocated_focuses
        
        # Normalize weights to fit within capacity
        total_needed = sum(attention_needs.values())
        capacity = self.attention_state.total_attention_capacity
        
        for attention_type, needed_weight in attention_needs.items():
            normalized_weight = (needed_weight / total_needed) * capacity * 0.8  # Leave 20% buffer
            
            focus_id = self.allocate_attention(
                attention_type=attention_type,
                target=f"{attention_type.value}_focus",
                weight=normalized_weight,
                priority=AttentionPriority.MEDIUM,
                metadata={"strategy": "balanced"}
            )
            
            if focus_id:
                focus = next(f for f in self.attention_state.current_focuses 
                           if f.focus_id == focus_id)
                allocated_focuses.append(focus)
        
        return allocated_focuses
    
    def _focused_attention_strategy(self, 
                                  attention_needs: Dict[AttentionType, float],
                                  working_memory: WorkingMemory) -> List[AttentionFocus]:
        """
        Focused attention allocation strategy.
        
        Concentrates most attention on the highest priority need.
        """
        allocated_focuses = []
        
        if not attention_needs:
            return allocated_focuses
        
        # Find the highest priority need
        primary_need = max(attention_needs.items(), key=lambda x: x[1])
        primary_type, primary_weight = primary_need
        
        # Allocate 70% of capacity to primary need
        primary_allocation = self.attention_state.total_attention_capacity * 0.7
        focus_id = self.allocate_attention(
            attention_type=primary_type,
            target=f"{primary_type.value}_primary",
            weight=primary_allocation,
            priority=AttentionPriority.HIGH,
            metadata={"strategy": "focused", "primary": True}
        )
        
        if focus_id:
            focus = next(f for f in self.attention_state.current_focuses 
                       if f.focus_id == focus_id)
            allocated_focuses.append(focus)
        
        # Distribute remaining 30% among other needs
        remaining_capacity = self.attention_state.total_attention_capacity * 0.3
        other_needs = {k: v for k, v in attention_needs.items() if k != primary_type}
        
        if other_needs:
            total_other = sum(other_needs.values())
            for attention_type, needed_weight in other_needs.items():
                secondary_weight = (needed_weight / total_other) * remaining_capacity
                
                focus_id = self.allocate_attention(
                    attention_type=attention_type,
                    target=f"{attention_type.value}_secondary",
                    weight=secondary_weight,
                    priority=AttentionPriority.LOW,
                    metadata={"strategy": "focused", "primary": False}
                )
                
                if focus_id:
                    focus = next(f for f in self.attention_state.current_focuses 
                               if f.focus_id == focus_id)
                    allocated_focuses.append(focus)
        
        return allocated_focuses
    
    def _exploratory_attention_strategy(self, 
                                      attention_needs: Dict[AttentionType, float],
                                      working_memory: WorkingMemory) -> List[AttentionFocus]:
        """
        Exploratory attention allocation strategy.
        
        Spreads attention widely to explore different possibilities.
        """
        allocated_focuses = []
        
        # Include all possible attention types, not just identified needs
        all_types = list(AttentionType)
        capacity_per_type = self.attention_state.total_attention_capacity / len(all_types)
        
        for attention_type in all_types:
            # Use identified need or default weight
            base_weight = attention_needs.get(attention_type, 0.1)
            exploratory_weight = min(capacity_per_type, base_weight + 0.1)
            
            focus_id = self.allocate_attention(
                attention_type=attention_type,
                target=f"{attention_type.value}_exploratory",
                weight=exploratory_weight,
                priority=AttentionPriority.MEDIUM,
                metadata={"strategy": "exploratory"}
            )
            
            if focus_id:
                focus = next(f for f in self.attention_state.current_focuses 
                           if f.focus_id == focus_id)
                allocated_focuses.append(focus)
        
        return allocated_focuses
    
    def _update_focus_durations(self, cycle_duration: float) -> None:
        """Update duration for all current focuses."""
        for focus in self.attention_state.current_focuses:
            focus.increase_duration(cycle_duration)
    
    def _generate_attention_guidance(self) -> Dict[str, Any]:
        """Generate guidance for other processors based on current attention."""
        dominant_focus = self.attention_state.get_dominant_focus()
        
        guidance = {
            "primary_focus": dominant_focus.attention_type.value if dominant_focus else None,
            "attention_distribution": {},
            "processing_recommendations": []
        }
        
        # Calculate attention distribution
        for focus in self.attention_state.current_focuses:
            focus_type = focus.attention_type.value
            if focus_type not in guidance["attention_distribution"]:
                guidance["attention_distribution"][focus_type] = 0.0
            guidance["attention_distribution"][focus_type] += focus.weight
        
        # Generate processing recommendations
        if dominant_focus:
            if dominant_focus.attention_type == AttentionType.MEMORY_SEARCH:
                guidance["processing_recommendations"].append(
                    "Prioritize memory retrieval and association finding"
                )
            elif dominant_focus.attention_type == AttentionType.INSIGHT_GENERATION:
                guidance["processing_recommendations"].append(
                    "Focus on generating new insights and connections"
                )
            elif dominant_focus.attention_type == AttentionType.EMOTIONAL_PROCESSING:
                guidance["processing_recommendations"].append(
                    "Emphasize emotional analysis and empathetic responses"
                )
            elif dominant_focus.attention_type == AttentionType.RESPONSE_GENERATION:
                guidance["processing_recommendations"].append(
                    "Concentrate on crafting coherent and relevant responses"
                )
        
        return guidance 