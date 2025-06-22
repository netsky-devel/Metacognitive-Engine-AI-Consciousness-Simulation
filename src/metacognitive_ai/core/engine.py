"""
Core Metacognitive Engine

The main orchestrator for AI self-awareness and introspection capabilities.
"""

import asyncio
import time
from typing import Any, Dict, List, Optional, Callable, AsyncGenerator
from dataclasses import dataclass, field
from enum import Enum
import uuid
from loguru import logger

# Temporary: Remove these imports until we implement the classes
# from .thought_tracker import ThoughtTracker
# from .introspection import IntrospectionEngine


class CognitiveState(Enum):
    """Current state of the cognitive system"""
    IDLE = "idle"
    THINKING = "thinking"
    ANALYZING = "analyzing"
    REFLECTING = "reflecting"
    RESPONDING = "responding"


@dataclass 
class CognitiveStep:
    """Single step in the thinking process"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: float = field(default_factory=time.time)
    content: str = ""
    step_type: str = "reasoning"
    confidence: float = 0.5
    emotional_state: Dict[str, float] = field(default_factory=dict)
    connections: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MetacognitiveSession:
    """Complete session of metacognitive thinking"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    start_time: float = field(default_factory=time.time)
    end_time: Optional[float] = None
    initial_prompt: str = ""
    final_response: str = ""
    cognitive_steps: List[CognitiveStep] = field(default_factory=list)
    patterns_detected: List[str] = field(default_factory=list)
    introspection_report: Dict[str, Any] = field(default_factory=dict)
    performance_metrics: Dict[str, float] = field(default_factory=dict)


