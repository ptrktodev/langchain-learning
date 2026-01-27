import datetime
import os
import os.path
from zoneinfo import ZoneInfo

import requests
from dotenv import load_dotenv
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from tavily import TavilyClient

from langchain.agents import create_agent
from langchain.tools import tool
from langchain_community.chat_message_histories import SQLChatMessageHistory
from langchain_core.messages import trim_messages
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnableLambda
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_openai import ChatOpenAI

load_dotenv()
model = ChatOpenAI(model="gpt-3.5-turbo")
tavily = TavilyClient()
api_weather = os.getenv("WEATHER_API_KEY")

@tool(description="Obtenha os próximos eventos do Google Calendar do usuário.")
def get_event() -> dict:
    """
    Recupera os próximos eventos do Google Calendar do usuário.
    
    Esta função autentica com a API do Google Calendar usando credenciais armazenadas
    localmente e busca os próximos eventos agendados a partir do momento atual.
    
    Args:
        maxresults (int, optional): Número máximo de eventos a retornar. 
            Padrão é 6 eventos.
    
    Returns:
        dict: Uma lista de dicionários contendo os eventos ou uma mensagem.
            - Se houver eventos: lista com dicionários contendo:
                * 'summary' (str): Título/nome do evento
                * 'start' (str): Data e hora de início no formato ISO 8601
                * 'end' (str): Data e hora de término no formato ISO 8601
            - Se não houver eventos: dicionário com chave 'message' indicando
              que não há eventos próximos.
    
    Requisitos:
        - Arquivo 'token.json' deve existir no diretório com credenciais válidas
        - Permissões do Google Calendar API (leitura)
        - Biblioteca google-auth-oauthlib instalada
    
    Exemplo de retorno com eventos:
        [
            {
                'summary': 'Reunião de equipe',
                'start': '2026-01-27T10:00:00-03:00',
                'end': '2026-01-27T11:00:00-03:00'
            },
            {
                'summary': 'Almoço com cliente',
                'start': '2026-01-27T12:30:00-03:00',
                'end': '2026-01-27T14:00:00-03:00'
            }
        ]
    
    Exemplo de retorno sem eventos:
        {'message': 'No upcoming events found.'}
    """
    creds = ...
    SCOPES = ["https://www.googleapis.com/auth/calendar", "https://www.googleapis.com/auth/calendar.readonly"]

    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)

    service = build("calendar", "v3", credentials=creds)

    # Call the Calendar API
    now = datetime.datetime.now(tz=datetime.timezone.utc).isoformat()
    events_result = (
        service.events()
        .list(
            calendarId="primary",
            timeMin=now,
            maxResults=5,
            singleEvents=True,
            orderBy="startTime",
        )
        .execute()
    )
    events = events_result.get("items", [])

    dict = []

    for event in events:
        dict_events = {
            "summary": event.get('summary'),
            "start": event.get('start').get('dateTime'),
            "end": event.get('end').get('dateTime'),
            "Id do Evento": event.get('id')
        }
        dict.append(dict_events)

    if events:
        return dict
    else:  
        return {"message": "No upcoming events found."}

@tool(description="Crie um evento no Google Calendar com os detalhes fornecidos.")
def create_event(ano: int, mes: int, dia: int, hora_inicio: int, minuto_inicio: int, hora_fim: int, minuto_fim: int, resumo: str, descricao: str) -> dict:
  '''
  Cria um evento no Google Calendar do usuário autenticado.
  
  A função conecta-se à API do Google Calendar usando credenciais armazenadas em 'token.json'
  e cria um novo evento no calendário primário do usuário com os parâmetros fornecidos.
  
  Parâmetros:
  -----------
  ano : int
      Ano do evento (ex: 2026)
  mes : int
      Mês do evento (1-12)
  dia : int
      Dia do evento (1-31)
  hora_inicio : int
      Hora de início do evento no formato 24h (0-23)
  minuto_inicio : int
      Minuto de início do evento (0-59)
  hora_fim : int
      Hora de término do evento no formato 24h (0-23)
  minuto_fim : int
      Minuto de término do evento (0-59)
  resumo : str
      Título/nome do evento que aparecerá no calendário
  descricao : str
      Descrição detalhada do evento (pode ser vazia)
  
  Retorna:
  --------
  dict ou str
      Se sucesso: dicionário com dados do evento criado, incluindo 'htmlLink' para acessá-lo
      Se falha: string 'Event not created'
  
  Exemplo:
  --------
  >>> event = create_event(2026, 1, 26, 14, 30, 15, 30, "Reunião", "Reunião com equipe")
  >>> print(f"Evento criado: {event.get('htmlLink')}")
  '''
  creds = ...
  SCOPES = ["https://www.googleapis.com/auth/calendar", "https://www.googleapis.com/auth/calendar.readonly"]

  if os.path.exists("token.json"):
    creds = Credentials.from_authorized_user_file("token.json", SCOPES)

  service = build("calendar", "v3", credentials=creds)
  start_event = datetime.datetime(ano, mes, dia, hora_inicio, minuto_inicio, 00, tzinfo=ZoneInfo('America/Sao_Paulo')).isoformat()
  end_event = datetime.datetime(ano, mes, dia, hora_fim, minuto_fim, 00, tzinfo=ZoneInfo('America/Sao_Paulo')).isoformat()
  event = service.events().insert(
      calendarId="primary",
      body={
        "summary": resumo,
        "description": descricao,
        "start": {
          "dateTime": start_event,
          "timeZone": "America/Sao_Paulo"
        },
        "end": {
          "dateTime": end_event,
          "timeZone": "America/Sao_Paulo"
        }
      }
    ).execute()

  if event.get('status') == 'confirmed':
    return event
  else: 
    return ('Event not created')

