# Development Guide

This document provides detailed information for developers working on the Metacognitive Engine project.

## 🏗️ Development Setup

### Local Environment

1. **Clone and setup**
   ```bash
   git clone https://github.com/netsky-devel/Metacognitive-Engine-AI-Consciousness-Simulation.git
   cd Metacognitive-Engine-AI-Consciousness-Simulation
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Install development tools**
   ```bash
   pip install black mypy flake8 bandit pre-commit
   pre-commit install
   ```

3. **Environment configuration**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

### IDE Configuration

#### VSCode

Create `.vscode/settings.json`:
```json
{
    "python.defaultInterpreterPath": "./venv/bin/python",
    "python.testing.pytestEnabled": true,
    "python.testing.pytestArgs": ["tests"],
    "python.linting.enabled": true,
    "python.linting.flake8Enabled": true,
    "python.formatting.provider": "black",
    "editor.formatOnSave": true
}
```

#### PyCharm

- Set interpreter to `./venv/bin/python`
- Enable pytest as test runner
- Configure Black as code formatter
- Enable type checking with mypy

## 🧪 Testing Strategy

### Test Structure

```
tests/
├── test_comprehensive.py      # All component tests
├── test_mcp_server.py        # API endpoint tests
├── test_long_term_memory.py  # Legacy memory tests
└── conftest.py              # Shared fixtures
```

### Test Categories

- **Unit Tests**: Test individual components in isolation
- **Integration Tests**: Test component interactions
- **API Tests**: Test REST endpoints
- **End-to-End Tests**: Full system workflow tests

### Running Tests

```bash
# All tests
pytest

# With coverage
pytest --cov=src --cov-report=html --cov-report=term

# Specific categories
pytest -m unit
pytest -m integration
pytest -m "not slow"

# Specific files
pytest tests/test_comprehensive.py
pytest tests/test_mcp_server.py -v

# With debugging
pytest -s --pdb
```

### Writing Tests

#### Test Naming Convention
- Test files: `test_*.py`
- Test classes: `Test*`
- Test methods: `test_*`

#### Example Test Structure
```python
class TestComponentName:
    """Test the ComponentName class"""
    
    @pytest.fixture
    def component(self):
        """Create test component instance"""
        return ComponentName()
    
    def test_basic_functionality(self, component):
        """Test basic functionality works"""
        result = component.do_something()
        assert result is not None
    
    def test_error_handling(self, component):
        """Test error handling"""
        with pytest.raises(ValueError):
            component.invalid_operation()
```

#### Mocking Guidelines
- Mock external services (Gemini API, ChromaDB)
- Use temporary databases for persistence tests
- Mock time-dependent functions for deterministic tests

## 🏛️ Architecture Principles

### Global Workspace Theory Implementation

The system implements Global Workspace Theory through:

1. **Central Blackboard** (WorkingMemory)
   - Shared state across all processors
   - Coordinates information flow
   - Maintains current cognitive context

2. **Specialized Processors**
   - Each handles specific cognitive function
   - Operates on shared working memory
   - Can trigger other processors

3. **Attention Mechanism**
   - AssociativeEngine focuses on relevant memories
   - IntrospectionEngine analyzes current context
   - ResponseGenerator synthesizes final output

### Design Patterns

#### Repository Pattern
```python
class LongTermMemory:
    """Abstracts memory storage implementation"""
    def add_memory(self, entry: Entry) -> None: ...
    def query(self, text: str, n_results: int) -> List[Entry]: ...
    def search_memories(self, text: str) -> List[Dict]: ...
```

#### Strategy Pattern
```python
class CognitiveProcessor:
    """Base class for cognitive processing strategies"""
    def process(self, working_memory: WorkingMemory) -> bool: ...
```

#### Observer Pattern
```python
class WorkingMemory:
    """Notifies processors of state changes"""
    def add_insight(self, insight: Entry) -> None:
        self.generated_insights.append(insight)
        # Notify observers of new insight
```

## 🔧 Code Quality Standards

### Code Formatting

Use Black for consistent formatting:
```bash
black src/ tests/
```

Configuration in `pyproject.toml`:
```toml
[tool.black]
line-length = 88
target-version = ['py39']
include = '\.pyi?$'
```

### Type Checking

Use mypy for static type analysis:
```bash
mypy src/
```

Configuration in `mypy.ini`:
```ini
[mypy]
python_version = 3.9
warn_return_any = True
warn_unused_configs = True
disallow_untyped_defs = True
```

### Linting

Use flake8 for code quality:
```bash
flake8 src/ tests/
```

Configuration in `.flake8`:
```ini
[flake8]
max-line-length = 88
extend-ignore = E203, W503
exclude = .git,__pycache__,build,dist
```

### Security

Use bandit for security analysis:
```bash
bandit -r src/
```

## 🚀 Deployment

### Docker Setup

Create `Dockerfile`:
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY src/ src/
COPY data/ data/

EXPOSE 8000
CMD ["uvicorn", "src.mcp_server:app", "--host", "0.0.0.0", "--port", "8000"]
```

Create `docker-compose.yml`:
```yaml
version: '3.8'
services:
  metacognitive-engine:
    build: .
    ports:
      - "8000:8000"
    environment:
      - GEMINI_API_KEY=${GEMINI_API_KEY}
    volumes:
      - ./data:/app/data
```

