from dotenv import load_dotenv
from langchain_groq.chat_models import ChatGroq
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from langchain_core.messages import trim_messages
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_community.chat_message_histories import SQLChatMessageHistory

load_dotenv()

llm = ChatGroq(model='llama-3.1-8b-instant')

def get_session_history(session_id: str):
    # String de conexão PostgreSQL para Supabase
    connection_string = "postgresql://postgres.dinyovfkphixokpdlsyi:HlHKV6c3iXS9cIEU@aws-1-sa-east-1.pooler.supabase.com:6543/postgres"
    
    return SQLChatMessageHistory(
        session_id=session_id,
        connection=connection_string,
        table_name="message_store"
    )

trimmer = trim_messages(
    max_tokens=10,  # cada mensagem conta como 1 token
    strategy="last",   # seleciona as últimas mensagens
    token_counter=lambda x: 1,  # Cada mensagem conta como 1 token
)

# Prompt
prompt = ChatPromptTemplate.from_messages([
    ("system", "Você é um assistente prestativo."),
    MessagesPlaceholder(variable_name="history"),
    ("human", "{user_input}")
])

def vizu(x):
    print(x)
    return x

# CHAIN
chain = (
    {
        "user_input": lambda x: x["user_input"],
        "history": lambda x: trimmer.invoke(x["history"])  # Aplica o trimmer
    }
    | RunnableLambda(vizu)
    | prompt
    | llm
    | StrOutputParser()
)

runnable_with_history = RunnableWithMessageHistory(
    chain,
    get_session_history,
    input_messages_key="user_input",
    history_messages_key="history"
)

# EXECUTAR
user_input = "qual o meu nome?"
response = runnable_with_history.invoke(
    {"user_input": user_input},
    config={"configurable": {"session_id": "1"}} 
)

print(response)

