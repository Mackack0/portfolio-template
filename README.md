# Portfolio Full-Stack Template
Este es un template base para un portafolio personal utilizando una arquitectura de microservicios con Docker.

## Arquitectura
- **Frontend**: Nginx (Alpine) sirviendo HTML/JS estático.
- **Backend**: Python FastAPI para manejo de APIs (GitHub & Clima).
- **Proxy**: Nginx Proxy Manager para gestión de dominios y SSL.

## Despliegue
1. Clonar el repositorio.
2. Crear un archivo `.env` basado en `.env.example`.
3. Ejecutar `docker-compose up -d`.
