from langchain_community.document_loaders import PyPDFLoader

doc = PyPDFLoader('src/Aulas/docs/doc_teste.pdf')
pages = doc.load()

for page in pages:
    print(page.page_content)
    print('---')
    print(page.metadata)
