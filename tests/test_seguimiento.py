def _payload_orden(reclamo_creado, cuadrilla):
    return {
        "id_reclamo": reclamo_creado["id_reclamo"],
        "id_cuadrilla": cuadrilla["id_cuadrilla"],
        "fecha_asignacion": "2026-09-26",
    }


def test_crear_orden_reclamo_inexistente_retorna_404(client, auth_headers, cuadrilla_creada):
    response = client.post(
        "/seguimiento/ordenes",
        headers=auth_headers,
        json={"id_reclamo": 9999, "id_cuadrilla": cuadrilla_creada["id_cuadrilla"], "fecha_asignacion": "2026-09-26"},
    )
    assert response.status_code == 404


def test_crear_orden_cuadrilla_inexistente_retorna_404(client, auth_headers, reclamo_creado):
    response = client.post(
        "/seguimiento/ordenes",
        headers=auth_headers,
        json={"id_reclamo": reclamo_creado["id_reclamo"], "id_cuadrilla": 9999, "fecha_asignacion": "2026-09-26"},
    )
    assert response.status_code == 404


def test_crear_orden_devuelve_el_nombre_de_la_cuadrilla(client, auth_headers, reclamo_creado, cuadrilla_creada):
    """El cliente envia el id y el nombre lo responde el servidor."""
    response = client.post(
        "/seguimiento/ordenes",
        headers=auth_headers,
        json=_payload_orden(reclamo_creado, cuadrilla_creada),
    )
    assert response.status_code == 201
    assert response.json()["id_cuadrilla"] == cuadrilla_creada["id_cuadrilla"]
    assert response.json()["cuadrilla"] == cuadrilla_creada["nombre"]


def test_crear_orden_duplicada_retorna_409(client, auth_headers, reclamo_creado, cuadrilla_creada):
    payload = _payload_orden(reclamo_creado, cuadrilla_creada)
    assert client.post("/seguimiento/ordenes", headers=auth_headers, json=payload).status_code == 201
    assert client.post("/seguimiento/ordenes", headers=auth_headers, json=payload).status_code == 409


def test_actualizar_orden_persista_cuadrilla_y_fecha(client, auth_headers, reclamo_creado, crear_cuadrilla):
    origen = crear_cuadrilla("Cuadrilla Origen")
    destino = crear_cuadrilla("Cuadrilla Destino")
    orden = client.post(
        "/seguimiento/ordenes",
        headers=auth_headers,
        json=_payload_orden(reclamo_creado, origen),
    ).json()

    response = client.put(
        f"/seguimiento/ordenes/{orden['id_orden']}",
        headers=auth_headers,
        json={"id_cuadrilla": destino["id_cuadrilla"], "fecha_asignacion": "2026-09-27", "estado_orden": "en_curso"},
    )
    assert response.status_code == 200
    persisted = client.get(f"/seguimiento/ordenes/{orden['id_orden']}", headers=auth_headers).json()
    assert persisted["id_cuadrilla"] == destino["id_cuadrilla"]
    assert persisted["cuadrilla"] == "Cuadrilla Destino"
    assert persisted["fecha_asignacion"] == "2026-09-27"
    assert persisted["estado_orden"] == "en_curso"


