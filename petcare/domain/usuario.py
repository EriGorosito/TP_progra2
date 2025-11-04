#petcare/domain/usuario.py
from datetime import date, timedelta
from typing import List

from petcare.domain.mascota import Mascota
from petcare.domain.resena import Resena
from passlib.context import CryptContext 

# Define el contexto para el hashing de contraseñas (usa bcrypt)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class Usuario:
    def __init__(self, id: int, nombre: str, email: str, contrasena: str):
        self.id = id
        self.nombre = nombre
        self.email = email
        # Almacenar la versión hasheada, NO el texto plano
        self.contrasena_hash = self.get_password_hash(contrasena)
        
    # Implementación de seguridad
    def get_password_hash(self, contrasena: str) -> str:
        """Hashea la contraseña."""
        return pwd_context.hash(contrasena)

    def verify_password(self, contrasena: str) -> bool:
        """Verifica la contraseña contra el hash almacenado."""
        return pwd_context.verify(contrasena, self.contrasena_hash)

    def registrarse(self):
        pass

    def iniciar_sesion(self, email: str, contraseña: str) -> bool:
        pass


class Cliente(Usuario):
    def __init__(self, id: int, nombre: str, email: str, contrasena: str):
        super().__init__(id, nombre, email, contrasena)
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
    def __init__(self, id: int, nombre: str, email: str, contrasena: str, descripcion: str = ""):
        super().__init__(id, nombre, email, contrasena)
        self.descripcion = descripcion
        self.servicios: List[str] = []  # especies que puede cuidar
        self.tarifas: dict = {}         # especie -> precio por día
        self.dias_no_disponibles: List[date] = []  # fechas que no puede trabajar
        self.resenas: List[Resena] = []

    def marcar_no_disponible(self, fecha: date):
        if fecha not in self.dias_no_disponibles:
            self.dias_no_disponibles.append(fecha)

    def esta_disponible(self, fecha_inicio: date, fecha_fin: date) -> bool:
        dias = [fecha_inicio + timedelta(days=i) for i in range((fecha_fin - fecha_inicio).days + 1)]
        return all(dia not in self.dias_no_disponibles for dia in dias)

    def actualizar_perfil(self, descripcion: str, servicios: List[str], tarifas: dict):
        self.descripcion = descripcion
        self.servicios = servicios
        self.tarifas = tarifas

    def aceptar_reserva(self, reserva, event_manager=None):
        reserva.confirmar(event_manager)

          # Marcar los días como no disponibles
        for i in range((reserva.fecha_fin - reserva.fecha_inicio).days + 1):
            self.marcar_no_disponible(reserva.fecha_inicio + timedelta(days=i))

    def rechazar_reserva(self, reserva, event_manager=None):
        reserva.rechazar(event_manager)

