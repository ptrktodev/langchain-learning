
import datetime
import os.path
from zoneinfo import ZoneInfo
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

def get_event() -> dict:
    creds = ...
    SCOPES = ["https://www.googleapis.com/auth/calendar", "https://www.googleapis.com/auth/calendar.readonly"]

    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)

    service = build("calendar", "v3", credentials=creds)

    # Call the Calendar API
    now = datetime.datetime.now(tz=datetime.timezone.utc).isoformat()
    print("Getting the upcoming 10 events")
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

if __name__ == "__main__":
    print(delete_event('0afddd5ef7d2436d9b8db903652c57ae'))
    

    '''
    
    for event in get_event():
        print(event)
        print('-----------------------')

    
    '''