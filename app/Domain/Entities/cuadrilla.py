from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Cuadrilla:
    id_cuadrilla: int
    nombre: str
    especialidad: str
    capacidad: int
    contacto: str
