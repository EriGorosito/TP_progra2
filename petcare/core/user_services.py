# petcare/core/user_services.py 

from petcare.core.map_services import GeoService
from sqlalchemy.orm import Session
from fastapi import HTTPException, status 

# Importar la UTILIDAD de Seguridad para hashing
from ..core.security import get_password_hash 

# Importar el modelo de Persistencia (ORM)
from ..domain.models.usuario_model import Usuario as UsuarioModel 

# Importar los esquemas Pydantic
from ..schemas.user_schema import UserCreate

# Nota: La lógica de Dominio (usuario.py) no se importa aquí, solo la seguridad.

def get_user_by_email(db: Session, email: str) -> UsuarioModel | None:
    """Busca un usuario en la DB real por email."""
    return db.query(UsuarioModel).filter(UsuarioModel.email == email).first()


def create_user_account(db: Session, user_data: UserCreate) -> UsuarioModel:
    """
    Crea un nuevo usuario y lo guarda en la DB real.
    """
    
    # 1. Validar unicidad (Consulta a la DB)
    if get_user_by_email(db, user_data.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El email ya está registrado."
        )
        

    # 2. HASHING DE CONTRASEÑA (Llamamos a la capa de seguridad)
    contrasena_hash = get_password_hash(user_data.contrasena)

    # 3. geocode
    coords = GeoService.geocode(user_data.direccion)
    if not coords:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se encontró la dirección. Por favor verifique o ingrese otra."
        )

    lat, lon = coords
    
    # 4. Armar URL de verificación de mapa
    map_url = f"https://www.openstreetmap.org/?mlat={lat}&mlon={lon}#map=16/{lat}/{lon}"

    # 5. CREAR INSTANCIA DEL MODELO ORM (Persistencia)
    # Ya no necesitas las subclases ClienteModel/CuidadorModel si usas la Tabla Única
    NewUserModel = UsuarioModel(
        nombre=user_data.nombre,
        email=user_data.email,
        contrasena_hash=contrasena_hash,  # <- Usamos el hash seguro
        tipo=user_data.tipo.lower(), # Guarda 'cliente' o 'cuidador'
        direccion=user_data.direccion,
        lat=lat,
        lon=lon,
        map_url=map_url
    )

    # 6. Persistir en la DB
    db.add(NewUserModel)
    db.commit()
    db.refresh(NewUserModel) 

    return NewUserModel