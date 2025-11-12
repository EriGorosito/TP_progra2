from sqlalchemy import Column, Integer, String, Float, ForeignKey, JSON
from sqlalchemy.orm import relationship

from petcare.core.database import Base


class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    contrasena_hash = Column(String, nullable=False)
    tipo = Column(String, nullable=False)  # Define el tipo polimórfico: "cliente" o "cuidador"
    direccion = Column(String)
    lat = Column(Float)
    lon = Column(Float)
    map_url = Column(String)

    __mapper_args__ = {
        "polymorphic_on": tipo,
        "polymorphic_identity": "usuario"
    }


class Cliente(Usuario):
    __tablename__ = "clientes"

    id = Column(Integer, ForeignKey("usuarios.id"), primary_key=True)
    
    mascotas = relationship("Mascota", back_populates="owner")
   
    __mapper_args__ = {
        "polymorphic_identity": "cliente"
    }


class Cuidador(Usuario):
    __tablename__ = "cuidadores"

    id = Column(Integer, ForeignKey("usuarios.id"), primary_key=True)
    descripcion = Column(String, nullable=True)
    servicios = Column(JSON, nullable=True)  # lista de especies
    tarifas = Column(JSON, nullable=True)    # especie -> precio por día
    dias_no_disponibles = Column(JSON, nullable=True)

    __mapper_args__ = {
        "polymorphic_identity": "cuidador"
    }


