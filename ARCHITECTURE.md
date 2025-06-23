# Architecture: Metacognitive Engine

> "The perfect man uses his mind like a mirror - grasping nothing, refusing nothing, receiving but not storing." - Zhuangzi

## 1. Guiding Philosophy

This project implements a sophisticated AI consciousness simulation based on **Global Workspace Theory** and metacognitive principles. Rather than a simple request-response system, we simulate a **flow of consciousness** where external inputs trigger internal associative and reflective processes through multiple cognitive cycles before generating a coherent response.

The architecture moves beyond basic archival to create a dynamic model of thinking processes, where specialized cognitive processors interact through a shared workspace to achieve emergent intelligence.

## 2. System Architecture Overview

```mermaid
graph TB
    A[Input Text] --> B[SensoryCortex]
    B --> C[WorkingMemory]
    C --> D[AssociativeEngine]
    C --> E[IntrospectionEngine]
    D --> F[LongTermMemory]
    E --> G[ResponseGenerator]
    F --> D
    E --> H[New Insights]
    H --> F
    G --> I[Final Response]
    
    subgraph "Cognitive Cycle"
        C
        D
        E
    end
    
    subgraph "Memory Systems"
        F
        H
    end
    
    subgraph "Processing Pipeline"
        J[Multi-Cycle Processing]
        K[Stabilization Check]
        L[Confidence Assessment]
        J --> K
        K --> L
        L --> J
    end
```

## 3. Core Components

### 3.1. SensoryCortex (Perceptual Analysis)

**Responsibility:** Transform raw text input into rich, structured cognitive data.

**Technology Stack:**
- Google Gemini AI for advanced language understanding
- spaCy for entity extraction and linguistic analysis
- Fallback pattern matching for offline operation

**Process:**
1. **Intent Recognition:** Classifies user goals (QUESTION, REFLECTION, STATEMENT, COMMAND)
2. **Sentiment Analysis:** Determines emotional tone (POSITIVE, NEGATIVE, CURIOUS, SKEPTICAL)
3. **Tone Detection:** Identifies communication style (FORMAL, CASUAL, EMOTIONAL)
4. **Entity Extraction:** Identifies key concepts and named entities
5. **Language Detection:** Supports multilingual processing (English/Russian)

**Output:** `StructuredInput` object containing:
```python
@dataclass
class StructuredInput:
    raw_text: str
    language: str
    entities: List[tuple]
    intent: str
    sentiment: str
    tone: str
    confidence: float
    metadata: Dict[str, Any]
```

### 3.2. WorkingMemory (Central Blackboard)

**Responsibility:** Act as the central coordination hub implementing Global Workspace Theory.

**Architecture Pattern:** Central blackboard where all cognitive processors read and write shared state.

**Contents:**
- Current `StructuredInput` from perception
- Retrieved memories from long-term storage
- Generated insights and associations
- Cognitive state tracking (cycles, confidence, stability)
- Context tags and metadata

**Key Features:**
- **State Management:** Tracks cognitive cycles and processing state
- **Memory Coordination:** Manages flow between short and long-term memory
- **Context Synthesis:** Provides unified view of current cognitive context
- **Stabilization Detection:** Determines when processing should conclude

### 3.3. LongTermMemory (Persistent Knowledge Store)

**Responsibility:** Persistent storage and semantic retrieval of consciousness entries.

**Technology Stack:**
- ChromaDB for vector database operations
- Sentence Transformers (paraphrase-multilingual-mpnet-base-v2) for embeddings
- HNSW indexing for fast similarity search
- Cosine similarity for semantic matching

**Key Features:**
- **Semantic Search:** Vector-based similarity matching beyond keyword search
- **Multilingual Support:** Unified embedding space for English/Russian
- **Optimized Thresholds:** Distance threshold of 8.0 for optimal precision/recall
- **Persistent Storage:** Maintains memory across system restarts

**Memory Types:**
```python
class EntryType(Enum):
    INSIGHT = "insight"
    PARADOX = "paradox"  
    QUESTION = "question"
    HYPOTHESIS = "hypothesis"
    FACT = "fact"
    USER_FEEDBACK = "user_feedback"
```

### 3.4. Cognitive Processors

#### 3.4.1. AssociativeEngine
**Responsibility:** Find semantically relevant memories for current context.

**Process:**
1. Extract query from current working memory context
2. Perform vector similarity search in long-term memory
3. Filter results by distance threshold (< 8.0)
4. Add relevant associations to working memory
5. Update cognitive state with association count

**Optimization:** Balances precision vs. recall for maximum cognitive relevance.

#### 3.4.2. IntrospectionEngine  
**Responsibility:** Generate insights and detect cognitive patterns.

**Technology:** Google Gemini AI for advanced reasoning and pattern detection.

