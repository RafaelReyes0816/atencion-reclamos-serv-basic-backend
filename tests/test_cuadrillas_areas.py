def test_crear_cuadrilla_datos_validos_retorna_201(client, auth_headers):
    response = client.post(
        "/cuadrillas/",
        headers=auth_headers,
        json={"nombre": "Cuadrilla Alpha", "especialidad": "agua", "capacidad": 3, "contacto": "555-0101"},
    )
    assert response.status_code == 201
    assert response.json()["especialidad"] == "agua"


def test_crear_cuadrilla_especialidad_invalida_retorna_422(client, auth_headers):
    response = client.post(
        "/cuadrillas/",
        headers=auth_headers,
        json={"nombre": "Cuadrilla X", "especialidad": "gas", "capacidad": 3, "contacto": "555-0101"},
    )
    assert response.status_code == 422


def test_actualizar_cuadrilla_persista_todos_los_campos(client, auth_headers):
    created = client.post(
        "/cuadrillas/",
        headers=auth_headers,
        json={"nombre": "Cuadrilla Alpha", "especialidad": "agua", "capacidad": 3, "contacto": "555-0101"},
    ).json()

    response = client.put(
        f"/cuadrillas/{created['id_cuadrilla']}",
        headers=auth_headers,
        json={"nombre": "Cuadrilla Renombrada", "capacidad": 8},
    )
    assert response.status_code == 200
    persisted = client.get(f"/cuadrillas/{created['id_cuadrilla']}", headers=auth_headers).json()
    assert persisted["nombre"] == "Cuadrilla Renombrada"
    assert persisted["capacidad"] == 8
    assert persisted["especialidad"] == "agua"
    assert persisted["contacto"] == "555-0101"


def test_actualizar_cuadrilla_inexistente_retorna_404(client, auth_headers):
    response = client.put("/cuadrillas/9999", headers=auth_headers, json={"nombre": "No existe"})
    assert response.status_code == 404


def test_obtener_cuadrillas_disponibles_por_especialidad(client, auth_headers):
    client.post(
        "/cuadrillas/",
        headers=auth_headers,
        json={"nombre": "Cuadrilla Agua", "especialidad": "agua", "capacidad": 3, "contacto": "555-0101"},
    )
    client.post(
        "/cuadrillas/",
        headers=auth_headers,
        json={"nombre": "Cuadrilla Luz", "especialidad": "luz", "capacidad": 2, "contacto": "555-0102"},
    )
    response = client.get("/cuadrillas/disponibles/agua", headers=auth_headers)
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["especialidad"] == "agua"


def test_obtener_cuadrillas_disponibles_especialidad_invalida_retorna_422(client, auth_headers):
    assert client.get("/cuadrillas/disponibles/gas", headers=auth_headers).status_code == 422


def test_cuadrilla_sin_ordenes_reporta_carga_cero(client, auth_headers, crear_cuadrilla):
    """Lo que no tiene ordenes muestra tope completo y disponible."""
    cuadrilla = crear_cuadrilla("Cuadrilla Sin Carga", capacidad=3)
    data = client.get(f"/cuadrillas/{cuadrilla['id_cuadrilla']}", headers=auth_headers).json()
    assert data["ordenes_activas"] == 0
    assert data["disponible"] is True


