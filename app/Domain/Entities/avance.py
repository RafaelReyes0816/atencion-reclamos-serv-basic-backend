from dataclasses import dataclass, field
from typing import Optional
from datetime import date


@dataclass
class Avance:
    id_avance: int
    id_orden: int
    fecha_avance: date
    descripcion: str
    estado_parcial: str
    orden: Optional[object] = field(default=None)
