import pytest
from fastapi.testclient import TestClient
from petcare.api.main import app
from petcare.core.database import Base, get_db
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool


# --- Base de datos temporal en memoria ---
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"


engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}, poolclass=StaticPool
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# --- Sobrescribir la dependencia get_db para usar la BD de prueba ---
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="function")
def client():
    # Re-crear las tablas para cada test, asegurando independencia
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    with TestClient(app) as c:
        yield c


@pytest.fixture(scope="function")
def seeded_client(client):
    """Cliente con datos iniciales cargados (por ejemplo, un usuario Erika)."""
    payload = {
        "nombre": "Erika",
        "email": "erika@mail.com",
        "contrasena": "password123",
        "tipo": "cuidador",
        "direccion": "Av. Corrientes 1234, Buenos Aires, Argentina"
    }
    client.post("/v1/users/register", json=payload)
    return client


# import pytest
# from fastapi.testclient import TestClient
# from petcare.api.main import app
# from petcare.core.database import Base, get_db
# from sqlalchemy import create_engine
# from sqlalchemy.orm import sessionmaker




# # --- Base de datos temporal en memoria ---
# SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"




# engine = create_engine(
#     SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
# )
# TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)




# # --- Sobrescribir la dependencia get_db para usar la BD de prueba ---
# def override_get_db():
#     db = TestingSessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()




# # --- Aplicar la sobreescritura ---
# app.dependency_overrides[get_db] = override_get_db




# # --- Crear tablas antes de los tests ---
# Base.metadata.create_all(bind=engine)




# @pytest.fixture(scope="module")
# def client():
#     with TestClient(app) as c:
#         yield c


