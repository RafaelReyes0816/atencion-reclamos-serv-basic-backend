"""Pruebas de los medidores del cliente.

Cubre el alta automatica de los dos medidores (agua y luz) al crear la cuenta, la
regla de un solo medidor por servicio, la edicion del numero y la lista que
consumen los roles internos al registrar un reclamo en ventanilla.
"""
import re

from conftest import _id_medidor


def test_registro_crea_medidor_de_agua_y_luz(client, usuario_id):
    """Toda cuenta nueva nace con sus dos medidores, sin que nadie los pida."""
    response = client.post(
        "/auth/register",
        json={
            "nombre": "Nuevo Cliente",
            "documento": "80000001",
            "telefono": "5554444",
            "contraseña": "clave123",
            "email": "nuevo@correo.com",
            "direccion": "Calle 5 #6-7",
        },
    )
    assert response.status_code == 201, response.text

    login = client.post(
        "/auth/login", data={"username": "80000001", "password": "clave123"}
    )
    headers = {"Authorization": f"Bearer {login.json()['access_token']}"}

    medidores = client.get("/medidores/", headers=headers)
    assert medidores.status_code == 200
    cuerpo = medidores.json()
    assert len(cuerpo) == 2
    assert {m["servicio"] for m in cuerpo} == {"agua", "luz"}
    for m in cuerpo:
        # El codigo lo genera el sistema; el documento del cliente no aparece.
        assert re.fullmatch(r"(AG|LUZ)-[A-Z0-9]{8}", m["numero"]), m["numero"]
        assert "80000001" not in m["numero"]
    assert cuerpo[0]["numero"] != cuerpo[1]["numero"]


def test_codigos_de_medidor_no_se_repiten_entre_clientes(client, usuario_id):
    """Dos clientes nunca comparten codigo: es lo que distingue un suministro."""
    vistos = set()
    for i, documento in enumerate(["80000010", "80000011", "80000012", "80000013"]):
        registro = client.post(
            "/auth/register",
            json={
                "nombre": f"Cliente {i}",
                "documento": documento,
                "telefono": "5554444",
                "contraseña": "clave123",
                "email": f"{documento}@correo.com",
                "direccion": "Calle 1",
            },
        )
        assert registro.status_code == 201, registro.text
        login = client.post("/auth/login", data={"username": documento, "password": "clave123"})
        headers = {"Authorization": f"Bearer {login.json()['access_token']}"}
        for m in client.get("/medidores/", headers=headers).json():
            assert m["numero"] not in vistos, f"codigo repetido: {m['numero']}"
            vistos.add(m["numero"])
    assert len(vistos) == 8


def test_numero_aleatorio_no_deriva_del_documento():
    """El codigo se sortea, asi que dos altas seguidas dan numeros distintos."""
    from app.Application.usecase.medidor.gestionar_medidor import generar_numero_medidor

    primeros = {generar_numero_medidor("agua") for _ in range(50)}
    assert len(primeros) > 45, "el alfabeto es demasiado pequeno para ser un codigo"
    for numero in primeros:
        assert re.fullmatch(r"AG-[A-Z0-9]{8}", numero)
        assert not re.search(r"80000", numero)


def test_usuario_creado_por_admin_tambien_recibe_medidores(client, headers_admin):
    response = client.post(
        "/usuarios/",
        headers=headers_admin,
        json={
            "nombre": "Vecino Registrado",
            "documento": "80000002",
            "telefono": "5555555",
            "contraseña": "clave123",
            "email": "vecino@correo.com",
            "direccion": "Calle 9 #1-2",
            "rol": "ciudadano",
        },
    )
    assert response.status_code == 201, response.text
    id_nuevo = response.json()["id_usuario"]

    medidores = client.get(f"/medidores/?id_usuario={id_nuevo}", headers=headers_admin)
    assert medidores.status_code == 200
    assert len(medidores.json()) == 2


