from fastapi import FastAPI
from petcare.api.v1.routes.users import user_router
from petcare.api.v1.routes.pets import pet_router
from petcare.api.v1.routes.reservas import reserva_router
from petcare.api.v1.routes.cuidadores import cuidadores_router
from petcare.api.v1.routes.resenas import review_router

# --- AÑADIR IMPORTS PARA LA BASE DE DATOS ---
from petcare.core.database import engine, Base
from petcare.tasks.scheduler import start_scheduler
# ---------------------------------------------

# Crea la instancia principal de la app
app = FastAPI(
    title="PetCare API",
    description="API para conectar dueños de mascotas con cuidadores."
)

start_scheduler()

# --- FUNCIÓN DE INICIALIZACIÓN DE DB ---
def initialize_database():
    """
    Función que asegura que todas las tablas ORM definidas 
    en Base se creen en la DB si aún no existen.
    """
    print("Iniciando la conexión a la base de datos...")
    # Base.metadata.create_all necesita el 'engine' que definimos en database.py
    Base.metadata.create_all(bind=engine)
    print("Estructura de la base de datos verificada y lista.")

# --- EVENTO DE CICLO DE VIDA ---
@app.on_event("startup")
async def startup_event():
    """
    Ejecuta la inicialización de la base de datos solo una vez cuando 
    la aplicación arranca.
    """
    initialize_database()
# ---------------------------------

# Incluye los routers
app.include_router(user_router, prefix="/v1")
app.include_router(cuidadores_router, prefix="/v1")
app.include_router(pet_router, prefix="/v1")
app.include_router(reserva_router, prefix="/v1")
app.include_router(review_router, prefix="/v1")


@app.get("/")
def read_root():
    return {"message": "Bienvenido a PetCare API. Ve a /docs para ver la documentación."}

# # petcare/api/main.py
# from fastapi import FastAPI
# from petcare.api.v1.routes.users import user_router
# from petcare.api.v1.routes.pets import pet_router
# from petcare.api.v1.routes.reservas import reserva_router



# # Crea la instancia principal de la app
# app = FastAPI(
#     title="PetCare API",
#     description="API para conectar dueños de mascotas con cuidadores."
# )

# # Incluye el router de usuarios
# app.include_router(user_router, prefix="/v1")
# # Incluye el router de mascotas
# app.include_router(pet_router, prefix="/v1")
# #incluye el router de reserva
# app.include_router(reserva_router, prefix="/v1")

# @app.get("/")
# def read_root():
#     return {"message": "Bienvenido a PetCare API. Ve a /docs para ver la documentación."}