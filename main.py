import os
import requests
import time
from fastapi import FastAPI, Request, Response
from dotenv import load_dotenv
from google import genai
from apscheduler.schedulers.background import BackgroundScheduler

load_dotenv()

app = FastAPI()
gemini_client = genai.Client()

# --- FUNCIONES DE ENVÍO POR MESSENGER ---
def send_message(recipient_id, text):
    url = f"https://graph.facebook.com/v18.0/me/messages?access_token={os.getenv('PAGE_ACCESS_TOKEN')}"
    payload = {
        "recipient": {"id": recipient_id},
        "message": {"text": text}
    }
    requests.post(url, json=payload)

def enviar_imagen_messenger(recipient_id, image_url):
    url = f"https://graph.facebook.com/v18.0/me/messages?access_token={os.getenv('PAGE_ACCESS_TOKEN')}"
    payload = {
        "recipient": {"id": recipient_id},
        "message": {
            "attachment": {
                "type": "image",
                "payload": {"url": image_url, "is_reusable": True}
            }
        }
    }
    requests.post(url, json=payload)

# --- FUNCIONES DE TMDB ---
def buscar_pelicula_tmdb(nombre_pelicula):
    tmdb_api_key = os.getenv("TMDB_API_KEY")
    if not tmdb_api_key:
        return None
    
    url = f"https://api.themoviedb.org/3/search/movie?api_key={tmdb_api_key}&query={nombre_pelicula}&language=es-ES"
    try:
        response = requests.get(url, timeout=10)
        data = response.json()
        if data["results"]:
            pelicula = data["results"][0]
            return {
                "titulo": pelicula.get("title"),
                "sinopsis": pelicula.get("overview"),
                "poster_url": f"https://image.tmdb.org/t/p/w500{pelicula.get('poster_path')}" if pelicula.get("poster_path") else None
            }
    except Exception as e:
        print(f"Error buscando en TMDB: {e}")
    return None

def obtener_poster_tmdb():
    tmdb_api_key = os.getenv("TMDB_API_KEY")
    if not tmdb_api_key:
        return None, None
    
    url = f"https://api.themoviedb.org/3/movie/popular?api_key={tmdb_api_key}&language=es-ES&page=1"
    try:
        response = requests.get(url, timeout=10)
        data = response.json()
        pelicula = data["results"][0]
        titulo = pelicula["title"]
        poster_path = pelicula.get("poster_path")
        
        if poster_path:
            poster_url = f"https://image.tmdb.org/t/p/w500{poster_path}"
            return poster_url, titulo
    except Exception as e:
        print(f"Error consultando TMDB popular: {e}")
    return None, None

# --- FUNCIONES DE PUBLICACIÓN EN EL MURO ---
def publicar_en_muro(mensaje):
    url = f"https://graph.facebook.com/v18.0/me/feed?access_token={os.getenv('PAGE_ACCESS_TOKEN')}"
    payload = {"message": mensaje}
    response = requests.post(url, json=payload)
    print(f"Publicación enviada. Código: {response.status_code} - Detalle: {response.text}")

def publicar_en_muro_con_imagen(mensaje, image_url):
    url = f"https://graph.facebook.com/v18.0/me/photos"
    payload = {
        "message": mensaje,
        "url": image_url,
        "access_token": os.getenv('PAGE_ACCESS_TOKEN')
    }
    response = requests.post(url, data=payload)
    print(f"Publicación con imagen enviada. Código: {response.status_code} - Detalle: {response.text}")

# --- RUTAS DEL SERVIDOR ---
@app.get("/webhook")
async def verify(request: Request):
    params = request.query_params
    if params.get("hub.mode") == "subscribe" and params.get("hub.verify_token") == os.getenv("VERIFY_TOKEN"):
        return Response(content=params.get("hub.challenge"), media_type="text/plain")
    return Response(content="Error de verificación", status_code=403)

