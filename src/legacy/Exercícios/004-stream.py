from dotenv import load_dotenv
from langchain_groq.chat_models import ChatGroq # Chat Model
import time

load_dotenv()

llm = ChatGroq(model='llama-3.1-8b-instant')
prompt = "Explique a teoria da relatividade de forma simples."

def main():
     for chunk in llm.stream(prompt):
        print(chunk.content, end='', flush=True)
        time.sleep(0.1)  # Simula um pequeno atraso para visualização

main()

# A função 'main' abaixo é síncrona. O código vai ser executado de forma bloqueante
# enquanto aguarda a resposta do modelo. Isso significa que:
# - O programa fica "preso" na linha 'for chunk in model.stream(prompt)' até que 
#   todos os dados sejam recebidos.
# - Durante esse tempo, se você tivesse outras tarefas a realizar (como mais chamadas 
#   de funções, interações com a interface do usuário, outras requisições de rede), 
#   o fluxo do programa ficaria travado, esperando o retorno do 'model.stream(prompt)'.
# - Caso o modelo ou a API demore para responder, ou o fluxo de dados seja contínuo, 
#   o seu programa inteiro pode **ficar travado** até que todo o conteúdo seja retornado.