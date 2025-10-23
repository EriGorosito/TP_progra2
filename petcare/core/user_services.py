# petcare/core/user_service.py
from typing import List, Union

# Importar las clases de dominio (donde se define el hashing de contraseñas)
from petcare.domain.usuario import Usuario, Cliente, Cuidador

# Importar los esquemas Pydantic para la entrada de datos (register)
from petcare.schemas.user_schema import UserCreate

# MOCK: Simulación de la "Base de Datos" en memoria
# Usamos List[Usuario] para indicar que almacena objetos de nuestras clases de dominio
MOCK_USERS: List[Usuario] = []
next_id = 1 # Contador para simular IDs únicos/clave primaria

def get_user_by_email(email: str) -> Union[Usuario, None]:
    """
    Busca un usuario en la 'DB' por email.
    Se usa para validar unicidad (registro) y verificar credenciales (login).
    """
    for user in MOCK_USERS:
        if user.email == email:
            return user
    return None

def create_user_account(user_data: UserCreate) -> Usuario:
    """
    Crea un nuevo usuario (Cliente o Cuidador), valida unicidad y lo guarda.
    
    Args:
        user_data: Objeto Pydantic UserCreate con email, nombre, contraseña y tipo.

    Returns:
        El objeto Usuario (Cliente o Cuidador) recién creado.

    Raises:
        ValueError: Si el email ya está registrado.
    """
    global next_id
    
    # 1. Validar unicidad de email (Flujo Principal: Sistema valida unicidad de email)
    if get_user_by_email(user_data.email):
        raise ValueError("El email ya está registrado.")
        
    # 2. Crear instancia de Cliente o Cuidador (Flujo Principal: Sistema crea cuenta)
    if user_data.user_type == "Cliente":
        NewUser = Cliente(
            nombre=user_data.nombre,
            email=user_data.email,
            contraseña=user_data.contrasena
        )
    elif user_data.user_type == "Cuidador":
        NewUser = Cuidador(
            nombre=user_data.nombre,
            email=user_data.email,
            contraseña=user_data.contrasena
        )
    else:
        # Esto es una validación de redundancia, Pydantic ya lo limita con Literal
        raise ValueError("Tipo de usuario inválido.") 

    # 3. Asignar ID (simulación de DB)
    # Usamos setattr para añadir el atributo 'id' a la instancia
    setattr(NewUser, 'id', next_id) 
    next_id += 1

    # 4. Guardar en 'DB'
    MOCK_USERS.append(NewUser)
    
    # 5. Envío de email de confirmación (PENDIENTE - Flujo Principal: Sistema envía email de confirmación)
    # En una implementación real, esto llamaría a un servicio de envío de emails (ej: SendGrid, Mailgun)
    print(f"DEBUG: Email de confirmación simulado enviado a {NewUser.email}")

    return NewUser

# NOTA: La lógica de verificación de contraseña (verify_password) 
# reside en la clase Usuario (petcare/domain/usuarios.py).