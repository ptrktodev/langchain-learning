from langchain_core.runnables import RunnableLambda

def sum_(x: int) -> int: # isso aqui é uma função
    return x + 1

def mult(x: int) -> int: # isso aqui é uma função
    return x * 2

run_1 = RunnableLambda(sum_) # Runnables: componente executável.
run_2 = RunnableLambda(mult) 

sequence = run_1 | run_2  # isso aqui é um Runnable composto: uma cadeia de Runnables.

response = sequence.invoke(2)  

print(response)  

# Runnable sequence: Serve para invocar uma cadeia sequencia onde a saída 
# de um componente serve de entrada para o próximo componente.