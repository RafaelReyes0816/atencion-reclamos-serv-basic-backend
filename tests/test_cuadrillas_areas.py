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
