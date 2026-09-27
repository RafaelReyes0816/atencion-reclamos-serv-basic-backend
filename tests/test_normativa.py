def test_crear_normativa_datos_validos_retorna_201(client, auth_headers):
    response = client.post(
        "/normativa/",
        headers=auth_headers,
        json={
            "servicio": "agua",
            "categoria": "fuga",
            "urgencia": "critica",
            "plazo_maximo_dias": 3,
            "vigencia_desde": "2026-01-01",
        },
    )
    assert response.status_code == 201
    assert response.json()["plazo_maximo_dias"] == 3


def test_crear_normativa_catalogo_invalido_retorna_422(client, auth_headers):
    response = client.post(
        "/normativa/",
        headers=auth_headers,
        json={
            "servicio": "gas",
            "categoria": "fuga",
            "urgencia": "critica",
            "plazo_maximo_dias": 3,
            "vigencia_desde": "2026-01-01",
        },
    )
    assert response.status_code == 422


def test_crear_normativa_plazo_negativo_retorna_422(client, auth_headers):
    response = client.post(
        "/normativa/",
        headers=auth_headers,
        json={
            "servicio": "agua",
            "categoria": "fuga",
            "urgencia": "critica",
            "plazo_maximo_dias": -5,
            "vigencia_desde": "2026-01-01",
        },
    )
    assert response.status_code == 422


def test_actualizar_normativa_existente_retorna_200(client, auth_headers):
    created = client.post(
        "/normativa/",
        headers=auth_headers,
        json={
            "servicio": "agua",
            "categoria": "fuga",
            "urgencia": "critica",
            "plazo_maximo_dias": 3,
            "vigencia_desde": "2026-01-01",
        },
    ).json()

    response = client.put(
        f"/normativa/{created['id_normativa']}",
        headers=auth_headers,
        json={"plazo_maximo_dias": 10},
    )
    assert response.status_code == 200
    assert response.json()["plazo_maximo_dias"] == 10


def test_actualizar_normativa_no_borra_campos_no_enviados(client, auth_headers):
    created = client.post(
        "/normativa/",
        headers=auth_headers,
        json={
            "servicio": "agua",
            "categoria": "fuga",
            "urgencia": "critica",
            "plazo_maximo_dias": 3,
            "vigencia_desde": "2026-01-01",
        },
    ).json()

    client.put(f"/normativa/{created['id_normativa']}", headers=auth_headers, json={"plazo_maximo_dias": 10})

    persisted = client.get(f"/normativa/{created['id_normativa']}", headers=auth_headers).json()
    assert persisted["servicio"] == "agua"
    assert persisted["categoria"] == "fuga"
    assert persisted["urgencia"] == "critica"
    assert persisted["vigencia_desde"] == "2026-01-01"
    assert persisted["plazo_maximo_dias"] == 10


def test_actualizar_normativa_inexistente_retorna_404(client, auth_headers):
    response = client.put("/normativa/9999", headers=auth_headers, json={"plazo_maximo_dias": 5})
    assert response.status_code == 404


def test_obtener_normativa_vigente(client, auth_headers):
    client.post(
        "/normativa/",
        headers=auth_headers,
        json={
            "servicio": "agua",
            "categoria": "fuga",
            "urgencia": "critica",
            "plazo_maximo_dias": 3,
            "vigencia_desde": "2026-01-01",
        },
    )
    response = client.get(
        "/normativa/vigente",
        headers=auth_headers,
        params={"servicio": "agua", "categoria": "fuga", "urgencia": "critica"},
    )
    assert response.status_code == 200
    assert response.json()["plazo_maximo_dias"] == 3


def test_obtener_normativa_vigente_sin_match_retorna_404(client, auth_headers):
    response = client.get(
        "/normativa/vigente",
        headers=auth_headers,
        params={"servicio": "luz", "categoria": "corte", "urgencia": "programada"},
    )
    assert response.status_code == 404


def test_obtener_normativa_vigente_catalogo_invalido_retorna_422(client, auth_headers):
    response = client.get(
        "/normativa/vigente",
        headers=auth_headers,
        params={"servicio": "gas", "categoria": "corte", "urgencia": "alta"},
    )
    assert response.status_code == 422


def test_filtrar_normativa_por_servicio(client, auth_headers):
    for servicio, categoria in [("agua", "fuga"), ("luz", "corte")]:
        client.post(
            "/normativa/",
            headers=auth_headers,
            json={
                "servicio": servicio,
                "categoria": categoria,
                "urgencia": "alta",
                "plazo_maximo_dias": 5,
                "vigencia_desde": "2026-01-01",
            },
        )
    response = client.get("/normativa/?servicio=luz", headers=auth_headers)
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["servicio"] == "luz"


def test_eliminar_normativa(client, auth_headers):
    created = client.post(
        "/normativa/",
        headers=auth_headers,
        json={
            "servicio": "agua",
            "categoria": "fuga",
            "urgencia": "critica",
            "plazo_maximo_dias": 3,
            "vigencia_desde": "2026-01-01",
        },
    ).json()
    assert client.delete(f"/normativa/{created['id_normativa']}", headers=auth_headers).status_code == 200
    assert client.get(f"/normativa/{created['id_normativa']}", headers=auth_headers).status_code == 404


def test_eliminar_normativa_inexistente_retorna_404(client, auth_headers):
    assert client.delete("/normativa/9999", headers=auth_headers).status_code == 404
