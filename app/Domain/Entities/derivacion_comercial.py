from dataclasses import dataclass, field
from typing import Optional
from datetime import date


@dataclass
class DerivacionComercial:
    id_derivacion: int
    id_reclamo: int
    fecha_derivacion: date
    area_comercial: str
    estado_derivacion: str
    reclamo: Optional[object] = field(default=None)
