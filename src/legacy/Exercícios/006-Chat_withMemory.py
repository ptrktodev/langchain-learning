from dotenv import load_dotenv
from langchain_groq.chat_models import ChatGroq # Chat Model
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
import time

load_dotenv()  # Carrega as variáveis do .env

# cria o modelo
llm = ChatGroq( model='llama-3.3-70b-versatile')

# criando um pequeno historico de mensagens
message = [SystemMessage(
    content="Você é um assistente útil, seja objetivo e direto.",
)]
print(message)

while True:
    prompt = input("Digite seu prompt (ou 'sair' para encerrar): ")

    if prompt.lower() == 'sair':
        break
    else: 
        message.append(HumanMessage(content=prompt))
        response = ""

        for chunk in llm.stream(message):
            print(chunk.content, end='', flush=True)
            response += chunk.content
            time.sleep(0.07)
        message.append(AIMessage(content=response))
        print()
        
