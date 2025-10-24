# petcare/api/v1/routes/pets.py
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List

from ....schemas.pet_schema import PetCreate, PetOut
from petcare.core import pet_services
from ....domain.usuario import Usuario

# Importa tu "cerradura" de seguridad
from ....core.security import get_current_user

pet_router = APIRouter(
    prefix="/pets",
    tags=["Mascotas"]
)

@pet_router.post("/", 
    response_model=PetOut, 
    status_code=status.HTTP_201_CREATED,
    summary="Registrar una nueva mascota"
)
async def create_new_pet(
    pet_data: PetCreate,
    # ¡LA DEPENDENCIA! FastAPI inyectará aquí al usuario logueado
    current_user: Usuario = Depends(get_current_user) 
):
    """
    Registra una nueva mascota para el usuario 'Cliente' actualmente logueado.
    
    - Requiere autenticación (token JWT).
    - Solo los usuarios de tipo 'Cliente' pueden crear mascotas.
    """
    # 1. Verificar Rol (Precondición de tu doc [cite: 35])
    if current_user.user_type != "Cliente":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo los 'Clientes' pueden registrar mascotas."
        )
        
    # 2. Llamar al servicio
    # Pasamos el pet_data y el ID del usuario que obtuvimos del token
    new_pet = pet_services.create_pet(pet_data, owner_id=current_user.id)
    return new_pet


@pet_router.get("/", 
    response_model=List[PetOut],
    summary="Ver mis mascotas"
)
async def get_my_pets(
    current_user: Usuario = Depends(get_current_user)
):
    """
    Devuelve la lista de mascotas registradas por el usuario logueado.
    
    - Requiere autenticación (token JWT).
    """
    # 1. Verificar Rol
    if current_user.user_type != "Cliente":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo los 'Clientes' pueden ver sus mascotas."
        )

    # 2. Llamar al servicio
    pets = pet_services.get_pets_by_owner(owner_id=current_user.id)
    return pets