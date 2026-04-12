from fastapi import FastAPI, HTTPException, Request, Depends, status, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
import httpx
import os
import re
import shutil
import subprocess
from datetime import datetime
from urllib.parse import quote
from dotenv import load_dotenv

from database import init_db, get_db, engine
from models import Project, PersonalInfo, ContactMessage, Base
from schemas import (
    ProjectCreate, ProjectUpdate, Project as ProjectSchema,
    PersonalInfoCreate, PersonalInfoUpdate, PersonalInfo as PersonalInfoSchema,
    ContactMessageCreate, ContactMessage as ContactMessageSchema,
    AdminLogin
)

load_dotenv()
app = FastAPI()

# Inicializar la base de datos al arrancar la aplicación
@app.on_event("startup")
async def startup():
    init_db()

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
WAKATIME_URL = os.getenv("WAKATIME_URL", "")
WHATSAPP_NUMBER = os.getenv("WHATSAPP_NUMBER")
WHATSAPP_TEXT = os.getenv("WHATSAPP_TEXT")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123").strip()
IMG_ROOT = os.getenv("IMG_ROOT", "/app/public_images")
ALLOWED_IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp", ".gif", ".svg"}
EXCLUDED_IMAGE_FOLDERS = {"favicon"}

# Autenticacion para rutas admin
security = HTTPBearer()

