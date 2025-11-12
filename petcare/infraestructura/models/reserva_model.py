from sqlalchemy import Column, Integer, ForeignKey, Date, String, Table
from sqlalchemy.orm import relationship

#Importaciones locales
from petcare.core.database import Base
from .mascota_model import Mascota

# Tabla intermedia para la relación muchos-a-muchos
reserva_mascota = Table(
    "reserva_mascota",
    Base.metadata,
    Column("reserva_id", Integer, ForeignKey("reservas.id")),
    Column("mascota_id", Integer, ForeignKey("mascotas.id"))
)


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
