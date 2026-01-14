from dotenv import load_dotenv
from langchain_groq.chat_models import ChatGroq
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_community.chat_message_histories import SQLChatMessageHistory
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables.history import RunnableWithMessageHistory
from sqlalchemy import create_engine, text

load_dotenv()

# Inicializa o modelo de linguagem Groq com o modelo Llama 3.1 8B
llm = ChatGroq(model='llama-3.1-8b-instant')

def get_session_history(session_id: int):
    """ 
    Retorna o objeto de histórico de chat para uma sessão específica.
    
    Args:
        session_id: Identificador único da sessão de conversa
        
    Returns:
        SQLChatMessageHistory: Objeto que gerencia o histórico no SQLite
    """
    # Cria/conecta ao banco SQLite e retorna o histórico da sessão
    return SQLChatMessageHistory(
        session_id, 
        connection='sqlite:///chat_memory.db'
    )

# Define a estrutura da conversa com o modelo
prompts_template = ChatPromptTemplate.from_messages([
    # Mensagem de sistema: define o comportamento do assistente
    ('system', "Você é um assistente útil, seja objetivo e direto."),
    
    # Placeholder: local onde o histórico de mensagens será inserido automaticamente
    MessagesPlaceholder(variable_name="history"),
    
    # Mensagem do usuário: será preenchida com o input atual
    ('human', "{user_input}"),
])

# Pipeline de processamento: Template → Modelo → Parser de String
chain_chat = prompts_template | llm | StrOutputParser()

# Envolve a chain com gerenciamento automático de histórico
runnable_with_history = RunnableWithMessageHistory(
    chain_chat,                          # Chain a ser executada
    get_session_history,                 # Função para obter histórico
    input_messages_key="user_input",     # Chave do input no template
    history_messages_key="history"       # Chave do histórico no template
)

# FLUXO DE EXECUÇÃO:
# 1. Usuário envia mensagem via 'user_input'
# 2. get_session_history() busca mensagens antigas no SQLite
# 3. RunnableWithMessageHistory injeta histórico no placeholder "history"
# 4. Template completo é enviado ao modelo
# 5. Resposta é salva automaticamente no banco de dados

def get_new_session():
    """
    Obtém o próximo ID de sessão disponível consultando o banco de dados.
    
    Returns:
        int: Maior session_id existente no banco (ou None se vazio)
    """
    # Cria/conecta ao banco de dados SQLite
    eng = create_engine('sqlite:///chat_memory.db')
    
    # Abre conexão com o banco
    with eng.connect() as db:
        # Consulta SQL: converte session_id para inteiro e pega o maior valor
        max_id = db.execute(text("""
            SELECT MAX(CAST(session_id AS INTEGER))
            FROM message_store
        """)).scalar()  # Extrai o valor para utilização em Python
        
        return max_id + 1

# Obtém o último session_id e incrementa em 1 para criar nova sessão
session_new = get_new_session()

while True:
    # Solicita input do usuário
    prompt_user = input("Digite seu prompt (ou 'sair' para encerrar): ")

    # Verifica se o usuário quer sair
    if prompt_user.lower() == 'sair':
        break
    
    # Processa a mensagem do usuário
    else:
        # Invoca a chain com histórico
        response = runnable_with_history.invoke(
            {'user_input': prompt_user},  # Input do usuário
            config={
                'configurable': {
                    'session_id': session_new  # ID da sessão atual
                }
            }
        )
        
        # Exibe a resposta do modelo
        print(response)
        print()  # Linha em branco para melhor legibilidade




        