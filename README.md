# 🤖 Agil.IA | DELTA

> *Um assistente inteligente que revoluciona a gestão ágil de projetos*

**Agil.IA** é um chat conversacional inteligente conectado ao Azure DevOps, criado para apoiar PMOs na gestão ágil de projetos. Através de processamento de linguagem natural, transformamos consultas complexas em respostas instantâneas, democratizando o acesso à informação e economizando tempo valioso da equipe.

## 💡 O Problema

Tradicionalmente, consultar dados no Azure DevOps exige:
- ⏱️ Navegação manual e complexa pela plataforma
- 🔍 Criação de queries e filtros elaborados
- 📊 Dificuldade em obter visão consolidada de projetos
- ⚠️ Alto risco de erros manuais

**Uma consulta média leva 15 minutos para ser realizada.**

## ✨ Nossa Solução

E se pudéssemos simplesmente **perguntar** ao sistema o que precisamos saber? 

O Agil.IA permite que você faça perguntas em linguagem natural e receba respostas instantâneas com dados reais do Azure DevOps:

- *"Quantos dias faltam para finalizar o projeto?"*
- *"Quantas tarefas estão atrasadas?"*
- *"Quem está alocado no projeto?"*

**15+ prompts já implementados** e prontos para uso!

## 📈 Impacto e Resultados

| Métrica | Resultado | Economia |
|---------|-----------|----------|
| **Tempo de Aprendizado** | Não há | **100% de redução** |
| | | *(interface familiar de chat)* |
| **Tempo de Consulta** | 1 minuto | **94% de redução** |
| | | *(antes: 15 min/consulta)* |
| **Economia Operacional** | R$ 33k/projeto | Cálculos impossíveis |
| | | via consultas tradicionais |

## 🎯 Benefícios

- ⚡ **Economia de tempo** - Respostas em segundos
- ✅ **Redução de erros** - Eliminação de consultas manuais
- 🎯 **Visão estratégica** - Insights rápidos e consolidados
- 🌐 **Acesso democratizado** - Informação para todos os níveis da equipe

## 🏗️ Arquitetura e Tecnologias

### Backend
- **Python 3.x** - Linguagem principal
- **FastAPI** - Framework web assíncrono de alta performance
- **Azure OpenAI** - Processamento de linguagem natural
- **Azure DevOps API** - Integração com dados de projetos
- **Pydantic** - Validação de dados
- **Uvicorn** - Servidor ASGI

### Frontend
- **React 19.x** - Biblioteca UI moderna
- **TypeScript** - Tipagem estática
- **Vite** - Build tool e dev server ultra-rápido
- **Styled Components** - Estilização dinâmica
- **React Icons** - Iconografia

### Integrações
- 🔷 **Azure DevOps** - Gestão de projetos e tasks
- 💬 **Microsoft Teams** - Comunicação (planejado)
- 🤖 **Azure OpenAI** - Inteligência artificial


## 🚀 Como Começar

### Pré-requisitos

- Python 3.x instalado
- Node.js e npm instalados
- Conta Azure DevOps com token de acesso
- Acesso ao Azure OpenAI

### 1️⃣ Instalação do Backend

Clone o repositório e configure o ambiente:

```bash
# Clone o projeto
git clone https://github.com/emanuelly-souza-ey/projetodelta.git
cd projetodelta

# Crie e ative o ambiente virtual
python -m venv .venv
.\.venv\Scripts\activate  # Windows

# Instale as dependências
pip install -r requirements.txt
```

Configure as variáveis de ambiente criando um arquivo `.env` na raiz:

```env
# Azure DevOps
AZURE_DEVOPS_URL=sua-url-aqui
AZURE_DEVOPS_TOKEN=seu-token-aqui

# Azure OpenAI
AZURE_OPENAI_ENDPOINT=seu-endpoint-aqui
AZURE_OPENAI_KEY=sua-key-aqui
AZURE_DEPLOYMENT_NAME=seu-deployment-aqui
AZURE_OPENAI_API_VERSION=versao-api-aqui
```

### 2️⃣ Instalação do Frontend

```bash
# Navegue até a pasta do frontend
cd frontend\my-app

# Instale as dependências
npm install
```

## ▶️ Executando o Projeto

### Backend (API)

```bash
# Na raiz do projeto
.\.venv\Scripts\activate
uvicorn backend.main:app --reload
```

✅ API disponível em: `http://localhost:8000`  
📚 Documentação interativa: `http://localhost:8000/docs`

### Frontend (Aplicação: React + Vite)

```bash
# Na pasta frontend/my-app
cd frontend\my-app
npm run dev
```

✅ Aplicação disponível em: `http://localhost:5173`

## 💬 Exemplos de Uso

Basta conversar com o Agil.IA como você faria com um assistente:

```
👤 Você: "Oi! Tem alguma tarefa atrasada no meu projeto?"
🤖 Agil.IA: "Sim, encontrei 8 tarefas com atraso. Alice tem 5 tarefas atrasadas 
            e Bob tem 3. A maioria está bloqueada aguardando aprovação. 
            As principais são: Implementação da API, Revisão de código 
            e Documentação técnica."

👤 Você: "Quem tá mais sobrecarregado agora?"
🤖 Agil.IA: "Alice está com 15 tarefas atribuídas, seguida por Bob com 8 tarefas 
            e Charlie com 5 tarefas."

👤 Você: "Quantas tasks tão bloqueadas?"
🤖 Agil.IA: "Há 6 tarefas bloqueadas no momento. Alice possui 3 delas, 
            Bob tem 2 e Charlie 1."

👤 Você: "Me dá um resumo dos projetos"
🤖 Agil.IA: "Claro! Temos 3 projetos ativos em desenvolvimento, 2 projetos 
            concluídos este mês e 4 projetos no backlog."
```

### 📋 Consultas Disponíveis

O Agil.IA já possui **15+ prompts implementados**, incluindo:

| Categoria | Exemplos |
|-----------|----------|
| **📊 Status de Projetos** | Projetos ativos, concluídos, em backlog |
| **⚠️ Gestão de Riscos** | Tasks atrasadas, bloqueadas, em risco |
| **👥 Alocação de Equipe** | Ranking de responsáveis, distribuição de tarefas |
| **📈 Métricas** | Distribuição de estados, conclusão de tarefas |
| **🔍 Análises** | Tasks ativas, fechadas, por responsável |

## 👥 Equipe

| Nome | Papel |
|------|-------|
| **Thamires Azeredo** | PMO \| Agile Master |
| **Davi Tavares** | PMO \| Métricas |
| **Emanuelly Souza** | Engenheira de Dados IA |
| **Maria Caceres** | Engenheira de IA |

## 🔗 Links

- 📂 [Repositório do Projeto](https://github.com/emanuelly-souza-ey/projetodelta)
- 📖 [Documentação da API](http://localhost:8000/docs) *(após iniciar o backend)*

---

<div align="center">

**Créditos ❤️**
Desenvolvido por Maria Caceres e Emanuelly Souza
Apoio PMO | Thamires Azeredo e Davi Tavares

*Transformando a gestão ágil através da inteligência artificial*

</div>
