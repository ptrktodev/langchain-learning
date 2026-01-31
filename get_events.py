
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

def update_event(event_id: str, resumo: str, descricao: str, start_event: str, end_event: str) -> dict:
    creds = ...
    SCOPES = ["https://www.googleapis.com/auth/calendar", "https://www.googleapis.com/auth/calendar.readonly"]

    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)

    service = build("calendar", "v3", credentials=creds)

    events_result = (
        service.events()
        .update(
            calendarId="primary",
            eventId=event_id,
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
    ) 

    if events_result['status'] == 'confirmed':
        return {"message": "Evento atualizado com sucesso."}
    else: 
        return {"message": "Erro ao atualizar o evento."}

if __name__ == "__main__":
    print(update_event(event_id="6392754ce8cb4a3dac5f545cff4a740c", 
                       resumo="Reunião Atualizada", 
                       descricao="Descrição Atualizada", 
                       start_event="2026-01-29T20:50:00-03:00", 
                       end_event="2026-01-29T21:30:00-03:00"))
'''    
    for event in get_event():
        print(event)
        print('-----------------------')'''