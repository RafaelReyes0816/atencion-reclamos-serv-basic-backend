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


def main() -> int:
    print(f"Base de datos: {engine.url.render_as_string(hide_password=True)}\n")
    cambios = 0

    cambios += agregar_columna_si_falta(
        "usuarios", "rol", "rol VARCHAR(20) NOT NULL DEFAULT 'ciudadano'"
    )

    if not cambios:
        print("\nNo hacia falta ningun cambio: el esquema ya estaba al dia.")
    else:
        print(f"\nSe aplicaron {cambios} cambio(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
