def test_listar_usuarios_retorna_lista(client, auth_headers):
    response = client.get("/usuarios/", headers=auth_headers)
    assert response.status_code == 200
    assert len(response.json()) == 1


def test_obtener_usuario_por_documento(client, auth_headers, usuario_admin):
    response = client.get(f"/usuarios/documento/{usuario_admin.documento}", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["documento"] == usuario_admin.documento
    assert response.json()["rol"] == "admin"


def test_obtener_usuario_documento_inexistente_retorna_404(client, auth_headers):
    assert client.get("/usuarios/documento/00000000", headers=auth_headers).status_code == 404


def test_crear_usuario_documento_duplicado_retorna_400(client, auth_headers, usuario_admin):
    response = client.post(
        "/usuarios/",
        headers=auth_headers,
        json={
            "nombre": "Duplicado",
            "documento": usuario_admin.documento,
            "telefono": "5559999",
            "contraseña": "clave123",
            "email": "dup@correo.com",
            "direccion": "Calle 2",
        },
    )
    assert response.status_code == 400


def test_crear_usuario_admin_puede_asignar_rol(client, auth_headers):
    response = client.post(
        "/usuarios/",
        headers=auth_headers,
        json={
            "nombre": "Tec Asignado",
            "documento": "55500001",
            "telefono": "5559999",
            "contraseña": "clave123",
            "email": "tec@correo.com",
            "direccion": "Calle 2",
            "rol": "tecnico",
        },
    )
    assert response.status_code == 201
    assert response.json()["rol"] == "tecnico"


def test_actualizar_usuario_persista_campos(client, auth_headers, usuario_id, usuario_admin):
    response = client.put(
        f"/usuarios/{usuario_id}",
        headers=auth_headers,
        json={"nombre": "Nombre Actualizado", "telefono": "5551234", "direccion": "Nueva Direccion 123"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["nombre"] == "Nombre Actualizado"
    assert body["telefono"] == "5551234"
    assert body["direccion"] == "Nueva Direccion 123"
    assert body["documento"] == usuario_admin.documento


def test_actualizar_usuario_no_borra_campos_no_enviados(client, auth_headers, usuario_admin, usuario_id):
    client.put(f"/usuarios/{usuario_id}", headers=auth_headers, json={"telefono": "5551234"})
    body = client.get(f"/usuarios/{usuario_id}", headers=auth_headers).json()
    assert body["nombre"] == usuario_admin.nombre
    assert body["email"] == usuario_admin.email
    assert body["telefono"] == "5551234"


def test_admin_puede_cambiar_rol_de_usuario(client, auth_headers, usuario_ciudadano, usuario_admin):
    response = client.put(
        f"/usuarios/{usuario_ciudadano.id_usuario}",
        headers=auth_headers,
        json={"rol": "supervisor"},
    )
    assert response.status_code == 200
    assert response.json()["rol"] == "supervisor"


def test_cambiar_contrasena_actualiza_el_hash(client, headers_admin, usuario_admin):
    response = client.put(
        f"/usuarios/{usuario_admin.id_usuario}/contrasena",
        headers=headers_admin,
        json={"contrasena_actual": "clave123", "contrasena_nueva": "nueva123"},
    )
    assert response.status_code == 200

    login_viejo = client.post(
        "/auth/login",
        data={"username": usuario_admin.documento, "password": "clave123"},
    )
    assert login_viejo.status_code == 401

    login_nuevo = client.post(
        "/auth/login",
        data={"username": usuario_admin.documento, "password": "nueva123"},
    )
    assert login_nuevo.status_code == 200


def test_cambiar_contrasena_actual_incorrecta_retorna_422(client, headers_admin, usuario_admin):
    response = client.put(
        f"/usuarios/{usuario_admin.id_usuario}/contrasena",
        headers=headers_admin,
        json={"contrasena_actual": "equivocada", "contrasena_nueva": "nueva123"},
    )
    assert response.status_code == 422


def test_cambiar_contrasena_de_otro_usuario_retorna_403(client, headers_admin, usuario_ciudadano):
    response = client.put(
        f"/usuarios/{usuario_ciudadano.id_usuario}/contrasena",
        headers=headers_admin,
        json={"contrasena_actual": "clave123", "contrasena_nueva": "nueva123"},
    )
    assert response.status_code == 403


def test_actualizar_usuario_inexistente_retorna_404(client, auth_headers):
    response = client.put("/usuarios/9999", headers=auth_headers, json={"nombre": "No existe"})
    assert response.status_code == 404


def test_eliminar_usuario_sin_reclamos(client, auth_headers):
    creado = client.post(
        "/usuarios/",
        headers=auth_headers,
        json={
            "nombre": "Usuario Temporal",
            "documento": "77777777",
            "telefono": "5550600",
            "contraseña": "clave123",
            "email": "temp@correo.com",
            "direccion": "Calle 7",
        },
    ).json()
    assert client.delete(f"/usuarios/{creado['id_usuario']}", headers=auth_headers).status_code == 200
    assert client.get(f"/usuarios/{creado['id_usuario']}", headers=auth_headers).status_code == 404


def test_eliminar_usuario_con_reclamos_retorna_409(client, auth_headers, usuario_id, reclamo_creado):
    response = client.delete(f"/usuarios/{usuario_id}", headers=auth_headers)
    assert response.status_code == 409
    assert "reclamos" in response.json()["detail"].lower()


def test_eliminar_usuario_inexistente_retorna_404(client, auth_headers):
    assert client.delete("/usuarios/9999", headers=auth_headers).status_code == 404


def test_health_retorna_ok(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
