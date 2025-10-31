# petcare/domain/mascota.py
from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from petcare.core.database import Base

class Mascota(Base):
    __tablename__ = "mascotas"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False)
    especie = Column(String, nullable=False)
    raza = Column(String)
    edad = Column(Integer)
    peso = Column(Float)
    caracteristicas_especiales = Column(String)

    # Relación con Usuario
    owner_id = Column(Integer, ForeignKey("usuarios.id"))
    owner = relationship("Usuario")
