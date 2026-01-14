from dotenv import load_dotenv  
load_dotenv()  
  
from langchain_core.output_parsers import PydanticOutputParser  
from pydantic import BaseModel, Field 
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq.chat_models import ChatGroq # Chat Modelfrom pydantic import BaseModel, Field  

llm = ChatGroq(model='llama-3.3-70b-versatile')
 
# Criando o template de prompt com mensagens
prompt = ChatPromptTemplate([
    ("system", """Você é um roteador inteligente. Analise a pergunta e decida para qual setor encaminhar.

Setores disponíveis:
- financeiro: questões sobre contas, saldo, pagamentos, investimentos
- tecnico: problemas técnicos, bugs, sistema, aplicativo
- RH: reclamações, elogios, dúvidas gerais sobre serviços
- geral: outros assuntos

{instructions}"""),
    ("user", "{pergunta}")
])

# Definindo a minha estrutura de saída para a LLM 
class Rota(BaseModel):  
    escolha: int = Field(description="Financeiro = 1, Técnico = 2, RH = 3, Geral = 4")  
    pensamento: str = Field(description="Campo para o pensamento que levou a decisão da rota escolhida")  
    confianca: float = Field(description="Nível de confiança na decisão, entre 0 e 1")

# Criando o parser de saída baseado na estrutura definida  
parser = PydanticOutputParser(pydantic_object=Rota) 

# Injeta as instruções do parser no prompt
prompt = prompt.partial(instructions=parser.get_format_instructions())

chain = prompt | llm | parser 

pergunta = "Quando é minhas ferias anuais e como posso agendá-las?"
resultado = chain.invoke({"pergunta": pergunta})

print(f"{type(resultado)}")
print(f"Escolha: {resultado.escolha}")
print(f"Pensamento: {resultado.pensamento}")
print(f"Confiança: {resultado.confianca}")