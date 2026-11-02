# 🤖 Bot de Facebook con IA para MovieSpay

Este proyecto es un bot de atención al cliente y recomendaciones de películas para la página de Facebook **MovieSpay**. Utiliza la API oficial de Meta para recibir mensajes y la inteligencia artificial de **Google Gemini** para generar respuestas naturales y contextuales.

## ✨ Características

- 💬 Respuestas automáticas en tiempo real en Messenger.
- 🎬 Recomendación de películas con IA (Google Gemini 3.8 Flash).
- ☁️ Desplegado en la nube (Render) para funcionar 24/7.
- 🔒 Protección de credenciales mediante variables de entorno.

## 🛠️ Tecnologías utilizadas

- **Python 3**
- **FastAPI** (Servidor web para el Webhook)
- **Google GenAI SDK** (Inteligencia Artificial)
- **Meta Graph API** (Conexión con Facebook)
- **Render** (Hosting y despliegue)
- **Uvicorn** (Servidor ASGI)

## 🚀 Cómo desplegar este proyecto (para desarrolladores)

### Requisitos previos
1. Una página de Facebook y una App en [Meta for Developers](https://developers.facebook.com/).
2. Una API Key gratuita de [Google AI Studio](https://aistudio.google.com/).
3. Una cuenta en [Render](https://render.com/) (o cualquier otro servicio de hosting).

### Configuración local
1. Clona este repositorio:
   ```bash
   git clone https://github.com/SpAy2024/bot-facebook-spaycine.git
   cd bot-facebook-spaycine