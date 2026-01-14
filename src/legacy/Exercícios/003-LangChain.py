from dotenv import load_dotenv
from langchain_core.prompts import PromptTemplate # criar template com variaveis
from langchain_groq.chat_models import ChatGroq # Chat Model

load_dotenv()  # Carrega as variáveis do .env

llm = ChatGroq(model='llama-3.1-8b-instant')

# padronizar e estruturar prompts com variaveis:
template_tema = PromptTemplate(
    input_variabes=["tema"],
    template="Explique de maneira lúdica para qualquer um entender: {tema}"
)

assuntos = ["Por que as galinhas nao voam sempre?", "por que o nosso sistema solar tem apenas um sol?"]

prompts = [template_tema.format(tema=a) for a in assuntos]

response = [llm.invoke(a) for a in prompts]

# combina os elementos das duas listas em pares, usando a mesma posição de cada lista:
for a, r in zip(assuntos, response):
    print(f"{a}: {r.content}")
    print(f"{'-'*40}")