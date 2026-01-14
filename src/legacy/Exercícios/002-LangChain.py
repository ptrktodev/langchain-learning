from dotenv import load_dotenv
from langchain_core.prompts import PromptTemplate # criar template com variaveis
from langchain_groq.chat_models import ChatGroq # Chat Model

load_dotenv()  # Carrega as variáveis do .env

llm = ChatGroq(model='llama-3.1-8b-instant')

# padronizar e estruturar prompts com variaveis:
template_tema = PromptTemplate(
    template="Escreva um resumo direto e objetivo sobre o seguinte assunto: {tema}"
)

prompt = template_tema.format(tema="Inteligência Artificial e seu impacto na sociedade moderna.")

response = llm.invoke(prompt)

print(response.content)