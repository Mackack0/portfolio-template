# Guía de Configuración del Panel de Administración del Portfolio

## Qué cambió

El portafolio se actualizó de un único archivo HTML con contenido fijo a un sistema dinámico con:

- **Base de datos**: SQLite almacena proyectos, información personal y mensajes de contacto.
- **Panel de administración**: [https://tu-dominio/admin.html](https://tu-dominio/admin.html) o solo /admin si aplicaste la configuracion de nginx.
- **Backend API**: FastAPI ahora entrega contenido dinámico en lugar de archivos estáticos.
- **Actualizaciones instantáneas**: Los cambios en el panel de administración se aplican de inmediato sin volver a desplegar.

## Configuración inicial

### 0. Ajustar rutas del servidor (obligatorio)

Antes de levantar el proyecto, alinea todas las rutas hardcodeadas para que apunten a TU servidor.
Ahora mismo hay una mezcla de rutas (`/home/opc/...` y `/home/tu_usuario/...`) que puede romper backup, seed y lectura de base de datos.

Define una sola base, por ejemplo:

```bash
/home/TU_USUARIO/portfolio
```

Y actualiza estos archivos para que usen la misma ruta base:

1. `backend/main.py`: `backup_path`, `original_db` y `cwd` dentro de `POST /api/admin/deploy`.

1. `backend/database.py`: `DATABASE_URL` (ruta del archivo `portfolio.db`).

1. `backend/seed.py`: `sys.path.insert(...)` (ruta del backend en el servidor).

1. `docker-compose.yml`: volumen de backend para `./data` (debe apuntar al mismo path que usa `DATABASE_URL`).

Si estas rutas no coinciden entre sí, el panel puede "funcionar" pero leer/escribir en archivos distintos.

### 1. Actualizar dependencias

El backend ahora requiere SQLAlchemy y paquetes adicionales. Ya están agregados en `requirements.txt`, pero reinstala:

```bash
cd /home/TU_USUARIO/portfolio
pip install -r backend/requirements.txt
```

### 2. Inicializar base de datos

Ejecuta el script de seed para poblar la base de datos con datos iniciales:

```bash
python backend/seed.py
```

Esto crea:

- Información personal por defecto (nombre, bio, stack, universidad, ubicación).
- Proyectos por defecto.

### 3. Definir contraseña de administrador

Cambia la contraseña de administrador por defecto en `backend/.env`:

```dotenv
ADMIN_PASSWORD=tu_contrasena_segura_aqui
```

⚠️ Importante: si no defines `ADMIN_PASSWORD`, el backend usa `admin123` como fallback.
Debes cambiarlo antes de publicar o exponer el panel admin a internet.

Mantenla en secreto. Esta contraseña protege el panel de administración.

### 4. Reiniciar contenedores

Reconstruye y reinicia para aplicar el nuevo código:

```bash
docker compose up -d --build
```

## Uso del panel de administración

### Acceso

1. Ve a [http://tu-dominio/admin.html](http://tu-dominio/admin.html)
2. Ingresa tu contraseña de administrador.
3. Quedarás autenticado durante la sesión.

### Funcionalidades

### Pestaña Resumen

- Estadísticas rápidas: total de mensajes, mensajes no leídos y total de proyectos.

### Pestaña Información personal

- Edita nombre, título, bio, stack tecnológico, herramientas, universidad y ubicación.
- Los cambios aparecen al instante en la página principal.

### Pestaña Proyectos

- Agrega nuevos proyectos con título, descripción, tecnologías, URL de imagen y enlace de GitHub.
- Edita proyectos existentes.
- Elimina proyectos.
- Los cambios aparecen al instante en la página principal.

### Pestaña Mensajes

- Visualiza todos los envíos del formulario de contacto.
- Marca mensajes como leídos.
- Consulta email, fecha/hora y contenido del mensaje.

### Pestaña Deploy

- Reconstruye y reinicia todos los contenedores Docker.
- Crea automáticamente un respaldo de la base de datos antes de desplegar.
- Úsala cuando cambies CSS, código o dependencias.

## Estructura de archivos

```text
backend/
  main.py              (Aplicación FastAPI con todos los endpoints)
  models.py            (Modelos de base de datos con SQLAlchemy)
  schemas.py           (Esquemas de solicitud/respuesta con Pydantic)
  database.py          (Configuración de base de datos)
  seed.py              (Script de carga inicial)
  requirements.txt     (Actualizado con SQLAlchemy, passlib, etc.)

data/
  portfolio.db         (Base de datos SQLite, creada en el primer inicio)
  portfolio_backup_*.db (Respaldos automáticos antes de desplegar)

html/
  index.html           (Ahora obtiene datos de la API)
  admin.html           (NUEVO - Panel de administración)

```

## Endpoints de la API

### Endpoints públicos (sin autenticación)

- `GET /api/status` - Estado del backend.
- `GET /api/projects` - Todos los proyectos.
- `GET /api/personal-info` - Información personal.
- `GET /api/github-projects` - Repositorios de GitHub con el topic "portfolio".
- `GET /api/weather` - Clima actual.
- `GET /api/discord-status` - Presencia de Discord.
- `GET /api/public-config` - Configuración pública del frontend (DISCORD_ID, CITY, WAKATIME_URL).
- `GET /api/whatsapp` - Enlace de WhatsApp.
- `POST /api/contact` - Envía formulario de contacto (guarda en base de datos y envía a Formspree).

### Endpoints de administración (requieren autorización: `Bearer {admin_password}`)

- `POST /api/admin/projects` - Crear proyecto.
- `PUT /api/admin/projects/{project_id}` - Actualizar proyecto.
- `DELETE /api/admin/projects/{project_id}` - Eliminar proyecto.
- `POST /api/admin/personal-info` - Crear/actualizar información personal.
- `PUT /api/admin/personal-info` - Actualizar información personal.
- `GET /api/admin/messages` - Obtener todos los mensajes de contacto.
- `PUT /api/admin/messages/{message_id}` - Marcar mensaje como leído.
- `POST /api/admin/deploy` - Desplegar app (respaldo + reconstrucción con docker compose).

## Flujo de trabajo

### Hacer un cambio

**Si es contenido (proyectos, bio, stack, etc.):**

1. Inicia sesión en el panel de administración.
2. Edita el contenido.
3. Haz clic en guardar.
4. Los cambios aparecen al instante en el sitio público.

**Si es código, CSS o dependencias:**

1. Realiza los cambios localmente o en el código.
2. Ve al panel de administración -> pestaña Deploy.
3. Haz clic en "Deploy Now".
4. Espera a que termine la compilación.
5. Los cambios se publican.

**El botón Deploy:**

- Crea un respaldo de la base de datos en `data/portfolio_backup_TIMESTAMP.db`.
- Ejecuta `docker compose up -d --build`.
- Reconstruye todos los contenedores.
- Tarda aproximadamente 1-2 minutos.

## Respaldo y recuperación

Los respaldos de base de datos se crean automáticamente antes de cada despliegue. Se guardan en `/data/` con marca de tiempo:

```text
portfolio_backup_20260407_143022.db
portfolio_backup_20260407_142500.db
```

Para restaurar un respaldo:

```bash
cp /home/TU_USUARIO/portfolio/data/portfolio_backup_TIMESTAMP.db /home/TU_USUARIO/portfolio/data/portfolio.db
docker compose restart portfolio-backend
```

## Configuración pública en `.env`

La configuración pública del frontend ahora se define en `backend/.env` y se expone mediante `GET /api/public-config`.

Variables públicas soportadas:

- `DISCORD_ID`
- `CITY`
- `WAKATIME_URL`

Además, `GITHUB_TOPIC` sigue leyéndose desde `backend/.env` para filtrar repositorios en `GET /api/github-projects`.

## Solución de problemas

**No puedes acceder al panel de administración?**

- Asegúrate de usar la contraseña correcta de `backend/.env`.
- Verifica que el backend esté corriendo con `docker ps`.

**No aparecen los cambios?**

- Limpia la caché del navegador (Ctrl+Shift+Delete).
- Fuerza recarga (Ctrl+Shift+R).
- Revisa la consola del navegador por errores (F12).

**La base de datos está bloqueada?**

- No debería pasar, pero si ocurre: `docker compose restart portfolio-backend`.

**Perdiste datos?**

- Restaura desde un respaldo en `/data/`.

## Próximos pasos

1. Cambia la contraseña de administrador en `backend/.env` por una segura.
2. Ejecuta `python backend/seed.py` para inicializar la base de datos.
3. Reconstruye con `docker compose up -d --build`.
4. Visita `/admin.html` y empieza a editar.

## Notas de seguridad

- El panel de administración corre sobre HTTP por defecto. Si lo expones a internet, configura HTTPS (Nginx Proxy Manager lo gestiona).
- La contraseña de admin se envía en el header HTTP Authorization. Usa una contraseña robusta.
- El archivo de base de datos está en `/data/`, montado al contenedor backend. Protege tus secretos.
- Los mensajes de contacto se almacenan en la base de datos y solo son visibles en el panel admin.

## Preguntas?

Revisa el [README.md](README.md) principal para las instrucciones originales de configuración.
