from dotenv import load_dotenv
from langchain_groq.chat_models import ChatGroq # Chat Model
import time

load_dotenv()  # Carrega as variáveis do .env

# cria o modelo
llm = ChatGroq(model='llama-3.1-8b-instant')

while True:
    prompt = input("Digite seu prompt (ou 'sair' para encerrar): ")

    if prompt.lower() == 'sair':
        break
    else: 
        def main():
            for chunk in llm.stream(prompt):
                print(chunk.content, end='', flush=True)
                time.sleep(0.1)
            print()
        main()
