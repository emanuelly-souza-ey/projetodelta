# Testes de API - Chat Endpoint

Testes completos para o endpoint de chat (`/api/v1/chat`).

## Estrutura de Testes

### 1. **Fluxo de Sucesso** (`test_chat_successful_flow`)
- ✅ Teste do fluxo completo: Router → Handler → Answer Agent
- ✅ Validação da resposta completa
- ✅ Verificação de chamadas a todos os componentes

### 2. **Casos de Uso**
- `test_chat_without_conversation_id` - Chat sem ID de conversa
- `test_chat_with_empty_data` - Handler retorna dados vazios
- `test_chat_context_flow` - Fluxo de contexto conversacional

### 3. **Diferentes Intents** (`test_chat_different_intents`)
- Testes parametrizados para todos os intents:
  - `worked_hours` - Horas trabalhadas
  - `project_progress` - Progresso do projeto
  - `delayed_tasks` - Tarefas atrasadas
  - `project_team` - Equipe do projeto
  - `daily_activities` - Atividades diárias
  - `other` - Consultas genéricas DevOps
  - `default` - Consultas não relacionadas

### 4. **Tratamento de Erros**
- `test_chat_router_failure` - Erro na classificação de intent
- `test_chat_handler_exception` - Exceção no handler
- `test_chat_answer_agent_exception` - Erro na geração de resposta
- `test_chat_propagates_http_exception` - Propagação correta de HTTPException

### 5. **Gestão de Conversas**
- `test_clear_conversation_success` - Limpar conversa com sucesso
- `test_clear_conversation_not_found` - Conversa não encontrada (404)
- `test_list_conversations` - Listar conversas ativas
- `test_list_conversations_empty` - Lista vazia

### 6. **Validação de Modelos Pydantic**
- `test_chat_request_validation` - Validação de ChatRequest
- `test_chat_response_validation` - Validação de ChatResponse

### 7. **Propagação de Session ID**
- `test_session_id_propagation` - Verifica que session_id é propagado para todos os componentes

### 8. **Casos Extremos**
- `test_chat_with_very_long_message` - Mensagens muito longas (10k caracteres)
- `test_chat_with_special_characters` - Caracteres especiais e emojis
- `test_chat_confidence_edge_values` - Valores extremos de confiança (0.0, 1.0)

### 9. **Verificação do Router FastAPI**
- `test_router_includes_endpoints` - Validação de rotas registradas

## Cobertura

**Total: 25 testes** cobrindo:
- ✅ Fluxo de sucesso completo
- ✅ Todos os tipos de intents
- ✅ Tratamento abrangente de erros
- ✅ Gestão de conversas
- ✅ Validação de modelos
- ✅ Casos extremos e especiais
- ✅ Propagação correta de session_id

## Executar Testes

### Todos os testes
```bash
.venv\Scripts\activate
python -m pytest tests/backend/api/test_chat.py -v
```

### Teste específico
```bash
python -m pytest tests/backend/api/test_chat.py::test_chat_successful_flow -v
```

### Com cobertura
```bash
python -m pytest tests/backend/api/test_chat.py --cov=backend.api.v1.endpoints.chat --cov-report=html
```

### Somente testes de tratamento de erros
```bash
python -m pytest tests/backend/api/test_chat.py -k "error" -v
```

### Executar com output detalhado
```bash
python -m pytest tests/backend/api/test_chat.py -vv -s
```

## Mocks Utilizados

### `mock_router_agent`
Simula o RouterAgent para evitar chamadas reais ao Azure OpenAI.

### `mock_answer_agent`
Simula o AnswerAgent para respostas controladas.

### `mock_handler`
Handler assíncrono mock que retorna dados de teste.

### `mock_get_handler`
Factory function mock que retorna o handler.

### `mock_memory`
Simula o sistema de memória conversacional.

## Requisitos

As dependências de teste já estão no `requirements.txt`:
```bash
pytest>=7.0.0
pytest-asyncio>=0.21.0
pytest-mock>=3.10.0
httpx
```

Para instalar:
```bash
.venv\Scripts\activate
pip install -r requirements.txt
```

## Notas Importantes

- ✅ Todos os testes usam mocks para evitar dependências externas
- ✅ Testes assíncronos usam `@pytest.mark.asyncio`
- ✅ Validação exaustiva de parâmetros e respostas
- ✅ Cobertura de casos de sucesso e de erro
- ✅ Sem chamadas reais a APIs externas (Azure OpenAI)
- ✅ Testes rápidos e determinísticos
