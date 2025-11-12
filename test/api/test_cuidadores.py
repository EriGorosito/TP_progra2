
import pytest


# tests/test_cuidadores.py
def test_completar_datos_cuidador(seeded_client):
    # Paso 1: Loguearse para obtener el token
    login_payload = {
        "email": "claudio@mail.com",
        "contrasena": "123"
    }
    login_response = seeded_client.post("/v1/users/login", json=login_payload)
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]

    # Paso 2: Completar datos del cuidador
    payload = {
        "descripcion": "Amo cuidar gatos y perros",
        "servicios": ["gato", "perro"],
        "tarifas": {"gato": 10000, "perro": 12000},
        "dias_no_disponibles": ["2025-11-15"]
    }

    response = seeded_client.post(
        "/v1/cuidadores/completar/2",  
        json=payload,
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 400
    data = response.json()
    assert data["detail"] == "El usuario no es cuidador"
   

def test_completar_datos_cuidador_exitoso(seeded_client):
    # Paso 1: Loguearse para obtener el token
    login_payload = {
        "email": "laura@mail.com",
        "contrasena": "password123"
    }
    login_response = seeded_client.post("/v1/users/login", json=login_payload)
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]

    # Paso 2: Completar datos del cuidador
    payload = {
        "descripcion": "Amo cuidar gatos y perros",
        "servicios": ["gato", "perro"],
        "tarifas": {"gato": 10000, "perro": 12000},
        "dias_no_disponibles": ["2025-11-15"]
    }

    response = seeded_client.post(
        "/v1/cuidadores/completar/1",  # Laura es la usuaria con id=1
        json=payload,
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["mensaje"] == "Datos del cuidador completados correctamente"


def test_completar_datos_usuario_inexistente(seeded_client):
    login_payload = {"email": "laura@mail.com", "contrasena": "password123"}
    token = seeded_client.post("/v1/users/login", json=login_payload).json()["access_token"]

    payload = {
        "descripcion": "Cuido animales",
        "servicios": ["gato"],
        "tarifas": {"gato": 8000},
        "dias_no_disponibles": []
    }

    response = seeded_client.post(
        "/v1/cuidadores/completar/999",  # ID inexistente
        json=payload,
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Usuario no encontrado"


def test_completar_datos_usuario_no_cuidador(client):
    payload = {
        "nombre": "Claudio",
        "email": "claudio@mail.com",
        "contrasena": "123",
        "tipo": "Cliente",
        "direccion": "Av. Rivadavia 2000, Buenos Aires, Argentina"
    }
    register_response = client.post("/v1/users/register", json=payload)
    user_id = register_response.json()["id"]

    login_payload = {
        "email": "claudio@mail.com",
        "contrasena": "123"
    }
    login_response = client.post("/v1/users/login", json=login_payload)

    assert login_response.status_code == 200
    token = login_response.json()["access_token"]
   
    # Intentar completar como cuidador
    payload = {
        "descripcion": "No debería poder",
        "servicios": ["perro"],
        "tarifas": {"perro": 10000},
        "dias_no_disponibles": []
    }

    response = client.post(
        f"/v1/cuidadores/completar/{user_id}",
        json=payload,
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "El usuario no es cuidador"


def test_buscar_cuidadores_cercanos_cliente(seeded_client):
    login_payload = {"email": "claudio@mail.com", "contrasena": "123"}
    token = seeded_client.post("/v1/users/login", json=login_payload).json()["access_token"]

    params = {
        "especies": ["gato", "perro"],
        "fecha_inicio": "2025-11-10",
        "fecha_fin": "2025-11-15"
    }

    response = seeded_client.get(
        "/v1/cuidadores/cercanos",
        params=params,
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
   

def test_buscar_cuidadores_cercanos_no_cliente(seeded_client):
    # Login de Laura (cuidadora)
    login_payload = {"email": "laura@mail.com", "contrasena": "password123"}
    token = seeded_client.post("/v1/users/login", json=login_payload).json()["access_token"]

    params = {
        "especies": ["gato", "perro"],
        "fecha_inicio": "2025-11-10",
        "fecha_fin": "2025-11-15"
    }

    response = seeded_client.get(
        "/v1/cuidadores/cercanos",
        params=params,
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "Solo los clientes pueden buscar cuidadores cercanos."
