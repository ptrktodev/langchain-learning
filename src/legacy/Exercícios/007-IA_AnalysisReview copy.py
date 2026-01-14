#  assistente que recebe uma review de um filme e ele tem que analisar prós e contras

from langchain_groq.chat_models import ChatGroq  
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableParallel
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv

load_dotenv()
str_output = StrOutputParser()

llm = ChatGroq(model='llama-3.3-70b-versatile', temperature=0.7)

prompt_pro = ChatPromptTemplate.from_messages([
    ('system', 'Você é um assistente que analisa reviews de filmes, destacando somente os pontos positivos de forma objetiva e direta.'),
    ('user', 'Analise a seguinte review de filme:\n\n{review}'),
])

prompt_contra = ChatPromptTemplate.from_messages([
    ('system', 'Você é um assistente que analisa reviews de filmes, destacando somente os pontos negativos de forma objetiva e direta.'),
    ('user', 'Analise a seguinte review de filme:\n\n{review}'),
])

chain = RunnableParallel({
    'pro': prompt_pro | llm | str_output,
    'con': prompt_contra | llm | str_output
})

input_user = """Crítica de "O Gladiador 2"  
"O Gladiador 2", dirigido por Ridley Scott, chega aos cinemas com a expectativa de reviver a grandiosidade épica de \  
seu antecessor. No entanto, apesar do histórico impressionante de Scott, que inclui clássicos como "Blade Runner" e \  
"Alien", o filme parece tropeçar em sua própria ambição.  
  
Desde o início, o filme tenta inovar ao incorporar cenas animadas e elementos de inteligência artificial, \  
possivelmente como uma homenagem ao primeiro "Gladiador". No entanto, essa escolha estética, embora ousada, \  
não se integra de maneira fluida à narrativa, criando uma desconexão que pode confundir o espectador.  
  
A tentativa de trazer novidade às lutas no Coliseu, com a introdução de navios vikings e tubarões, é um exemplo \  
de como o filme busca surpreender. No entanto, essas cenas acabam por sacrificar a autenticidade histórica em prol \  
do espetáculo, o que pode afastar aqueles que esperavam uma representação mais fiel das arenas romanas. A inclusão \  
de macacos em combate, por sua vez, remete a outras franquias cinematográficas, diluindo ainda mais a originalidade \  
do enredo.  
  
Apesar dessas escolhas questionáveis, é importante reconhecer o esforço de Scott em tentar oferecer algo novo e \  
visualmente impactante. No entanto, a falta de uma pesquisa histórica mais aprofundada se faz sentir, e o filme \  
poderia ter se beneficiado de uma abordagem mais cuidadosa nesse aspecto.  
  
Em suma, "O Gladiador 2" é uma obra que, embora repleta de potencial e com momentos de brilho visual, acaba por se \  
perder em sua tentativa de inovar. Para os fãs do gênero e do diretor, pode ser uma experiência mista, que levanta \  
questões sobre até que ponto a inovação deve ir sem comprometer a essência e a coerência da narrativa.  
"""  

# tratamento de erro
try:
    response = chain.invoke({'review':input_user})

    print(response['pro'])
    print("--"*20)
    print(response['con'])
except Exception as e:
    print("Ocorreu um erro durante a análise:", str(e))
  