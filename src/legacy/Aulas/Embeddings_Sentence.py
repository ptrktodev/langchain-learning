from langchain_openai import OpenAIEmbeddings
from dotenv import load_dotenv  
load_dotenv()

emb_model = OpenAIEmbeddings(model="text-embedding-ada-002")

documents = [
    "Olá!",
    "Quantos anos você tem?",
    "Qual seu nome?",
    "Meu amigo se chama flávio",
    "Oi!"
]

# gera um vetor representativo de alta dimensão para cada string (sentence embedding)
emb_1 = emb_model.embed_documents(documents) 

print(len(emb_1))        # Deve ser 5, pois temos 5 documentos
print(len(emb_1[0]))     # Cada embedding costuma ter 1536 dimensões, dependendo do modelo

print()

emb_2 = emb_model.embed_query("Olá, me chamo pedrinho") 

print(len(emb_2))          