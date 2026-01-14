from langchain_core.runnables import RunnableMap
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate # criar template com variaveis
from dotenv import load_dotenv

load_dotenv()

llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0.8)

prompt_resumo = PromptTemplate(
    input_variabes=["texto"],
    template="Analise o sentimento do seguinte texto e retorne apenas uma palavra, sem explicações ou pontuação: {texto}"
)

# isso aqqui é um Runnable composto: uma cadeia de Runnables.
chain = RunnableMap({
    'resumo': prompt_resumo | llm
})

input_user1 = "Devo comparar-te a um dia de verão? Tu és mais amável e mais temperado. Os ventos rudes sacodem os queridos botões de maio, E o arrendamento do verão tem prazo muito curto. Mas tua eterna beleza não se desvanecerá, Nem perderás a posse da graça que tens; Nem a Morte se vangloriará de que vagueias na sua sombra, Quando em versos eternos ao tempo tu cresceres. Enquanto os homens puderem respirar ou os olhos puderem ver, Viverá este poema — e ele te fará viver."
input_user2 = "A tecnologia blockchain está revolucionando a forma como armazenamos e compartilhamos informações. Com sua estrutura descentralizada, ela oferece maior segurança e transparência, tornando-se uma ferramenta essencial para diversas indústrias, desde finanças até saúde."
input_user3 = "A mudança climática é um dos maiores desafios que a humanidade enfrenta atualmente. O aumento das temperaturas globais está causando eventos climáticos extremos, como furacões, secas e inundações, que afetam milhões de pessoas em todo o mundo."

response = chain.invoke([input_user1, input_user2, input_user3])   

print(response['resumo'].content) 

# Parallel: tarefas diferentes, mesmo input.
# Map: mesma tarefa, inputs diferentes.