class MetacognitiveEngine:
    """
    Main engine for AI metacognition and self-awareness.
    
    This class orchestrates the entire metacognitive process:
    1. Tracks thinking steps in real-time
    2. Analyzes cognitive patterns
    3. Generates introspection reports
    4. Provides self-awareness capabilities
    """
    
    def __init__(self, 
                 introspection_level: str = "medium",
                 enable_real_time: bool = True,
                 max_session_duration: float = 300.0):
        """
        Initialize the metacognitive engine.
        
        Args:
            introspection_level: How deep to analyze ("low", "medium", "high")
            enable_real_time: Whether to enable real-time monitoring
            max_session_duration: Maximum session duration in seconds
        """
        self.introspection_level = introspection_level
        self.enable_real_time = enable_real_time
        self.max_session_duration = max_session_duration
        
        # Core components (placeholder for now)
        # self.thought_tracker = ThoughtTracker()
        # self.introspection_engine = IntrospectionEngine()
        
        # Session management
        self.current_session: Optional[MetacognitiveSession] = None
        self.session_history: List[MetacognitiveSession] = []
        self.cognitive_state = CognitiveState.IDLE
        
        # Real-time monitoring
        self._real_time_subscribers: List[Callable] = []
        self._monitoring_task: Optional[asyncio.Task] = None
        
        logger.info(f"MetacognitiveEngine initialized with level: {introspection_level}")
    
    async def start_session(self, prompt: str) -> str:
        """
        Start a new metacognitive session.
        
        Args:
            prompt: The initial prompt to process
            
        Returns:
            Session ID
        """
        # End current session if active
        if self.current_session:
            await self.end_session()
        
        # Create new session
        self.current_session = MetacognitiveSession(
            initial_prompt=prompt,
            start_time=time.time()
        )
        
        self.cognitive_state = CognitiveState.THINKING
        
        # Start real-time monitoring if enabled
        if self.enable_real_time:
            self._monitoring_task = asyncio.create_task(self._monitor_realtime())
        
        logger.info(f"Started metacognitive session: {self.current_session.id}")
        return self.current_session.id
    
    async def add_thought_step(self, 
                              content: str, 
                              step_type: str = "reasoning",
                              confidence: float = 0.5,
                              emotional_state: Optional[Dict[str, float]] = None) -> str:
        """
        Add a step to the current thinking process.
        
        Args:
            content: The thought content
            step_type: Type of thinking step
            confidence: Confidence level (0.0-1.0)
            emotional_state: Current emotional state
            
        Returns:
            Step ID
        """
        if not self.current_session:
            raise ValueError("No active session. Call start_session() first.")
        
        step = CognitiveStep(
            content=content,
            step_type=step_type,
            confidence=confidence,
            emotional_state=emotional_state or {}
        )
        
        # Track the thought (placeholder)
        # await self.thought_tracker.track_thought(step)
        
        # Add to current session
        self.current_session.cognitive_steps.append(step)
        
        # Notify real-time subscribers
        if self.enable_real_time:
            await self._notify_subscribers(step)
        
        logger.debug(f"Added thought step: {step.id[:8]}... ({step_type})")
        return step.id
    
    async def generate_introspection(self) -> Dict[str, Any]:
        """
        Generate introspection report for current session.
        
        Returns:
            Introspection report
        """
        if not self.current_session:
            raise ValueError("No active session")
        
        self.cognitive_state = CognitiveState.ANALYZING
        
        # Basic introspection analysis
        report = {
            "session_id": self.current_session.id,
            "total_steps": len(self.current_session.cognitive_steps),
            "thinking_patterns": self._analyze_thinking_patterns(),
            "confidence_analysis": self._analyze_confidence(),
            "cognitive_flow": self._analyze_cognitive_flow(),
            "insights": self._generate_insights(),
            "summary": self._generate_summary()
        }
        
        self.current_session.introspection_report = report
        
        logger.info("Generated introspection report")
        return report
    
    async def end_session(self, final_response: str = "") -> MetacognitiveSession:
        """
        End the current metacognitive session.
        
        Args:
            final_response: The final response generated
            
        Returns:
            Completed session
        """
        if not self.current_session:
            raise ValueError("No active session")
        
        # Stop real-time monitoring
        if self._monitoring_task:
            self._monitoring_task.cancel()
            self._monitoring_task = None
        
        # Finalize session
        self.current_session.end_time = time.time()
        self.current_session.final_response = final_response
        
        # Generate final introspection if not already done
        if not self.current_session.introspection_report:
            await self.generate_introspection()
        
        # Calculate performance metrics
        session_duration = self.current_session.end_time - self.current_session.start_time
        self.current_session.performance_metrics = {
            "session_duration": session_duration,
            "total_steps": len(self.current_session.cognitive_steps),
            "average_confidence": self._calculate_average_confidence(),
            "cognitive_complexity": self._calculate_complexity()
        }
        
        # Archive session
        completed_session = self.current_session
        self.session_history.append(completed_session)
        self.current_session = None
        self.cognitive_state = CognitiveState.IDLE
        
        logger.info(f"Ended session: {completed_session.id[:8]}... "
                   f"({session_duration:.2f}s, {len(completed_session.cognitive_steps)} steps)")
        
        return completed_session
    
    async def stream_thoughts(self) -> AsyncGenerator[CognitiveStep, None]:
        """
        Stream thoughts in real-time during active session.
        
        Yields:
            Cognitive steps as they occur
        """
        if not self.current_session:
            raise ValueError("No active session")
        
        # Yield existing steps
        for step in self.current_session.cognitive_steps:
            yield step
        
        # Stream new steps
        last_step_count = len(self.current_session.cognitive_steps)
        while self.current_session and self.cognitive_state != CognitiveState.IDLE:
            await asyncio.sleep(0.1)  # Small delay
            
            current_step_count = len(self.current_session.cognitive_steps)
            if current_step_count > last_step_count:
                # Yield new steps
                for step in self.current_session.cognitive_steps[last_step_count:]:
                    yield step
                last_step_count = current_step_count
    
    def get_session_summary(self, session_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Get summary of a session.
        
        Args:
            session_id: Session ID (current session if None)
            
        Returns:
            Session summary
        """
        if session_id is None:
            session = self.current_session
        else:
            session = next((s for s in self.session_history if s.id == session_id), None)
        
        if not session:
            raise ValueError(f"Session not found: {session_id}")
        
        return {
            "id": session.id,
            "duration": (session.end_time or time.time()) - session.start_time,
            "step_count": len(session.cognitive_steps),
            "patterns": session.patterns_detected,
            "performance": session.performance_metrics,
            "introspection_summary": session.introspection_report.get("summary", "")
        }
    
    def subscribe_realtime(self, callback: Callable[[CognitiveStep], None]) -> None:
        """Subscribe to real-time thought updates"""
        self._real_time_subscribers.append(callback)
    
    def unsubscribe_realtime(self, callback: Callable[[CognitiveStep], None]) -> None:
        """Unsubscribe from real-time thought updates"""
        if callback in self._real_time_subscribers:
            self._real_time_subscribers.remove(callback)
    
    # Private methods for analysis
    
    def _analyze_thinking_patterns(self) -> Dict[str, Any]:
        """Analyze patterns in the thinking process"""
        if not self.current_session:
            return {}
        
        steps = self.current_session.cognitive_steps
        if not steps:
            return {}
        
        # Analyze step types
        step_types = [step.step_type for step in steps]
        type_counts = {}
        for step_type in step_types:
            type_counts[step_type] = type_counts.get(step_type, 0) + 1
        
        # Analyze sequences
        sequences = []
        for i in range(len(steps) - 1):
            sequence = f"{steps[i].step_type} -> {steps[i+1].step_type}"
            sequences.append(sequence)
        
        return {
            "step_type_distribution": type_counts,
            "common_sequences": list(set(sequences)),
            "total_transitions": len(sequences)
        }
    
    def _analyze_confidence(self) -> Dict[str, Any]:
        """Analyze confidence patterns"""
        if not self.current_session:
            return {}
        
        confidences = [step.confidence for step in self.current_session.cognitive_steps]
        if not confidences:
            return {}
        
        return {
            "average": sum(confidences) / len(confidences),
            "min": min(confidences),
            "max": max(confidences),
            "variance": self._calculate_confidence_variance(),
            "trend": self._analyze_confidence_trend(confidences)
        }
    
    def _analyze_cognitive_flow(self) -> Dict[str, Any]:
        """Analyze the flow of cognitive processes"""
        if not self.current_session:
            return {}
        
        steps = self.current_session.cognitive_steps
        if len(steps) < 2:
            return {}
        
        # Calculate time gaps between steps
        time_gaps = []
        for i in range(len(steps) - 1):
            gap = steps[i+1].timestamp - steps[i].timestamp
            time_gaps.append(gap)
        
        return {
            "average_step_duration": sum(time_gaps) / len(time_gaps) if time_gaps else 0,
            "total_thinking_time": steps[-1].timestamp - steps[0].timestamp,
            "step_count": len(steps),
            "thinking_rhythm": "steady" if len(set(time_gaps)) < 3 else "variable"
        }
    
    def _generate_insights(self) -> List[str]:
        """Generate insights about the thinking process"""
        insights = []
        
        if not self.current_session:
            return insights
        
        steps = self.current_session.cognitive_steps
        if not steps:
            return insights
        
        # Confidence insights
        avg_confidence = self._calculate_average_confidence()
        if avg_confidence > 0.8:
            insights.append("High confidence throughout the thinking process")
        elif avg_confidence < 0.3:
            insights.append("Low confidence may indicate uncertainty or complex problem")
        
        # Pattern insights
        step_types = set(step.step_type for step in steps)
        if len(step_types) == 1:
            insights.append(f"Consistent {list(step_types)[0]} approach")
        elif len(step_types) > 3:
            insights.append("Diverse thinking strategies employed")
        
        # Temporal insights
        if len(steps) > 10:
            insights.append("Extended thinking process indicates thorough analysis")
        elif len(steps) < 3:
            insights.append("Rapid thinking process - intuitive or simple problem")
        
        return insights
    
    def _generate_summary(self) -> str:
        """Generate a summary of the metacognitive session"""
        if not self.current_session:
            return ""
        
        steps = self.current_session.cognitive_steps
        if not steps:
            return "No cognitive steps recorded"
        
        step_count = len(steps)
        avg_confidence = self._calculate_average_confidence()
        dominant_type = max(set(step.step_type for step in steps), 
                          key=lambda x: sum(1 for step in steps if step.step_type == x))
        
        return (f"Session involved {step_count} cognitive steps "
                f"with {avg_confidence:.1%} average confidence. "
                f"Dominant thinking mode: {dominant_type}.")
    
    def _calculate_average_confidence(self) -> float:
        """Calculate average confidence across all steps"""
        if not self.current_session or not self.current_session.cognitive_steps:
            return 0.0
        
        total = sum(step.confidence for step in self.current_session.cognitive_steps)
        return total / len(self.current_session.cognitive_steps)
    
    def _calculate_complexity(self) -> float:
        """Calculate cognitive complexity score"""
        if not self.current_session:
            return 0.0
        
        steps = self.current_session.cognitive_steps
        if not steps:
            return 0.0
        
        # Simple complexity metric
        step_types = set(step.step_type for step in steps)
        confidence_variance = self._calculate_confidence_variance()
        
        complexity = (
            len(steps) * 0.3 +
            len(step_types) * 0.4 +
            confidence_variance * 0.3
        )
        
        return min(complexity, 10.0)  # Cap at 10
    
    def _calculate_confidence_variance(self) -> float:
        """Calculate variance in confidence levels"""
        if not self.current_session or len(self.current_session.cognitive_steps) < 2:
            return 0.0
        
        confidences = [step.confidence for step in self.current_session.cognitive_steps]
        mean = sum(confidences) / len(confidences)
        variance = sum((c - mean) ** 2 for c in confidences) / len(confidences)
        
        return variance
    
    def _analyze_confidence_trend(self, confidences: List[float]) -> str:
        """Analyze trend in confidence levels"""
        if len(confidences) < 2:
            return "stable"
        
        # Simple trend analysis
        first_half = confidences[:len(confidences)//2]
        second_half = confidences[len(confidences)//2:]
        
        first_avg = sum(first_half) / len(first_half)
        second_avg = sum(second_half) / len(second_half)
        
        if second_avg > first_avg + 0.1:
            return "increasing"
        elif second_avg < first_avg - 0.1:
            return "decreasing"
        else:
            return "stable"
    
    async def _monitor_realtime(self) -> None:
        """Monitor cognitive processes in real-time"""
        while self.current_session and self.cognitive_state != CognitiveState.IDLE:
            await asyncio.sleep(0.5)
            
            # Detect patterns in current session
            if len(self.current_session.cognitive_steps) > 3:
                patterns = await self._detect_patterns()
                self.current_session.patterns_detected.extend(patterns)
    
    async def _notify_subscribers(self, step: CognitiveStep) -> None:
        """Notify real-time subscribers of new thought step"""
        for callback in self._real_time_subscribers:
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(step)
                else:
                    callback(step)
            except Exception as e:
                logger.error(f"Error in real-time subscriber: {e}")
    
    async def _detect_patterns(self) -> List[str]:
        """Detect patterns in current thinking process"""
        patterns = []
        
        if not self.current_session:
            return patterns
        
        steps = self.current_session.cognitive_steps
        if len(steps) < 3:
            return patterns
        
        # Check for repetitive reasoning patterns
        recent_types = [step.step_type for step in steps[-3:]]
        if len(set(recent_types)) == 1:
            patterns.append(f"repetitive_{recent_types[0]}")
        
        # Check for confidence trends
        recent_confidence = [step.confidence for step in steps[-3:]]
        if all(recent_confidence[i] > recent_confidence[i+1] for i in range(len(recent_confidence)-1)):
            patterns.append("declining_confidence")
        elif all(recent_confidence[i] < recent_confidence[i+1] for i in range(len(recent_confidence)-1)):
            patterns.append("increasing_confidence")
        
        return patterns 