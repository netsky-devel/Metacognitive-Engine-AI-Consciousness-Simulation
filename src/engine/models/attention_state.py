"""
Attention State Models for Metacognitive Engine

This module defines the data structures for attention management,
including attention focus, weights, and state tracking.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any
import uuid


class AttentionType(Enum):
    """Types of attention focus"""
    MEMORY_SEARCH = "memory_search"
    INSIGHT_GENERATION = "insight_generation"
    EMOTIONAL_PROCESSING = "emotional_processing"
    RESPONSE_GENERATION = "response_generation"
    META_COGNITION = "meta_cognition"


class AttentionPriority(Enum):
    """Priority levels for attention allocation"""
    CRITICAL = "critical"      # Immediate attention required
    HIGH = "high"             # Important but not urgent
    MEDIUM = "medium"         # Normal processing priority
    LOW = "low"              # Background processing
    MINIMAL = "minimal"       # Minimal attention allocation


@dataclass
class AttentionFocus:
    """Represents a single focus of attention"""
    focus_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    attention_type: AttentionType = AttentionType.MEMORY_SEARCH
    target: str = ""                    # What we're focusing on
    weight: float = 0.5                 # Attention weight (0.0-1.0)
    priority: AttentionPriority = AttentionPriority.MEDIUM
    duration: float = 0.0               # How long we've been focusing (seconds)
    created_at: datetime = field(default_factory=datetime.now)
    last_updated: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def update_weight(self, new_weight: float) -> None:
        """Update attention weight with validation"""
        self.weight = max(0.0, min(1.0, new_weight))
        self.last_updated = datetime.now()
    
    def increase_duration(self, seconds: float) -> None:
        """Increase focus duration"""
        self.duration += seconds
        self.last_updated = datetime.now()
    
    def is_expired(self, max_duration: float = 300.0) -> bool:
        """Check if focus has been active too long"""
        return self.duration > max_duration
    
    def get_relevance_score(self) -> float:
        """Calculate relevance based on weight, priority, and recency"""
        priority_weights = {
            AttentionPriority.CRITICAL: 1.0,
            AttentionPriority.HIGH: 0.8,
            AttentionPriority.MEDIUM: 0.6,
            AttentionPriority.LOW: 0.4,
            AttentionPriority.MINIMAL: 0.2
        }
        
        # Time decay factor (newer focuses are more relevant)
        time_diff = (datetime.now() - self.last_updated).total_seconds()
        time_factor = max(0.1, 1.0 - (time_diff / 3600))  # Decay over 1 hour
        
        relevance = (
            self.weight * 0.4 +
            priority_weights[self.priority] * 0.4 +
            time_factor * 0.2
        )
        
        return min(1.0, relevance)


@dataclass
class AttentionState:
    """Current state of the attention system"""
    current_focuses: List[AttentionFocus] = field(default_factory=list)
    attention_history: List[AttentionFocus] = field(default_factory=list)
    total_attention_capacity: float = 1.0      # Total available attention
    current_attention_usage: float = 0.0       # Currently allocated attention
    attention_threshold: float = 0.1           # Minimum attention to maintain focus
    max_concurrent_focuses: int = 5            # Maximum simultaneous focuses
    created_at: datetime = field(default_factory=datetime.now)
    last_updated: datetime = field(default_factory=datetime.now)
    
    def add_focus(self, focus: AttentionFocus) -> bool:
        """Add a new attention focus if capacity allows"""
        if len(self.current_focuses) >= self.max_concurrent_focuses:
            # Remove lowest priority focus to make room
            self._remove_lowest_priority_focus()
        
        # Check if we have enough attention capacity
        required_attention = focus.weight
        if self.current_attention_usage + required_attention > self.total_attention_capacity:
            # Reduce weights of existing focuses to make room
            self._rebalance_attention(required_attention)
        
        self.current_focuses.append(focus)
        self.current_attention_usage += focus.weight
        self.last_updated = datetime.now()
        return True
    
    def remove_focus(self, focus_id: str) -> bool:
        """Remove a specific attention focus"""
        for i, focus in enumerate(self.current_focuses):
            if focus.focus_id == focus_id:
                removed_focus = self.current_focuses.pop(i)
                self.current_attention_usage -= removed_focus.weight
                self.attention_history.append(removed_focus)
                self.last_updated = datetime.now()
                return True
        return False
    
    def update_focus_weight(self, focus_id: str, new_weight: float) -> bool:
        """Update the weight of a specific focus"""
        for focus in self.current_focuses:
            if focus.focus_id == focus_id:
                old_weight = focus.weight
                focus.update_weight(new_weight)
                self.current_attention_usage += (new_weight - old_weight)
                self.last_updated = datetime.now()
                return True
        return False
    
    def get_dominant_focus(self) -> Optional[AttentionFocus]:
        """Get the focus with highest relevance score"""
        if not self.current_focuses:
            return None
        
        return max(self.current_focuses, key=lambda f: f.get_relevance_score())
    
    def get_focuses_by_type(self, attention_type: AttentionType) -> List[AttentionFocus]:
        """Get all focuses of a specific type"""
        return [f for f in self.current_focuses if f.attention_type == attention_type]
    
    def cleanup_expired_focuses(self, max_duration: float = 300.0) -> int:
        """Remove expired focuses and return count removed"""
        expired = [f for f in self.current_focuses if f.is_expired(max_duration)]
        for focus in expired:
            self.remove_focus(focus.focus_id)
        return len(expired)
    
    def get_attention_summary(self) -> Dict[str, Any]:
        """Get summary of current attention state"""
        focus_types = {}
        for focus in self.current_focuses:
            focus_type = focus.attention_type.value
            if focus_type not in focus_types:
                focus_types[focus_type] = {"count": 0, "total_weight": 0.0}
            focus_types[focus_type]["count"] += 1
            focus_types[focus_type]["total_weight"] += focus.weight
        
        dominant_focus = self.get_dominant_focus()
        
        return {
            "total_focuses": len(self.current_focuses),
            "attention_usage": f"{self.current_attention_usage:.2f}/{self.total_attention_capacity}",
            "usage_percentage": f"{(self.current_attention_usage / self.total_attention_capacity) * 100:.1f}%",
            "dominant_focus": dominant_focus.target if dominant_focus else None,
            "dominant_focus_type": dominant_focus.attention_type.value if dominant_focus else None,
            "focus_distribution": focus_types,
            "last_updated": self.last_updated.isoformat()
        }
    
    def _remove_lowest_priority_focus(self) -> None:
        """Remove focus with lowest priority and relevance"""
        if not self.current_focuses:
            return
        
        # Sort by priority (ascending) then by relevance (ascending)
        priority_order = {
            AttentionPriority.MINIMAL: 0,
            AttentionPriority.LOW: 1,
            AttentionPriority.MEDIUM: 2,
            AttentionPriority.HIGH: 3,
            AttentionPriority.CRITICAL: 4
        }
        
        lowest_focus = min(
            self.current_focuses,
            key=lambda f: (priority_order[f.priority], f.get_relevance_score())
        )
        
        self.remove_focus(lowest_focus.focus_id)
    
    def _rebalance_attention(self, required_attention: float) -> None:
        """Rebalance existing attention weights to make room for new focus"""
        if not self.current_focuses:
            return
        
        # Calculate how much we need to reduce
        available_capacity = self.total_attention_capacity - self.current_attention_usage
        reduction_needed = required_attention - available_capacity
        
        if reduction_needed <= 0:
            return
        
        # Reduce weights proportionally, prioritizing lower priority focuses
        total_reducible_weight = sum(
            max(0, f.weight - self.attention_threshold) 
            for f in self.current_focuses
        )
        
        if total_reducible_weight <= 0:
            return
        
        for focus in self.current_focuses:
            reducible_weight = max(0, focus.weight - self.attention_threshold)
            if reducible_weight > 0:
                reduction_ratio = reducible_weight / total_reducible_weight
                weight_reduction = reduction_needed * reduction_ratio
                new_weight = max(self.attention_threshold, focus.weight - weight_reduction)
                self.current_attention_usage -= (focus.weight - new_weight)
                focus.update_weight(new_weight) 