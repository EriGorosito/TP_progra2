# petcare/domain/models/resena_model.py
from sqlalchemy import Column, Integer, ForeignKey, String
from petcare.core.database import Base

class Resena(Base):
    __tablename__ = "resenas"

    id = Column(Integer, primary_key=True)
    cliente_id = Column(Integer, ForeignKey("usuarios.id"))
    cuidador_id = Column(Integer, ForeignKey("usuarios.id"))
    puntaje = Column(Integer, nullable=False)
    comentario = Column(String)