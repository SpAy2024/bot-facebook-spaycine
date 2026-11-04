# 🤖 Bot de Facebook con IA para MovieSpay


![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![Gemini](https://img.shields.io/badge/Google%20Gemini-3.8%20Flash-8E75B2?style=for-the-badge&logo=google&logoColor=white)
![TMDB](https://img.shields.io/badge/TMDB-API-01B4E4?style=for-the-badge&logo=themoviedatabase&logoColor=white)
![Licencia](https://img.shields.io/badge/Licencia-MIT-yellow?style=for-the-badge)

Este proyecto es un bot integral de atención al cliente y *Community Manager* automático para la página de Facebook **MovieSpay**. Utiliza la API oficial de Meta para interactuar en Messenger y publicar en el muro, la inteligencia artificial de **Google Gemini** para generar respuestas y textos naturales, y la API de **TMDB** para adjuntar pósteres de películas reales.

## ✨ Características

- 💬 **Respuestas automáticas en Messenger**: Contesta dudas y saluda a los usuarios en tiempo real.
- 🎬 **Búsqueda de películas**: Si un usuario pregunta por una película, el bot busca su sinopsis y envía el póster oficial usando la API de TMDB.
- 📢 **Publicaciones automáticas diarias**: Cada día a las 10:00 AM, el bot redacta un post sobre una película en tendencia y lo publica en el muro con su respectiva imagen.
- 📲 **Enlace de descarga integrado**: El bot promociona constantemente la App **SpayNext** con su enlace real de Play Store.
- 🛡️ **Manejo de errores**: Incluye sistemas de reintentos automáticos para evitar fallos por saturación de los servidores de IA.
- ☁️ **Desplegado en la nube**: Funciona 24/7 gracias a Render y UptimeRobot.
- 🔒 **Protección de credenciales**: Uso de variables de entorno para mantener seguros los tokens y API Keys.

## 🛠️ Tecnologías utilizadas

- **Python 3**
- **FastAPI** (Servidor web para el Webhook)
- **Google GenAI SDK** (Inteligencia Artificial para texto)
- **TMDB API** (Base de datos de películas e imágenes)
- **Meta Graph API** (Conexión con Facebook Messenger y Muro)
- **APScheduler** (Programador de tareas diarias)
- **Render** (Hosting y despliegue en la nube)
- **Uvicorn** (Servidor ASGI)

## 🚀 Cómo implementar este proyecto (para desarrolladores)

### Requisitos previos
1. Una página de Facebook y una App en [Meta for Developers](https://developers.facebook.com/).
2. Una API Key gratuita de [Google AI Studio](https://aistudio.google.com/).
3. Una API Key gratuita de [The Movie Database (TMDB)](https://www.themoviedb.org/).
4. Una cuenta en [Render](https://render.com/).

### Configuración local
1. Clona este repositorio:
   ```bash
   git clone https://github.com/SpAy2024/bot-facebook-spaycine.git
   cd bot-facebook-spaycine