def test_registro_es_idempotente_no_duplica_medidores(
    client, headers_admin, db_session, usuario_ciudadano
):
    """Asignar de nuevo los medidores de una cuenta existente no los repite."""
    from app.Application.usecase.medidor.gestionar_medidor import (
        AsignarMedidoresPorDefectoUseCase,
    )
    from app.Infraestructura.repositories.medidor_repository import MedidorRepository
    from app.Infraestructura.repositories.usuario_repository import UsuarioRepository

    antes = client.get(
        f"/medidores/?id_usuario={usuario_ciudadano.id_usuario}", headers=headers_admin
    ).json()

    use_case = AsignarMedidoresPorDefectoUseCase(
        MedidorRepository(db_session), UsuarioRepository(db_session)
    )
    assert use_case.execute(usuario_ciudadano.id_usuario) == []

    despues = client.get(
        f"/medidores/?id_usuario={usuario_ciudadano.id_usuario}", headers=headers_admin
    ).json()
    assert len(despues) == len(antes) == 2


def test_no_se_puede_crear_segundo_medidor_del_mismo_servicio(
    client, headers_admin, usuario_ciudadano
):
    response = client.post(
        "/medidores/",
        headers=headers_admin,
        json={
            "id_usuario": usuario_ciudadano.id_usuario,
            "servicio": "agua",
            "numero": "AG-OTRO-999",
        },
    )
    assert response.status_code == 400
    assert "ya tiene un medidor" in response.json()["detail"]


def test_crear_medidor_para_usuario_inexistente_retorna_404(client, headers_admin):
    response = client.post(
        "/medidores/",
        headers=headers_admin,
        json={"id_usuario": 9999, "servicio": "agua", "numero": "AG-999999"},
    )
    assert response.status_code == 404


def test_numero_muy_corto_retorna_422(client, headers_admin, usuario_ciudadano, db_session):
    id_agua = _id_medidor(db_session, usuario_ciudadano, "agua")
    response = client.put(
        f"/medidores/{id_agua}", headers=headers_admin, json={"numero": "A1"}
    )
    assert response.status_code == 422


def test_numero_con_simbolos_retorna_422(client, headers_admin, usuario_ciudadano, db_session):
    id_agua = _id_medidor(db_session, usuario_ciudadano, "agua")
    response = client.put(
        f"/medidores/{id_agua}", headers=headers_admin, json={"numero": "AG 100245"}
    )
    assert response.status_code == 422


def test_ciudadano_edita_el_numero_de_su_medidor(
    client, headers_ciudadano, usuario_ciudadano, db_session
):
    id_agua = _id_medidor(db_session, usuario_ciudadano, "agua")
    response = client.put(
        f"/medidores/{id_agua}", headers=headers_ciudadano, json={"numero": "AG-COR-55"}
    )
    assert response.status_code == 200
    assert response.json()["numero"] == "AG-COR-55"


def test_ciudadano_no_edita_el_medidor_de_otro(
    client, headers_ciudadano, usuario_admin, db_session
):
    ajeno = _id_medidor(db_session, usuario_admin, "agua")
    response = client.put(
        f"/medidores/{ajeno}", headers=headers_ciudadano, json={"numero": "AG-INTRUSO"}
    )
    assert response.status_code == 403


def test_lista_de_ciudadanos_incluye_sus_medidores(client, headers_tecnico, usuario_ciudadano):
    """Es el endpoint que consume el formulario interno al registrar por ventanilla."""
    response = client.get("/medidores/ciudadanos", headers=headers_tecnico)
    assert response.status_code == 200
    cuerpo = response.json()
    assert len(cuerpo) == 1
    entry = cuerpo[0]
    assert entry["id_usuario"] == usuario_ciudadano.id_usuario
    assert entry["documento"] == usuario_ciudadano.documento
    assert {m["servicio"] for m in entry["medidores"]} == {"agua", "luz"}


def test_lista_de_ciudadanos_omite_cuentas_internas(
    client, headers_supervisor, usuario_admin, usuario_supervisor
):
    response = client.get("/medidores/ciudadanos", headers=headers_supervisor)
    assert response.status_code == 200
    documentos = {c["documento"] for c in response.json()}
    assert usuario_admin.documento not in documentos
    assert usuario_supervisor.documento not in documentos