def test_disponibles_ordena_por_carga_y_marca_saturada(
    client, auth_headers, reclamo_creado, crear_cuadrilla, usuario_admin, db_session
):
    """La cuadrilla con menos trabajo se ofrece primero, y la llena queda al
    final aunque todavia aparezca en la lista."""
    from tests.conftest import _id_medidor

    vacia = crear_cuadrilla("Cuadrilla Con Mucho Cupo", capacidad=5)
    casi = crear_cuadrilla("Cuadrilla Con Poco Cupo", capacidad=3)
    llena = crear_cuadrilla("Cuadrilla Ya Llena", capacidad=1)

    otro = client.post(
        "/reclamos/",
        headers=auth_headers,
        json={
            "id_usuario": usuario_admin.id_usuario,
            "canal": "web",
            "servicio": "agua",
            "id_medidor": _id_medidor(db_session, usuario_admin, "agua"),
            "categoria": "fuga",
            "urgencia": "alta",
            "descripcion": "Segunda fuga",
            "nombre_cuenta": "Maria Lopez",
            "direccion": "Calle 45 # 12-30",
        },
    ).json()
    client.post(
        "/seguimiento/ordenes",
        headers=auth_headers,
        json={"id_reclamo": reclamo_creado["id_reclamo"], "id_cuadrilla": casi["id_cuadrilla"], "fecha_asignacion": "2026-09-26"},
    )
    client.post(
        "/seguimiento/ordenes",
        headers=auth_headers,
        json={"id_reclamo": otro["id_reclamo"], "id_cuadrilla": llena["id_cuadrilla"], "fecha_asignacion": "2026-09-26"},
    )

    listado = client.get("/cuadrillas/disponibles/agua", headers=auth_headers).json()
    por_id = {c["id_cuadrilla"]: c for c in listado}
    assert por_id[vacia["id_cuadrilla"]]["ordenes_activas"] == 0
    assert por_id[casi["id_cuadrilla"]]["ordenes_activas"] == 1
    assert por_id[llena["id_cuadrilla"]]["ordenes_activas"] == 1
    assert por_id[llena["id_cuadrilla"]]["disponible"] is False
    # Sin carga, luego la de una orden, y la saturada al final.
    assert [c["id_cuadrilla"] for c in listado] == [
        vacia["id_cuadrilla"], casi["id_cuadrilla"], llena["id_cuadrilla"]
    ]


def test_orden_resuelta_no_cuenta_en_la_carga(client, auth_headers, reclamo_creado, crear_cuadrilla):
    """Solo `asignada` y `en_curso` ocupan; al resolver, el cupo queda libre."""
    cuadrilla = crear_cuadrilla("Cuadrilla Se Libera", capacidad=1)
    orden = client.post(
        "/seguimiento/ordenes",
        headers=auth_headers,
        json={"id_reclamo": reclamo_creado["id_reclamo"], "id_cuadrilla": cuadrilla["id_cuadrilla"], "fecha_asignacion": "2026-09-26"},
    ).json()
    assert client.get(f"/cuadrillas/{cuadrilla['id_cuadrilla']}", headers=auth_headers).json()["ordenes_activas"] == 1

    client.post(
        "/seguimiento/avances",
        headers=auth_headers,
        json={"id_orden": orden["id_orden"], "fecha_avance": "2026-09-26", "descripcion": "Reparacion hecha", "estado_parcial": "verificado"},
    )
    client.put(f"/seguimiento/ordenes/{orden['id_orden']}", headers=auth_headers, json={"estado_orden": "resuelta"})

    data = client.get(f"/cuadrillas/{cuadrilla['id_cuadrilla']}", headers=auth_headers).json()
    assert data["ordenes_activas"] == 0
    assert data["disponible"] is True


def test_bajar_capacidad_por_debajo_de_la_carga_avisa(
    client, auth_headers, reclamo_creado, crear_cuadrilla
):
    """Se puede bajar la capacidad aunque la cuadrilla quede por encima del
    tope; la respuesta lo deja claro en lugar de fallar en silencio."""
    cuadrilla = crear_cuadrilla("Cuadrilla Que Se Achica", capacidad=3)
    client.post(
        "/seguimiento/ordenes",
        headers=auth_headers,
        json={"id_reclamo": reclamo_creado["id_reclamo"], "id_cuadrilla": cuadrilla["id_cuadrilla"], "fecha_asignacion": "2026-09-26"},
    )

    response = client.put(
        f"/cuadrillas/{cuadrilla['id_cuadrilla']}",
        headers=auth_headers,
        json={"capacidad": 1},
    )
    assert response.status_code == 200
    assert response.json()["capacidad"] == 1
    # 1 orden activa con tope 1: al limite y sin cupo para la siguiente.
    assert response.json()["ordenes_activas"] == 1
    assert response.json()["disponible"] is False


