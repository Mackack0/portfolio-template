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

## Tailwind (instalación local)

1. Instalar dependencias en la raíz del proyecto: `npm install`.
2. Generar CSS una vez: `npm run build:css`.
3. Durante desarrollo, usar modo watch: `npm run watch:css`.
4. `npm install` también genera automáticamente `package-lock.json`.

El archivo generado queda en `html/styles.css`, que es servido por Nginx.
