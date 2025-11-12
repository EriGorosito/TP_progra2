import pytest

# --- Helper para loguear y obtener token ---
def login_and_get_token(client, email, contrasena):
    resp = client.post("/v1/users/login", json={"email": email, "contrasena": contrasena})
    assert resp.status_code == 200, f"Error al loguear {email}: {resp.text}"
    return resp.json()["access_token"]


# --- TEST: Crear mascota exitosamente ---
def test_create_pet_success(seeded_client):
    client = seeded_client
    # Login del cliente (Claudio)
    token = login_and_get_token(client, "claudio@mail.com", "123")

    payload = {
        "nombre": "Firulais",
        "especie": "Perro",
        "raza": "Labrador",
        "edad": 3,
        "peso": 20,
        "caracteristicas_especiales": "Le gusta jugar a la pelota"
    }

    headers = {"Authorization": f"Bearer {token}"}
    resp = client.post("/v1/pets/", json=payload, headers=headers)
    print(resp.json())
    assert resp.status_code == 201
    data = resp.json()
    
    assert data["nombre"] == "Firulais"
    assert data["especie"] == "perro"
    assert data["raza"] == "Labrador"
    assert data["edad"] == 3
    assert "id" in data

# --- TEST: Crear mascota siendo cuidador (prohibido) ---
def test_create_pet_forbidden_for_cuidador(seeded_client):
    client = seeded_client
    token = login_and_get_token(client, "laura@mail.com", "password123")

    payload = {
        "nombre": "Michi",
        "especie": "Gato",
        "raza": "Siames",
        "edad": 2,
        "peso": 3
    }
    headers = {"Authorization": f"Bearer {token}"}
    resp = client.post("/v1/pets/", json=payload, headers=headers)

    assert resp.status_code == 403
    assert "Solo los 'Clientes'" in resp.text


# --- TEST: Listar mascotas del cliente (con dos mascotas) ---
def test_get_my_pets(seeded_client):
    client = seeded_client
    token = login_and_get_token(client, "claudio@mail.com", "123")
    headers = {"Authorization": f"Bearer {token}"}

    # Crear primera mascota
    pet1_payload = {
        "nombre": "Rocky",
        "especie": "Perro",
        "raza": None,
        "edad": 5,
        "peso": 25,
        "caracteristicas_especiales": "Le gusta correr"
    }
    resp1 = client.post("/v1/pets/", json=pet1_payload, headers=headers)
    assert resp1.status_code == 201, f"Error al crear la primera mascota: {resp1.text}"

    # Crear segunda mascota
    pet2_payload = {
        "nombre": "Mishi",
        "especie": "Gato",
        "raza": None,
        "edad": 2,
        "peso": 4.5,
        "caracteristicas_especiales": "Muy cariñoso"
    }
    resp2 = client.post("/v1/pets/", json=pet2_payload, headers=headers)
    assert resp2.status_code == 201, f"Error al crear la segunda mascota: {resp2.text}"

    # Obtener todas las mascotas del cliente
    resp_list = client.get("/v1/pets/", headers=headers)
    assert resp_list.status_code == 200, f"Error al listar mascotas: {resp_list.text}"

    data = resp_list.json()
    assert isinstance(data, list)
    assert len(data) == 2, f"Se esperaban 2 mascotas, pero se obtuvieron {len(data)}"
    nombres = [p["nombre"] for p in data]
    assert "Rocky" in nombres
    assert "Mishi" in nombres


# --- TEST: Cuidador no puede ver mascotas ---
def test_get_my_pets_forbidden_for_cuidador(seeded_client):
    client = seeded_client
    token = login_and_get_token(client, "laura@mail.com", "password123")
    headers = {"Authorization": f"Bearer {token}"}

    resp = client.get("/v1/pets/", headers=headers)
    assert resp.status_code == 403
    assert "Solo los 'Clientes'" in resp.text