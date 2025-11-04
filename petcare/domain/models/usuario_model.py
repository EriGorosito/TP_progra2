# petcare/domain/models/usuario_model.py
from sqlalchemy import Column, Integer, String
from petcare.core.database import Base
from sqlalchemy.orm import relationship

class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False)
    email = Column(String, unique=True, index=True)
    contrasena_hash = Column(String, nullable=False)
    tipo = Column(String, nullable=False)  # 'cliente' o 'cuidador'

    cuidador = relationship("Cuidador", back_populates="usuario", uselist=False)