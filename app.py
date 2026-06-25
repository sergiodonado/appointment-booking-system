from connection import SessionLocal, engine
from fastapi import FastAPI, Depends, HTTPException, Query
from tables import User, Professional, p_horarios, appointment
from sqlalchemy.orm import Session, sessionmaker
from datetime import datetime, time, timedelta, timezone, date
import bcrypt, jwt, os
from fastapi.security import HTTPBearer, OAuth2PasswordBearer
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi import Request
from fastapi.responses import FileResponse

DURACION_SLOT =30

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
def index():
    return FileResponse("templates/index.html")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/registro")
def register_user(dni: int, name: str, email_address: str, password: str, telefono: str, db: Session = Depends(get_db)):

    existente = db.query(User).filter(User.dni == dni).first()
    if existente:
        raise HTTPException(status_code=400, detail="El usuario ya existe")
    
    hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

    new_user = User(
        dni=dni,
        name=name,
        email_address=email_address,
        password=hashed_password,
        telefono=telefono,
        fecha_creacion=datetime.now()
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {
    "message": "Usuario registrado exitosamente",
    "dni": new_user.dni,
    "name": new_user.name,
    "email_address": new_user.email_address
}

SECRET_KEY = os.getenv("SECRET_KEY")

@app.post("/login")
def login_user(dni: int, password: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.dni == dni).first()
    if not user:
        raise HTTPException(status_code=400, detail="Usuario no encontrado")
    
    if not bcrypt.checkpw(password.encode(), user.password.encode()):
        raise HTTPException(status_code=400, detail="Contraseña incorrecta")
    
    expiracion = datetime.now(timezone.utc) + timedelta(hours=1)

    payload = {
        "sub": str(user.dni),
        "exp": expiracion
    }

    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
    
    return {
        "message": "Inicio de sesión exitoso",
        "access_token": token,
        "token_type": "bearer"
    }

security = HTTPBearer()

def verifica_token(credenciales = Depends(security)):
    token = credenciales.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return int(payload["sub"])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expirado")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Token inválido")
    
@app.get("/perfil")
def ver_perfil(dni_usuario: int = Depends(verifica_token)):
    return {"tu_dni": dni_usuario}


@app.post("/registro_profesional")
def register_professional(dni: int, name: str, email_address: str, password: str, telefono: str, db: Session = Depends(get_db)):

    existente = db.query(Professional).filter(Professional.dni == dni).first()
    if existente:
        raise HTTPException(status_code=400, detail="El profesional ya existe")
    
    hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

    new_professional = Professional(
        dni=dni,
        name=name,
        email_address=email_address,
        password=hashed_password,
        telefono=telefono,
        fecha_creacion=datetime.now()
    )

    db.add(new_professional)
    db.commit()
    db.refresh(new_professional)

    return {"message": "Profesional registrado exitosamente", "dni": new_professional.dni}

@app.post("/login_profesional")
def login_professional(dni: int, password: str, db: Session = Depends(get_db)):
    professional = db.query(Professional).filter(Professional.dni == dni).first()
    if not professional:
        raise HTTPException(status_code=400, detail="Profesional no encontrado")
    
    if not bcrypt.checkpw(password.encode(), professional.password.encode()):
        raise HTTPException(status_code=400, detail="Contraseña incorrecta")
    
    expiracion = datetime.now(timezone.utc) + timedelta(hours=1)

    payload = {
        "sub": str(professional.dni),
        "exp": expiracion
    }

    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
    
    return {
        "message": "Inicio de sesión exitoso",
        "access_token": token,
        "token_type": "bearer"
    }

@app.post("/crear_p_horario")
def crear_p_horario(dia_semana: str, h_start: time, h_end: time, db: Session = Depends(get_db), professional_dni: int = Depends(verifica_token)):
    profesional = db.query(Professional).filter(Professional.dni == professional_dni).first()
    if not profesional:
        raise HTTPException(status_code=400, detail="Profesional no encontrado")
    
    new_horario = p_horarios(
        professional_dni=professional_dni,
        dia_semana=dia_semana,
        h_start=h_start,
        h_end=h_end,
        duracion_slot=DURACION_SLOT
    )

    db.add(new_horario)
    db.commit()
    db.refresh(new_horario)

    return {"message": "Horario creado exitosamente", "id": new_horario.id}


@app.get("/disponibilidad")
def consultar_disponibilidad(professional_dni: int, fecha: date, db: Session = Depends(get_db)):
    if fecha < date.today():
        raise HTTPException(status_code=400, detail="No puedes consultar disponibilidad en fechas pasadas")
    dias = ["lunes", "martes", "miercoles", "jueves", "viernes", "sabado", "domingo"]
    dia_semana_texto = dias[fecha.weekday()]
    
    horario = db.query(p_horarios).filter(
        p_horarios.professional_dni == professional_dni,
        p_horarios.dia_semana == dia_semana_texto
    ).first()
    
    if not horario:
        raise HTTPException(status_code=404, detail="El profesional no atiende ese día")
    
    actual = datetime.combine(fecha, horario.h_start)
    fin = datetime.combine(fecha, horario.h_end)
    
    slots_posibles = []
    while actual < fin:
        slots_posibles.append(actual.time())
        actual += timedelta(minutes=horario.duracion_slot)
    
    citas_existentes = db.query(appointment).filter(
        appointment.professional_dni == professional_dni,
        appointment.fecha == fecha
    ).all()
    
    horas_ocupadas = [cita.h_start for cita in citas_existentes]
    
    slots_disponibles = [s.strftime("%H:%M") for s in slots_posibles if s not in horas_ocupadas]
    
    return {"fecha": str(fecha), "dia_semana": dia_semana_texto, "slots_disponibles": slots_disponibles}

