def test_crear_orden_reclamo_inexistente_retorna_404(client, auth_headers):
    response = client.post(
        "/seguimiento/ordenes",
        headers=auth_headers,
        json={"id_reclamo": 9999, "cuadrilla": "Cuadrilla Alpha", "fecha_asignacion": "2026-09-26"},
    )
    assert response.status_code == 404


def test_crear_orden_duplicada_retorna_409(client, auth_headers, reclamo_creado):
    payload = {"id_reclamo": reclamo_creado["id_reclamo"], "cuadrilla": "Cuadrilla Alpha", "fecha_asignacion": "2026-09-26"}
    assert client.post("/seguimiento/ordenes", headers=auth_headers, json=payload).status_code == 201
    assert client.post("/seguimiento/ordenes", headers=auth_headers, json=payload).status_code == 409


def test_actualizar_orden_persista_cuadrilla_y_fecha(client, auth_headers, reclamo_creado):
    orden = client.post(
        "/seguimiento/ordenes",
        headers=auth_headers,
        json={"id_reclamo": reclamo_creado["id_reclamo"], "cuadrilla": "Cuadrilla Alpha", "fecha_asignacion": "2026-09-26"},
    ).json()

    response = client.put(
        f"/seguimiento/ordenes/{orden['id_orden']}",
        headers=auth_headers,
        json={"cuadrilla": "Cuadrilla Beta", "fecha_asignacion": "2026-09-27", "estado_orden": "en_curso"},
    )
    assert response.status_code == 200
    persisted = client.get(f"/seguimiento/ordenes/{orden['id_orden']}", headers=auth_headers).json()
    assert persisted["cuadrilla"] == "Cuadrilla Beta"
    assert persisted["fecha_asignacion"] == "2026-09-27"
    assert persisted["estado_orden"] == "en_curso"


def test_actualizar_orden_estado_invalido_retorna_422(client, auth_headers, reclamo_creado):
    orden = client.post(
        "/seguimiento/ordenes",
        headers=auth_headers,
        json={"id_reclamo": reclamo_creado["id_reclamo"], "cuadrilla": "Cuadrilla Alpha", "fecha_asignacion": "2026-09-26"},
    ).json()
    response = client.put(f"/seguimiento/ordenes/{orden['id_orden']}", headers=auth_headers, json={"estado_orden": "volando"})
    assert response.status_code == 422


def test_crear_avance_orden_inexistente_retorna_404(client, auth_headers):
    response = client.post(
        "/seguimiento/avances",
        headers=auth_headers,
        json={"id_orden": 9999, "fecha_avance": "2026-09-26", "descripcion": "Se localizo la fuga", "estado_parcial": "iniciado"},
    )
    assert response.status_code == 404


def test_crear_avance_orden_resuelta_retorna_409(client, auth_headers, reclamo_creado):
    orden = client.post(
        "/seguimiento/ordenes",
        headers=auth_headers,
        json={"id_reclamo": reclamo_creado["id_reclamo"], "cuadrilla": "Cuadrilla Alpha", "fecha_asignacion": "2026-09-26"},
    ).json()
    client.put(f"/seguimiento/ordenes/{orden['id_orden']}", headers=auth_headers, json={"estado_orden": "resuelta"})

    response = client.post(
        "/seguimiento/avances",
        headers=auth_headers,
        json={"id_orden": orden["id_orden"], "fecha_avance": "2026-09-26", "descripcion": "Avance tardio", "estado_parcial": "iniciado"},
    )
    assert response.status_code == 409


def test_listar_avances_de_orden(client, auth_headers, reclamo_creado):
    orden = client.post(
        "/seguimiento/ordenes",
        headers=auth_headers,
        json={"id_reclamo": reclamo_creado["id_reclamo"], "cuadrilla": "Cuadrilla Alpha", "fecha_asignacion": "2026-09-26"},
    ).json()
    client.post(
        "/seguimiento/avances",
        headers=auth_headers,
        json={"id_orden": orden["id_orden"], "fecha_avance": "2026-09-26", "descripcion": "Se localizo la fuga", "estado_parcial": "iniciado"},
    )
    response = client.get(f"/seguimiento/avances/{orden['id_orden']}", headers=auth_headers)
    assert response.status_code == 200
    assert len(response.json()) == 1


