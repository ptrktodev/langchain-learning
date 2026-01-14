from langchain_community.document_loaders import TextLoader

doc = TextLoader('src/Aulas/docs/exemplo_arquivo.txt')
pages = doc.load()

for page in pages:
    print(page.page_content)
    print('---')
    print(page.metadata)