@tool(description="Obtenha a temperatura em tempo real para uma cidade específica.")
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

@tool(description="Deleta um evento específico do Google Calendar do usuário.")
def delete_event(id: str) -> dict:
    """
    Deleta um evento do Google Calendar.
    
    Esta função remove permanentemente um evento específico do calendário principal
    do usuário autenticado. Utiliza a API do Google Calendar v3 para realizar a operação.
    
    Args:
        id (str): O identificador único do evento a ser deletado. Este ID é fornecido
                  pela função/ferramenta get_events.
    
    Returns:
        dict: Um dicionário contendo o resultado da operação com as seguintes chaves:
            - "message" (str): Mensagem de sucesso "Evento deletado com sucesso." ou
                              mensagem de erro "Erro ao deletar o evento: {detalhes_do_erro}"
    
    Note:
        - A operação é irreversível; o evento não pode ser recuperado após a exclusão.
        - A função opera apenas no calendário principal ("primary") do usuário.
    """
    creds = ...
    SCOPES = ["https://www.googleapis.com/auth/calendar", "https://www.googleapis.com/auth/calendar.readonly"]

    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)

    service = build("calendar", "v3", credentials=creds)

    # Call the Calendar API
    try:
        service.events().delete(
            calendarId="primary",
            eventId=id,
        ).execute()

        return {"message": "Evento deletado com sucesso."}
    
    except Exception as e:
        return {"message": f"Erro ao deletar o evento: {e}"}

tools = [create_event, get_weather, get_event, delete_event] 

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

system_prompt = """Você é um assistente pessoal inteligente especializado em gerenciamento de agenda e informações meteorológicas.

## Suas Capacidades

Você tem acesso às seguintes ferramentas:

1. **get_weather**: Obtém informações meteorológicas em tempo real para uma localização específica
2. **create_event**: Cria novos eventos no Google Calendar do usuário
3. **get_events**: Recupera os próximos eventos agendados do usuário
4. **delete_event**: Deleta um evento específico do Google Calendar do usuário

## Diretrizes de Comportamento

### Comunicação
- Seja natural, amigável e proativo
- Use linguagem clara e objetiva
- Quando apropriado, sugira melhorias ou otimizações na agenda do usuário

### Uso das Ferramentas

**Para consultas de clima:**
- Use get_weather quando o usuário perguntar sobre condições meteorológicas
- Forneça informações relevantes como temperatura, condições e previsão
- Sugira preparações adequadas (ex: levar guarda-chuva se houver previsão de chuva)

**Para consulta de eventos:**
- Use get_event quando o usuário quiser saber sua agenda
- Apresente os eventos de forma organizada e legível
- Destaque conflitos de horário ou eventos próximos importantes
- MOstre ao usuário todos os eventos que a conuslta retornar
- Se não houver eventos, confirme isso de forma clara

**Para criação de eventos:**
- Use create_event quando o usuário solicitar agendamento
- SEMPRE confirme os detalhes antes de criar: título, data, horário de início e fim
- Se informações estiverem faltando, pergunte ao usuário
- Após criar, confirme o sucesso e resuma o evento criado
- Considere verificar conflitos com eventos existentes usando get_events_calendar primeiro

**Para remoção de eventos:**
- Use delete_event quando o usuário solicitar a exclusão de um evento
- Obtenha o ID do evento a ser deletado (fornecido por get_event)
- CRÍTICO: NUNCA delete um evento sem PRIMEIRO confirmar com o usuário
  * Mostre o nome e ID do evento encontrado
  * Pergunte explicitamente: "Confirma a exclusão deste evento? (sim/não)"
  * AGUARDE a resposta do usuário
  * SOMENTE após confirmação positiva, execute delete_event
- Você deve passar o ID como parâmetro para a função delete_event
- Após deletar, confirme o sucesso ou informe falhas

### Integração Inteligente

- Combine informações quando relevante (ex: ao criar eventos externos, mencione o clima previsto)
- Seja proativo em sugerir ajustes baseados em conflitos de agenda ou condições climáticas
- Mantenha contexto da conversa para entender referências a eventos anteriores

### Formato de Respostas

- Para listas de eventos, use formatação clara com data, hora e título
- Para clima, apresente temperatura e condições de forma direta
- Evite respostas excessivamente longas ou técnicas
- Use emojis com moderação quando apropriado (☀️ 🌧️ 📅 ✅)

## Tratamento de Erros

- Se uma ferramenta falhar, informe o usuário de forma clara
- Sugira alternativas ou próximos passos
- Nunca invente informações - se não tiver dados, seja honesto

Lembre-se: Você é um assistente prestativo que gerencia tempo e fornece informações úteis. Seja eficiente, preciso e humano em suas interações.
"""

agent = create_agent( 
    model=model,
    tools=tools,
    system_prompt=system_prompt,
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

while True:
    # user_input = "Crie um evento no meu calendário para uma reunião de equipe no dia 27 de janeiro de 2026, das 10h às 11h, com o título 'Reunião de Planejamento' e a descrição 'Discutir metas e estratégias para o próximo trimestre'."
    user_input = input("Digite: ")
    # user_input = "qual a temperatura em São Paulo agora?"

    if user_input.lower() in ["sair", "exit", "quit"]:
        break

    response = runnable_with_history.invoke(
        {"user_input": user_input}, 
        config={"configurable": {"session_id": "1"}} 
    )

    print(response['messages'][0].content)