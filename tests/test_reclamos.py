def test_crear_reclamo_datos_validos_retorna_201(client, auth_headers, usuario_id):
    response = client.post(
        "/reclamos/",
        headers=auth_headers,
        json={
            "id_usuario": usuario_id,
            "canal": "web",
            "servicio": "agua",
            "categoria": "fuga",
            "urgencia": "alta",
            "descripcion": "Fuga en tuberia principal",
        },
    )
    assert response.status_code == 201
    body = response.json()
    assert body["estado"] == "registrado"
    assert body["servicio"] == "agua"


def test_crear_reclamo_canal_invalido_retorna_422(client, auth_headers, usuario_id):
    response = client.post(
        "/reclamos/",
        headers=auth_headers,
        json={
            "id_usuario": usuario_id,
            "canal": "INVALIDO",
            "servicio": "agua",
            "categoria": "fuga",
            "urgencia": "alta",
            "descripcion": "Fuga en tuberia",
        },
    )
    assert response.status_code == 422


def test_crear_reclamo_servicio_invalido_retorna_422(client, auth_headers, usuario_id):
    response = client.post(
        "/reclamos/",
        headers=auth_headers,
        json={
            "id_usuario": usuario_id,
            "canal": "web",
            "servicio": "teletransporte",
            "categoria": "fuga",
            "urgencia": "alta",
            "descripcion": "Fuga en tuberia",
        },
    )
    assert response.status_code == 422


def test_crear_reclamo_urgencia_invalida_retorna_422(client, auth_headers, usuario_id):
    response = client.post(
        "/reclamos/",
        headers=auth_headers,
        json={
            "id_usuario": usuario_id,
            "canal": "web",
            "servicio": "agua",
            "categoria": "fuga",
            "urgencia": "nuclear",
            "descripcion": "Fuga en tuberia",
        },
    )
    assert response.status_code == 422


def test_crear_reclamo_usuario_inexistente_retorna_404(client, auth_headers):
    response = client.post(
        "/reclamos/",
        headers=auth_headers,
        json={
            "id_usuario": 9999,
            "canal": "web",
            "servicio": "agua",
            "categoria": "fuga",
            "urgencia": "alta",
            "descripcion": "Fuga en tuberia",
        },
    )
    assert response.status_code == 404


def test_crear_reclamo_descripcion_corta_retorna_422(client, auth_headers, usuario_id):
    response = client.post(
        "/reclamos/",
        headers=auth_headers,
        json={
            "id_usuario": usuario_id,
            "canal": "web",
            "servicio": "agua",
            "categoria": "fuga",
            "urgencia": "alta",
            "descripcion": "x",
        },
    )
    assert response.status_code == 422


