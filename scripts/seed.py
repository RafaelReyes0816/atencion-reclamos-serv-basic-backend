"""Carga datos de prueba: usuarios con cada rol, normativa, cuadrillas, areas y reclamos.

Uso:
    python -m scripts.seed          # crea lo que falte
    python -m scripts.seed --reset  # borra SOLO los datos de este script y los recarga

Es idempotente: no duplica si ya existe. `--reset` nunca toca registros que no
hayan sido creados por este script, asi que es seguro en una base con datos reales.
"""
import argparse
import sys
from datetime import date, timedelta

from sqlalchemy import and_, or_

from app.Infraestructura.database import engine, Base, SessionLocal
import app.Infraestructura.database.models  # noqa: F401  registra los ORM
from app.Infraestructura.repositories.usuario_repository import UsuarioRepository
from app.Infraestructura.repositories.reclamo_repository import ReclamoRepository
from app.Infraestructura.repositories.normativa_plazo_repository import NormativaPlazoRepository
from app.Infraestructura.repositories.cuadrilla_repository import CuadrillaRepository
from app.Infraestructura.repositories.area_comercial_repository import AreaComercialRepository
from app.Infraestructura.security import get_password_hash
from app.Infraestructura.database.models.usuario import UsuarioORM
from app.Infraestructura.database.models.reclamo import ReclamoORM
from app.Infraestructura.database.models.normativa_plazo import NormativaPlazoORM
from app.Infraestructura.database.models.cuadrilla import CuadrillaORM
from app.Infraestructura.database.models.area_comercial import AreaComercialORM
from app.Infraestructura.database.models.orden_trabajo import OrdenTrabajoORM
from app.Infraestructura.database.models.avance import AvanceORM
from app.Infraestructura.database.models.derivacion_comercial import DerivacionComercialORM
from app.Domain.Entities.catalogos import Rol

CONTRASENA_DEMO = "clave123"

USUARIOS = [
    ("Admin Demo", "10000001", Rol.admin),
    ("Supervisor Demo", "10000002", Rol.supervisor),
    ("Tecnico Demo", "10000003", Rol.tecnico),
    ("Ciudadano Demo", "10000004", Rol.ciudadano),
]

NORMATIVA = [
    ("agua", "fuga", "alta", 3),
    ("agua", "corte", "alta", 2),
    ("agua", "facturacion", "normal", 15),
    ("luz", "corte", "alta", 2),
    ("luz", "falla_tecnica", "critica", 1),
    ("luz", "facturacion", "normal", 15),
]

CUADRILLAS = [
    ("Cuadrilla Agua Norte", "agua", "3105550101", 3),
    ("Cuadrilla Agua Sur", "agua", "3105550102", 2),
    ("Cuadrilla Luz Centro", "luz", "3105550103", 4),
]

AREAS = [
    ("Facturación", "facturacion", "3105550201"),
    ("Cobranza", "cobranza", "3105550202"),
]

RECLAMOS = [
    ("10000004", "web", "agua", "fuga", "alta", "Fuga de agua en la tuberia de la cocina", -2, "cerrado"),
    ("10000004", "telefonico", "luz", "corte", "alta", "Sin energia electrica en todo el barrio", 0, "en_atencion_tecnica"),
    ("10000004", "presencial", "agua", "facturacion", "normal", "Factura con cobro doble", 5, "clasificado"),
    ("10000004", "web", "luz", "falla_tecnica", "critica", "Poste de luz caido en la carrera 5", -1, "escalado"),
    ("10000004", "web", "agua", "corte", "alta", "Corte de agua en el sector norte", 1, "registrado"),
]


DOCUMENTOS_DEMO = {documento for _, documento, _ in USUARIOS}
NOMBRES_CUADRILLA_DEMO = {nombre for nombre, _, _, _ in CUADRILLAS}
NOMBRES_AREA_DEMO = {nombre for nombre, _, _ in AREAS}
CLAVES_NORMATIVA_DEMO = {(s, c, u) for s, c, u, _ in NORMATIVA}


