from connection import engine
from sqlalchemy import ForeignKey, Integer, String, DateTime, Time, create_engine
from sqlalchemy.orm import DeclarativeBase, mapped_column, Mapped
from datetime import datetime, time



class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"

    dni: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(80), nullable=False)
    email_address: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    telefono: Mapped[str] = mapped_column(String(20), nullable=False)
    fecha_creacion: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    def __repr__(self) -> str:
        return f"User(id={self.dni}, name='{self.name}', email_address='{self.email_address}')"

class Professional(Base):
    __tablename__ = "professionals"

    dni: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(80), nullable=False)
    email_address: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    telefono: Mapped[str] = mapped_column(String(20), nullable=False)
    fecha_creacion: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    def __repr__(self) -> str:
        return f"Professional(id={self.dni}, name='{self.name}', email_address='{self.email_address}')"


class p_horarios(Base):
    __tablename__ = "p_horarios"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    professional_dni: Mapped[int] = mapped_column(Integer, ForeignKey("professionals.dni"), nullable=False)
    dia_semana: Mapped[str] = mapped_column(String(20), nullable=False)  # "lunes", "martes", etc.
    h_start: Mapped[time] = mapped_column(Time, nullable=False)
    h_end: Mapped[time] = mapped_column(Time, nullable=False)
    duracion_slot: Mapped[int] = mapped_column(Integer, nullable=False)  # en minutos, ej. 30

    def __repr__(self) -> str:
        return f"PHorario(id={self.id}, professional_dni={self.professional_dni}, dia_semana='{self.dia_semana}', h_start='{self.h_start}', h_end='{self.h_end}', duracion_slot={self.duracion_slot})"
    
class appointment(Base):
    __tablename__ = "appointments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_dni: Mapped[int] = mapped_column(Integer, ForeignKey("users.dni"), nullable=False)
    professional_dni: Mapped[int] = mapped_column(Integer, ForeignKey("professionals.dni"), nullable=False)
    fecha: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    h_start: Mapped[time] = mapped_column(Time, nullable=False)
    h_end: Mapped[time] = mapped_column(Time, nullable=False)
    estado: Mapped[str] = mapped_column(String(20), default="confirmada")

    def __repr__(self) -> str:
        return f"Appointment(id={self.id}, user_dni={self.user_dni}, professional_dni={self.professional_dni}, fecha='{self.fecha}', h_start='{self.h_start}')"

Base.metadata.create_all(engine)