def test_actualizar_orden_estado_invalido_retorna_422(client, auth_headers, reclamo_creado, cuadrilla_creada):
    orden = client.post(
        "/seguimiento/ordenes",
        headers=auth_headers,
        json=_payload_orden(reclamo_creado, cuadrilla_creada),
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


def test_crear_avance_orden_resuelta_retorna_409(client, auth_headers, reclamo_creado, cuadrilla_creada):
    orden = client.post(
        "/seguimiento/ordenes",
        headers=auth_headers,
        json=_payload_orden(reclamo_creado, cuadrilla_creada),
    ).json()
    # Sin avances la orden no se puede resolver, asi que primero se registra uno.
    client.post(
        "/seguimiento/avances",
        headers=auth_headers,
        json={"id_orden": orden["id_orden"], "fecha_avance": "2026-09-26", "descripcion": "Se localizo la fuga", "estado_parcial": "iniciado"},
    )
    client.put(f"/seguimiento/ordenes/{orden['id_orden']}", headers=auth_headers, json={"estado_orden": "resuelta"})

    response = client.post(
        "/seguimiento/avances",
        headers=auth_headers,
        json={"id_orden": orden["id_orden"], "fecha_avance": "2026-09-26", "descripcion": "Avance tardio", "estado_parcial": "iniciado"},
    )
    assert response.status_code == 409


def test_listar_avances_de_orden(client, auth_headers, reclamo_creado, cuadrilla_creada):
    orden = client.post(
        "/seguimiento/ordenes",
        headers=auth_headers,
        json=_payload_orden(reclamo_creado, cuadrilla_creada),
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


def test_eliminar_orden(client, auth_headers, reclamo_creado, cuadrilla_creada):
    orden = client.post(
        "/seguimiento/ordenes",
        headers=auth_headers,
        json=_payload_orden(reclamo_creado, cuadrilla_creada),
    ).json()
    assert client.delete(f"/seguimiento/ordenes/{orden['id_orden']}", headers=auth_headers).status_code == 200
    assert client.get(f"/seguimiento/ordenes/{orden['id_orden']}", headers=auth_headers).status_code == 404

def test_eliminar_reclamo_con_orden_y_avances_en_cascada(client, auth_headers, reclamo_creado, cuadrilla_creada):
    orden = client.post(
        "/seguimiento/ordenes",
        headers=auth_headers,
        json=_payload_orden(reclamo_creado, cuadrilla_creada),
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


# --- una atencion tecnica no culmina sin avances --------------------------------

def _crear_orden(client, headers, reclamo_creado, cuadrilla):
    return client.post(
        "/seguimiento/ordenes",
        headers=headers,
        json=_payload_orden(reclamo_creado, cuadrilla),
    ).json()


def _registrar_avance(client, headers, id_orden):
    return client.post(
        "/seguimiento/avances",
        headers=headers,
        json={"id_orden": id_orden, "fecha_avance": "2026-09-26", "descripcion": "Trabajo ejecutado en sitio", "estado_parcial": "verificado"},
    )


def _clasificar(client, headers, reclamo_creado):
    return client.put(
        f"/reclamos/{reclamo_creado['id_reclamo']}/clasificar",
        headers=headers,
        json={"servicio": "agua", "categoria": "fuga", "urgencia": "alta"},
    )


def _asignar_plazo(client, headers, reclamo_creado):
    normativa = client.post(
        "/normativa/",
        headers=headers,
        json={"servicio": "agua", "categoria": "fuga", "urgencia": "alta", "plazo_maximo_dias": 7, "vigencia_desde": "2026-01-01"},
    ).json()
    return client.put(
        f"/reclamos/{reclamo_creado['id_reclamo']}/asignar-plazo",
        headers=headers,
        json={"id_normativa": normativa["id_normativa"], "fecha_tope": "2026-10-15"},
    )


def test_actualizar_orden_a_resuelta_sin_avances_retorna_409(client, auth_headers, reclamo_creado, cuadrilla_creada):
    orden = _crear_orden(client, auth_headers, reclamo_creado, cuadrilla_creada)
    response = client.put(
        f"/seguimiento/ordenes/{orden['id_orden']}", headers=auth_headers, json={"estado_orden": "resuelta"}
    )
    assert response.status_code == 409
    # La orden no debe haberse movido de estado.
    actual = client.get(f"/seguimiento/ordenes/{orden['id_orden']}", headers=auth_headers).json()
    assert actual["estado_orden"] == "asignada"


def test_actualizar_orden_a_resuelta_con_avances_retorna_200(client, auth_headers, reclamo_creado, cuadrilla_creada):
    orden = _crear_orden(client, auth_headers, reclamo_creado, cuadrilla_creada)
    assert _registrar_avance(client, auth_headers, orden["id_orden"]).status_code == 201
    response = client.put(
        f"/seguimiento/ordenes/{orden['id_orden']}", headers=auth_headers, json={"estado_orden": "resuelta"}
    )
    assert response.status_code == 200
    assert response.json()["estado_orden"] == "resuelta"


def test_actualizar_orden_otros_campos_sin_avances_permitido(client, auth_headers, reclamo_creado, crear_cuadrilla):
    """La regla solo bloquea culminar, no reasignar cuadrilla."""
    origen = crear_cuadrilla("Cuadrilla Origen")
    destino = crear_cuadrilla("Cuadrilla Bravo")
    orden = _crear_orden(client, auth_headers, reclamo_creado, origen)
    response = client.put(
        f"/seguimiento/ordenes/{orden['id_orden']}",
        headers=auth_headers,
        json={"id_cuadrilla": destino["id_cuadrilla"]},
    )
    assert response.status_code == 200
    assert response.json()["cuadrilla"] == "Cuadrilla Bravo"


def test_resolver_reclamo_con_orden_sin_avances_retorna_409(client, auth_headers, reclamo_creado, cuadrilla_creada):
    _crear_orden(client, auth_headers, reclamo_creado, cuadrilla_creada)
    assert _clasificar(client, auth_headers, reclamo_creado).status_code == 200
    assert _asignar_plazo(client, auth_headers, reclamo_creado).status_code == 200
    response = client.put(
        f"/reclamos/{reclamo_creado['id_reclamo']}/resolver", headers=auth_headers, json={"resultado": "resuelto"}
    )
    assert response.status_code == 409


def test_resolver_reclamo_con_orden_con_avances_retorna_200(client, auth_headers, reclamo_creado, cuadrilla_creada):
    orden = _crear_orden(client, auth_headers, reclamo_creado, cuadrilla_creada)
    _registrar_avance(client, auth_headers, orden["id_orden"])
    assert _clasificar(client, auth_headers, reclamo_creado).status_code == 200
    assert _asignar_plazo(client, auth_headers, reclamo_creado).status_code == 200
    response = client.put(
        f"/reclamos/{reclamo_creado['id_reclamo']}/resolver", headers=auth_headers, json={"resultado": "resuelto"}
    )
    assert response.status_code == 200
    assert response.json()["estado"] == "resuelto"


def test_resolver_reclamo_sin_orden_sin_avances_retorna_200(client, auth_headers, reclamo_creado):
    """Regresion: sin orden de trabajo no hay avances que exigir."""
    assert _clasificar(client, auth_headers, reclamo_creado).status_code == 200
    assert _asignar_plazo(client, auth_headers, reclamo_creado).status_code == 200
    response = client.put(
        f"/reclamos/{reclamo_creado['id_reclamo']}/resolver", headers=auth_headers, json={"resultado": "resuelto"}
    )
    assert response.status_code == 200
    assert response.json()["estado"] == "resuelto"


# --- la capacidad limita la carga por cuadrilla --------------------------------

def _reclamo_para_asignar(client, headers, usuario_admin, db_session, sufijo):
    """Cada orden necesita su propio reclamo: una orden por reclamo."""
    from tests.conftest import _id_medidor

    response = client.post(
        "/reclamos/",
        headers=headers,
        json={
            "id_usuario": usuario_admin.id_usuario,
            "canal": "web",
            "servicio": "agua",
            "id_medidor": _id_medidor(db_session, usuario_admin, "agua"),
            "categoria": "fuga",
            "urgencia": "alta",
            "descripcion": f"Fuga {sufijo}",
            "nombre_cuenta": "Maria Lopez",
            "direccion": "Calle 45 # 12-30",
        },
    )
    assert response.status_code == 201, response.text
    return response.json()


def test_asignar_orden_con_capacidad_libre_retorna_201(client, auth_headers, reclamo_creado, crear_cuadrilla):
    cuadrilla = crear_cuadrilla("Cuadrilla Con Cupo", capacidad=2)
    response = client.post("/seguimiento/ordenes", headers=auth_headers, json=_payload_orden(reclamo_creado, cuadrilla))
    assert response.status_code == 201


def test_asignar_orden_en_la_ultima_plaza_retorna_201(
    client, auth_headers, reclamo_creado, crear_cuadrilla, usuario_admin, db_session
):
    cuadrilla = crear_cuadrilla("Cuadrilla Ultima Plaza", capacidad=2)
    otro = _reclamo_para_asignar(client, auth_headers, usuario_admin, db_session, "segunda")
    tercero = _reclamo_para_asignar(client, auth_headers, usuario_admin, db_session, "tercera")

    assert client.post("/seguimiento/ordenes", headers=auth_headers, json=_payload_orden(reclamo_creado, cuadrilla)).status_code == 201
    # La segunda orden ocupa la ultima plaza y entra: el tope es un maximo, no
    # un maximo exclusivo.
    assert client.post("/seguimiento/ordenes", headers=auth_headers, json=_payload_orden(otro, cuadrilla)).status_code == 201
    # Ya no queda ninguna.
    assert client.post("/seguimiento/ordenes", headers=auth_headers, json=_payload_orden(tercero, cuadrilla)).status_code == 409


def test_asignar_orden_con_capacidad_agotada_retorna_409(
    client, auth_headers, reclamo_creado, crear_cuadrilla, usuario_admin, db_session
):
    cuadrilla = crear_cuadrilla("Cuadrilla Llena", capacidad=1)
    otro = _reclamo_para_asignar(client, auth_headers, usuario_admin, db_session, "segunda")
    client.post("/seguimiento/ordenes", headers=auth_headers, json=_payload_orden(reclamo_creado, cuadrilla))
    tercero = _reclamo_para_asignar(client, auth_headers, usuario_admin, db_session, "tercera")

    response = client.post("/seguimiento/ordenes", headers=auth_headers, json=_payload_orden(tercero, cuadrilla))
    assert response.status_code == 409
    assert "capacidad" in response.json()["detail"].lower()


def test_resolver_orden_libera_el_cupo(
    client, auth_headers, reclamo_creado, crear_cuadrilla, usuario_admin, db_session
):
    """Una orden resuelta no ocupa a la cuadrilla: el cupo vuelve solo."""
    cuadrilla = crear_cuadrilla("Cuadrilla Que Libera", capacidad=1)
    siguiente = _reclamo_para_asignar(client, auth_headers, usuario_admin, db_session, "siguiente")
    orden = client.post("/seguimiento/ordenes", headers=auth_headers, json=_payload_orden(reclamo_creado, cuadrilla)).json()

    assert client.post("/seguimiento/ordenes", headers=auth_headers, json=_payload_orden(siguiente, cuadrilla)).status_code == 409

    _registrar_avance(client, auth_headers, orden["id_orden"])
    assert client.put(
        f"/seguimiento/ordenes/{orden['id_orden']}", headers=auth_headers, json={"estado_orden": "resuelta"}
    ).status_code == 200

    assert client.post("/seguimiento/ordenes", headers=auth_headers, json=_payload_orden(siguiente, cuadrilla)).status_code == 201


def test_reasignar_orden_a_cuadrilla_llena_retorna_409(
    client, auth_headers, reclamo_creado, crear_cuadrilla, usuario_admin, db_session
):
    """Mover trabajo a una cuadrilla sin cupo tambien se bloquea."""
    origen = crear_cuadrilla("Cuadrilla Con Cupo")
    destino = crear_cuadrilla("Cuadrilla Sin Cupo", capacidad=1)
    orden = _crear_orden(client, auth_headers, reclamo_creado, origen)
    otra = _reclamo_para_asignar(client, auth_headers, usuario_admin, db_session, "ocupante")
    client.post("/seguimiento/ordenes", headers=auth_headers, json=_payload_orden(otra, destino))

    response = client.put(
        f"/seguimiento/ordenes/{orden['id_orden']}",
        headers=auth_headers,
        json={"id_cuadrilla": destino["id_cuadrilla"]},
    )
    assert response.status_code == 409
    # La orden no debe haberse movido.
    actual = client.get(f"/seguimiento/ordenes/{orden['id_orden']}", headers=auth_headers).json()
    assert actual["id_cuadrilla"] == origen["id_cuadrilla"]


def test_reasignar_orden_a_cuadrilla_con_cupo_retorna_200(
    client, auth_headers, reclamo_creado, crear_cuadrilla, usuario_admin, db_session
):
    origen = crear_cuadrilla("Cuadrilla Origen")
    destino = crear_cuadrilla("Cuadrilla Destino", capacidad=2)
    orden = _crear_orden(client, auth_headers, reclamo_creado, origen)
    otra = _reclamo_para_asignar(client, auth_headers, usuario_admin, db_session, "ocupante")
    client.post("/seguimiento/ordenes", headers=auth_headers, json=_payload_orden(otra, destino))

    response = client.put(
        f"/seguimiento/ordenes/{orden['id_orden']}",
        headers=auth_headers,
        json={"id_cuadrilla": destino["id_cuadrilla"]},
    )
    assert response.status_code == 200
    assert response.json()["id_cuadrilla"] == destino["id_cuadrilla"]


def test_reasignar_orden_a_su_misma_cuadrilla_no_se_bloquea(
    client, auth_headers, reclamo_creado, crear_cuadrilla
):
    """Al reasignar, la orden se excluye del conteo: la ultima plaza no se
    bloquea a si misma."""
    cuadrilla = crear_cuadrilla("Cuadrilla Al Limite", capacidad=1)
    orden = _crear_orden(client, auth_headers, reclamo_creado, cuadrilla)

    response = client.put(
        f"/seguimiento/ordenes/{orden['id_orden']}",
        headers=auth_headers,
        json={"id_cuadrilla": cuadrilla["id_cuadrilla"]},
    )
    assert response.status_code == 200
