from fastapi import FastAPI
from contextlib import asynccontextmanager

# Importaciones locales de rutas
from petcare.api.v1.routes.users import user_router
from petcare.api.v1.routes.pets import pet_router
from petcare.api.v1.routes.reservas import reserva_router
from petcare.api.v1.routes.cuidadores import cuidadores_router
from petcare.api.v1.routes.resenas import review_router

# Importaciones para la base de datos y tareas
from petcare.core.database import engine, Base
from petcare.tasks.scheduler import start_scheduler

# Importación de modelos para que Base.metadata.create_all() los conozca
from petcare.infraestructura.models import (
    usuario_model,
    mascota_model,
    reserva_model,
    resena_model,
)


def initialize_database():
    """
    Función que asegura que todas las tablas ORM definidas
    en Base se creen en la DB si aún no existen.
    """
    print("Iniciando la conexión a la base de datos...")
    # Base.metadata.create_all necesita el 'engine' que definimos en database.py
    Base.metadata.create_all(bind=engine)
    print("Estructura de la base de datos verificada y lista.")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Código que se ejecuta al iniciar:
    print("--- Iniciando aplicación ---")
    initialize_database()
    start_scheduler()
    print("--- Aplicación lista ---")

    yield  

    # Código que se ejecuta al apagar:
    print("--- Cerrando aplicación ---")


# Crea la instancia principal de la app
app = FastAPI(
    title="PetCare API",
    description="API para conectar dueños de mascotas con cuidadores.",
    lifespan=lifespan
)

# Inicializa el scheduler al inicio de la aplicación
start_scheduler()

# Incluye los routers
app.include_router(user_router, prefix="/v1")
app.include_router(cuidadores_router, prefix="/v1")
app.include_router(pet_router, prefix="/v1")
app.include_router(reserva_router, prefix="/v1")
app.include_router(review_router, prefix="/v1")


@app.get("/")
def read_root():
    return {"message": "Bienvenido a PetCare API. Ve a /docs para ver la documentación."}