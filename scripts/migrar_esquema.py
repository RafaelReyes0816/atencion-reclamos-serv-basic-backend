"""Agrega tablas y columnas nuevas sin perder datos.

`Base.metadata.create_all()` no altera tablas que ya existen, asi que despues de
anadir una columna al ORM hay que ejecutar este script una vez. Para las tablas
inexistentes si basta `create_all`, que solo crea las que faltan.

Es idempotente: se puede ejecutar varias veces sin efecto.
"""
import sys

from sqlalchemy import inspect, text

from app.Infraestructura.database import engine, Base, SessionLocal
import app.Infraestructura.database.models  # noqa: F401  registra los ORM
from app.Infraestructura.database.models.usuario import UsuarioORM
from app.Infraestructura.database.models.medidor import MedidorORM
from app.Infraestructura.repositories.medidor_repository import MedidorRepository
from app.Infraestructura.repositories.usuario_repository import UsuarioRepository
from app.Application.usecase.medidor.gestionar_medidor import AsignarMedidoresPorDefectoUseCase


def _columnas(tabla: str) -> set:
    return {c["name"] for c in inspect(engine).get_columns(tabla)}


def agregar_columna_si_falta(tabla: str, columna: str, ddl: str) -> bool:
    if tabla not in inspect(engine).get_table_names():
        print(f"[skip] {tabla}: la tabla no existe todavia")
        return False
    if columna in _columnas(tabla):
        print(f"[ok]   {tabla}.{columna} ya existe")
        return False
    with engine.begin() as conn:
        conn.execute(text(f"ALTER TABLE {tabla} ADD COLUMN {ddl}"))
    print(f"[nuevo] {tabla}.{columna} agregada")
    return True


def crear_tablas_faltantes() -> bool:
    """Crea solo las tablas del ORM que no existen. Nunca modifica las que ya estan."""
    existentes = set(inspect(engine).get_table_names())
    faltantes = sorted(set(Base.metadata.tables) - existentes)
    if not faltantes:
        print("[ok]   no hay tablas nuevas que crear")
        return False
    Base.metadata.create_all(bind=engine, checkfirst=True)
    for tabla in faltantes:
        print(f"[nuevo] tabla {tabla} creada")
    return True


def completar_medidores_existentes() -> int:
    """Da de alta el medidor de agua y el de luz a las cuentas que ya existian.

    La API ya los crea al registrar un usuario, pero las cuentas anteriores a esta
    tabla nunca los tuvieron. Usa el mismo caso de uso, asi que respeta la regla de
    un medidor por servicio y no duplica si ya existe.
    """
    db = SessionLocal()
    try:
        use_case = AsignarMedidoresPorDefectoUseCase(MedidorRepository(db), UsuarioRepository(db))
        creados = 0
        for usuario in db.query(UsuarioORM).order_by(UsuarioORM.id_usuario).all():
            nuevos = use_case.execute(usuario.id_usuario)
            creados += len(nuevos)
            if nuevos:
                print(f"[nuevo] medidores para {usuario.documento}: "
                      + ", ".join(f"{m.servicio} {m.numero}" for m in nuevos))
        if not creados:
            print("[ok]   todas las cuentas ya tienen sus medidores")
        return creados
    finally:
        db.close()


def agregar_indice_unico_si_falta(indice: str, tabla: str) -> bool:
    """Una restriccion unica que el ORM ya declara pero que create_all no puede
    agregar despues, porque solo crea indices junto con la tabla."""
    if tabla not in inspect(engine).get_table_names():
        print(f"[skip] {tabla}: la tabla no existe todavia")
        return False
    existentes = {i["name"] for i in inspect(engine).get_indexes(tabla)}
    existentes |= {u["name"] for u in inspect(engine).get_unique_constraints(tabla)}
    if indice in existentes:
        print(f"[ok]   {indice} ya existe")
        return False
    with engine.begin() as conn:
        conn.execute(text(f"ALTER TABLE {tabla} ADD CONSTRAINT {indice} UNIQUE (numero)"))
    print(f"[nuevo] {indice} agregada")
    return True


