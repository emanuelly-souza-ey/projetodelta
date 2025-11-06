# Projeto Delta

Este é um projeto que fornece uma API e interface web para gerenciamento e monitoramento de projetos DevOps, integrando-se com serviços Azure DevOps e Microsoft Teams.

## Descrição

O Projeto Delta é uma aplicação web construída com FastAPI e Streamlit que permite:
- Monitoramento de horas trabalhadas em projetos (semanal/mensal)
- Acompanhamento do status de projetos
- Visualização de tarefas atrasadas
- Gerenciamento de tarefas diárias
- Integração com Azure DevOps para gestão de projetos
- Integração com Microsoft Teams para comunicação

## Tecnologias Utilizadas

- Python 3.x
- FastAPI - Framework web assíncrono para APIs
- Streamlit - Framework para interfaces web em Python
- Pydantic - Validação de dados
- Uvicorn - Servidor ASGI para Python
- Requests - Cliente HTTP
- Python-dotenv - Gerenciamento de variáveis de ambiente

## Estrutura do Projeto


## Instalação

1. Clone o repositório:
```bash
git clone https://github.com/emanuelly-souza-ey/projetodelta.git
cd projetodelta
```

2. Crie um ambiente virtual e ative-o:
```bash
python -m venv venv
source venv/bin/activate  # Linux/MacOS
# ou
venv\Scripts\activate     # Windows
```

3. Instale as dependências:
```bash
pip install -r requirements.txt
```

4. Configure as variáveis de ambiente criando um arquivo `.env` na raiz do projeto.

```
AZURE_DEVOPS_URL=
AZURE_DEVOPS_TOKEN=

AZURE_OPENAI_ENDPOINT = 
AZURE_OPENAI_KEY = 
AZURE_DEPLOYMENT_NAME = 
AZURE_OPENAI_API_VERSION = 
```

## Uso

### Executando a API

Para iniciar o servidor da API:
```bash
uvicorn app.main:app --reload
```

A API estará disponível em `http://localhost:8000`

### Executando a Interface Streamlit

Para iniciar a interface web:
```bash
streamlit run streamlit_app.py
```



## Contato


Link do projeto: [https://github.com/emanuelly-souza-ey/projetodelta](https://github.com/emanuelly-souza-ey/projetodelta)
