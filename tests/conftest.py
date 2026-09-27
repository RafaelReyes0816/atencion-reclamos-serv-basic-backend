import os
import tempfile

os.environ.setdefault("DATABASE_URL", f"sqlite:///{tempfile.gettempdir()}/test_reclamos.db")
os.environ.setdefault("SECRET_KEY", "clave_secreta_de_pruebas_1234567890")
os.environ.setdefault("ALGORITHM", "HS256")
os.environ.setdefault("ACCESS_TOKEN_EXPIRE_MINUTES", "60")

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.Infraestructura.database import Base, get_db
import app.Infraestructura.database.models  # noqa: F401  registra los ORM
from app.Infraestructura.security import get_password_hash
from app.Infraestructura.database.models.usuario import UsuarioORM
from app.Infraestructura.tasks import scheduler as scheduler_module
from app.main import app
from app.Domain.Entities.catalogos import Rol


@pytest.fixture(scope="function")
def db_session():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    @event.listens_for(engine, "connect")
    def _activar_fks(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)
        engine.dispose()


@pytest.fixture(scope="function")
def client(db_session, monkeypatch):
    def override_get_db():
        yield db_session

    # hay que parchear el modulo, no app.main: lifespan resuelve el atributo en
    # tiempo de llamada, asi que el parche si surte efecto.
    monkeypatch.setattr(scheduler_module, "init_scheduler", lambda: None)
    monkeypatch.setattr(scheduler_module, "shutdown_scheduler", lambda: None)

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        assert not scheduler_module.scheduler.running, "el scheduler no debe arrancar durante los tests"
        yield test_client

    app.dependency_overrides.clear()


def _crear_usuario_directo(db_session, nombre, documento, rol, telefono="5550100"):
    """Crea un usuario sin pasar por /auth/register, que siempre asigna rol ciudadano."""
    usuario = UsuarioORM(
        nombre=nombre,
        documento=documento,
        telefono=telefono,
        contraseña_hash=get_password_hash("clave123"),
        email=f"{documento}@test.local",
        direccion="Calle 1 #2-3",
        rol=rol.value,
    )
    db_session.add(usuario)
    db_session.commit()
    db_session.refresh(usuario)
    return usuario


def _login(client, documento, password="clave123"):
    response = client.post("/auth/login", data={"username": documento, "password": password})
    assert response.status_code == 200, response.text
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


@pytest.fixture
def usuario_admin(db_session):
    return _crear_usuario_directo(db_session, "Admin Test", "10000001", Rol.admin)


@pytest.fixture
def usuario_supervisor(db_session):
    return _crear_usuario_directo(db_session, "Supervisor Test", "10000002", Rol.supervisor)


@pytest.fixture
def usuario_tecnico(db_session):
    return _crear_usuario_directo(db_session, "Tecnico Test", "10000003", Rol.tecnico)


@pytest.fixture
def usuario_ciudadano(db_session):
    return _crear_usuario_directo(db_session, "Ciudadano Test", "10000004", Rol.ciudadano)


@pytest.fixture
def headers_admin(client, usuario_admin):
    return _login(client, usuario_admin.documento)


@pytest.fixture
def headers_supervisor(client, usuario_supervisor):
    return _login(client, usuario_supervisor.documento)


@pytest.fixture
def headers_tecnico(client, usuario_tecnico):
    return _login(client, usuario_tecnico.documento)


@pytest.fixture
def headers_ciudadano(client, usuario_ciudadano):
    return _login(client, usuario_ciudadano.documento)


@pytest.fixture
def auth_headers(headers_admin):
    """Alias historico: los tests existentes usan un usuario con permisos totales."""
    return headers_admin


@pytest.fixture
def usuario_id(usuario_admin):
    return usuario_admin.id_usuario


@pytest.fixture
def tokens_por_rol(
    client,
    usuario_admin,
    usuario_supervisor,
    usuario_tecnico,
    usuario_ciudadano,
):
    """Headers de autenticacion para los cuatro roles, en una sola sesion de test."""
    return {
        Rol.admin.value: _login(client, usuario_admin.documento),
        Rol.supervisor.value: _login(client, usuario_supervisor.documento),
        Rol.tecnico.value: _login(client, usuario_tecnico.documento),
        Rol.ciudadano.value: _login(client, usuario_ciudadano.documento),
    }


@pytest.fixture
def reclamo_creado(headers_admin, usuario_id, client):
    response = client.post(
        "/reclamos/",
        headers=headers_admin,
        json={
            "id_usuario": usuario_id,
            "canal": "web",
            "servicio": "agua",
            "categoria": "fuga",
            "urgencia": "alta",
            "descripcion": "Fuga en tuberia principal",
        },
    )
    assert response.status_code == 201, response.text
    return response.json()
