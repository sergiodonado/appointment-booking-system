# Sistema de Reservas de Citas

Aplicación web para gestión de citas entre usuarios y profesionales. Permite a los usuarios consultar disponibilidad y agendar citas, mientras que los profesionales gestionan sus horarios de atención.


## Stack tecnológico

**Backend**
- Python 3.13
- FastAPI — framework para la API REST
- SQLAlchemy — ORM para manejo de base de datos
- PostgreSQL — base de datos relacional
- JWT (PyJWT) — autenticación y autorización
- bcrypt — hash seguro de contraseñas

**Frontend**
- HTML5, CSS3, JavaScript (Vanilla)
- Fetch API para comunicación con el backend

## Funcionalidades

**Usuarios**
- Registro e inicio de sesión con autenticación JWT
- Consulta de disponibilidad de profesionales por fecha
- Agendamiento de citas en slots disponibles
- Visualización y cancelación de citas propias

**Profesionales**
- Registro e inicio de sesión independiente
- Configuración de horarios de atención por día de la semana
- Visualización de citas agendadas con sus pacientes

## Seguridad
- Contraseñas hasheadas con bcrypt (nunca texto plano)
- Autenticación mediante JWT con expiración de 1 hora
- Rutas protegidas — el usuario solo puede ver/cancelar sus propias citas
- Validaciones en el backend (fechas pasadas, choques de horario, slots ocupados)

## Instalación

### Requisitos previos
- Python 3.13+
- PostgreSQL instalado y corriendo

### Pasos

1. Clonar el repositorio
```bash
git clone https://github.com/sergiodonado/appointment-booking-system.git
cd sistema-citas
```

2. Instalar dependencias
```bash
pip install -r requirements.txt
```

3. Crear el archivo `.env` en la raíz del proyecto
```
USER_NAME=postgres
PASSWORD=tu_contraseña
HOST=localhost
PORT=5432
DATABASE_NAME=nombre_de_tu_bd
SECRET_KEY=tu_clave_secreta
DURACION_SLOT=30
```

4. Crear la base de datos en PostgreSQL
```sql
CREATE DATABASE nombre_de_tu_bd;
```

5. Correr la aplicación
```bash
python -m uvicorn app:app --reload
```

6. Abrir en el navegador
```
http://127.0.0.1:8000
```

## Endpoints principales

| Método | Ruta | Descripción | Protegido |
|--------|------|-------------|-----------|
| POST | `/registro` | Registro de usuario | No |
| POST | `/login` | Login de usuario | No |
| POST | `/registro_profesional` | Registro de profesional | No |
| POST | `/login_profesional` | Login de profesional | No |
| GET | `/profesionales` | Lista de profesionales | No |
| GET | `/disponibilidad` | Slots disponibles de un profesional | Sí |
| POST | `/crear_appointment` | Crear una cita | Sí |
| GET | `/mis_citas` | Ver citas del usuario autenticado | Sí |
| DELETE | `/cancelar_cita/{id}` | Cancelar una cita | Sí |
| POST | `/crear_p_horario` | Crear horario de atención | Sí (profesional) |
| GET | `/citas_profesional` | Ver citas del profesional autenticado | Sí (profesional) |

La documentación interactiva completa está disponible en `http://127.0.0.1:8000/docs`

## Estructura del proyecto

```
sistema-citas/
├── app.py              # Endpoints y lógica de la API
├── tables.py           # Modelos de base de datos (SQLAlchemy ORM)
├── connection.py       # Conexión a PostgreSQL
├── static/
│   ├── script.js       # Lógica del frontend
│   └── styles.css      # Estilos
├── templates/
│   └── index.html      # Interfaz de usuario
├── .env                # Variables de entorno (no incluido en el repo)
├── requirements.txt    # Dependencias
└── README.md
```

## Modelo de datos

```
users ──────────────────────────── appointments
professionals ──┬─── p_horarios        │
                └───────────────── appointments
```

- `users`: pacientes/usuarios del sistema
- `professionals`: profesionales que ofrecen el servicio
- `p_horarios`: horarios de atención semanales por profesional (día, hora inicio, hora fin, duración del slot)
- `appointments`: citas agendadas (usuario + profesional + fecha + hora)
