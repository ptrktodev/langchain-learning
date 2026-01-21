from dotenv import load_dotenv
import requests
import psycopg2
from langchain_openai import ChatOpenAI
import os
from langchain.tools import tool
from tavily import TavilyClient
from langchain_community.chat_message_histories import SQLChatMessageHistory
from langchain_core.messages import trim_messages
from langchain.agents import create_agent
from langchain.agents.structured_output import ToolStrategy
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage
from rich.pretty import pprint
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.runnables import RunnableLambda

load_dotenv()

model = ChatOpenAI(model="gpt-3.5-turbo")

tavily = TavilyClient()
api_weather = os.getenv("WEATHER_API_KEY")

@tool
def get_capital(country: str) -> str:
    """Get the capital of a country."""
    capital = tavily.search(
        query=f"What is the capital of {country}?",
        search_depth="ultra-fast", # ultra-fast, fast, medium, advanced 
        max_results=1,
    )
    return capital

@tool(description="Get Realtime weather of a city.")
def get_weather(city: str) -> str:
    url = f"https://api.tomorrow.io/v4/weather/realtime?location={city}&apikey={api_weather}"
    headers = {
        "accept": "application/json",
        "accept-encoding": "deflate, gzip, br"
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:  
        return f"Erro: status code {response.status_code}"

tools = [get_capital, get_weather] 

def get_session_history(session_id: str):
    # String de conexão PostgreSQL para Supabase
    connection_string = "sqlite:///message_store.db"
    
    return SQLChatMessageHistory(
        session_id=session_id,
        connection=connection_string,
        table_name="message_store"
    )

def extract_last_message(agent_output): # Extrai apenas a última mensagem da saída do agent
    if isinstance(agent_output, dict) and "messages" in agent_output:
        return {"messages": [agent_output["messages"][-1]]}
    return agent_output

trimmer = trim_messages(
    max_tokens=20,  # cada mensagem conta como 1 token
    strategy="last",   # seleciona as últimas mensagens
    token_counter=lambda x: 1,  # Cada mensagem conta como 1 token
)

prompt = ChatPromptTemplate.from_messages([
    ("system", "Você é um assistente prestativo."),
    MessagesPlaceholder(variable_name="history"),
    ("human", "{user_input}")
])

agent = create_agent( 
    model=model,
    tools=tools
    # response_format=ToolStrategy(AgentResponse),
)

trim_chain = {
    "user_input": lambda x: x["user_input"],
    "history": lambda x: trimmer.invoke(x["history"]),
}

chain = trim_chain | prompt | agent | RunnableLambda(extract_last_message)

# adicionando histórico de conversação a chain
runnable_with_history = RunnableWithMessageHistory(
    chain,
    get_session_history,
    input_messages_key="user_input", # a chave do dict de entrada contém a mensagem do usuário
    history_messages_key="history", # a chave será usada para injetar o histórico na chain
    output_messages_key="messages" # a chave do dict de saída contém as mensagens geradas
)

user_input = "qual o seu modelo?"
response = runnable_with_history.invoke(
    {"user_input": user_input},
    config={"configurable": {"session_id": "1"}} 
)

print(response['messages'][0].content)