from apscheduler.schedulers.background import BackgroundScheduler
from petcare.tasks.update_reserva import actualizar_reservas_automatica

def start_scheduler():
    """Verifica automaticamente el estado de la reserva cada 10 min"""
    scheduler = BackgroundScheduler()
    scheduler.add_job(actualizar_reservas_automatica, "interval", minutes=10)
    scheduler.start()
