# Tests for Backend Agents

This directory contains comprehensive tests for all backend agents.

## Structure

```
tests/backend/agents/
├── __init__.py
└── test_router_agent.py    # Tests for RouterAgent
```

## Running Tests

### Run all agent tests
```bash
python -m pytest tests/backend/agents/ -v
```

### Run specific test file
```bash
python -m pytest tests/backend/agents/test_router_agent.py -v
```

### Run specific test class
```bash
python -m pytest tests/backend/agents/test_router_agent.py::TestClassifyIntent -v
```

### Run specific test
```bash
python -m pytest tests/backend/agents/test_router_agent.py::TestClassifyIntent::test_classify_intent_success -v
```

### Run with coverage
```bash
python -m pytest tests/backend/agents/ --cov=backend.agents --cov-report=html
```

### Run standalone (alternative)
```bash
python tests/backend/agents/test_router_agent.py
```

## Test Coverage

### RouterAgent Tests (`test_router_agent.py`)

**Initialization Tests:**
- ✅ Initialize without session_id
- ✅ Initialize with session_id and logger
- ✅ Verify shared Azure config singleton

**Intent Classification Tests:**
- ✅ Successful intent classification
- ✅ Prompt includes registered categories
- ✅ Sets original_query correctly
- ✅ Logging during classification

**Routing Tests:**
- ✅ Route to registered intent handlers
- ✅ Fallback to default_agent for unregistered intents
- ✅ Uses IntentRegistry.get() correctly
- ✅ Logs warnings on fallback

**Process Query Tests:**
- ✅ Successful end-to-end query processing
- ✅ Error handling for classification failures
- ✅ Error handling for routing failures
- ✅ Multiple intent types

**Integration Tests:**
- ✅ Routes to all registered handlers
- ✅ Verifies intent metadata structure

**Edge Cases:**
- ✅ Empty query
- ✅ Very long query
- ✅ Special characters in query
- ✅ Low confidence intents

## Dependencies

Required packages (in `requirements.txt`):
```
pytest>=7.0.0
pytest-asyncio>=0.21.0
pytest-mock>=3.10.0
```

## Mock Strategy

Tests use `unittest.mock` to:
- **Mock Azure OpenAI API** - Avoid real API calls and costs
- **Mock logging** - Test logging calls without writing to files
- **Mock IntentRegistry** - Test routing logic in isolation

## Best Practices

1. **Always mock external dependencies** (Azure API, file I/O, etc.)
2. **Test both success and failure paths**
3. **Verify method calls and arguments** with mocks
4. **Test edge cases** (empty strings, special chars, etc.)
5. **Use fixtures** for common setup
6. **Organize tests** by functionality (classes)

## Adding New Tests

When adding tests for new agents:

1. Create `test_<agent_name>.py` in this directory
2. Follow the structure from `test_router_agent.py`
3. Include these sections:
   - Fixtures
   - Initialization tests
   - Method-specific tests
   - Integration tests
   - Edge cases
4. Update this README with coverage info
