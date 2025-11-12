# petcare/test/test_resenas.py
import pytest
from datetime import date, timedelta

# --- TEST: crear reseña ---
def test_crear_review_desde_reserva_finalizada(seeded_client, crear_cuidador):
    """
    Prueba la creación de una reseña para una reserva finalizada.
    """
    client = seeded_client

    # --- Login del cliente (Claudio) ---
    login_payload = {"email": "claudio@mail.com", "contrasena": "123"}
    login_response = client.post("/v1/users/login", json=login_payload)
    assert login_response.status_code == 200, login_response.text
    token_cliente = login_response.json()["access_token"]
    headers_cliente = {"Authorization": f"Bearer {token_cliente}"}


    # --- Crear una mascota ---
    mascota_payload = {
        "nombre": "Luna",
        "especie": "perro",
        "raza": None,
        "edad": 3,
        "peso": 12.5,
        "caracteristicas_especiales": "Perra muy sociable"
    }
    mascota_response = client.post(
        "/v1/pets/",
        json=mascota_payload,
        headers=headers_cliente
    )
    assert mascota_response.status_code == 201, mascota_response.text
    mascota_id = mascota_response.json()["id"]

    cuidador_id = crear_cuidador["id"]

    # --- Crear una reserva ---
    reserva_payload = {
        "cuidador_id": cuidador_id,
        "mascotas_ids": [mascota_id],
        "fecha_inicio": "2024-07-18",
        "fecha_fin": "2024-07-23"
    }
    reserva_response = client.post(
        "/v1/reservas/",
        json=reserva_payload,
        headers=headers_cliente
    )
    assert reserva_response.status_code == 201, reserva_response.text
    reserva_id = reserva_response.json()["id"]

    headers_cuidador = {"Authorization": f"Bearer {crear_cuidador['token']}"}
    patch_resp = client.patch(
        f"/v1/reservas/{reserva_id}/estado",
        params={"estado_reserva": "aceptada"},
        headers=headers_cuidador
    )
    # --- Verificaciones ---
    assert patch_resp.status_code == 200, f"Error al actualizar estado: {patch_resp.text}"

    # --- Crear reseña sobre la reserva finalizada ---
    review_payload = {
        "reserva_id": reserva_id,
        "comentario": "Excelente cuidado, volvería a contratarla",
        "puntaje": 5
    }
    review_response = client.post(
        "/v1/reviews/",
        json=review_payload,
        headers={"Authorization": f"Bearer {token_cliente}"}
    )

    assert review_response.status_code == 201, f"Error al crear reseña: {review_response.text}"
    data = review_response.json()
    assert data["puntaje"] == 5
    assert data["comentario"] == review_payload["comentario"]
    assert data["cuidador_id"] == 1
    assert data["reserva_id"] == reserva_id
