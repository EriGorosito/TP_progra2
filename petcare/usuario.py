from datetime import date
from typing import List

from petcare.mascota import Mascota
from petcare.resena import Resena


class Usuario:
    def __init__(self, nombre: str, email: str, contraseña: str):
        self.nombre = nombre
        self.email = email
        self.contraseña = contraseña

    def registrarse(self):
        pass

    def iniciar_sesion(self, email: str, contraseña: str) -> bool:
        pass


class Cliente(Usuario):
    def __init__(self, nombre: str, email: str, contraseña: str):
        super().__init__(nombre, email, contraseña)
        self.mascotas: List['Mascota'] = []

    def registrar_mascota(self, mascota):
        pass

    def buscar_cuidador(self, tipo_mascota: str, fecha_inicio: date, fecha_fin: date, ubicacion: str):
        pass

    def crear_reserva(self, cuidador, mascota, fecha_inicio, fecha_fin):
        pass

    def dejar_resena(self, cuidador, puntaje: int, comentario: str = ""):
        pass


class Cuidador(Usuario):
    def __init__(self, nombre: str, email: str, contraseña: str, descripcion: str = ""):
        super().__init__(nombre, email, contraseña)
        self.descripcion = descripcion
        self.servicios: List[str] = []
        self.tarifas = {}
        self.disponibilidad = []
        self.reseñas: List[Resena] = []

    def actualizar_perfil(self, descripcion: str, servicios: List[str], tarifas: dict):
        pass

    def aceptar_reserva(self, reserva):
        pass

    def rechazar_reserva(self, reserva):
        pass

