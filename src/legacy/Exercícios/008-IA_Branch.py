from langchain_core.runnables import RunnableBranch, RunnableLambda
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser  
from pydantic import BaseModel, Field 
from dotenv import load_dotenv

load_dotenv()

llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0.2)

class Rota(BaseModel):  
    escolha: int = Field(description="IA = 1, Humano = 2")  
    pensamento: str = Field(description="Campo para o pensamento que levou a decisão da rota escolhida")  
    confianca: float = Field(description="Nível de confiança na decisão, entre 0 e 1")

def escolha_ia(rota):
    return "Você escolheu ser atendido por uma IA. Um assistente virtual irá ajudá-lo em breve."

def escolha_humano(rota):
    return "Você escolheu ser atendido por um Humano. Um assistente irá ajudá-lo em breve."

def default(rota):
    return "Opa"

prompt_ask = ChatPromptTemplate.from_messages([ 
    ('system', 'Pergunte ao User se ele gostaria de ser atendido por uma IA ou por um humano'),
    ('user', '{input}'),
])

prompt_branch = ChatPromptTemplate.from_messages([ 
    ("system", """Você é um roteador inteligente. Analise a resposta e decida para qual encaminhar.

Opções disponíveis:
- IA: para um atendimento com IA
- Ser Humano: para um atendimento com Humano
{instructions}"""),
    ("user", "{input}")
])

parser = PydanticOutputParser(pydantic_object=Rota)
prompt = prompt_branch.partial(instructions=parser.get_format_instructions())

user_branch = RunnableBranch(
    (lambda x: x.escolha == 1, RunnableLambda(escolha_ia)),
    (lambda x: x.escolha == 2, RunnableLambda(escolha_humano)),
    RunnableLambda(default)
)

chain = prompt_ask | llm
chain2 = prompt | llm | parser | user_branch

input_user = input('digite: ')
response = chain.invoke({'input': input_user})
print(response.content)

input_user2 = input('digite: ')
response = chain2.invoke({'input': input_user2})
print(response)