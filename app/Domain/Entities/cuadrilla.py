from dataclasses import dataclass


@dataclass
class Cuadrilla:
    id_cuadrilla: int
    nombre: str
    especialidad: str
    capacidad: int
    contacto: str
    # Derivados: los arma el caso de uso contando las ordenes activas. No se
    # guardan, se recalculan en cada lectura. El default describe a una
    # cuadrilla recien creada, que es justamente cuando no hay caso de uso que
    # los llene y aun asi debe poder serializarse.
    ordenes_activas: int = 0
    disponible: bool = True
