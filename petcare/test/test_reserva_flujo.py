import pytest
from datetime import date
from petcare.domain.factory_usuario import UsuarioFactory
from petcare.domain.mascota import Mascota
from petcare.domain.reserva import Reserva

def test_flujo_dominio_reserva():
    # 1️⃣ Crear usuarios
    cliente = UsuarioFactory.crear_usuario(
        tipo="cliente",
        id=1,
        nombre="Ana Cliente",
        email="ana@example.com",
        contrasena="1234"
    )
    cuidador = UsuarioFactory.crear_usuario(
        tipo="cuidador",
        id=2,
        nombre="Pablo Cuidador",
        email="pablo@example.com",
        contrasena="abcd",
        descripcion="Amo los perros"
    )

    # 2️⃣ Crear mascota
    mascota = Mascota(
        id=1,
        nombre="Coco",
        especie="Perro",
        raza="Labrador",
        edad=3,
        peso=20,
        caracteristicas_especiales="Juguetón",
        owner_id=cliente.id
    )
    assert mascota.nombre == "Coco"
    cliente.mascotas.append(mascota)

    # 3️⃣ Crear reserva
    fecha_inicio = date(2025, 11, 5)
    fecha_fin = date(2025, 11, 7)

    reserva = Reserva(
        id=1,
        cliente=cliente,
        cuidador=cuidador,
        mascotas=[mascota],
        fecha_inicio=fecha_inicio,
        fecha_fin=fecha_fin
    )

    assert reserva.estado == "pendiente"
    assert reserva.cliente.nombre == "Ana Cliente"

    # 4️⃣ Aceptar reserva
    cuidador.aceptar_reserva(reserva)
    assert reserva.estado == "confirmada"

    # 5️⃣ Rechazar reserva
    reserva_rechazada = Reserva(
        id=2,
        cliente=cliente,
        cuidador=cuidador,
        mascotas=[mascota],
        fecha_inicio=date(2025, 11, 10),
        fecha_fin=date(2025, 11, 12)
    )
    cuidador.rechazar_reserva(reserva_rechazada)
    assert reserva_rechazada.estado == "rechazada"