@app.post("/crear_appointment")
def crear_appointment(professional_dni: int, fecha: date, h_start: time, db: Session = Depends(get_db), user_dni: int = Depends(verifica_token)):

    cita_choque_usuario = db.query(appointment).filter(
    appointment.user_dni == user_dni,
    appointment.fecha == fecha,
    appointment.h_start == h_start,
    appointment.estado == "confirmada"
    ).first()

    if cita_choque_usuario:
        raise HTTPException(status_code=400, detail="Ya tienes una cita agendada a esa misma hora")
    if fecha < date.today():

        raise HTTPException(status_code=400, detail="No puedes agendar citas en fechas pasadas")
    

    profesional = db.query(Professional).filter(Professional.dni == professional_dni).first()
    if not profesional:
        raise HTTPException(status_code=404, detail="Profesional no encontrado")
    
    dias = ["lunes", "martes", "miercoles", "jueves", "viernes", "sabado", "domingo"]
    dia_semana_texto = dias[fecha.weekday()]
    
    horario = db.query(p_horarios).filter(
        p_horarios.professional_dni == professional_dni,
        p_horarios.dia_semana == dia_semana_texto
    ).first()
    
    if not horario:
        raise HTTPException(status_code=400, detail="El profesional no atiende ese día")
    
    if h_start < horario.h_start or h_start >= horario.h_end:
        raise HTTPException(status_code=400, detail="Hora fuera del horario de atención")
    
    cita_existente = db.query(appointment).filter(
    appointment.professional_dni == professional_dni,
    appointment.fecha == fecha,
    appointment.h_start == h_start,
    appointment.estado == "confirmada"  # ← agregar esto
    ).first()
    
    if cita_existente:
        raise HTTPException(status_code=400, detail="Ese horario ya está ocupado")
    
    h_end_calculado = (datetime.combine(fecha, h_start) + timedelta(minutes=horario.duracion_slot)).time()
    
    nueva_cita = appointment(
        user_dni=user_dni,
        professional_dni=professional_dni,
        fecha=fecha,
        h_start=h_start,
        h_end=h_end_calculado,
        estado="confirmada"
    )
    
    db.add(nueva_cita)
    db.commit()
    db.refresh(nueva_cita)
    
    return {"message": "Cita creada exitosamente", "id": nueva_cita.id}

@app.get("/mis_citas")
def consultar_citas(db: Session = Depends(get_db), user_dni: int = Depends(verifica_token)):
    citas = db.query(appointment).filter(
        appointment.user_dni == user_dni
    ).all()
    
    if not citas:
        raise HTTPException(status_code=404, detail="No hay citas pendientes")
    
    resultado = []
    for cita in citas:
        profesional = db.query(Professional).filter(Professional.dni == cita.professional_dni).first()
        
        resultado.append({
            "id": cita.id,
            "profesional": profesional.name,
            "fecha": str(cita.fecha),
            "h_start": str(cita.h_start),
            "h_end": str(cita.h_end),
            "estado": cita.estado
        })
    
    return resultado

@app.delete("/cancelar_cita/{id_cita}")
def cancelar_cita(id_cita: int, db: Session = Depends(get_db), user_dni: int = Depends(verifica_token)):
    cita = db.query(appointment).filter(appointment.id == id_cita).first()
    
    if not cita:
        raise HTTPException(status_code=404, detail="Cita no encontrada")
    
    if cita.user_dni != user_dni:
        raise HTTPException(status_code=403, detail="No puedes cancelar una cita que no es tuya")
    
    cita.estado = "cancelada"
    db.commit()
    
    return {"message": "Cita cancelada exitosamente", "id": cita.id}

@app.get("/profesionales")
def listar_profesionales(db: Session = Depends(get_db)):
    profesionales = db.query(Professional).all()
    return [{"dni": p.dni, "name": p.name} for p in profesionales]

@app.get("/citas_profesional")
def ver_citas_profesional(db: Session = Depends(get_db), professional_dni: int = Depends(verifica_token)):
    citas = db.query(appointment).filter(
        appointment.professional_dni == professional_dni
    ).all()
    
    if not citas:
        raise HTTPException(status_code=404, detail="No hay citas")
    
    resultado = []
    for cita in citas:
        usuario = db.query(User).filter(User.dni == cita.user_dni).first()
        resultado.append({
            "id": cita.id,
            "paciente": usuario.name,
            "fecha": str(cita.fecha),
            "h_start": str(cita.h_start),
            "h_end": str(cita.h_end),
            "estado": cita.estado
        })
    
    return resultado