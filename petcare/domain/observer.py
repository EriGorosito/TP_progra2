#petcare/domain/observer.py
from petcare.domain.notificacion import Notificacion


class EventManager:
    """Clase central del patrón Observer: maneja suscripciones y notificaciones."""
    def __init__(self):
        self._subscribers = {}  # evento -> lista de observadores


    def subscribe(self, event_name: str, observer):
        """Suscribe un observador a un evento."""
        self._subscribers.setdefault(event_name, []).append(observer)


    def notify(self, event_name: str, data):
        """Notifica a todos los observadores suscritos al evento."""
        for observer in self._subscribers.get(event_name, []):
            observer.update(event_name, data)


class NotificationObserver:
    """Observador concreto que genera notificaciones ante eventos."""
    def __init__(self):
        self.notificaciones = []

    def update(self, event_name: str, data):
        """Reacciona a los eventos creando una Notificación."""
        
        # --- ¡ARREGLO PARA 'reserva_creada'! ---
        if event_name == "reserva_creada":
            noti = Notificacion(
                id=len(self.notificaciones) + 1,
                usuario_id=data["cuidador_id"], # Lee el ID
                mensaje=f"Nueva reserva solicitada por {data['cliente_nombre']}.", # Lee el string
                tipo="reserva"
            )

        # --- ¡ARREGLO PARA 'reserva_confirmada'! ---
        elif event_name == "reserva_confirmada":
            noti = Notificacion(
                id=len(self.notificaciones) + 1,
                usuario_id=data["cliente_id"], # Asumo que el payload enviará esto
                mensaje=f"Tu reserva con {data['cuidador_nombre']} fue confirmada.", # Asumo payload
                tipo="reserva"
            )

        # --- ¡ARREGLO PARA 'reserva_rechazada'! ---
        elif event_name == "reserva_rechazada":
            noti = Notificacion(
                id=len(self.notificaciones) + 1,
                usuario_id=data["cliente_id"], # Asumo payload
                mensaje=f"Tu reserva con {data['cuidador_nombre']} fue cancelada.", # Asumo payload
                tipo="reserva"
            )

        # --- ¡ARREGLO PARA 'resena_creada'! ---
        elif event_name == "resena_creada":
            noti = Notificacion(
                id=len(self.notificaciones) + 1,
                usuario_id=data["cuidador_id"], # Asumo payload
                mensaje=f"{data['cliente_nombre']} dejó una reseña: {data['comentario']}", # Asumo payload
                tipo="resena"
            )

        # --- ¡ARREGLO PARA 'mascota_registrada'! ---
        elif event_name == "mascota_registrada":
            noti = Notificacion(
                id=len(self.notificaciones) + 1,
                usuario_id=data["owner_id"], # Asumo payload
                mensaje=f"¡Felicidades! Tu mascota '{data['pet_nombre']}' ({data['pet_especie']}) ha sido registrada.",
                tipo="registro"
            )

        else:
            return

        self.notificaciones.append(noti)
'''
class NotificationObserver:
    """Observador concreto que genera notificaciones ante eventos."""
    def __init__(self):
        self.notificaciones = []  # se podría persistir luego en base de datos


    def update(self, event_name: str, data):
        """Reacciona a los eventos creando una Notificación."""
        if event_name == "reserva_creada":
            noti = Notificacion(
                id=len(self.notificaciones) + 1,
                usuario_id=data["cuidador_id"],
                mensaje=f"Nueva reserva solicitada por {data['cliente'].nombre}.",
                tipo="reserva"
            )


        elif event_name == "reserva_confirmada":
            noti = Notificacion(
                id=len(self.notificaciones) + 1,
                usuario_id=data["cliente"].id,
                mensaje=f"Tu reserva con {data['cuidador'].nombre} fue confirmada.",
                tipo="reserva"
            )

        elif event_name == "reserva_rechazada":
            noti = Notificacion(
                id=len(self.notificaciones) + 1,
                usuario_id=data["cliente"].id,
                mensaje=f"Tu reserva con {data['cuidador'].nombre} fue cancelada.",
                tipo="reserva"
            )

        elif event_name == "resena_creada":
            noti = Notificacion(
                id=len(self.notificaciones) + 1,
                usuario_id=data["cuidador"].id,
                mensaje=f"{data['cliente'].nombre} dejó una reseña: {data['comentario']}",
                tipo="resena"
            )

        elif event_name == "mascota_registrada":
            # La notificación es para el propietario mismo
            # para confirmar que su mascota fue registrada
            noti = Notificacion(
                id=len(self.notificaciones) + 1,
                usuario_id=data["owner"].id,
                mensaje=f"¡Felicidades! Tu mascota '{data['pet'].nombre}' ({data['pet'].especie}) ha sido registrada.",
                tipo="registro"
            )


        else:
            # Si no se reconoce el evento, no se hace nada
            return


        self.notificaciones.append(noti)
'''
# Inicialización única del sistema de eventos
event_manager = EventManager()
noti_observer = NotificationObserver()

# Suscripciones
event_manager.subscribe("mascota_registrada", noti_observer)
event_manager.subscribe("reserva_creada", noti_observer)
event_manager.subscribe("reserva_confirmada", noti_observer)
event_manager.subscribe("reserva_rechazada", noti_observer)