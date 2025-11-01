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
        self.notificaciones = []  # se podría persistir luego en base de datos


    def update(self, event_name: str, data):
        """Reacciona a los eventos creando una Notificación."""
        if event_name == "reserva_creada":
            noti = Notificacion(
                id=len(self.notificaciones) + 1,
                usuario_id=data["cuidador"].id,
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


        else:
            # Si no se reconoce el evento, no se hace nada
            return


        self.notificaciones.append(noti)
