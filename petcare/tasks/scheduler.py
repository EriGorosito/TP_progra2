from apscheduler.schedulers.background import BackgroundScheduler
from petcare.tasks.update_reserva import actualizar_reservas_finalizadas

def start_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(actualizar_reservas_finalizadas, "interval", minutes=10)
    scheduler.start()
