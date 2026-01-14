# ==================== IMPORTAÇÕES ====================
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from dotenv import load_dotenv  
from langchain_qdrant import QdrantVectorStore  
from langchain_core.runnables import RunnableBranch, RunnableLambda, RunnablePassthrough
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_community.chat_message_histories import SQLChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.output_parsers import PydanticOutputParser 
from langchain_core.output_parsers import StrOutputParser
from langchain_groq.chat_models import ChatGroq 
from pydantic import BaseModel, Field 
import tiktoken
import os
import wget

# ==================== CONFIGURAÇÕES INICIAIS ====================
load_dotenv()

llm = ChatGroq(model='llama-3.1-8b-instant')
emb_model = OpenAIEmbeddings(model="text-embedding-3-large")

filename = 'companyPolicies.txt'
url = 'https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/6JDbUb_L3egv_eOkouY71A.txt'

# ==================== FUNÇÕES ====================

class Rota(BaseModel):  
    escolha: int = Field(description="Chat Memory = 1, Recuperação = 2")  
    pensamento: str = Field(description="Campo para o pensamento que levou a decisão da rota escolhida")  
    confianca: float = Field(description="Nível de confiança na decisão, entre 0 e 1")

def download_file(url, filename):
    wget.download(url, out=filename)
    with open(filename, 'r', encoding='utf-8') as file:
        text = file.read()
    return text

def split_text(document_input):
    enc = tiktoken.get_encoding("cl100k_base")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=300, # limite de tokens por chunk
        chunk_overlap=50,  # overlap entre chunks
        length_function=lambda x: len(enc.encode(x)) # contar tokens
    )
    chunks = text_splitter.split_text(document_input)
    return chunks

def create_collection(chunks):
    qdrant = QdrantVectorStore.from_texts(
        texts=chunks,
        embedding=emb_model,
        collection_name="policy-teste",
        api_key=os.getenv("QDRANT_API_KEY"),
        url=os.getenv("QDRANT_API_URL"),
        prefer_grpc=True # protocolo de comunicação
    )

def connect_to_collection():
    server = QdrantVectorStore.from_existing_collection(
        collection_name="policy-teste",
        api_key=os.getenv("QDRANT_API_KEY"),
        url=os.getenv("QDRANT_API_URL"),
        embedding=emb_model,
    )
    return server

def get_session_history(session_id: int):
    """ 
    Retorna o objeto de histórico de chat para uma sessão específica.
    Args:
        session_id: Identificador único da sessão de conversa
        
    Returns:
        SQLChatMessageHistory: Objeto que gerencia o histórico no SQLite
    """ 
    # Cria/conecta ao banco SQLite e retorna o histórico da sessão
    return SQLChatMessageHistory(
        session_id, 
        connection='sqlite:///chat_memory.db'
    )

def default(rota):
    return "Putz, não consegui saber o que você precisa."

def memory(rota):
    return "Opa, memory"

# ==================== PROMPT ====================

prompt_branch = ChatPromptTemplate.from_messages([ 
        ("system", """Você é um roteador inteligente. Analise a pergunta do usuário e decida para qual rota encaminhar.

    Opções disponíveis:
    - Chat Memory (escolha = 1): para perguntas sobre conversas anteriores, histórico ou contexto de diálogos passados
    - Recuperação (escolha = 2): para perguntas sobre políticas corporativas, código de conduta, documentos ou conteúdo textual específico

    CRÍTICO: Você DEVE responder APENAS com JSON válido seguindo exatamente o formato especificado abaixo. 
    NÃO inclua texto explicativo antes ou depois do JSON.

    {instructions}"""),
        ("user", "Pergunta do usuário: {input}")
])

parser = PydanticOutputParser(pydantic_object=Rota) 
prompt_branch = prompt_branch.partial(instructions=parser.get_format_instructions())

prompt_retriever = ChatPromptTemplate([
    ("system", """
    Você é um assistente especializado em políticas corporativas da empresa.
    Responda SEMPRE em português brasileiro, com linguagem formal, clara e objetiva.
    Mesmo que a pergunta do usuário esteja em inglês ou em qualquer outro idioma,
    sempre responda em português.
    Não traduza a pergunta para o usuário, apenas responda diretamente em PT-BR.

    Utilize o seguinte Contexto para responder a pergunta do usuário: {context}"""),
    ("user", "{question}")
])

# ==================== EXECUÇÃO (descomente as linhas conforme necessário) ====================

# text_str = download_file(url, filename)
# chunks = split_text(text_str)
# create_collection(chunks)

# Teste de consulta
input_user = 'politicas de recrutamento'

chain_main = (
    prompt_branch 
    | llm 
    | parser 
    | RunnableLambda(lambda x: x.model_dump())
    | RunnablePassthrough.assign(
        resultado=RunnableBranch(
            (lambda x: x["escolha"] == 1, 
             RunnableLambda(lambda x: memory(x))),
            (lambda x: x["escolha"] == 2,  
                RunnableLambda(lambda x: {
                    "question": input_user,
                    "context": "\n\n".join(doc.page_content for doc in connect_to_collection().similarity_search(input_user, k=4))
                }) | prompt_retriever | llm | StrOutputParser()),
            RunnableLambda(lambda x: default(x))
        )
    )
)

response = chain_main.invoke({'input': input_user})

print(response['escolha'])
print('----' * 10)
print(response['pensamento'])
print('----' * 10)
print(response['confianca'])
print('----' * 10)
print(response['resultado'])