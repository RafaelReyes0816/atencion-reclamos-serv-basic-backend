"""Verifica la matriz de permisos por rol.

    Endpoint                                  ciudadano  tecnico  supervisor  admin
    GET    /usuarios/                              -         -         G          A
    POST   /usuarios/                              -         -         -          A
    GET    /usuarios/{otro}                     propio       G         G          A
    DELETE /usuarios/{id}                          -         -         -          A
    GET    /normativa/                             -         L         L          A
    POST   /normativa/                             -         -         G          A
    GET    /cuadrillas/                            -         L         L          A
    POST   /cuadrillas/                            -         -         G          A
    GET    /areas-comerciales/                     -         L         L          A
    POST   /areas-comerciales/                     -         -         G          A
    GET    /seguimiento/ordenes                    -         L         L          A
    POST   /seguimiento/avances                    -         L         L          A
    GET    /reportes/                              -         -         G          A
    POST   /reportes/diario                        -         -         G          A
    GET    /dashboard/                             -         -         G          A
    POST   /plazos/verificar-vencidos              -         -         G          A
    PUT    /reclamos/{id}/clasificar               -         L         L          A
    PUT    /reclamos/{id}/asignar-plazo            -         -         G          A
    PUT    /reclamos/{id}/cerrar                   -         -         G          A
    DELETE /reclamos/{id}                          -         -         -          A

`esperado` es el codigo cuando el rol SI tiene permiso (404 = la ruta esta
protegida correctamente pero el recurso no existe).
"""
import pytest

TODOS = ("ciudadano", "tecnico", "supervisor", "admin")

MATRIZ = [
    ("listar_usuarios", "GET", "/usuarios/", None, 200, ("supervisor", "admin")),
    ("crear_usuario", "POST", "/usuarios/", {
        "nombre": "Nuevo Tec", "documento": "90000001", "telefono": "5551111",
        "contraseña": "clave123", "email": "nuevo@correo.com", "direccion": "Calle 1",
    }, 201, ("admin",)),
    ("eliminar_usuario", "DELETE", "/usuarios/9999", None, 404, ("admin",)),

    ("listar_normativa", "GET", "/normativa/", None, 200, ("tecnico", "supervisor", "admin")),
    ("crear_normativa", "POST", "/normativa/", {
        "servicio": "agua", "categoria": "corte", "urgencia": "alta",
        "plazo_maximo_dias": 5, "vigencia_desde": "2026-01-01",
    }, 201, ("supervisor", "admin")),

    ("listar_cuadrillas", "GET", "/cuadrillas/", None, 200, ("tecnico", "supervisor", "admin")),
    ("crear_cuadrilla", "POST", "/cuadrillas/", {
        "nombre": "Cuadrilla Test", "especialidad": "agua",
        "contacto": "5552222", "capacidad": 2,
    }, 201, ("supervisor", "admin")),

    ("listar_areas", "GET", "/areas-comerciales/", None, 200, ("tecnico", "supervisor", "admin")),
    ("crear_area", "POST", "/areas-comerciales/", {
        "nombre": "Area Test", "tipo": "facturacion", "contacto": "5553333",
    }, 201, ("supervisor", "admin")),

    ("listar_ordenes", "GET", "/seguimiento/ordenes", None, 200, ("tecnico", "supervisor", "admin")),
    ("crear_avance", "POST", "/seguimiento/avances", {
        "id_orden": 9999, "fecha_avance": "2026-01-01",
        "descripcion": "Avance", "estado_parcial": "iniciado",
    }, 404, ("tecnico", "supervisor", "admin")),

    ("listar_reportes", "GET", "/reportes/", None, 200, ("supervisor", "admin")),
    ("generar_reporte_diario", "POST", "/reportes/diario", None, 201, ("supervisor", "admin")),
    ("dashboard", "GET", "/dashboard/", None, 200, ("supervisor", "admin")),
    ("verificar_vencidos", "POST", "/plazos/verificar-vencidos", None, 200, ("supervisor", "admin")),

    ("clasificar_reclamo", "PUT", "/reclamos/9999/clasificar", {
        "servicio": "agua", "categoria": "fuga", "urgencia": "alta",
    }, 404, ("tecnico", "supervisor", "admin")),
    ("asignar_plazo", "PUT", "/reclamos/9999/asignar-plazo", {
        "id_normativa": 1, "fecha_tope": "2026-12-31",
    }, 404, ("supervisor", "admin")),
    ("cerrar_reclamo", "PUT", "/reclamos/9999/cerrar", {"resultado": "resuelto"}, 404, ("supervisor", "admin")),
    ("eliminar_reclamo", "DELETE", "/reclamos/9999", None, 404, ("admin",)),
]

IDS = [m[0] for m in MATRIZ]


def _peticion(client, headers, metodo, ruta, body):
    kwargs = {"headers": headers}
    if body is not None:
        kwargs["json"] = body
    return client.request(metodo, ruta, **kwargs)


@pytest.mark.parametrize("rol", TODOS)
@pytest.mark.parametrize("nombre,metodo,ruta,body,esperado,permitidos", MATRIZ, ids=IDS)
def test_matriz_de_permisos(client, tokens_por_rol, rol, nombre, metodo, ruta, body, esperado, permitidos):
    response = _peticion(client, tokens_por_rol[rol], metodo, ruta, body)
    if rol in permitidos:
        assert response.status_code == esperado, (
            f"{rol} en {nombre}: {response.status_code} {response.text[:200]}"
        )
    else:
        assert response.status_code == 403, (
            f"{rol} en {nombre}: {response.status_code} {response.text[:200]}"
        )


