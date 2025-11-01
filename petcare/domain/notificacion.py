#petcare/domain/notificacion.py
from datetime import datetime


class Notificacion:
    def __init__(self, id: int, usuario_id: int, mensaje: str, tipo: str):
        self.id = id
        self.usuario_id = usuario_id
        self.mensaje = mensaje
        self.tipo = tipo
        self.fecha_creacion = datetime.now()
        self.leida = False


    def marcar_como_leida(self):
        """Marca la notificación como leída."""
        self.leida = True


    def __str__(self):
        estado = "✅ Leída" if self.leida else "📩 No leída"
        return f"[{estado}] ({self.tipo}) {self.mensaje} - {self.fecha_creacion.strftime('%Y-%m-%d %H:%M')}"




