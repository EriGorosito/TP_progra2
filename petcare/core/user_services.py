from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from petcare.core.map_services import GeoService
from petcare.core.security import get_password_hash
from petcare.infraestructura.factories.factory_usuario import UserFactory
from petcare.infraestructura.models.usuario_model import Usuario as UsuarioModel
from petcare.schemas.user_schema import UserCreate


def get_user_by_email(db: Session, email: str) -> UsuarioModel | None:
    """Busca un usuario en la DB real por email."""
    return db.query(UsuarioModel).filter(UsuarioModel.email == email).first()


def create_user_account(db: Session, user_data):
    """
    Crea una nueva cuenta de usuario (Cliente o Cuidador)
    verificando unicidad del email y geocodificando la dirección.
    """
    # Verificar que el email no exista
    if get_user_by_email(db, user_data.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El email ya está registrado."
        )
   
    # Hashear la contraseña
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

    # Crear usuario con la Factory
    try:
        user = UserFactory.create_user(
            tipo=user_data.tipo,
            nombre=user_data.nombre,
            email=user_data.email,
            contrasena_hash=contrasena_hash,
            direccion=user_data.direccion,
            lat=lat,
            lon=lon,
            map_url=map_url
        )

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    db.add(user)
    db.commit()
    db.refresh(user)
    return user
