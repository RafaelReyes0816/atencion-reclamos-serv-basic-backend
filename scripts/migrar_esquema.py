"""Agrega columnas nuevas sin perder datos.

`Base.metadata.create_all()` no altera tablas que ya existen, asi que despues de
anadir una columna al ORM hay que ejecutar este script una vez.

Es idempotente: se puede ejecutar varias veces sin efecto.
"""
import sys

from sqlalchemy import inspect, text

from app.Infraestructura.database import engine
import app.Infraestructura.database.models  # noqa: F401  registra los ORM


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

    cambios += agregar_columna_si_falta(
        "usuarios", "rol", "rol VARCHAR(20) NOT NULL DEFAULT 'ciudadano'"
    )
    cambios += agregar_columna_si_falta(
        "reclamos", "nombre_cuenta", "nombre_cuenta VARCHAR(120)"
    )
    cambios += agregar_columna_si_falta("reclamos", "direccion", "direccion VARCHAR(255)")

    completar_desde_usuarios()

    if not cambios:
        print("\nNo hacia falta ningun cambio: el esquema ya estaba al dia.")
    else:
        print(f"\nSe aplicaron {cambios} cambio(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
