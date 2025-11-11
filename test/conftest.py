import pytest
from fastapi.testclient import TestClient
from petcare.api.main import app
from petcare.core.database import Base, get_db
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from datetime import date


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
        "nombre": "Laura",
        "email": "laura@mail.com",
        "contrasena": "password123",
        "tipo": "cuidador",
        "direccion": "Av. Corrientes 1234, Buenos Aires, Argentina"
    }
    cuidador = client.post("/v1/users/register", json=payload)
    assert cuidador.status_code in (200, 201), f"Error al registrar Erika: {cuidador.status_code} {cuidador.text}"

    claudio_payload = {
        "nombre": "Claudio",
        "email": "claudio@mail.com",
        "contrasena": "123",
        "tipo": "cliente",
        "direccion": "Av. Rivadavia 2000, Buenos Aires, Argentina"
    }

    resp2 = client.post("/v1/users/register", json=claudio_payload)
    assert resp2.status_code in (200, 201), f"Error al registrar Claudio: {resp2.status_code} {resp2.text}"

    return client

@pytest.fixture
def crear_cuidador(seeded_client):
    """Crea y configura un cuidador disponible para usar en otros tests."""
    client = seeded_client

    # Paso 1: Login del cuidador Laura (creada por seed)
    login_payload = {"email": "laura@mail.com", "contrasena": "password123"}
    login_response = client.post("/v1/users/login", json=login_payload)
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]

    # Paso 2: Completar perfil del cuidador
    payload = {
        "descripcion": "Amo cuidar gatos y perros",
        "servicios": ["gato", "perro"],
        "tarifas": {"gato": 10000, "perro": 12000},
        "dias_no_disponibles": [str(date.today().replace(day=date.today().day + 1))]
    }

    response = client.post(
        "/v1/cuidadores/completar/1",  # ID=1 porque Laura es el primer usuario en el seed
        json=payload,
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200, f"Error creando cuidador: {response.text}"

    # Devuelve el ID y token del cuidador por si se necesita
    return {"id": 1, "token": token}


