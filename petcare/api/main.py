# petcare/api/main.py
from fastapi import FastAPI
from petcare.api.v1.routes.users import user_router, pet_router

# Crea la instancia principal de la app
app = FastAPI(
    title="PetCare API",
    description="API para conectar dueños de mascotas con cuidadores."
)

# Incluye el router de usuarios
app.include_router(user_router, prefix="/v1")
# Incluye el router de mascotas
app.include_router(pet_router, prefix="/v1")

@app.get("/")
def read_root():
    return {"message": "Bienvenido a PetCare API. Ve a /docs para ver la documentación."}