### Production Considerations

1. **Environment Variables**
   - Use environment-specific `.env` files
   - Never commit API keys to version control
   - Use secrets management in production

2. **Database Persistence**
   - Mount data volume for ChromaDB persistence
   - Consider backup strategies for vector database
   - Monitor database size and performance

3. **Monitoring**
   - Add logging throughout the system
   - Monitor API response times
   - Track memory usage and vector search performance

## 📊 Performance Optimization

### Vector Search Optimization

1. **Distance Thresholds**
   ```python
   # Current optimized values
   MAX_DISTANCE = 8.0  # Balance precision/recall
   N_RESULTS = 5       # Optimal result count
   ```

2. **Batch Processing**
   ```python
   # Process multiple memories together
   def add_memories_batch(self, entries: List[Entry]) -> None:
       # Batch vector generation and insertion
   ```

3. **Caching Strategies**
   ```python
   # Cache frequently accessed memories
   @lru_cache(maxsize=100)
   def get_cached_associations(self, query_hash: str) -> List[Dict]:
       # Return cached associations
   ```

### Memory Management

1. **Working Memory Cleanup**
   ```python
   def clear_working_memory(self) -> None:
       """Clear transient state between requests"""
       self.structured_input = None
       self.retrieved_memories.clear()
       self.generated_insights.clear()
   ```

2. **Vector Model Optimization**
   ```python
   # Use smaller model for faster processing if needed
   MODEL_NAME = "paraphrase-multilingual-mpnet-base-v2"  # 768 dims
   # Alternative: "all-MiniLM-L6-v2"  # 384 dims, faster
   ```

## 🔒 Security Considerations

### API Security

1. **Input Validation**
   ```python
   def validate_input(content: str) -> str:
       if len(content) > MAX_CONTENT_LENGTH:
           raise ValueError("Content too long")
       return content.strip()
   ```

2. **Rate Limiting**
   ```python
   from slowapi import Limiter
   limiter = Limiter(key_func=get_remote_address)
   
   @app.post("/process")
   @limiter.limit("10/minute")
   async def process_thought(request: Request, data: ProcessRequest):
       # Process with rate limiting
   ```

3. **Error Handling**
   ```python
   # Never expose internal errors
   try:
       result = process_dangerous_operation()
   except Exception as e:
       logger.error(f"Internal error: {e}")
       raise HTTPException(status_code=500, detail="Internal server error")
   ```

### Data Privacy

1. **Memory Encryption**
   - Consider encrypting sensitive memories at rest
   - Implement secure deletion of memories
   - Audit memory access patterns

2. **API Key Security**
   - Rotate API keys regularly
   - Use least-privilege access
   - Monitor API usage

## 🐛 Debugging

### Logging Configuration

```python
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Component-specific loggers
ltm_logger = logging.getLogger('long_term_memory')
engine_logger = logging.getLogger('metacognitive_engine')
```

### Debug Mode

Enable debug output:
```python
# In development
DEBUG = True

if DEBUG:
    print(f"Working memory state: {working_memory.get_context_summary()}")
    print(f"Retrieved {len(associations)} associations")
```

### Common Issues

1. **Vector Search Returns No Results**
   - Check distance threshold settings
   - Verify model compatibility
   - Ensure database has data

2. **AI Analysis Fails**
   - Verify API key configuration
   - Check network connectivity
   - Implement fallback mechanisms

3. **Memory Performance Issues**
   - Monitor vector database size
   - Optimize batch operations
   - Consider memory cleanup strategies

## 📈 Monitoring and Metrics

### Performance Metrics

Track key performance indicators:
```python
import time
from functools import wraps

def measure_time(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        duration = time.time() - start
        logger.info(f"{func.__name__} took {duration:.3f}s")
        return result
    return wrapper

@measure_time
def process_thought(self, text: str) -> str:
    # Measured processing
```

### Health Checks

```python
@app.get("/health")
async def health_check():
    """System health check endpoint"""
    return {
        "status": "healthy",
        "memory_count": engine.ltm.get_memory_count(),
        "last_processing": engine.last_processing_time,
        "version": "1.0.0"
    }
```

## 🔄 Continuous Integration

### GitHub Actions

Create `.github/workflows/test.yml`:
```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v2
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: 3.9
        
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        
    - name: Run tests
      run: |
        pytest --cov=src --cov-report=xml
        
    - name: Upload coverage
      uses: codecov/codecov-action@v1
```

### Pre-commit Hooks

Configure `.pre-commit-config.yaml`:
```yaml
repos:
-   repo: https://github.com/psf/black
    rev: 22.3.0
    hooks:
    -   id: black
-   repo: https://github.com/pycqa/flake8
    rev: 4.0.1
    hooks:
    -   id: flake8
-   repo: https://github.com/pre-commit/mirrors-mypy
    rev: v0.950
    hooks:
    -   id: mypy
```

## 📚 Additional Resources

- [Global Workspace Theory](https://en.wikipedia.org/wiki/Global_workspace_theory)
- [ChromaDB Documentation](https://docs.trychroma.com/)
- [Sentence Transformers](https://www.sbert.net/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Google Gemini API](https://developers.generativeai.google/) 