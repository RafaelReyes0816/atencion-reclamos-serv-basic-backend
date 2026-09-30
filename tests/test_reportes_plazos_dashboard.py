from datetime import date, timedelta

HOY = date.today()


def test_generar_reporte_diario_retorna_201(client, auth_headers):
    response = client.post("/reportes/diario", headers=auth_headers)
    assert response.status_code == 201
    assert "id_reporte" in response.json()


def test_generar_reporte_mensual_retorna_201(client, auth_headers):
    response = client.post("/reportes/mensual", headers=auth_headers)
    assert response.status_code == 201
    assert "id_reporte" in response.json()


def test_generar_reporte_mensual_por_defecto_usa_mes_anterior(client, auth_headers):
    esperado = (HOY.replace(day=1) - timedelta(days=1)).strftime("%Y-%m")
    response = client.post("/reportes/mensual", headers=auth_headers)
    assert response.status_code == 201
    assert response.json()["periodo"] == esperado


def test_generar_reporte_mensual_acepta_periodo_explicito(client, auth_headers, reclamo_creado):
    periodo = HOY.strftime("%Y-%m")
    response = client.post(f"/reportes/mensual?periodo={periodo}", headers=auth_headers)
    assert response.status_code == 201
    body = response.json()
    assert body["periodo"] == periodo
    # El reclamo del fixture seCreo hoy, asi que el mes en curso no va en cero.
    detalle = client.get(f"/reportes/{body['id_reporte']}", headers=auth_headers).json()
    assert detalle["datos"]["total_ingresados"] >= 1
    assert detalle["datos"]["periodo"] == periodo


def test_generar_reporte_mensual_periodo_invalido_retorna_422(client, auth_headers):
    assert client.post("/reportes/mensual?periodo=2026-13", headers=auth_headers).status_code == 422
    assert client.post("/reportes/mensual?periodo=septiembre", headers=auth_headers).status_code == 422


def test_generar_reporte_mensual_ignora_reclamos_de_otros_meses(client, auth_headers, reclamo_creado):
    otro = (HOY.replace(day=1) - timedelta(days=1)).strftime("%Y-%m")
    response = client.post(f"/reportes/mensual?periodo={otro}", headers=auth_headers)
    detalle = client.get(f"/reportes/{response.json()['id_reporte']}", headers=auth_headers).json()
    # El unico reclamo es de hoy, asi que el mes anterior queda en cero.
    assert detalle["datos"]["total_ingresados"] == 0


def test_obtener_reporte_desglosado(client, auth_headers):
    id_reporte = client.post("/reportes/diario", headers=auth_headers).json()["id_reporte"]
    response = client.get(f"/reportes/{id_reporte}", headers=auth_headers)
    assert response.status_code == 200
    body = response.json()
    assert body["tipo_reporte"] == "operativo_diario"
    assert "fecha" in body["datos"]
    assert "ingresados" in body["datos"]


def test_obtener_reporte_inexistente_retorna_404(client, auth_headers):
    assert client.get("/reportes/9999", headers=auth_headers).status_code == 404


def test_descargar_reporte_excel_retorna_xlsx(client, auth_headers):
    id_reporte = client.post("/reportes/diario", headers=auth_headers).json()["id_reporte"]
    response = client.get(f"/reportes/{id_reporte}/excel", headers=auth_headers)
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    assert "attachment" in response.headers["content-disposition"]
    assert ".xlsx" in response.headers["content-disposition"]
    assert response.content[:2] == b"PK"


def test_descargar_reporte_excel_inexistente_retorna_404(client, auth_headers):
    assert client.get("/reportes/9999/excel", headers=auth_headers).status_code == 404


def test_verificar_vencimientos_sin_datos_retorna_vacio(client, auth_headers):
    response = client.post("/plazos/verificar-vencimientos", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["total"] == 0


def test_verificar_vencidos_detecta_reclamo_vencido(client, auth_headers, reclamo_creado):
    normativa = client.post(
        "/normativa/",
        headers=auth_headers,
        json={"servicio": "agua", "categoria": "fuga", "urgencia": "alta", "plazo_maximo_dias": 7, "vigencia_desde": "2026-01-01"},
    ).json()
    vencido = (HOY - timedelta(days=10)).isoformat()
    client.put(
        f"/reclamos/{reclamo_creado['id_reclamo']}/asignar-plazo",
        headers=auth_headers,
        json={"id_normativa": normativa["id_normativa"], "fecha_tope": vencido},
    )
    client.put(
        f"/reclamos/{reclamo_creado['id_reclamo']}/clasificar",
        headers=auth_headers,
        json={"servicio": "agua", "categoria": "fuga", "urgencia": "alta"},
    )

    response = client.post("/plazos/verificar-vencidos", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["total"] >= 1


def test_verificar_criticos_detecta_urgencia_critica(client, auth_headers, reclamo_creado):
    client.put(
        f"/reclamos/{reclamo_creado['id_reclamo']}/clasificar",
        headers=auth_headers,
        json={"servicio": "agua", "categoria": "fuga", "urgencia": "critica"},
    )
    response = client.post("/plazos/verificar-criticos", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["total"] >= 1
    assert response.json()["alarmas"][0]["urgencia"] == "critica"


def test_obtener_dashboard_sin_datos_retorna_ceros(client, auth_headers):
    response = client.get("/dashboard/", headers=auth_headers)
    assert response.status_code == 200
    body = response.json()
    assert body["total_reclamos"] == 0
    assert body["porcentaje_cumplimiento"] == 0.0


def test_obtener_dashboard_con_reclamos(client, auth_headers, reclamo_creado):
    client.put(
        f"/reclamos/{reclamo_creado['id_reclamo']}/clasificar",
        headers=auth_headers,
        json={"servicio": "agua", "categoria": "fuga", "urgencia": "critica"},
    )
    body = client.get("/dashboard/", headers=auth_headers).json()
    assert body["total_reclamos"] == 1
    assert body["total_usuarios"] == 1
    assert body["por_estado"]["clasificado"] == 1
    assert body["por_servicio"][0]["servicio"] == "agua"
    assert body["criticos"] == 1


def test_obtener_dashboard_requiere_auth(client):
    assert client.get("/dashboard/").status_code == 401
