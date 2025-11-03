
from typing import List
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

# Importar el Modelo ORM (Asumo que lo renombraste a mascota_model)
from ..domain.models.mascota_model import Mascota as MascotaModel 
from ..schemas.pet_schema import PetCreate # Importa tu esquema Pydantic

from petcare.domain.observer import event_manager
from petcare.domain.models.usuario_model import Usuario as UsuarioModel


def create_pet(db: Session, pet_data: PetCreate, current_user: UsuarioModel) -> MascotaModel:
    """
    Crea un nuevo perfil de mascota y lo asocia a su dueño, guardándolo en la DB.
    """
    
    # 1. Crear instancia del Modelo ORM
    # La desestructuración usa los atributos de PetCreate y añadimos owner_id
    db_pet = MascotaModel(
        nombre=pet_data.nombre,
        especie=pet_data.especie,
        raza=pet_data.raza,
        edad=pet_data.edad,
        peso=pet_data.peso,
        caracteristicas_especiales=pet_data.caracteristicas_especiales,
        owner_id=current_user.id # <--- Clave Foránea del dueño autenticado
    )
    
    # 2. Persistir en la DB
    db.add(db_pet)
    db.commit()
    db.refresh(db_pet) # Para obtener el ID generado automáticamente por la DB

    event_manager.notify("mascota_registrada", {
        "owner": current_user, 
        "pet": db_pet
    })

    return db_pet

def get_pets_by_owner(db: Session, owner_id: int) -> List[MascotaModel]:
    """
    Devuelve la lista de mascotas de un dueño específico consultando la DB.
    """
    # Consulta a SQLAlchemy: Filtra por el owner_id
    return db.query(MascotaModel).filter(MascotaModel.owner_id == owner_id).all()
