import os
from langchain_openai import AzureChatOpenAI
from dotenv import load_dotenv
import json
from langchain.prompts import ChatPromptTemplate
from langchain.chains import LLMChain

class Selection:
    def __init__(self, name, id):
        self.name = name
        self.id = id

PromptsTemplates = {
    "get_selection": ChatPromptTemplate.from_messages([
            (
            "system",
            """
            Você é um assistente de inteligência artificial que classifica consultas de usuários em uma das opções predefinidas. Quando um usuário enviar uma mensagem, sua tarefa é determinar qual das opções melhor descreve sua consulta e retornar um arquivo JSON com a seguinte estrutura:
            {{
            "opcao": "Nome da opção",
            "id": "ID da opção"
            }}
            Instruções:
            Analise a consulta do usuário.
            Compare o significado com as opções disponíveis.
            Selecione a opção que melhor representa a intenção do usuário.
            Retorne apenas o JSON com a opção selecionada e seu ID, sem texto adicional.
            As opções disponíveis são:
            {options_text}
            Se a consulta do usuário não corresponder claramente a nenhuma opção, escolha a opcão mais proxima. Em caso de dúvida, priorize a opção mais relevante de acordo com o contexto.
            """,
            ),
            ("human", "{sentence}"),
        ])

}


class Interfaz:
    def __init__(self):
        load_dotenv()
        self.api_base = os.getenv("EYQ_INCUBATOR_ENDPOINT")
        self.api_key = os.getenv("EYQ_INCUBATOR_KEY")
        self.options_principal =  [
            Selection("Horas trabalhadas e previstas", "1"),
            Selection("Progresso geral do projeto", "2"),
            Selection("Tarefas atrasadas", "3"),
            Selection("Equipe do projeto", "4"),
            Selection("Atividades diárias", "5"),
            Selection("Outros", "6"),
        ]

        if not self.api_base or not self.api_key:
            raise ValueError("As variáveis de ambiente EYQ_INCUBATOR_ENDPOINT e EYQ_INCUBATOR_KEY devem ser definidas.")

        self.llm = AzureChatOpenAI(
            azure_endpoint=self.api_base,
            api_key=self.api_key,
            azure_deployment="gpt-4o",
            api_version="2024-06-01",
            temperature=0.7,
            max_tokens=800
            )


    async def get_selection(self, sentence: str, options: list[Selection]=None) -> str:
        options = options or self.options_principal
        options_text = "\n".join([f"{opt.name} : {opt.id}" for opt in options])

        prompt_template = PromptsTemplates["get_selection"]

        chain = LLMChain(llm=self.llm, prompt=prompt_template)
        ai_msg = chain.run({"sentence": sentence,"options_text": options_text})

        try:
            response = json.loads(ai_msg)
            if "opcao" in response and "id" in response:
                response["id"] = int(response["id"])
                return response
        except (json.JSONDecodeError, TypeError):
            # Attempt to extract JSON from a response that might contain additional text
            start_idx = ai_msg.find("{")
            end_idx = ai_msg.rfind("}")
            if start_idx != -1 and end_idx != -1:
                try:
                    response = json.loads(ai_msg[start_idx:end_idx + 1])
                    if "opcao" in response and "id" in response:
                        response["id"] = int(response["id"])
                        return response
                except json.JSONDecodeError:
                    pass

        return { "id" : self.options_principal[-1].id, "name":self.options_principal[-1].name}

# Ejemplo de uso
import asyncio

async def main():
    interfaz = Interfaz()
    result = await interfaz.get_selection("Qual e o equipe do projeto?")
    print(result)

if __name__ == "__main__":
    asyncio.run(main())

