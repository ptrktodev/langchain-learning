from langchain_core.runnables import RunnableLambda

def sum_(x: int) -> int: # isso aqui é uma função
    return x + 1

run_1 = RunnableLambda(sum_) # Runnables: componente executável.

response = run_1.invoke(2)  

print(response) 

# Runnable Lambda: Permite criar Runnables a partir de funções Python simples.