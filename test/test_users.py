# tests/test_users.py
import pytest


# --- TEST: registro exitoso ---
def test_register_user_success(client):
    payload = {
        "nombre": "Laura",
        "email": "laura@mail.com",
        "contrasena": "123456",
        "tipo": "cuidador",
        "direccion": "Av. Corrientes 1200, Buenos Aires"
    }


    response = client.post("/v1/users/register", json=payload)
    print(response.json())
    assert response.status_code == 201
    data = response.json()

    assert data["email"] == "laura@mail.com"
    assert data["nombre"] == "Laura"
    assert "id" in data


def test_register_user_conflict_email(seeded_client):
    # Mismo email que el usuario anterior
    payload = {
        "nombre": "Laura",
        "email": "laura@mail.com",
        "contrasena": "password123",
        "tipo": "cuidador",
        "direccion": "Av. Corrientes 1234, Buenos Aires"
    }


    response = seeded_client.post("/v1/users/register", json=payload)


    assert response.status_code in (400, 409)
    data = response.json()
    assert "detail" in data


# --- TEST: login exitoso ---
def test_login_success(seeded_client):
    payload = {
        "email": "laura@mail.com",
        "contrasena": "password123"
    }

    response = seeded_client.post("/v1/users/login", json=payload)
    assert response.status_code == 200

    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


# --- TEST: login con contraseña incorrecta ---
def test_login_wrong_password(client):
    register_payload = {
        "nombre": "Juan",
        "email": "juan@mail.com",
        "contrasena": "123456",
        "tipo": "cliente",
        "direccion": "Av. Rivadavia 2000, Buenos Aires"
    }
    client.post("/v1/users/register", json=register_payload)


    # Intentar login con contraseña incorrecta
    login_payload = {
        "email": "juan@mail.com",
        "contrasena": "wrongpass"
    }

    response = client.post("/v1/users/login", json=login_payload)
    assert response.status_code == 401
    assert response.json()["detail"] == "Credenciales incorrectas"


# --- TEST: login con usuario inexistente ---
def test_login_user_not_found(client):
    payload = {
        "email": "inexistente@example.com",
        "contrasena": "whatever"
    }

    response = client.post("/v1/users/login", json=payload)
    assert response.status_code == 401
    assert response.json()["detail"] == "Credenciales incorrectas"