def test_clasificar_reclamo_persista_campos(client, auth_headers, reclamo_creado):
    response = client.put(
        f"/reclamos/{reclamo_creado['id_reclamo']}/clasificar",
        headers=auth_headers,
        json={"servicio": "luz", "categoria": "corte", "urgencia": "critica"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["servicio"] == "luz"
    assert body["categoria"] == "corte"
    assert body["urgencia"] == "critica"
    assert body["estado"] == "clasificado"

    persisted = client.get(f"/reclamos/{reclamo_creado['id_reclamo']}", headers=auth_headers).json()
    assert persisted["urgencia"] == "critica"
    assert persisted["servicio"] == "luz"


def test_actualizar_reclamo_persista_descripcion(client, auth_headers, reclamo_creado):
    id_reclamo = reclamo_creado["id_reclamo"]
    response = client.put(f"/reclamos/{id_reclamo}", headers=auth_headers, json={"descripcion": "Descripcion actualizada"})
    assert response.status_code == 200
    persisted = client.get(f"/reclamos/{id_reclamo}", headers=auth_headers).json()
    assert persisted["descripcion"] == "Descripcion actualizada"


def test_asignar_plazo_persiste(client, auth_headers, reclamo_creado):
    id_reclamo = reclamo_creado["id_reclamo"]
    normativa = client.post(
        "/normativa/",
        headers=auth_headers,
        json={
            "servicio": "agua",
            "categoria": "fuga",
            "urgencia": "alta",
            "plazo_maximo_dias": 7,
            "vigencia_desde": "2026-01-01",
        },
    ).json()

    response = client.put(
        f"/reclamos/{id_reclamo}/asignar-plazo",
        headers=auth_headers,
        json={"id_normativa": normativa["id_normativa"], "fecha_tope": "2026-10-15"},
    )
    assert response.status_code == 200
    persisted = client.get(f"/reclamos/{id_reclamo}", headers=auth_headers).json()
    assert persisted["fecha_tope"] == "2026-10-15"
    assert persisted["id_normativa"] == normativa["id_normativa"]


def test_asignar_plazo_normativa_inexistente_retorna_404(client, auth_headers, reclamo_creado):
    response = client.put(
        f"/reclamos/{reclamo_creado['id_reclamo']}/asignar-plazo",
        headers=auth_headers,
        json={"id_normativa": 9999, "fecha_tope": "2026-10-15"},
    )
    assert response.status_code == 404


def test_cerrar_reclamo_no_resuelto_retorna_409(client, auth_headers, reclamo_creado):
    response = client.put(
        f"/reclamos/{reclamo_creado['id_reclamo']}/cerrar",
        headers=auth_headers,
        json={"resultado": "resuelto"},
    )
    assert response.status_code == 409


def test_flujo_completo_registro_hasta_cierre(client, auth_headers, reclamo_creado):
    id_reclamo = reclamo_creado["id_reclamo"]

    client.put(
        f"/reclamos/{id_reclamo}/clasificar",
        headers=auth_headers,
        json={"servicio": "agua", "categoria": "fuga", "urgencia": "alta"},
    )
    normativa = client.post(
        "/normativa/",
        headers=auth_headers,
        json={
            "servicio": "agua",
            "categoria": "fuga",
            "urgencia": "alta",
            "plazo_maximo_dias": 7,
            "vigencia_desde": "2026-01-01",
        },
    ).json()
    client.put(
        f"/reclamos/{id_reclamo}/asignar-plazo",
        headers=auth_headers,
        json={"id_normativa": normativa["id_normativa"], "fecha_tope": "2026-10-15"},
    )
    orden = client.post(
        "/seguimiento/ordenes",
        headers=auth_headers,
        json={"id_reclamo": id_reclamo, "cuadrilla": "Cuadrilla Alpha", "fecha_asignacion": "2026-09-26"},
    ).json()
    client.post(
        "/seguimiento/avances",
        headers=auth_headers,
        json={
            "id_orden": orden["id_orden"],
            "fecha_avance": "2026-09-26",
            "descripcion": "Se localizo la fuga",
            "estado_parcial": "iniciado",
        },
    )
    client.put(f"/seguimiento/ordenes/{orden['id_orden']}", headers=auth_headers, json={"estado_orden": "resuelta"})
    client.put(
        f"/reclamos/{id_reclamo}/resolver",
        headers=auth_headers,
        json={"resultado": "resuelto", "detalle": "Reparado"},
    )
    cierre = client.put(
        f"/reclamos/{id_reclamo}/cerrar",
        headers=auth_headers,
        json={"resultado": "resuelto"},
    )
    assert cierre.status_code == 200
    body = cierre.json()
    assert body["estado"] == "cerrado"
    assert body["fecha_cierre"] is not None


def test_consultar_estado_por_documento_numerico(client, reclamo_creado, usuario_admin):
    response = client.get(f"/reclamos/estado/{usuario_admin.documento}")
    assert response.status_code == 200
    assert response.json()["id_reclamo"] == reclamo_creado["id_reclamo"]


def test_consultar_estado_por_id(client, reclamo_creado):
    response = client.get(f"/reclamos/estado/{reclamo_creado['id_reclamo']}")
    assert response.status_code == 200
    assert response.json()["estado"] == "registrado"


def test_consultar_estado_documento_desconocido_retorna_404(client, auth_headers):
    client.post(
        "/auth/register",
        json={
            "nombre": "Sin Reclamos",
            "documento": "55555555",
            "telefono": "5550400",
            "contraseña": "clave123",
            "email": "sin@correo.com",
            "direccion": "Calle 9",
        },
    )
    assert client.get("/reclamos/estado/55555555").status_code == 404


def test_obtener_comprobante(client, auth_headers, reclamo_creado):
    response = client.get(f"/reclamos/{reclamo_creado['id_reclamo']}/comprobante", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["descripcion"] == "Fuga en tuberia principal"


def test_actualizar_contacto(client, auth_headers, reclamo_creado, usuario_id):
    response = client.put(
        f"/reclamos/{reclamo_creado['id_reclamo']}/contacto",
        headers=auth_headers,
        json={"telefono": "5557777", "email": "nuevo@correo.com"},
    )
    assert response.status_code == 200
    usuario = client.get(f"/usuarios/{usuario_id}", headers=auth_headers).json()
    assert usuario["telefono"] == "5557777"
    assert usuario["email"] == "nuevo@correo.com"


def test_actualizar_contacto_email_invalido_retorna_422(client, auth_headers, reclamo_creado):
    response = client.put(
        f"/reclamos/{reclamo_creado['id_reclamo']}/contacto",
        headers=auth_headers,
        json={"telefono": "5557777", "email": "no-es-email"},
    )
    assert response.status_code == 422


def test_filtrar_reclamos_por_servicio(client, auth_headers, usuario_id):
    client.post(
        "/reclamos/",
        headers=auth_headers,
        json={
            "id_usuario": usuario_id,
            "canal": "web",
            "servicio": "agua",
            "categoria": "fuga",
            "urgencia": "alta",
            "descripcion": "Reclamo de agua",
        },
    )
    client.post(
        "/reclamos/",
        headers=auth_headers,
        json={
            "id_usuario": usuario_id,
            "canal": "web",
            "servicio": "luz",
            "categoria": "corte",
            "urgencia": "alta",
            "descripcion": "Reclamo de luz",
        },
    )
    response = client.get("/reclamos/?servicio=luz", headers=auth_headers)
    assert response.status_code == 200
    body = response.json()
    assert len(body) == 1
    assert body[0]["servicio"] == "luz"


def test_filtrar_reclamos_por_estado(client, auth_headers, reclamo_creado):
    client.put(
        f"/reclamos/{reclamo_creado['id_reclamo']}/clasificar",
        headers=auth_headers,
        json={"servicio": "agua", "categoria": "fuga", "urgencia": "alta"},
    )
    response = client.get("/reclamos/?estado=clasificado", headers=auth_headers)
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert client.get("/reclamos/?estado=cerrado", headers=auth_headers).json() == []


def test_filtrar_reclamos_catalogo_invalido_retorna_422(client, auth_headers):
    assert client.get("/reclamos/?servicio=teletransporte", headers=auth_headers).status_code == 422


def test_eliminar_reclamo(client, auth_headers, reclamo_creado):
    id_reclamo = reclamo_creado["id_reclamo"]
    assert client.delete(f"/reclamos/{id_reclamo}", headers=auth_headers).status_code == 200
    assert client.get(f"/reclamos/{id_reclamo}", headers=auth_headers).status_code == 404


def test_eliminar_reclamo_inexistente_retorna_404(client, auth_headers):
    assert client.delete("/reclamos/9999", headers=auth_headers).status_code == 404
