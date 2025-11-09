# petcare/domain/models/resena_model.py

# from sqlalchemy import Column, Integer, ForeignKey, String
# from petcare.core.database import Base
from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from petcare.core.database import Base

# class Resena(Base):
#     __tablename__ = "resenas"

#     id = Column(Integer, primary_key=True)
#     cliente_id = Column(Integer, ForeignKey("usuarios.id"))
#     cuidador_id = Column(Integer, ForeignKey("usuarios.id"))
#     puntaje = Column(Integer, nullable=False)
#     comentario = Column(String)

class Resena(Base):
    __tablename__ = "resenas"

    id = Column(Integer, primary_key=True, index=True)
    puntaje = Column(Integer, nullable=False)     # 1–5
    comentario = Column(Text, nullable=True)

    cliente_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    cuidador_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)

    reserva_id = Column(Integer, ForeignKey("reservas.id"), nullable=False)

    cliente = relationship("Usuario", foreign_keys=[cliente_id])
    cuidador = relationship("Usuario", foreign_keys=[cuidador_id])
    reserva = relationship("Reserva", back_populates="resena")