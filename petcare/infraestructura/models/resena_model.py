from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship

#Importacciones locales
from petcare.core.database import Base

class Resena(Base):
    __tablename__ = "resenas"

    id = Column(Integer, primary_key=True, index=True)
    puntaje = Column(Integer, nullable=False)     
    comentario = Column(Text, nullable=True)

    cliente_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    cuidador_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    reserva_id = Column(Integer, ForeignKey("reservas.id"), nullable=False, unique=True)

    cliente = relationship("Usuario", foreign_keys=[cliente_id])
    cuidador = relationship("Usuario", foreign_keys=[cuidador_id])
    reserva = relationship("Reserva", back_populates="resena")