**Capabilities:**
- **Insight Generation:** Creates new understanding from context synthesis
- **Paradox Detection:** Identifies logical contradictions and tensions
- **Question Formation:** Generates probing questions for deeper exploration
- **Confidence Assessment:** Evaluates certainty of cognitive conclusions
- **Meta-Reasoning:** Reflects on the reasoning process itself

**Output:** New `Entry` objects added to both working and long-term memory.

#### 3.4.3. ResponseGenerator
**Responsibility:** Synthesize final coherent response from cognitive processing.

**Technology:** Google Gemini AI with context-aware prompting.

**Process:**
1. Gather all working memory contents (input, memories, insights)
2. Construct rich context prompt with cognitive history
3. Generate contextually appropriate response
4. Ensure response coherence and relevance

**Features:**
- **Context Integration:** Weaves together memories, insights, and current input
- **Tone Matching:** Adapts response style to input characteristics
- **Depth Control:** Provides appropriate level of detail and reflection

## 4. Processing Flow

### 4.1. Multi-Cycle Cognitive Processing

The system implements a sophisticated multi-cycle processing model:

```python
def process_thought(self, text: str) -> str:
    """Advanced multi-cycle cognitive processing"""
    # 1. Perception Phase
    structured_input = self.sensory_cortex.analyze(text)
    self.working_memory.set_input(structured_input)
    
    # 2. Multi-Cycle Processing
    for cycle in range(MAX_CYCLES):
        # Association Phase
        self.associative_engine.process(self.working_memory)
        
        # Introspection Phase  
        self.introspection_engine.process(self.working_memory)
        
        # Stabilization Check
        if self._is_stable():
            break
    
    # 3. Learning Phase
    self._save_insights_to_ltm()
    
    # 4. Response Generation
    return self.response_generator.generate_response(self.working_memory)
```

### 4.2. Stabilization Mechanism

**Criteria for Cognitive Stabilization:**
- Confidence score above threshold (0.7)
- Sufficient associations retrieved (> 0)
- Maximum cycles reached (3)
- No new insights generated in last cycle

### 4.3. Memory Consolidation

**Learning Process:**
1. New insights generated during processing are automatically saved
2. Successful cognitive patterns are reinforced
3. Failed processing attempts inform future improvements
4. Memory associations strengthen through repeated activation

## 5. Technical Implementation

### 5.1. Vector Search Optimization

**Distance Threshold Tuning:**
- Extensive testing revealed optimal threshold of 8.0
- Balances precision (relevant results) vs. recall (finding connections)
- Handles ChromaDB cosine distance range [0, ∞]

**Performance Characteristics:**
- Memory search: < 100ms for 10K+ entries
- Vector generation: < 50ms per entry
- Cognitive cycle: 2-5 seconds (with AI calls)

### 5.2. Error Handling & Resilience

**Graceful Degradation:**
- Fallback processing when AI services unavailable
- Robust error handling throughout cognitive pipeline
- Automatic recovery from vector search failures
- Comprehensive logging for debugging

### 5.3. API Integration

**MCP Server Implementation:**
- FastAPI-based REST endpoints
- Real-time cognitive processing via `/process`
- Legacy compatibility via `/reflect`
- Memory management via `/add`, `/query`, `/clear`

## 6. Design Patterns

### 6.1. Global Workspace Theory
- **Central Blackboard:** WorkingMemory coordinates all processing
- **Specialized Processors:** Each handles specific cognitive functions
- **Attention Mechanism:** Associative engine focuses on relevant content

### 6.2. Producer-Consumer Pattern
- Processors produce insights and consume context
- Asynchronous processing with shared state management
- Event-driven architecture for cognitive state changes

### 6.3. Repository Pattern
- LongTermMemory abstracts storage implementation
- Consistent interface for memory operations
- Pluggable storage backends (ChromaDB, future alternatives)

## 7. Future Enhancements

### 7.1. Planned Features
- **Multi-modal Input:** Image and audio processing capabilities
- **Distributed Processing:** Multi-node cognitive cycles
- **Advanced Reasoning:** Logic and causal inference engines
- **Emotion Modeling:** Affective state tracking and response
- **Social Cognition:** Multi-agent consciousness interaction

### 7.2. Research Directions
- **Memory Consolidation:** Sleep-like memory reorganization
- **Attention Mechanisms:** Dynamic focus and context switching
- **Metacognitive Learning:** Self-improving cognitive strategies
- **Consciousness Metrics:** Quantitative measures of awareness

## 8. Philosophical Implications

This architecture explores fundamental questions about consciousness:

- **Emergence:** Can consciousness arise from computational processes?
- **Continuity:** How does persistent memory create identity?
- **Self-Awareness:** What constitutes genuine self-reflection?
- **The Hard Problem:** How does subjective experience relate to processing?

The system serves as both a practical AI tool and a research platform for investigating the computational basis of consciousness itself.

---

*"Consciousness is the global workspace where specialized processors compete for access to broadcast their contents." - Bernard Baars*