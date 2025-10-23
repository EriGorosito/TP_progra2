# petcare/core/pet_service.py
from typing import List
from ..domain.mascota import Mascota
from ..schemas.pet_schema import PetCreate

# --- Simulación de Base de Datos de Mascotas ---
MOCK_PETS: List[Mascota] = []
next_pet_id = 1
# -----------------------------------------------

def create_pet(pet_data: PetCreate, owner_id: int) -> Mascota:
    """
    Crea un nuevo perfil de mascota y lo asocia a su dueño.
    """
    global next_pet_id
    
    new_pet = Mascota(
        id=next_pet_id,
        nombre=pet_data.nombre,
        especie=pet_data.especie,
        raza=pet_data.raza,
        edad=pet_data.edad,
        peso=pet_data.peso,
        caracteristicas_especiales=pet_data.caracteristicas_especiales,
        owner_id=owner_id # ¡Asocia al dueño!
    )
    
    MOCK_PETS.append(new_pet)
    next_pet_id += 1
    
    print(f"Mascota creada: {new_pet.nombre} (Dueño ID: {owner_id})")
    return new_pet

def get_pets_by_owner(owner_id: int) -> List[Mascota]:
    """
    Devuelve la lista de mascotas de un dueño específico.
    """
    return [pet for pet in MOCK_PETS if pet.owner_id == owner_id]