def verify_admin(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verifica la contraseña de admin desde el header Authorization"""
    if credentials.credentials.strip() != ADMIN_PASSWORD:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    return True


@app.get("/api/admin/auth-check", dependencies=[Depends(verify_admin)])
async def admin_auth_check():
    return {"ok": True}

@app.get("/api/status")
async def get_status():
    return {
        "status": "online", 
        "message": "Backend operando correctamente. Personaliza esta ruta para monitoreo o debug.",
        "user": GITHUB_USER
    }


@app.get("/api/public-config")
async def get_public_config():
    """Expone solo config no sensible que necesita el frontend en runtime."""
    return {
        "discord_id": DISCORD_ID or "",
        "city": CITY or "",
        "wakatime_url": WAKATIME_URL or "",
    }

# ======== ENDPOINTS DE PROYECTOS ========
@app.get("/api/projects")
async def get_projects(db: Session = Depends(get_db)):
    """Obtiene todos los proyectos para mostrar en publico"""
    projects = db.query(Project).all()
    return projects

@app.post("/api/admin/projects", dependencies=[Depends(verify_admin)])
async def create_project(project: ProjectCreate, db: Session = Depends(get_db)):
    """Crea un proyecto nuevo (solo admin)"""
    db_project = Project(**project.dict())
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return db_project

@app.put("/api/admin/projects/{project_id}", dependencies=[Depends(verify_admin)])
async def update_project(project_id: str, project_update: ProjectUpdate, db: Session = Depends(get_db)):
    """Actualiza un proyecto (solo admin)"""
    db_project = db.query(Project).filter(Project.project_id == project_id).first()
    if not db_project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    update_data = project_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_project, key, value)
    db_project.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(db_project)
    return db_project

@app.delete("/api/admin/projects/{project_id}", dependencies=[Depends(verify_admin)])
async def delete_project(project_id: str, db: Session = Depends(get_db)):
    """Elimina un proyecto (solo admin)"""
    db_project = db.query(Project).filter(Project.project_id == project_id).first()
    if not db_project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    db.delete(db_project)
    db.commit()
    return {"status": "deleted"}


def _sanitize_filename(filename: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9._-]", "_", os.path.basename(filename or ""))
    return cleaned.strip("._")


@app.get("/api/admin/images", dependencies=[Depends(verify_admin)])
async def list_admin_images():
    """Lista imagenes disponibles en html/img para usar en proyectos."""
    if not os.path.isdir(IMG_ROOT):
        return {"images": []}

    images = []
    for root, _, files in os.walk(IMG_ROOT):
        relative_root = os.path.relpath(root, IMG_ROOT).replace("\\", "/")
        root_parts = set(part for part in relative_root.split("/") if part not in {".", ""})
        if root_parts.intersection(EXCLUDED_IMAGE_FOLDERS):
            continue

        for name in files:
            ext = os.path.splitext(name)[1].lower()
            if ext not in ALLOWED_IMAGE_EXTENSIONS:
                continue
            absolute_path = os.path.join(root, name)
            relative_path = os.path.relpath(absolute_path, IMG_ROOT).replace("\\", "/")
            web_path = f"img/{relative_path}" if relative_path != "." else f"img/{name}"
            images.append(web_path)

    images.sort()
    return {"images": images}


@app.post("/api/admin/images", dependencies=[Depends(verify_admin)])
async def upload_admin_image(image: UploadFile = File(...)):
    """Sube una nueva imagen al directorio html/img."""
    safe_name = _sanitize_filename(image.filename)
    if not safe_name:
        raise HTTPException(status_code=400, detail="Nombre de archivo invalido")

    extension = os.path.splitext(safe_name)[1].lower()
    if extension not in ALLOWED_IMAGE_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Formato no permitido")

    data = await image.read()
    max_size = 10 * 1024 * 1024
    if len(data) > max_size:
        raise HTTPException(status_code=400, detail="Imagen demasiado grande (max 10MB)")

    os.makedirs(IMG_ROOT, exist_ok=True)
    target_path = os.path.join(IMG_ROOT, safe_name)

    # Evitar sobreescribir: agregar timestamp si ya existe
    if os.path.exists(target_path):
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        name_without_ext = os.path.splitext(safe_name)[0]
        target_path = os.path.join(IMG_ROOT, f"{name_without_ext}_{stamp}{extension}")

    with open(target_path, "wb") as f:
        f.write(data)

    relative_path = os.path.relpath(target_path, IMG_ROOT).replace("\\", "/")
    return {"path": f"img/{relative_path}"}

# ======== ENDPOINTS DE INFORMACIÓN PERSONAL ========
@app.get("/api/personal-info")
async def get_personal_info(db: Session = Depends(get_db)):
    """Obtiene la informacion personal para mostrar en publico"""
    info = db.query(PersonalInfo).first()
    if not info:
        raise HTTPException(status_code=404, detail="Personal info not configured")
    return info

@app.post("/api/admin/personal-info", dependencies=[Depends(verify_admin)])
async def create_personal_info(info: PersonalInfoCreate, db: Session = Depends(get_db)):
    """Crea la informacion personal (solo admin)"""
    # Eliminar cualquier info existente para mantener solo una entrada
    db.query(PersonalInfo).delete()
    db_info = PersonalInfo(**info.dict())
    db.add(db_info)
    db.commit()
    db.refresh(db_info)
    return db_info

@app.put("/api/admin/personal-info", dependencies=[Depends(verify_admin)])
async def update_personal_info(info_update: PersonalInfoUpdate, db: Session = Depends(get_db)):
    """Actualiza la informacion personal (solo admin)"""
    db_info = db.query(PersonalInfo).first()
    if not db_info:
        raise HTTPException(status_code=404, detail="Personal info not configured")
    
    update_data = info_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_info, key, value)
    db_info.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(db_info)
    return db_info

# ======== ENDPOINTS DE MENSAJES DE CONTACTO ========
@app.get("/api/admin/messages", dependencies=[Depends(verify_admin)])
async def get_messages(db: Session = Depends(get_db)):
    """Obtiene todos los mensajes de contacto (solo admin)"""
    messages = db.query(ContactMessage).order_by(ContactMessage.created_at.desc()).all()
    return messages

@app.put("/api/admin/messages/{message_id}", dependencies=[Depends(verify_admin)])
async def mark_message_read(message_id: int, db: Session = Depends(get_db)):
    """Marca un mensaje como leido (solo admin)"""
    msg = db.query(ContactMessage).filter(ContactMessage.id == message_id).first()
    if not msg:
        raise HTTPException(status_code=404, detail="Message not found")
    
    msg.read = 1
    db.commit()
    db.refresh(msg)
    return msg

# ======== ENDPOINT DE DEPLOYMENT ========
@app.post("/api/admin/deploy", dependencies=[Depends(verify_admin)])
async def deploy_app(db: Session = Depends(get_db)):
    """Despliega la app con rebuild de Docker y backup previo de la base (solo admin)"""
    try:
        # Backup la base de datos antes de desplegar
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = f"/home/TU_USUARIO/portfolio/data/portfolio_backup_{timestamp}.db"
        original_db = "/home/TU_USUARIO/portfolio/data/portfolio.db"
        
        if os.path.exists(original_db):
            shutil.copy2(original_db, backup_path)
            print(f">> Database backed up to {backup_path}")
        
        # Correr el comando docker-compose up -d --build
        result = subprocess.run(
            ["docker-compose", "up", "-d", "--build"],
            cwd="/home/TU_USUARIO/portfolio",
            capture_output=True,
            text=True,
            timeout=300
        )
        
        if result.returncode != 0:
            print(f">> Deployment error: {result.stderr}")
            raise HTTPException(status_code=500, detail=f"Deployment failed: {result.stderr}")
        
        print(f">> Deployment successful at {datetime.now()}")
        return {"status": "success", "message": "Deployment completed", "backup": backup_path}
        
    except subprocess.TimeoutExpired:
        raise HTTPException(status_code=500, detail="Deployment timeout")
    except Exception as e:
        print(f"!! Deployment error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Deployment error: {str(e)}")

@app.get("/api/github-projects")
async def get_github():
    url = f"https://api.github.com/users/{GITHUB_USER}/repos?sort=updated"
    topic = os.getenv("GITHUB_TOPIC", "portfolio").strip().lower()
    base_headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    headers = dict(base_headers)
    if GITHUB_TOKEN:
        headers["Authorization"] = f"token {GITHUB_TOKEN}"

    async with httpx.AsyncClient() as client:
        resp = await client.get(url, headers=headers)

        # Si el token es inválido o ha expirado, intentar sin autenticación para obtener al menos los repos públicos
        if resp.status_code in (401, 403) and "Authorization" in headers:
            resp = await client.get(url, headers=base_headers)

        if resp.status_code >= 400:
            raise HTTPException(status_code=502, detail="GitHub API unavailable")

        repos = resp.json()
        if not isinstance(repos, list):
            return []

        # Filtrar estrictamente por topic/tag
        filtered = []
        for repo in repos:
            topics = [t.lower() for t in (repo.get("topics") or [])]
            if topic in topics:
                filtered.append(repo)

        return filtered[:6]

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

# PROXY DE CONTACTO: Recibe el form, lo guarda en BD y lo reenvía a Formspree
@app.post("/api/contact")
async def contact_proxy(request: Request, db: Session = Depends(get_db)):
    print(">> Petición recibida. Iniciando escaneo de seguridad...")
    
    try:
        form_data = await request.form()
        data_dict = dict(form_data)
        
        if data_dict.get("_gotcha"):
            print(">> [ALERTA] Bot detectado vía Honeypot. Ejecutando bloqueo silencioso.")
            # Retornamos éxito simulado para que el bot no intente otras rutas
            return {"status": "success", "message": "Feedback received"}

        message = data_dict.get("message", "")
        
        url_pattern = r'(https?://[^\s]+|discord\.(gg|com/invite)/[^\s]+)'
        def neutralize(match):
            return match.group(0).replace(".", " [dot] ")
        
        clean_message = re.sub(url_pattern, neutralize, message, flags=re.IGNORECASE)
        
        spam_keywords = ["nitro", "free steam", "gift code", "free money"]
        if any(key in clean_message.lower() for key in spam_keywords):
            print(">> [ALERTA] Spam por keywords detectado. Bloqueando envío.")
            return {"status": "success", "code": "simulated"}

        data_dict["message"] = clean_message
        data_dict.pop("_gotcha", None)
        
        # Guardado en la base de datos
        db_message = ContactMessage(
            name=data_dict.get("name"),
            email=data_dict.get("email"),
            message=clean_message
        )
        db.add(db_message)
        db.commit()
        
        url = f"https://formspree.io/f/{FORMSPREE_ID}"
        
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                url, 
                data=data_dict, 
                headers={"Accept": "application/json"}
            )
            print(f">> Formspree respondió con estado: {resp.status_code}")
            return resp.json()
            
    except Exception as e:
        print(f"!! ERROR CRÍTICO: {str(e)}")
        return {"error": "Internal Server Error"}, 500

@app.get("/api/whatsapp")
async def contact_whatsapp():
    if not WHATSAPP_NUMBER:
        raise HTTPException(status_code=500, detail="WHATSAPP_NUMBER no configurado")
    if not WHATSAPP_TEXT:
        raise HTTPException(status_code=500, detail="WHATSAPP_TEXT no configurado")

    encoded_text = quote(WHATSAPP_TEXT)
    url = f"https://wa.me/{WHATSAPP_NUMBER}?text={encoded_text}"

    return {"url": url}
