#!/usr/bin/env python3
"""
Seed script to initialize the database with default data and environment values.
Run this once to populate the database with initial projects and personal info.
"""

import sys
import os
sys.path.insert(0, '/home/TU_USUARIO/portfolio/backend')

from database import SessionLocal, init_db
from models import Project, PersonalInfo
from dotenv import load_dotenv

load_dotenv()

# Inicializa la base de datos (crea tablas si no existen)
init_db()

# Crea una sesión de base de datos
db = SessionLocal()

try:
    # Revisa si la información personal ya existe para evitar duplicados
    existing_info = db.query(PersonalInfo).first()
    if not existing_info:
        # Crea la información personal a partir de los datos en .env o valores por defecto
        personal_info = PersonalInfo(
            name="Tu Nombre",
            title="",
            short_bio="",
            bio="",
            stack=["", "", "", "", ""],
            tools=["", "", ""],
            university="",
            location=""
        )
        db.add(personal_info)
        print("✓ Created personal info")
    else:
        print("ℹ Personal info already exists")

    # Revisa si los proyectos ya existen para evitar duplicados
    existing_projects = db.query(Project).count()
    if existing_projects == 0:
        # Crea los proyectos por defecto (puedes editar estos datos para que reflejen tus proyectos reales desde la vista de administración)
        projects = [
            {
            "project_id": 'proyecto-1',
            "title": 'Nombre del Proyecto 1',
            "short_desc": 'Descripción breve del proyecto para mostrar en la tarjeta.',
            "long_desc": 'Explica aquí el objetivo del proyecto, cómo lo construiste y qué problema resuelve. Puedes incluir decisiones técnicas, resultados y próximos pasos.',
            "tech": ['Tecnologia 1', 'Tecnologia 2', 'Tecnologia 3'],
            "image": '/img/proyecto1.png',
            "link": 'https://github.com/tu-usuario/tu-repo'
        },
        {
            "project_id": 'proyecto-2',
            "title": 'Nombre del Proyecto 2',
            "short_desc": 'Otra descripción corta con foco en impacto o funcionalidad.',
            "long_desc": 'Usa este bloque para contar el contexto del proyecto, su arquitectura y los aprendizajes clave. Mantén un tono claro y directo.',
            "tech": ['Framework', 'Backend', 'Frontend', 'Cloud'],
            "image": 'https://via.placeholder.com/600x400/111/00ff00?text=Proyecto+2',
            "link": 'https://github.com/tu-usuario/otro-repo'
        }
        ]

        for p in projects:
            project = Project(**p)
            db.add(project)
            print(f"✓ Created project: {p['title']}")
    else:
        print(f"ℹ Database already contains {existing_projects} project(s)")

    db.commit()
    print("\n✓ Database initialization complete!")
    print("✓ Login to admin panel with password:", os.getenv('ADMIN_PASSWORD', 'admin123'))

except Exception as e:
    db.rollback()
    print(f"✗ Error: {e}")
    sys.exit(1)
finally:
    db.close()
