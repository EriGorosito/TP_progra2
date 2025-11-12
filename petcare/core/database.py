import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Carga las variables del archivo .env 
load_dotenv()


# Base de datos SQLite local
# 1. Busca la variable de entorno 'DATABASE_URL'
# 2. Si no la encuentra, usa la base de datos local 'petcare.db' por defecto
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./petcare.db")

# Para PostgreSQL (más adelante)
# SQLALCHEMY_DATABASE_URL = "postgresql://usuario:password@localhost/nombre_bd"

connect_args = {}
# Si la URL de la base de datos es de SQLite, añade el argumento
if SQLALCHEMY_DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}
# -----------------------------

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args=connect_args  # <-- Pasa los argumentos condicionales
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    """
    Función generadora para obtener y cerrar la sesión de la DB.
    Usada como dependencia en los endpoints de FastAPI.
    """
    db = SessionLocal()
    try:
        # Entrega la sesión activa
        yield db
    finally:
        # Asegura que la sesión se cierre al terminar la solicitud
        db.close()