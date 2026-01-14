from dotenv import load_dotenv
from langchain_core.output_parsers import StrOutputParser
from langchain_groq.chat_models import ChatGroq # Chat Model

load_dotenv()  # Carrega as variáveis do .env

# cria o modelo (por padrão usa o GPT-4o-mini)
llm = ChatGroq(model='llama-3.1-8b-instant')

analisadro_output = StrOutputParser() # Analisador de saída para strings simples

prompt = "Gere ideias para um post de blog sobre os benefícios do sono."

chain = llm | analisadro_output # Output em String

res = chain.invoke(prompt)

print(res)