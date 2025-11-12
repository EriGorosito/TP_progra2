from sqlalchemy import Column, Integer, ForeignKey, Date, String, Table
from sqlalchemy.orm import relationship

#Importaciones locales
from petcare.core.database import Base
from .mascota_model import Mascota
from .tablas_asociacion import reserva_mascota



class Reserva(Base):
    __tablename__ = "reservas"

    id = Column(Integer, primary_key=True)
    cliente_id = Column(Integer, ForeignKey("usuarios.id"))
    cuidador_id = Column(Integer, ForeignKey("usuarios.id"))
    fecha_inicio = Column(Date, nullable=False)
    fecha_fin = Column(Date, nullable=False)
    estado = Column(String, default="pendiente")

    cliente = relationship("Usuario", foreign_keys=[cliente_id])
    cuidador = relationship("Usuario", foreign_keys=[cuidador_id])
    mascotas = relationship("Mascota", secondary=reserva_mascota, back_populates="reservas")
    resena = relationship("Resena", back_populates="reserva", uselist=False)
