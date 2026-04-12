from sqlalchemy import Column, Integer, String, Text, DateTime, JSON
from database import Base
from datetime import datetime

class Project(Base):
    __tablename__ = "projects"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(String, unique=True, index=True)  # ID unico para cada proyecto
    title = Column(String, index=True)
    short_desc = Column(String)
    long_desc = Column(Text)
    tech = Column(JSON)  # Lista de tecnologías usadas, almacenada como JSON
    image = Column(String)  # URL de la imagen del proyecto o ruta local
    link = Column(String)  # Link al proyecto (GitHub, demo, etc.)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class PersonalInfo(Base):
    __tablename__ = "personal_info"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    title = Column(String)  # Ejemplo: "Software Engineer", "Full Stack Developer", etc.
    bio = Column(Text)  # Biografía principal
    short_bio = Column(Text)  # Biografía corta para mostrar en la tarjeta de presentación
    stack = Column(JSON)  # Lista de tecnologías: ["Laravel", "Python", "Docker", ...]
    tools = Column(JSON)  # Lista de herramientas: ["VS Code", "Git", "Linux", ...]
    university = Column(String)
    location = Column(String)  # Ejemplo: "Viña del Mar"
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class ContactMessage(Base):
    __tablename__ = "contact_messages"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    email = Column(String, index=True)
    message = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    read = Column(Integer, default=0)  # 0 = no leído, 1 = leído
