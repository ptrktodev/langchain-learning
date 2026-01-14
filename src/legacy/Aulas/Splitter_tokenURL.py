import wget 
from langchain_text_splitters import RecursiveCharacterTextSplitter
import tiktoken

filename = 'companyPolicies.txt'
url = 'https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/6JDbUb_L3egv_eOkouY71A.txt'
wget.download(url, out=filename)

with open(filename, 'r', encoding='utf-8') as file:
    text = file.read()

enc = tiktoken.get_encoding("cl100k_base")

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=150, # limite de tokens por chunk
    chunk_overlap=30, # overlap entre chunks
    length_function=lambda x: len(enc.encode(x)) # contar tokens
)

chunks = text_splitter.split_text(text)

print()
print(f"total de chunks criados: {len(chunks)}")


for i, chunk in enumerate(chunks[0:4]): 
    print(f"--- Chunk {i} ---")
    print(chunk)
    print(len(enc.encode(chunk)), "tokens")
    print()