def _wipe(db):
    """Borra unicamente los registros que creo este script.

    Se identifican por los valores de las listas de arriba (documentos 1000000X,
    nombres de cuadrilla/area y combinaciones de normativa). Los reclamos se toman
    por propietario: todo lo registrado por una cuenta demo es dato demo, aunque
    se haya creado a mano durante una prueba.
    """
    print("Borrando datos de prueba (solo los de este script)...")

    usuarios_demo_ids = [
        u.id_usuario
        for u in db.query(UsuarioORM).filter(UsuarioORM.documento.in_(DOCUMENTOS_DEMO)).all()
    ]

    reclamos_ids = [
        r.id_reclamo
        for r in db.query(ReclamoORM).filter(ReclamoORM.id_usuario.in_(usuarios_demo_ids)).all()
    ]
    if reclamos_ids:
        ordenes_ids = [
            o.id_orden
            for o in db.query(OrdenTrabajoORM)
            .filter(OrdenTrabajoORM.id_reclamo.in_(reclamos_ids)).all()
        ]
        if ordenes_ids:
            n = db.query(AvanceORM).filter(AvanceORM.id_orden.in_(ordenes_ids)).delete(
                synchronize_session=False
            )
            print(f"  {n} avance(s)")
        n = db.query(OrdenTrabajoORM).filter(OrdenTrabajoORM.id_reclamo.in_(reclamos_ids)).delete(
            synchronize_session=False
        )
        print(f"  {n} orden(es) de trabajo")
        n = db.query(DerivacionComercialORM).filter(
            DerivacionComercialORM.id_reclamo.in_(reclamos_ids)
        ).delete(synchronize_session=False)
        print(f"  {n} derivacion(es)")
        n = db.query(ReclamoORM).filter(ReclamoORM.id_reclamo.in_(reclamos_ids)).delete(
            synchronize_session=False
        )
        print(f"  {n} reclamo(s) de cuentas demo")

    # Cada fila se compara como tupla completa; con tres .in_() independientes
    # se borrarian combinaciones que nunca creo este script.
    filtros_normativa = [
        and_(
            NormativaPlazoORM.servicio == servicio,
            NormativaPlazoORM.categoria == categoria,
            NormativaPlazoORM.urgencia == urgencia,
        )
        for servicio, categoria, urgencia in CLAVES_NORMATIVA_DEMO
    ]
    n = db.query(NormativaPlazoORM).filter(or_(*filtros_normativa)).delete(
        synchronize_session=False
    )
    print(f"  {n} normativa(s)")

    n = db.query(CuadrillaORM).filter(CuadrillaORM.nombre.in_(NOMBRES_CUADRILLA_DEMO)).delete(
        synchronize_session=False
    )
    print(f"  {n} cuadrilla(s)")

    n = db.query(AreaComercialORM).filter(AreaComercialORM.nombre.in_(NOMBRES_AREA_DEMO)).delete(
        synchronize_session=False
    )
    print(f"  {n} area(s) comercial(es)")

    n = db.query(UsuarioORM).filter(UsuarioORM.documento.in_(DOCUMENTOS_DEMO)).delete(
        synchronize_session=False
    )
    print(f"  {n} usuario(s)")
    db.commit()


def seed_usuarios(db) -> dict:
    repo = UsuarioRepository(db)
    ids = {}
    for nombre, documento, rol in USUARIOS:
        existente = repo.get_by_documento(documento)
        if existente:
            ids[documento] = existente.id_usuario
            rol_real = getattr(existente.rol, "value", existente.rol)
            if rol_real != rol.value:
                print(f"[!]    usuario {documento} ya existe con rol '{rol_real}', "
                      f"se esperaba '{rol.value}'. Corregir con un admin si hace falta.")
            else:
                print(f"[ok]   usuario {documento} ya existe ({rol_real})")
            continue
        creado = repo.create({
            "nombre": nombre,
            "documento": documento,
            "telefono": "3105550000",
            "contraseña": CONTRASENA_DEMO,
            "email": f"{documento}@demo.local",
            "direccion": "Direccion de prueba",
            "rol": rol.value,
        })
        ids[documento] = creado.id_usuario
        print(f"[nuevo] usuario {documento} ({rol.value}) id={creado.id_usuario}")
    return ids


def seed_catalogos(db):
    for servicio, categoria, urgencia, dias in NORMATIVA:
        existe = db.query(NormativaPlazoORM).filter_by(
            servicio=servicio, categoria=categoria, urgencia=urgencia
        ).first()
        if existe:
            continue
        db.add(NormativaPlazoORM(
            servicio=servicio, categoria=categoria, urgencia=urgencia,
            plazo_maximo_dias=dias, vigencia_desde=date.today() - timedelta(days=365),
        ))
        db.commit()
        print(f"[nuevo] normativa {servicio}/{categoria}/{urgencia} = {dias} dias")

    for nombre, especialidad, contacto, capacidad in CUADRILLAS:
        if db.query(CuadrillaORM).filter_by(nombre=nombre).first():
            continue
        db.add(CuadrillaORM(
            nombre=nombre, especialidad=especialidad,
            contacto=contacto, capacidad=capacidad,
        ))
        db.commit()
        print(f"[nuevo] cuadrilla {nombre}")

    for nombre, tipo, contacto in AREAS:
        if db.query(AreaComercialORM).filter_by(nombre=nombre).first():
            continue
        db.add(AreaComercialORM(nombre=nombre, tipo=tipo, contacto=contacto))
        db.commit()
        print(f"[nuevo] area comercial {nombre}")


def seed_reclamos(db, ids):
    repo = ReclamoRepository(db)
    for idx, (doc, canal, servicio, categoria, urgencia, desc, offset, estado) in enumerate(RECLAMOS, 1):
        if db.query(ReclamoORM).filter_by(descripcion=desc).first():
            continue
        creado = repo.create({
            "id_usuario": ids[doc],
            "fecha_recepcion": date.today() - timedelta(days=3),
            "canal": canal,
            "servicio": servicio,
            "categoria": categoria,
            "urgencia": urgencia,
            "descripcion": desc,
            "estado": estado,
            "fecha_tope": date.today() + timedelta(days=offset),
        })
        print(f"[nuevo] reclamo {creado.id_reclamo} ({estado}): {desc[:45]}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Carga datos de prueba")
    parser.add_argument("--reset", action="store_true", help="Borra los datos de prueba antes de insertar")
    args = parser.parse_args()

    print(f"Base de datos: {engine.url.render_as_string(hide_password=True)}")
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        if args.reset:
            _wipe(db)
        print("\n-- Usuarios --")
        ids = seed_usuarios(db)
        print("\n-- Catalogos --")
        seed_catalogos(db)
        print("\n-- Reclamos --")
        seed_reclamos(db, ids)
        db.commit()
    finally:
        db.close()

    print(f"\nListo. Contrasena de todos los usuarios demo: {CONTRASENA_DEMO}")
    print(f"\nEjecuta el backend y prueba el login:")
    for nombre, documento, rol in USUARIOS:
        print(f"  {rol.value:<11} documento={documento}  contraseña={CONTRASENA_DEMO}  ({nombre})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