def test_listar_avances_orden_inexistente_retorna_404(client, auth_headers):
    assert client.get("/seguimiento/avances/9999", headers=auth_headers).status_code == 404


def test_crear_derivacion_reclamo_inexistente_retorna_404(client, auth_headers):
    response = client.post(
        "/seguimiento/derivaciones",
        headers=auth_headers,
        json={"id_reclamo": 9999, "fecha_derivacion": "2026-09-26", "area_comercial": "facturacion"},
    )
    assert response.status_code == 404


def test_crear_derivacion_area_invalida_retorna_422(client, auth_headers, reclamo_creado):
    response = client.post(
        "/seguimiento/derivaciones",
        headers=auth_headers,
        json={"id_reclamo": reclamo_creado["id_reclamo"], "fecha_derivacion": "2026-09-26", "area_comercial": "inventario"},
    )
    assert response.status_code == 422


def test_actualizar_derivacion_por_id_derivacion(client, auth_headers, reclamo_creado):
    derivacion = client.post(
        "/seguimiento/derivaciones",
        headers=auth_headers,
        json={"id_reclamo": reclamo_creado["id_reclamo"], "fecha_derivacion": "2026-09-26", "area_comercial": "facturacion"},
    ).json()

    response = client.put(
        f"/seguimiento/derivaciones/{derivacion['id_derivacion']}",
        headers=auth_headers,
        json={"estado_derivacion": "resuelta"},
    )
    assert response.status_code == 200
    assert response.json()["estado_derivacion"] == "resuelta"
    assert response.json()["area_comercial"] == "facturacion"


def test_actualizar_derivacion_inexistente_retorna_404(client, auth_headers):
    response = client.put("/seguimiento/derivaciones/9999", headers=auth_headers, json={"estado_derivacion": "resuelta"})
    assert response.status_code == 404


def test_obtener_derivacion_por_reclamo(client, auth_headers, reclamo_creado):
    client.post(
        "/seguimiento/derivaciones",
        headers=auth_headers,
        json={"id_reclamo": reclamo_creado["id_reclamo"], "fecha_derivacion": "2026-09-26", "area_comercial": "cobranza"},
    )
    response = client.get(f"/seguimiento/derivaciones/reclamo/{reclamo_creado['id_reclamo']}", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["area_comercial"] == "cobranza"


def test_eliminar_orden(client, auth_headers, reclamo_creado):
    orden = client.post(
        "/seguimiento/ordenes",
        headers=auth_headers,
        json={"id_reclamo": reclamo_creado["id_reclamo"], "cuadrilla": "Cuadrilla Alpha", "fecha_asignacion": "2026-09-26"},
    ).json()
    assert client.delete(f"/seguimiento/ordenes/{orden['id_orden']}", headers=auth_headers).status_code == 200
    assert client.get(f"/seguimiento/ordenes/{orden['id_orden']}", headers=auth_headers).status_code == 404

def test_eliminar_reclamo_con_orden_y_avances_en_cascada(client, auth_headers, reclamo_creado):
    orden = client.post(
        "/seguimiento/ordenes",
        headers=auth_headers,
        json={"id_reclamo": reclamo_creado["id_reclamo"], "cuadrilla": "Cuadrilla Alpha", "fecha_asignacion": "2026-09-26"},
    ).json()
    client.post(
        "/seguimiento/avances",
        headers=auth_headers,
        json={"id_orden": orden["id_orden"], "fecha_avance": "2026-09-26", "descripcion": "Fuga localizada", "estado_parcial": "iniciado"},
    )
    client.post(
        "/seguimiento/derivaciones",
        headers=auth_headers,
        json={"id_reclamo": reclamo_creado["id_reclamo"], "fecha_derivacion": "2026-09-26", "area_comercial": "facturacion"},
    )

    response = client.delete(f"/reclamos/{reclamo_creado['id_reclamo']}", headers=auth_headers)
    assert response.status_code == 200
    assert client.get(f"/reclamos/{reclamo_creado['id_reclamo']}", headers=auth_headers).status_code == 404
    assert client.get(f"/seguimiento/ordenes/{orden['id_orden']}", headers=auth_headers).status_code == 404
