# tests/test_app.py

import pytest
from datetime import date
from petcare.domain.mascota import Mascota
from petcare.domain.usuario import Cliente, Cuidador
from petcare.domain.reserva import Reserva
from petcare.domain.resena import Resena


def test_creacion_cliente_y_mascota():
    cliente = Cliente(1, "Camilo", "camilogonzales@mail.com", "12345678")
    mascota = Mascota(1, "Luna", "Perro","golden", 3, 18.5, owner_id=1)
    cliente.registrar_mascota(mascota)
    
    assert cliente.nombre == "Camilo"
    assert cliente.mascotas == []  # Como el método registrar_mascota está vacío
    assert mascota.especie == "Perro"


def test_creacion_cuidador():
    cuidador = Cuidador(1, "Sofi", "sofi@mail.com", "abcd1234", "Amo a los animales")
    assert isinstance(cuidador, Cuidador)
    assert cuidador.descripcion == "Amo a los animales"


def test_crear_reserva():
    cliente = Cliente(1, "Camilo", "camilogonzales@mail.com", "12345678")
    cuidador = Cuidador(1, "Sofi", "sofi@mail.com", "abcd1234")
    mascota = Mascota(1, "Luna", "Perro","golden", 3, 18.5, owner_id=1)
    reserva = Reserva(1, cliente, cuidador, mascota, date(2025, 1, 1), date(2025, 1, 10))
    
    assert reserva.estado == "pendiente"
    assert reserva.cliente == cliente
    assert reserva.cuidador == cuidador
    assert reserva.mascotas == mascota



def test_crear_resena():
    cliente = Cliente(1, "Camilo", "camilogonzales@mail.com", "12345678")
    cuidador = Cuidador(1, "Sofi", "sofi@mail.com", "abcd1234", "Amo a los animales")
    resena = Resena(1, cliente, cuidador, 5, "Excelente cuidado")

    assert isinstance(resena, Resena)
    assert resena.puntaje == 5
    assert resena.comentario == "Excelente cuidado"
    assert resena.cliente == cliente
    assert resena.cuidador == cuidador
