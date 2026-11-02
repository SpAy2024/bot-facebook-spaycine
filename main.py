import os
import requests
from fastapi import FastAPI, Request, Response
from dotenv import load_dotenv
from google import genai

import time
import threading
import datetime
from apscheduler.schedulers.background import BackgroundScheduler

load_dotenv()

app = FastAPI()
gemini_client = genai.Client()  # Lee GEMINI_API_KEY del .env

# 1. Verificación del Webhook
@app.get("/webhook")
async def verify(request: Request):
    params = request.query_params
    if params.get("hub.mode") == "subscribe" and params.get("hub.verify_token") == os.getenv("VERIFY_TOKEN"):
        return Response(content=params.get("hub.challenge"), media_type="text/plain")
    return Response(content="Error de verificación", status_code=403)

# 2. Recibir mensajes y responder con Gemini
@app.post("/webhook")
async def receive_message(request: Request):
    data = await request.json()
    
    if data.get("object") == "page":
        for entry in data.get("entry", []):
            for messaging_event in entry.get("messaging", []):
                if messaging_event.get("message") and messaging_event["message"].get("text"):
                    sender_id = messaging_event["sender"]["id"]
                    user_text = messaging_event["message"]["text"]
                    
                    try:
                        # Usamos el modelo actualizado que te indicó Google
                        response = gemini_client.models.generate_content(
                            model="gemini-3.6-flash",
                            contents=f"Eres el asistente virtual de la página de películas MovieSpay. Responde de forma amable, breve y en español. Si el usuario pregunta cómo descargar la aplicación o ver películas, responde SIEMPRE con este enlace: https://play.google.com/store/search?q=spaynext . El usuario dice: {user_text}"
                        )
                        bot_reply = response.text
                    except Exception as e:
                        print(f"Error con Gemini: {e}")
                        bot_reply = "Lo siento, estoy teniendo problemas para pensar. Intenta de nuevo más tarde."
                    
                    send_message(sender_id, bot_reply)
    return Response(content="OK", status_code=200)

# Función para enviar el mensaje usando la API de Facebook
def send_message(recipient_id, text):
    url = f"https://graph.facebook.com/v18.0/me/messages?access_token={os.getenv('PAGE_ACCESS_TOKEN')}"
    payload = {
        "recipient": {"id": recipient_id},
        "message": {"text": text}
    }
    requests.post(url, json=payload)

# --- NUEVA FUNCIÓN PARA PUBLICAR EN EL MURO ---
def publicar_en_muro(mensaje):
    url = f"https://graph.facebook.com/v18.0/me/feed?access_token={os.getenv('PAGE_ACCESS_TOKEN')}"
    payload = {"message": mensaje}
    response = requests.post(url, json=payload)
    print(f"Publicación enviada: {response.status_code}")

# --- TAREA DIARIA AUTOMÁTICA ---
def tarea_diaria():
    print("Ejecutando tarea diaria de estrenos...")
    
    # 1. Le pedimos a Gemini que invente el post del día
    prompt = """
    Eres el community manager de MovieSpay. Escribe un post corto, emocionante y con emojis de cine 
    recomendando los estrenos de la semana. 
    Al final del texto, SIEMPRE debes incluir este enlace para descargar nuestra App SpayNext: 
    '📲 Descarga nuestra App SpayNext aquí: https://play.google.com/store/apps/details?id=com.spaynext.app'
    No uses comillas en tu respuesta, solo el texto del post.
    """
    
    try:
        response = gemini_client.models.generate_content(
            model="gemini-3.8-flash",
            contents=prompt
        )
        texto_post = response.text
        publicar_en_muro(texto_post)
    except Exception as e:
        print(f"Error generando el post diario: {e}")

# --- CONFIGURAR EL PROGRAMADOR (Scheduler) ---
# Esto iniciará un reloj en segundo plano cuando arranque el servidor
scheduler = BackgroundScheduler()
# Programa la tarea todos los días a las 10:00 AM (hora del servidor)
# Ejecutar la tarea una vez al arrancar (para probar)
tarea_diaria()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)