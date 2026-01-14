from dotenv import load_dotenv
from langchain_groq.chat_models import ChatGroq # Chat Model
import asyncio
import time

load_dotenv()

llm = ChatGroq(model='llama-3.1-8b-instant')
prompt = "Explique a teoria da relatividade de forma simples."

async def main():
     async for chunk in llm.astream(prompt):
        print(chunk.content, end='', flush=True)
        time.sleep(0.1)  # Simula algum processamento adicional

asyncio.run(main())

# Se você estiver esperando dados do modelo (ou de outra fonte externa)
#  e tiver outras tarefas para realizar enquanto espera, o uso de async 
# pode permitir que o programa não bloqueie enquanto aguarda a resposta do model.stream().