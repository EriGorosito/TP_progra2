# test/test_observer.py
from datetime import date
# Importar las clases desde tu estructura
from petcare.domain.factory_usuario import UsuarioFactory
from petcare.domain.mascota import Mascota
from petcare.domain.reserva import Reserva
from petcare.domain.observer import EventManager, NotificationObserver


# --- Lógica de Prueba ---


def test_reserva_confirmada_genera_notificacion():
    """
    Verifica que confirmar una reserva dispare el evento y genere la notificación.
    """
    # 1. SETUP: Inicializar el sistema de Observadores
    # -----------------------------------------------
    event_manager = EventManager()
   
    # Creamos el Observador que escucha y crea las notificaciones
    noti_observer = NotificationObserver()
   
    # Suscribimos el Observador al evento específico de interés
    event_manager.subscribe("reserva_confirmada", noti_observer)
   
   
    # 2. CONFIGURACIÓN: Crear las entidades de dominio
    # ------------------------------------------------
    # (Asumiendo que Cliente y Cuidador tienen un 'id' y 'nombre')
    cliente = UsuarioFactory.crear_usuario("cliente", 1, "Camilo", "camilogonzales@mail.com", "12345678")
    cuidador = UsuarioFactory.crear_usuario("cuidador", 1, "Sofi", "sofi@mail.com", "abcd1234")
    mascota = Mascota(1, "Luna", "Perro", "golden", 3, 18.5, owner_id=1)
    reserva = Reserva(1, cliente, cuidador, mascota, date(2025, 1, 1), date(2025, 1, 10))
   
    # Crear la reserva asociada
    reserva = Reserva(id=101, cliente=cliente, cuidador=cuidador, mascotas=mascota, fecha_inicio=date(2025, 1, 1), fecha_fin=date(2025, 1, 10),  estado="pendiente")
   
    # Aseguramos que no haya notificaciones antes de empezar
    assert len(noti_observer.notificaciones) == 0
   
   
    # 3. ACCIÓN: Ejecutar el método que dispara el evento
    # ---------------------------------------------------
    # Llamamos al método, inyectando el EventManager
    reserva.confirmar(event_manager=event_manager)
   
   
    # 4. VERIFICACIÓN (ASSERTION)
    # ---------------------------
   
    # A. Verificar que se generó 1 notificación
    assert len(noti_observer.notificaciones) == 1
   
    # B. Obtener la notificación generada
    notificacion_generada = noti_observer.notificaciones[0]
   
    # C. Verificar el contenido de la notificación para el Cliente (como está en tu código de Observador)
    assert notificacion_generada.usuario_id == cliente.id
    assert "Tu reserva con Sofi fue confirmada." in notificacion_generada.mensaje
    assert notificacion_generada.tipo == "reserva"
   
    # D. Opcional: Verificar el estado de la reserva
    assert reserva.estado == "confirmada"