def renumerar_medidores_placeholder() -> int:
    """Sustituye los numeros que se derivaban del documento por codigos generados.

    Los numeros `AG-{documento}` fueron un provisional de una version anterior: no
    son los de ninguna empresa. Se cambian solo esos, y se avisa de cada cambio.
    """
    from app.Application.usecase.medidor.gestionar_medidor import numero_medidor_aleatorio

    db = SessionLocal()
    try:
        repo = MedidorRepository(db)
        cambiados = 0
        for medidor in db.query(MedidorORM).order_by(MedidorORM.id_medidor).all():
            documento = medidor.usuario.documento
            if medidor.numero != f"{'AG' if medidor.servicio == 'agua' else 'LUZ'}-{documento}":
                continue
            nuevo = numero_medidor_aleatorio(medidor.servicio, repo)
            anterior = medidor.numero
            medidor.numero = nuevo
            cambiados += 1
            print(f"[nuevo] {documento} {medidor.servicio}: {anterior} -> {nuevo}")
        if not cambiados:
            print("[ok]   ningun medidor usaba un numero provisional")
        return cambiados
    finally:
        db.commit()
        db.close()


def completar_desde_usuarios() -> None:
    """Backfill de reclamos anteriores a `nombre_cuenta` / `direccion`.

    Esos reclamos no tienen el dato, pero su titular sí: se registraron bajo
    un `id_usuario` que ya conía nombre y dirección. Solo rellena NULLs, así
    que es idempotente y no pisa lo capturado después.
    """
    if "reclamos" not in inspect(engine).get_table_names():
        return
    if not {"nombre_cuenta", "direccion"} <= _columnas("reclamos"):
        print("[skip] reclamos: faltan las columnas, corre el script de nuevo")
        return
    # El mapeo no es simétrico a propósito: la cuenta viene de usuarios.nombre.
    origenes = {"nombre_cuenta": "nombre", "direccion": "direccion"}
    with engine.begin() as conn:
        for columna, origen in origenes.items():
            # Los nombres de columna son literales de este modulo, no entrada externa.
            sql = (
                f"UPDATE reclamos SET {columna} = usuarios.{origen} "
                "FROM usuarios "
                "WHERE reclamos.id_usuario = usuarios.id_usuario "
                f"AND reclamos.{columna} IS NULL "
                f"AND usuarios.{origen} IS NOT NULL"
            )
            resultado = conn.execute(text(sql))
            print(f"[dato] reclamos.{columna} <- usuarios.{origen}: {resultado.rowcount or 0} fila(s)")


def main() -> int:
    print(f"Base de datos: {engine.url.render_as_string(hide_password=True)}\n")
    cambios = 0

    cambios += crear_tablas_faltantes()
    print()

    cambios += agregar_columna_si_falta(
        "usuarios", "rol", "rol VARCHAR(20) NOT NULL DEFAULT 'ciudadano'"
    )
    cambios += agregar_columna_si_falta(
        "reclamos", "nombre_cuenta", "nombre_cuenta VARCHAR(120)"
    )
    cambios += agregar_columna_si_falta("reclamos", "direccion", "direccion VARCHAR(255)")

    completar_desde_usuarios()

    # Nullable a proposito: los reclamos anteriores a los medidores se conservan
    # sin medidor asociado en lugar de quedar invalidos.
    cambios += agregar_columna_si_falta(
        "reclamos", "id_medidor", "id_medidor INTEGER REFERENCES medidores(id_medidor)"
    )

    print()
    cambios += agregar_indice_unico_si_falta("uq_medidor_numero", "medidores")

    print()
    cambios += completar_medidores_existentes()

    print()
    cambios += renumerar_medidores_placeholder()

    if not cambios:
        print("\nNo hacia falta ningun cambio: el esquema ya estaba al dia.")
    else:
        print(f"\nSe aplicaron {cambios} cambio(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
