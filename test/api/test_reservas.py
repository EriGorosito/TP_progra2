from datetime import date, timedelta

def login_and_get_token(client, email, contrasena):
    """Helper para loguear y obtener el token."""
    resp = client.post("/v1/users/login", json={"email": email, "contrasena": contrasena})
    assert resp.status_code == 200, f"Error al loguear {email}: {resp.text}"
    return resp.json()["access_token"]

def test_crear_reserva_exitosa(seeded_client, crear_cuidador):
    client = seeded_client
# Login del cliente Claudio
    token = login_and_get_token(client, "claudio@mail.com", "123")
    headers = {"Authorization": f"Bearer {token}"}

    # Crear una mascota asociada al cliente
    pet_payload = {
        "nombre": "Rocky",
        "especie": "Perro",
        "raza": "Labrador",
        "edad": 3,
        "peso": 20
    }
    pet_resp = client.post("/v1/pets/", json=pet_payload, headers=headers)
    assert pet_resp.status_code == 201, f"Error creando mascota: {pet_resp.text}"
    pet_id = pet_resp.json()["id"]

    # Usar el cuidador del fixture
    cuidador_id = crear_cuidador["id"]

    # Crear una reserva
    reserva_payload = {
        "cuidador_id": cuidador_id,
        "mascotas_ids": [pet_id],
        "fecha_inicio": str(date.today()),
        "fecha_fin": str(date.today() + timedelta(days=2))
    }

    resp = client.post("/v1/reservas/", json=reserva_payload, headers=headers)
    assert resp.status_code == 201, f"Error al crear reserva: {resp.text}"

    data = resp.json()
    assert data["estado"] == "pendiente"
    assert data["cliente"]["email"] == "claudio@mail.com"


def test_crear_reserva_como_cuidador_prohibido(seeded_client):
    client = seeded_client

    # Login del cuidador Laura
    token = login_and_get_token(client, "laura@mail.com", "password123")
    headers = {"Authorization": f"Bearer {token}"}

    payload = {
        "cuidador_id": 1,
        "mascotas_ids": [1],
        "fecha_inicio": "2025-05-01",
        "fecha_fin": "2025-05-05"
    }

    resp = client.post("/v1/reservas/", json=payload, headers=headers)
    assert resp.status_code == 403
    assert "Solo Clientes pueden crear reservas" in resp.text


def test_listar_reservas_cliente(seeded_client):
    client = seeded_client

    # Login del cliente Claudio
    token = login_and_get_token(client, "claudio@mail.com", "123")
    headers = {"Authorization": f"Bearer {token}"}

    resp = client.get("/v1/reservas/mias", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)


def test_aceptar_reserva_como_cuidador(seeded_client, crear_cuidador):
    client = seeded_client

    # --- Login del cliente para crear una reserva ---
    token_cliente = login_and_get_token(client, "claudio@mail.com", "123")
    headers_cliente = {"Authorization": f"Bearer {token_cliente}"}

    # Crear mascota
    pet_payload = {
        "nombre": "Toby",
        "especie": "Perro",
        "raza": "Beagle",
        "edad": 4,
        "peso": 15
    }
    pet_resp = client.post("/v1/pets/", json=pet_payload, headers=headers_cliente)
    assert pet_resp.status_code == 201, f"Error creando mascota: {pet_resp.text}"
    pet_id = pet_resp.json()["id"]

    cuidador_id = crear_cuidador["id"]

    # Crear reserva
    reserva_payload = {
        "cuidador_id": cuidador_id,
        "mascotas_ids": [pet_id],
        "fecha_inicio": "2025-05-01",
        "fecha_fin": "2025-05-02"
    }
    reserva = client.post("/v1/reservas/", json=reserva_payload, headers=headers_cliente).json()
    reserva_id = reserva["id"]

    # --- Login del cuidador ---
    token_cuidador = login_and_get_token(client, "laura@mail.com", "password123")
    headers_cuidador = {"Authorization": f"Bearer {token_cuidador}"}

    # Aceptar la reserva
    resp = client.put(f"/v1/reservas/{reserva_id}/aceptar", headers=headers_cuidador)
    assert resp.status_code == 200, f"Error al aceptar reserva: {resp.text}"
    data = resp.json()
    assert data["mensaje"] == "Reserva confirmada con éxito"


def test_actualizar_estado_reserva_exitoso(seeded_client, crear_cuidador):
    client = seeded_client

    # --- Paso 1: Login del cliente Claudio ---
    token_cliente = login_and_get_token(client, "claudio@mail.com", "123")
    headers_cliente = {"Authorization": f"Bearer {token_cliente}"}

    # --- Paso 2: Crear mascota asociada al cliente ---
    pet_payload = {
        "nombre": "Toby",
        "especie": "Perro",
        "raza": "Beagle",
        "edad": 4,
        "peso": 15
    }
    pet_resp = client.post("/v1/pets/", json=pet_payload, headers=headers_cliente)
    assert pet_resp.status_code == 201, f"Error creando mascota: {pet_resp.text}"
    pet_id = pet_resp.json()["id"]

    # --- Paso 3: Crear una reserva (Claudio → Laura cuidadora) ---
    reserva_payload = {
        "cuidador_id": crear_cuidador["id"],
        "mascotas_ids": [pet_id],
        "fecha_inicio": str(date.today()),
        "fecha_fin": str(date.today() + timedelta(days=2))
    }

    reserva_resp = client.post("/v1/reservas/", json=reserva_payload, headers=headers_cliente)
    assert reserva_resp.status_code == 201, f"Error creando reserva: {reserva_resp.text}"
    reserva_id = reserva_resp.json()["id"]

    # --- Paso 4: El cuidador actualiza el estado de la reserva ---
    headers_cuidador = {"Authorization": f"Bearer {crear_cuidador['token']}"}
    patch_resp = client.patch(
        f"/v1/reservas/{reserva_id}/estado",
        params={"estado_reserva": "aceptada"},
        headers=headers_cuidador
    )

    # --- Verificaciones ---
    assert patch_resp.status_code == 200, f"Error al actualizar estado: {patch_resp.text}"
    data = patch_resp.json()
    assert data["estado"] == "aceptada"
    assert data["id"] == reserva_id
    assert data["cuidador"]["email"] == "laura@mail.com"

