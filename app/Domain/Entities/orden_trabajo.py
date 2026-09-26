from dataclasses import dataclass, field
from typing import Optional, List
from datetime import date


@dataclass
class OrdenTrabajo:
    id_orden: int
    id_reclamo: int
    cuadrilla: str
    fecha_asignacion: date
    estado_orden: str
    avances: Optional[List[object]] = field(default=None)
    reclamo: Optional[object] = field(default=None)
