from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
import httpx
import os
from dotenv import load_dotenv

load_dotenv()
app = FastAPI()

# Permitir CORS para que tu frontend pueda consultar
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- CONFIGURACIÓN DESDE .ENV ---
GITHUB_USER = os.getenv("GITHUB_USER")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
WEATHER_KEY = os.getenv("WEATHER_KEY")
DISCORD_ID = os.getenv("DISCORD_ID")
FORMSPREE_ID = os.getenv("FORMSPREE_ID")
CITY = os.getenv("CITY")

@app.get("/api/status")
async def get_status():
    return {
        "status": "online", 
        "message": "Backend de Agustin operando en Oracle Cloud",
        "user": GITHUB_USER
    }

@app.get("/api/github-projects")
async def get_github():
    url = f"https://api.github.com/users/{GITHUB_USER}/repos?sort=updated"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    async with httpx.AsyncClient() as client:
        resp = await client.get(url, headers=headers)
        repos = resp.json()
        # Filtramos por el topic 'portfolio' como tienes en tu JS
        return [r for r in repos if r.get('topics') and 'portfolio' in r['topics']][:6]

@app.get("/api/weather")
async def get_weather():
    url = f"https://api.openweathermap.org/data/2.5/weather?q={CITY}&units=metric&appid={WEATHER_KEY}"
    async with httpx.AsyncClient() as client:
        resp = await client.get(url)
        return resp.json()

@app.get("/api/discord-status")
async def get_discord():
    url = f"https://api.lanyard.rest/v1/users/{DISCORD_ID}"
    async with httpx.AsyncClient() as client:
        resp = await client.get(url)
        return resp.json()

# PROXY DE CONTACTO: Recibe el form y lo reenvía a Formspree
@app.post("/api/contact")
async def contact_proxy(request: Request):
    print(">> Recibiendo petición de contacto...") # Esto saldrá en docker logs
    try:
        form_data = await request.form()
        data_dict = dict(form_data)
        print(f">> Datos recibidos: {data_dict}")

        url = f"https://formspree.io/f/{FORMSPREE_ID}"
        
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                url, 
                data=data_dict, 
                headers={"Accept": "application/json"}
            )
            print(f">> Respuesta de Formspree: {resp.status_code}")
            return resp.json()
            
    except Exception as e:
        print(f"!! ERROR EN EL PROXY: {str(e)}")
        return {"error": str(e)}, 500