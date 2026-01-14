from langchain_core.runnables import RunnableParallel, RunnableLambda
from langchain_core.prompts import PromptTemplate # criar template com variaveis
from langchain_groq import ChatGroq
from dotenv import load_dotenv

load_dotenv()

llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0.8)

prompt_resumo = PromptTemplate(
    input_variabes=["texto"],
    template="Resuma o texto em 5 palavras: {texto}"
)

prompt_sentimento = PromptTemplate(
    input_variabes=["texto"],
    template="Analise o sentimento do seguinte texto e retorne apenas um verbo, sem explicações ou pontuação: {texto}"
)

prompt_english = PromptTemplate(
    input_variabes=["texto"],
    template="Traduza o resumo para inglês: {texto}"
)

extract_content = RunnableLambda(lambda x: x.content) # extrai o 'conteúdo' da resposta do LLM

# isso aqqui é um Runnable composto: uma cadeia de Runnables.
chain = RunnableParallel({
    'summary': prompt_resumo | llm,
    'english': prompt_resumo | llm | extract_content | prompt_english | llm,
    'sentiment': prompt_sentimento | llm
})

input_user = "Devo comparar-te a um dia de verão? Tu és mais amável e mais temperado. Os ventos rudes sacodem os queridos botões de maio, E o arrendamento do verão tem prazo muito curto. Mas tua eterna beleza não se desvanecerá, Nem perderás a posse da graça que tens; Nem a Morte se vangloriará de que vagueias na sua sombra, Quando em versos eternos ao tempo tu cresceres. Enquanto os homens puderem respirar ou os olhos puderem ver, Viverá este poema — e ele te fará viver."

response = chain.invoke(input_user)  

print(f"Resumo: {response['summary'].content}")
print(f"English: {response['english'].content}")  
print(f"Análise de Sentimento: {response['sentiment'].content}") 

# Parallel: tarefas diferentes, mesmo input.
# Map: mesma tarefa, inputs diferentes.