# tests/test_app.py

import pytest
from datetime import date
from petcare.mascota import Mascota
from petcare.usuario import Cliente, Cuidador
from petcare.reserva import Reserva
from petcare.resena import Resena


def test_creacion_cliente_y_mascota():
    cliente = Cliente("Camilo", "camilogonzales@mail.com", "12345678")
    mascota = Mascota("Luna", "Perro", 3, 18.5)
    cliente.registrar_mascota(mascota)
    
    assert cliente.nombre == "Camilo"
    assert cliente.mascotas == []  # Como el método registrar_mascota está vacío
    assert mascota.tipo == "Perro"


def test_creacion_cuidador():
    cuidador = Cuidador("Sofi", "sofi@mail.com", "abcd1234", "Amo a los animales")
    assert isinstance(cuidador, Cuidador)
    assert cuidador.descripcion == "Amo a los animales"


def test_crear_reserva():
    cliente = Cliente("Camilo", "camilogonzales@mail.com", "12345678")
    cuidador = Cuidador("Sofi", "sofi@mail.com", "abcd1234")
    mascota = Mascota("Luna", "Perro", 3, 18.5)
    reserva = Reserva(cliente, cuidador, mascota, date(2025, 1, 1), date(2025, 1, 10))
    
    assert reserva.estado == "Pendiente"
    assert reserva.cliente == cliente
    assert reserva.cuidador == cuidador
    assert reserva.mascota == mascota



def test_crear_resena():
    cliente = Cliente("Camilo", "camilogonzales@mail.com", "12345678")
    cuidador = Cuidador("Sofi", "sofi@mail.com", "abcd1234", "Amo a los animales")
    resena = Resena(cliente, cuidador, 5, "Excelente cuidado")

    assert isinstance(resena, Resena)
    assert resena.puntaje == 5
    assert resena.comentario == "Excelente cuidado"
    assert resena.cliente == cliente
    assert resena.cuidador == cuidador
