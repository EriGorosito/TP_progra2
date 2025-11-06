# #test/test_registro_ubicacion.py
# import pytest
# from httpx import AsyncClient


# @pytest.mark.asyncio
# async def test_registrar_usuario_con_ubicacion(app):
#     """
#     Crea un usuario con una dirección y verifica que
#     se transforma correctamente en lat y lon.
#     """

#     user_data = {
#         "nombre": "Juan",
#         "email": "juan@example.com",
#         "direccion": "Av. Santa Fe 123, CABA"
#     }

#     async with AsyncClient(app=app, base_url="http://test") as ac:
#         resp = await ac.post("/users/", json=user_data)

#     assert resp.status_code == 201
#     result = resp.json()

#     assert "lat" in result
#     assert "lon" in result
#     assert result["direccion"] == user_data["direccion"]


# @pytest.mark.asyncio
# async def test_actualizar_ubicacion_usuario(app):
#     """Actualiza la dirección → cambia lat/lon."""

#     create_data = {
#         "nombre": "Maria",
#         "email": "maria@example.com",
#         "direccion": "Obelisco, CABA"
#     }

#     async with AsyncClient(app=app, base_url="http://test") as ac:
#         r1 = await ac.post("/users/", json=create_data)
#     assert r1.status_code == 201
#     user = r1.json()
#     user_id = user["id"]

#     update_data = {
#         "direccion": "Plaza de Mayo, CABA"
#     }

#     async with AsyncClient(app=app, base_url="http://test") as ac:
#         r2 = await ac.put(f"/users/{user_id}/direccion", json=update_data)

#     assert r2.status_code == 200
#     updated = r2.json()

#     assert updated["direccion"] == update_data["direccion"]
#     assert updated["lat"] != user["lat"]
#     assert updated["lon"] != user["lon"]


import pytest
from httpx import AsyncClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from petcare.core.database import Base, get_db
from petcare.api.main import app


# ==============================
# 🔹 BD TEMPORAL EN MEMORIA
# ==============================
TEST_DATABASE_URL = "sqlite://"


engine_test = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool      # Esto permite que la BD viva mientras dure el test
)

TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine_test
)


# ==============================
# 🔹 Override dependencia get_db
# ==============================
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.on_event("startup")
def create_test_db():
    """
    Se ejecuta al iniciar app en testing:
    crea las tablas declaradas en Base
    dentro de la BD en memoria.
    """
    Base.metadata.create_all(bind=engine_test)


# Sobrescribo get_db para que FastAPI use la DB temporal
app.dependency_overrides[get_db] = override_get_db


# ==============================
# 🔹 FIXTURE
# ==============================
@pytest.fixture
async def async_client():
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client


# ==============================
# 🔹 TESTS
# ==============================

# @pytest.mark.asyncio
# async def test_registrar_usuario_con_ubicacion(test_app, async_client):
#     """
#     Crear usuario con dirección → verifica lat/lon
#     """

#     user_data = {
#         "nombre": "Juan",
#         "email": "juan@example.com",
#         "direccion": "Av. Santa Fe 123, CABA"
#     }

#     resp = await async_client.post("/v1/users/register", json=user_data)

#     assert resp.status_code == 201
#     result = resp.json()

#     assert "lat" in result
#     assert "lon" in result
#     assert result["direccion"] == user_data["direccion"]


# @pytest.mark.asyncio
# async def test_actualizar_ubicacion_usuario(test_app, async_client):
#     """
#     Actualizar dirección → lat/lon deben cambiar
#     """

#     create_data = {
#         "nombre": "Maria",
#         "email": "maria@example.com",
#         "direccion": "Obelisco, CABA"
#     }

#     r1 = await async_client.post("/v1/users/register", json=create_data)
#     assert r1.status_code == 201

#     user = r1.json()
#     user_id = user["id"]

#     update_data = {
#         "direccion": "Plaza de Mayo, CABA"
#     }

#     r2 = await async_client.put(f"/users/{user_id}/direccion", json=update_data)
#     assert r2.status_code == 200

#     updated = r2.json()

#     assert updated["direccion"] == update_data["direccion"]
#     assert updated["lat"] != user["lat"]
#     assert updated["lon"] != user["lon"]

@pytest.mark.asyncio
async def test_registrar_usuario_con_ubicacion(client):
    user_data = {
        "nombre": "Juan",
        "email": "juan@example.com",
        "contrasena": "1234",
        "tipo": "Cliente",
        "direccion": "Av. Santa Fe 123, CABA"
    
    }

    resp = client.post("/v1/users/register", json=user_data)

    assert resp.status_code == 201
    result = resp.json()

    assert "lat" in result
    assert "lon" in result
    assert result["direccion"] == user_data["direccion"]


@pytest.mark.asyncio
def test_actualizar_ubicacion_usuario(client):
    create_data = {
        "nombre": "Juan",
        "email": "juan@example.com",
        "contrasena": "1234",
        "tipo": "Cliente",
        "direccion": "Obelisco, CABA"
    
    }

    r1 = client.post("/v1/users/register", json=create_data)
    assert r1.status_code == 201

    user = r1.json()
    user_id = user["id"]

    update_data = {
        "direccion": "Plaza de Mayo, CABA"
    }

    r2 = client.put(f"/v1/users/{user_id}/direccion", json=update_data)
    assert r2.status_code == 200

    updated = r2.json()

    assert updated["direccion"] == update_data["direccion"]
    assert updated["lat"] != user["lat"]
    assert updated["lon"] != user["lon"]
