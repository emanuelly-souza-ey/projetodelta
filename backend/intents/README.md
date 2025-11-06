# Chat AI Assistant Architecture

## Overview

This implementation provides a conversational AI assistant that:
1. Classifies user intents
2. Extracts parameters from natural language
3. Queries Azure DevOps API
4. Generates natural language responses in Portuguese

## Architecture

```
User Query → Router Agent → Intent Handler → Answer Agent → Response
              (classify)    (extract+query)   (generate text)
```

## Directory Structure

```
backend/
├── agents/
│   ├── router_agent.py       # Intent classification
│   ├── router_workflow.py    # LangGraph orchestration
│   ├── answer_agent.py       # Natural language response generation
│   └── memory.py             # Conversation context management
│
├── intents/                  # Intent handlers
│   ├── __init__.py           # Handler factory
│   ├── default_handler.py    # Fallback handler
│   │
│   ├── worked_hours/         # ✅ IMPLEMENTED
│   │   ├── models.py         # Data models
│   │   ├── extractor.py      # Parameter extraction with LLM
│   │   ├── service.py        # Azure DevOps API queries
│   │   └── handler.py        # Orchestration
│   │
│   ├── project_progress/     # 🚧 TODO
│   ├── delayed_tasks/        # 🚧 TODO
│   ├── project_team/         # 🚧 TODO
│   └── daily_activities/     # 🚧 TODO
│
└── api/
    └── v1/
        └── endpoints/
            └── chat.py       # Main chat endpoint

```

## API Endpoints

### POST `/api/v1/chat/chat`
Main chat endpoint.

**Request:**
```json
{
  "message": "Cuántas horas trabajó pepito esta semana?",
  "conversation_id": "optional-uuid"
}
```

**Response:**
```json
{
  "message": "Pepito trabalhou 40 horas esta semana.",
  "intent": "worked_hours",
  "confidence": 0.95,
  "data": {
    "person": "Pepito",
    "total_hours": 40.0,
    "start_date": "2025-11-03",
    "end_date": "2025-11-09",
    "breakdown": [
      {
        "date": "2025-11-03",
        "task_title": "Implement feature X",
        "hours": 8.0,
        "state": "Completed"
      }
    ]
  },
  "conversation_id": "uuid-here",
  "error": null
}
```

### DELETE `/api/v1/chat/conversation/{conversation_id}`
Clear conversation history.

### GET `/api/v1/chat/conversations`
List all active conversations.

## Flow Example

1. **User asks:** "Cuántas horas trabajó pepito esta semana?"

2. **Router Agent** classifies as `worked_hours` with high confidence

3. **WorkedHoursExtractor** extracts:
   - person_name: "pepito"
   - start_date: "2025-11-03" (calculated from "esta semana")
   - end_date: "2025-11-09"

4. **WorkedHoursService** queries Azure DevOps API with WIQL

5. **AnswerAgent** generates: "Pepito trabalhou 40 horas esta semana."

6. **Response** includes both the text and structured data for frontend rendering

## Conversation Memory

The system maintains context across queries:

```
User: "Cuántas horas trabajó pepito esta semana?"
→ Response with hours

User: "Y el mes pasado?"
→ System knows to query hours for "pepito" in previous month
```

Memory is stored in-memory by default. For production, use Redis or database.

## Environment Variables

Required in `.env`:

```bash
# Azure OpenAI (for LLM)
AZURE_OPENAI_ENDPOINT=https://your-endpoint.openai.azure.com/
AZURE_OPENAI_KEY=your-key
AZURE_DEPLOYMENT_NAME=gpt-4o
AZURE_OPENAI_API_VERSION=2024-06-01

# Azure DevOps (for data)
AZURE_DEVOPS_URL=https://dev.azure.com/your-org
AZURE_DEVOPS_TOKEN=your-pat-token
AZURE_PROJECT_ID=your-project-id
```

## Implementing New Intents

To add a new intent (e.g., `project_progress`):

1. **Create directory:** `backend/intents/project_progress/`

2. **Create models.py:**
```python
from pydantic import BaseModel

class ProjectProgressQuery(BaseModel):
    project_name: str | None = None
    project_id: str | None = None

class ProjectProgressResponse(BaseModel):
    project_name: str
    completion_percentage: float
    tasks_completed: int
    tasks_total: int
```

3. **Create extractor.py:** Extract parameters using LLM (similar to WorkedHoursExtractor)

4. **Create service.py:** Query Azure DevOps API

5. **Create handler.py:** Orchestrate extractor → service → response

6. **Update __init__.py:** Export the handler

7. **Update backend/intents/__init__.py:** Add to handler factory

## Frontend Integration (Streamlit)

```python
import requests
import streamlit as st

response = requests.post(
    "http://localhost:8000/api/v1/chat/chat",
    json={
        "message": user_input,
        "conversation_id": st.session_state.get("conversation_id")
    }
).json()

# Save conversation ID
st.session_state.conversation_id = response["conversation_id"]

# Show text response
st.write(response["message"])

# Render structured data
if response["intent"] == "worked_hours" and response["data"]:
    import pandas as pd
    df = pd.DataFrame(response["data"]["breakdown"])
    st.dataframe(df)
```

## Testing

Test the chat endpoint:

```bash
curl -X POST "http://localhost:8000/api/v1/chat/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Cuántas horas trabajó pepito esta semana?"
  }'
```

## Notes

- All code is in **English** except responses (Portuguese)
- Router classifies intent only, doesn't extract parameters
- Each intent handler is independent and self-contained
- Memory is simple in-memory storage (consider Redis for production)
- LLM is used twice: classification (router) and parameter extraction (extractors)
- Answer Agent generates final response in Portuguese
