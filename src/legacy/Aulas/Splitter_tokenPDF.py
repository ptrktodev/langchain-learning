from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
import tiktoken

doc = PyPDFLoader('src/Aulas/docs/doc_teste.pdf')
pages = doc.load()

enc = tiktoken.get_encoding("cl100k_base")
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=150, # limite de tokens por chunk
    chunk_overlap=30,  # overlap entre chunks
    length_function=lambda x: len(enc.encode(x)) # contar tokens
)

chunks = text_splitter.split_documents(pages)

print(len(chunks), "chunks criados")
print(type(pages))
