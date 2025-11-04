from sqlalchemy import Column, Integer, String, ForeignKey, JSON, Enum as SQLEnum
from sqlalchemy.orm import relationship
from petcare.core.database import Base
from petcare.domain.especie import Especie

class Cuidador(Base):
    __tablename__ = "cuidadores"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), unique=True)
    descripcion = Column(String, nullable=True)
    servicios = Column(JSON, nullable=True)  # lista de especies
    tarifas = Column(JSON, nullable=True)    # especie -> precio por día
    dias_no_disponibles = Column(JSON, nullable=True)

    usuario = relationship("Usuario", back_populates="cuidador")

    # @property
    # def especies_enum(self):
    #     from petcare.domain.especie import Especie
    #     return [Especie(s) for s in self.servicios]