def test_bajar_capacidad_por_debajo_de_la_carga_bloquea_asignaciones(
    client, auth_headers, reclamo_creado, crear_cuadrilla, usuario_admin, db_session
):
    """Con el tope por debajo de la carga, la cuadrilla ya no recibe trabajo."""
    from tests.conftest import _id_medidor

    cuadrilla = crear_cuadrilla("Cuadrilla Sobrecargada", capacidad=3)
    otro = client.post(
        "/reclamos/",
        headers=auth_headers,
        json={
            "id_usuario": usuario_admin.id_usuario,
            "canal": "web",
            "servicio": "agua",
            "id_medidor": _id_medidor(db_session, usuario_admin, "agua"),
            "categoria": "fuga",
            "urgencia": "alta",
            "descripcion": "Segunda fuga",
            "nombre_cuenta": "Maria Lopez",
            "direccion": "Calle 45 # 12-30",
        },
    ).json()
    client.post(
        "/seguimiento/ordenes",
        headers=auth_headers,
        json={"id_reclamo": reclamo_creado["id_reclamo"], "id_cuadrilla": cuadrilla["id_cuadrilla"], "fecha_asignacion": "2026-09-26"},
    )
    client.put(f"/cuadrillas/{cuadrilla['id_cuadrilla']}", headers=auth_headers, json={"capacidad": 1})

    response = client.post(
        "/seguimiento/ordenes",
        headers=auth_headers,
        json={"id_reclamo": otro["id_reclamo"], "id_cuadrilla": cuadrilla["id_cuadrilla"], "fecha_asignacion": "2026-09-26"},
    )
    assert response.status_code == 409


def test_ampliar_capacidad_habilita_de_nuevo(
    client, auth_headers, reclamo_creado, crear_cuadrilla, usuario_admin, db_session
):
    """La via de salida: ampliar el tope reabre la asignacion."""
    from tests.conftest import _id_medidor

    cuadrilla = crear_cuadrilla("Cuadrilla Que Crece", capacidad=1)
    otro = client.post(
        "/reclamos/",
        headers=auth_headers,
        json={
            "id_usuario": usuario_admin.id_usuario,
            "canal": "web",
            "servicio": "agua",
            "id_medidor": _id_medidor(db_session, usuario_admin, "agua"),
            "categoria": "fuga",
            "urgencia": "alta",
            "descripcion": "Segunda fuga",
            "nombre_cuenta": "Maria Lopez",
            "direccion": "Calle 45 # 12-30",
        },
    ).json()
    payload_otro = {
        "id_reclamo": otro["id_reclamo"],
        "id_cuadrilla": cuadrilla["id_cuadrilla"],
        "fecha_asignacion": "2026-09-26",
    }
    client.post(
        "/seguimiento/ordenes",
        headers=auth_headers,
        json={"id_reclamo": reclamo_creado["id_reclamo"], "id_cuadrilla": cuadrilla["id_cuadrilla"], "fecha_asignacion": "2026-09-26"},
    )
    assert client.post("/seguimiento/ordenes", headers=auth_headers, json=payload_otro).status_code == 409

    client.put(f"/cuadrillas/{cuadrilla['id_cuadrilla']}", headers=auth_headers, json={"capacidad": 4})
    assert client.post("/seguimiento/ordenes", headers=auth_headers, json=payload_otro).status_code == 201


def test_eliminar_cuadrilla(client, auth_headers):
    created = client.post(
        "/cuadrillas/",
        headers=auth_headers,
        json={"nombre": "Cuadrilla Alpha", "especialidad": "agua", "capacidad": 3, "contacto": "555-0101"},
    ).json()
    assert client.delete(f"/cuadrillas/{created['id_cuadrilla']}", headers=auth_headers).status_code == 200
    assert client.get(f"/cuadrillas/{created['id_cuadrilla']}", headers=auth_headers).status_code == 404


def test_eliminar_cuadrilla_inexistente_retorna_404(client, auth_headers):
    assert client.delete("/cuadrillas/9999", headers=auth_headers).status_code == 404


def test_crear_area_comercial_datos_validos_retorna_201(client, auth_headers):
    response = client.post(
        "/areas-comerciales/",
        headers=auth_headers,
        json={"nombre": "Facturacion Central", "tipo": "facturacion", "contacto": "555-0202"},
    )
    assert response.status_code == 201
    assert response.json()["tipo"] == "facturacion"


def test_crear_area_comercial_tipo_invalido_retorna_422(client, auth_headers):
    response = client.post(
        "/areas-comerciales/",
        headers=auth_headers,
        json={"nombre": "Area X", "tipo": "inventario", "contacto": "555-0202"},
    )
    assert response.status_code == 422


def test_eliminar_area_comercial_inexistente_retorna_404(client, auth_headers):
    assert client.delete("/areas-comerciales/9999", headers=auth_headers).status_code == 404