@app.post("/webhook")
async def receive_message(request: Request):
    data = await request.json()
    
    if data.get("object") == "page":
        for entry in data.get("entry", []):
            for messaging_event in entry.get("messaging", []):
                if messaging_event.get("message") and messaging_event["message"].get("text"):
                    sender_id = messaging_event["sender"]["id"]
                    user_text = messaging_event["message"]["text"]
                    
                    # 1. Analizar si pide una película
                    prompt_analisis = f"""
                    Analiza el siguiente mensaje: "{user_text}"
                    Si el usuario está preguntando por una película específica, responde SOLO con el nombre de la película.
                    Si el usuario saluda, pide recomendaciones generales o habla de otra cosa, responde SOLO con la palabra "NO".
                    """
                    try:
                        analisis = gemini_client.models.generate_content(
                            model="gemini-3.6-flash",
                            contents=prompt_analisis
                        ).text.strip()
                    except:
                        analisis = "NO"

                    # 2. Si pide película, buscamos en TMDB
                    if analisis != "NO" and len(analisis) > 2:
                        print(f"Película detectada: {analisis}")
                        info_pelicula = buscar_pelicula_tmdb(analisis)
                        
                        if info_pelicula:
                            if info_pelicula["poster_url"]:
                                enviar_imagen_messenger(sender_id, info_pelicula["poster_url"])
                            
                            mensaje_info = f"🎬 *{info_pelicula['titulo']}*\n\n{info_pelicula['sinopsis']}\n\n📲 Descarga la App: https://play.google.com/store/apps/details?id=com.companyname.spay&hl=es_BO"
                            send_message(sender_id, mensaje_info)
                            continue 
                    
                    # 3. Respuesta normal con Gemini
                    bot_reply = "Lo siento, estoy teniendo problemas para pensar. Intenta de nuevo más tarde."
                    max_intentos = 3
                    
                    for intento in range(max_intentos):
                        try:
                            response = gemini_client.models.generate_content(
                                model="gemini-3.6-flash",
                                contents=f"Eres el asistente virtual de MovieSpay. Responde breve y amable. Enlace App: https://play.google.com/store/apps/details?id=com.companyname.spay&hl=es_BO . Usuario: {user_text}"
                            )
                            bot_reply = response.text
                            break
                        except Exception as e:
                            print(f"Error con Gemini en intento {intento + 1}: {e}")
                            if intento < max_intentos - 1:
                                time.sleep(2)
                    
                    send_message(sender_id, bot_reply)
    return Response(content="OK", status_code=200)

# --- TAREA DIARIA ---
def tarea_diaria():
    print("Ejecutando tarea diaria de estrenos...")
    poster_url, titulo_pelicula = obtener_poster_tmdb()
    
    if not titulo_pelicula:
        titulo_pelicula = "los estrenos de la semana"

    prompt = f"""
    Eres el community manager de MovieSpay. Escribe un post corto, emocionante y con emojis de cine 
    recomendando la película '{titulo_pelicula}'. 
    Al final del texto, SIEMPRE debes incluir este enlace para descargar nuestra App SpayNext: 
    '📲 Descarga nuestra App SpayNext aquí: https://play.google.com/store/apps/details?id=com.companyname.spay&hl=es_BO'
    No uses comillas en tu respuesta, solo el texto del post.
    """
    
    max_intentos = 5
    for intento in range(max_intentos):
        try:
            response = gemini_client.models.generate_content(
                model="gemini-3.6-flash",
                contents=prompt
            )
            texto_post = response.text
            
            if poster_url:
                publicar_en_muro_con_imagen(texto_post, poster_url)
            else:
                publicar_en_muro(texto_post)
            return
        except Exception as e:
            if intento < max_intentos - 1:
                espera = 2 ** intento
                print(f"Intento {intento + 1} falló. Reintentando en {espera}s...")
                time.sleep(espera)
            else:
                print(f"Error tras {max_intentos} intentos: {e}")

# --- RUTA PARA FORZAR PUBLICACIÓN ---
@app.get("/forzar-post")
def forzar_post():
    print("Forzando publicación manual desde el navegador...")
    tarea_diaria()
    return {"mensaje": "Tarea ejecutada. Revisa los logs de Render o tu página de Facebook."}

# --- PROGRAMADOR ---
scheduler = BackgroundScheduler()
scheduler.add_job(tarea_diaria, 'cron', hour=10, minute=0) 
scheduler.start()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)