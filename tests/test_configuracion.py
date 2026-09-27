"""Pruebas de configuracion: invariantes que no dependen de un endpoint concreto."""
from app.Infraestructura.tasks import scheduler as scheduler_module


def test_scheduler_no_arranca_durante_los_tests(client):
    """El parche de conftest debe evitar que arranque el BackgroundScheduler real.

    Si esto falla, los jobs de fondo estarian corriendo contra la BD real
    (SessionLocal) en vez de la BD en memoria del fixture.
    """
    assert scheduler_module.scheduler.running is False
    assert scheduler_module.scheduler.get_jobs() == []


def test_fixture_usa_una_bd_distinta_a_la_real(db_session):
    """Aislamiento: la sesion de test no es la de SessionLocal()."""
    from app.Infraestructura.database import SessionLocal

    url_test = str(db_session.get_bind().url)
    url_real = str(SessionLocal.kw["bind"].url)
    assert url_test != url_real
    assert url_test.startswith("sqlite")


def test_health_retorna_ok(client):
    assert client.get("/health").json() == {"status": "ok"}
