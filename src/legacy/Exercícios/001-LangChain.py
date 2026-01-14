from dotenv import load_dotenv
from langchain_groq.chat_models import ChatGroq # Chat Model

load_dotenv()  # Carrega as variáveis do .env

# cria o modelo (por padrão usa o GPT-4o-mini)
llm = ChatGroq(model='llama-3.1-8b-instant')

prompt = "Gere ideias para um post de blog sobre os benefícios do sono."
response1 = llm.invoke(prompt)

print(response1.content) # resposta do modelo
# print(response1.response_metadata) # metadados adicionais da resposta

# Meu comentário: aqui eu estou simplesmente definindo o modleo com alguns parametros e enviando um prompt para o modelo que me responde e eu printo na tela
