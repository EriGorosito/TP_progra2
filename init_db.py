# petcare/init_db.py
from petcare.core.database import Base, engine
from petcare.infraestructura.models import usuario_model, mascota_model, reserva_model, resena_model  # importa los modelos ORM

from sqlalchemy import inspect

print("Creando tablas en la base de datos...")
Base.metadata.create_all(bind=engine)
print("Tablas creadas correctamente ✅")
# 2. PASO DE VERIFICACIÓN
# --- Código de Verificación ---

inspector = inspect(engine)
tablas_creadas = inspector.get_table_names()

print("\n--- Resultado de la Verificación ---")
if tablas_creadas:
    print(f"Tablas encontradas: {tablas_creadas}")
    # Puedes hacer una comprobación más específica aquí
    if 'usuarios' in tablas_creadas and 'mascotas' in tablas_creadas:
        print("¡Verificación exitosa! Las tablas 'usuarios' y 'mascotas' están en la DB. ✨")
    else:
        print("Atención: Las tablas 'usuarios' o 'mascotas' no se encontraron.")
else:
    print("Error: No se encontró ninguna tabla en la base de datos. ❌")

