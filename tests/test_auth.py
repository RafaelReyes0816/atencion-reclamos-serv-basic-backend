def test_register_usuario_creado_retorna_201(client):
    response = client.post(
        "/auth/register",
        json={
            "nombre": "Ana Gomez",
            "documento": "87654321",
            "telefono": "5550200",
            "contraseña": "clave123",
            "email": "ana@correo.com",
            "direccion": "Av. Siempre Viva 742",
        },
    )
    assert response.status_code == 201
    assert response.json()["documento"] == "87654321"


def test_register_usuario_no_expone_hash(client):
    response = client.post(
        "/auth/register",
        json={
            "nombre": "Ana Gomez",
            "documento": "87654321",
            "telefono": "5550200",
            "contraseña": "clave123",
            "email": "ana@correo.com",
            "direccion": "Av. Siempre Viva 742",
        },
    )
    assert "contraseña" not in response.json()
    assert "contraseña_hash" not in response.json()
    assert "password" not in response.json()


def test_register_documento_duplicado_retorna_400(client, usuario_admin):
    response = client.post(
        "/auth/register",
        json={
            "nombre": "Otro Usuario",
            "documento": usuario_admin.documento,
            "telefono": "5550300",
            "contraseña": "clave123",
            "email": "otro@correo.com",
            "direccion": "Calle 5",
        },
    )
    assert response.status_code == 400
    assert "documento" in response.json()["detail"].lower()


def test_register_siempre_asigna_rol_ciudadano(client):
    response = client.post(
        "/auth/register",
        json={
            "nombre": "Con Rol Forzado",
            "documento": "87654399",
            "telefono": "5550200",
            "contraseña": "clave123",
            "email": "forzado@correo.com",
            "direccion": "Calle 9",
            "rol": "admin",
        },
    )
    assert response.status_code == 201
    assert response.json()["rol"] == "ciudadano"


def test_register_campos_invalidos_retorna_422(client):
    response = client.post(
        "/auth/register",
        json={
            "nombre": "A",
            "documento": "1",
            "telefono": "1",
            "contraseña": "123",
            "email": "no-es-email",
            "direccion": "x",
        },
    )
    assert response.status_code == 422


def test_login_credenciales_validas_retorna_token(client, auth_headers):
    assert "Authorization" in auth_headers
    assert auth_headers["Authorization"].startswith("Bearer ")


def test_login_password_incorrecto_retorna_401(client, usuario_admin):
    response = client.post("/auth/login", data={"username": usuario_admin.documento, "password": "mala"})
    assert response.status_code == 401


def test_login_usuario_inexistente_retorna_401(client):
    response = client.post("/auth/login", data={"username": "99999999", "password": "clave123"})
    assert response.status_code == 401


def test_login_requiere_form_urlencoded(client, usuario_admin):
    response = client.post("/auth/login", json={"username": usuario_admin.documento, "password": "clave123"})
    assert response.status_code == 422


def test_login_devuelve_rol_y_id(client, usuario_admin):
    response = client.post(
        "/auth/login",
        data={"username": usuario_admin.documento, "password": "clave123"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["rol"] == "admin"
    assert body["id_usuario"] == usuario_admin.id_usuario


def test_token_sin_claim_sub_retorna_401(client):
    from app.Infraestructura.security import create_access_token

    token_sin_sub = create_access_token(data={"otro": "valor"})
    response = client.get(
        "/usuarios/", headers={"Authorization": f"Bearer {token_sin_sub}"}
    )
    assert response.status_code == 401


def test_endpoint_protegido_sin_token_retorna_401(client):
    assert client.get("/usuarios/").status_code == 401


def test_endpoint_protegido_token_invalido_retorna_401(client):
    response = client.get("/usuarios/", headers={"Authorization": "Bearer token_falso"})
    assert response.status_code == 401
