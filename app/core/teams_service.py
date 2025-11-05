import requests
from app.core.config import settings

def send_teams_message(message: str):
    teams_webhook_url = settings.TEAMS_WEBHOOK_URL

    payload = {"text": message}
    headers = {"Content-Type": "application/json"}

    response = requests.post(teams_webhook_url, json=payload, headers=headers)

    if response.status_code == 200:
        return {"sucess": "Mensagem enviada"}
    return {"error": f"Falha ao enviar mensagem"}