# --- alcance sobre los propios datos -----------------------------------------

def test_ciudadano_crea_reclamo_propio(client, headers_ciudadano, usuario_ciudadano):
    response = client.post("/reclamos/", headers=headers_ciudadano, json={
        "id_usuario": usuario_ciudadano.id_usuario, "canal": "web", "servicio": "agua",
        "categoria": "fuga", "urgencia": "alta", "descripcion": "Fuga en mi casa",
    })
    assert response.status_code == 201


def test_ciudadano_no_crea_reclamo_para_otro(client, headers_ciudadano, usuario_admin):
    response = client.post("/reclamos/", headers=headers_ciudadano, json={
        "id_usuario": usuario_admin.id_usuario, "canal": "web", "servicio": "agua",
        "categoria": "fuga", "urgencia": "alta", "descripcion": "Fuga ajena",
    })
    assert response.status_code == 403


def test_supervisor_registra_reclamo_por_ventanilla(client, headers_supervisor, usuario_ciudadano):
    response = client.post("/reclamos/", headers=headers_supervisor, json={
        "id_usuario": usuario_ciudadano.id_usuario, "canal": "web", "servicio": "agua",
        "categoria": "fuga", "urgencia": "alta", "descripcion": "Reclamo por ventanilla",
    })
    assert response.status_code == 201


def test_ciudadano_no_ve_reclamo_ajeno(client, headers_ciudadano, headers_admin, usuario_admin):
    ajeno = client.post("/reclamos/", headers=headers_admin, json={
        "id_usuario": usuario_admin.id_usuario, "canal": "web", "servicio": "luz",
        "categoria": "corte", "urgencia": "alta", "descripcion": "Corte en la calle",
    })
    assert ajeno.status_code == 201
    assert client.get(f"/reclamos/{ajeno.json()['id_reclamo']}", headers=headers_ciudadano).status_code == 403


def test_lista_reclamos_de_ciudadano_filtrada(client, headers_ciudadano, headers_admin, usuario_ciudadano, usuario_admin):
    client.post("/reclamos/", headers=headers_ciudadano, json={
        "id_usuario": usuario_ciudadano.id_usuario, "canal": "web", "servicio": "agua",
        "categoria": "fuga", "urgencia": "alta", "descripcion": "Fuga propia del ciudadano",
    })
    client.post("/reclamos/", headers=headers_admin, json={
        "id_usuario": usuario_admin.id_usuario, "canal": "web", "servicio": "luz",
        "categoria": "corte", "urgencia": "alta", "descripcion": "Corte ajeno del admin",
    })
    response = client.get("/reclamos/", headers=headers_ciudadano)
    assert response.status_code == 200
    cuerpo = response.json()
    assert len(cuerpo) == 1
    assert cuerpo[0]["id_usuario"] == usuario_ciudadano.id_usuario


def test_lista_reclamos_interno_ve_todos(client, headers_tecnico, headers_ciudadano, headers_admin, usuario_ciudadano, usuario_admin):
    client.post("/reclamos/", headers=headers_ciudadano, json={
        "id_usuario": usuario_ciudadano.id_usuario, "canal": "web", "servicio": "agua",
        "categoria": "fuga", "urgencia": "alta", "descripcion": "Fuga del ciudadano",
    })
    client.post("/reclamos/", headers=headers_admin, json={
        "id_usuario": usuario_admin.id_usuario, "canal": "web", "servicio": "luz",
        "categoria": "corte", "urgencia": "alta", "descripcion": "Corte del admin",
    })
    respuesta = client.get("/reclamos/", headers=headers_tecnico)
    assert respuesta.status_code == 200
    assert len(respuesta.json()) == 2


def test_ciudadano_no_ve_usuario_ajeno(client, headers_ciudadano, usuario_admin):
    assert client.get(f"/usuarios/{usuario_admin.id_usuario}", headers=headers_ciudadano).status_code == 403


def test_ciudadano_ve_su_propio_usuario(client, headers_ciudadano, usuario_ciudadano):
    assert client.get(f"/usuarios/{usuario_ciudadano.id_usuario}", headers=headers_ciudadano).status_code == 200


def test_ciudadano_no_puede_autopromoverse(client, headers_ciudadano, usuario_ciudadano):
    response = client.put(
        f"/usuarios/{usuario_ciudadano.id_usuario}",
        headers=headers_ciudadano,
        json={"rol": "admin"},
    )
    assert response.status_code == 200
    assert response.json()["rol"] == "ciudadano"


def test_tecnico_no_puede_cerrar_reclamos(client, headers_tecnico, headers_admin, usuario_admin):
    reclamo = client.post("/reclamos/", headers=headers_admin, json={
        "id_usuario": usuario_admin.id_usuario, "canal": "web", "servicio": "agua",
        "categoria": "fuga", "urgencia": "alta", "descripcion": "Reclamo para cerrar",
    }).json()
    id_reclamo = reclamo["id_reclamo"]
    resolver = client.put(
        f"/reclamos/{id_reclamo}/resolver", headers=headers_tecnico, json={"resultado": "resuelto"}
    )
    assert resolver.status_code == 200
    cerrar = client.put(
        f"/reclamos/{id_reclamo}/cerrar", headers=headers_tecnico, json={"resultado": "resuelto"}
    )
    assert cerrar.status_code == 403
