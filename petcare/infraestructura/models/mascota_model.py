# petcare/infraestructura/mascota_model.py
from sqlalchemy import Column, Integer, String, Float, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship

from petcare.core.database import Base
from petcare.domain.especie import Especie
from .reserva_model import reserva_mascota

class Mascota(Base):
    __tablename__ = "mascotas"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False)
    especie = Column(SQLEnum(Especie, name="especie_enum"), nullable=False)
    raza = Column(String)
    edad = Column(Integer)
    peso = Column(Float)
    caracteristicas_especiales = Column(String)

    # Relación con Usuario
    owner_id = Column(Integer, ForeignKey("usuarios.id"))
    owner = relationship("Usuario")

    reservas = relationship(
        "Reserva",
        secondary=reserva_mascota,
        back_populates="mascotas" # <--- APUNTA DE VUELTA A 'mascotas'
    )

