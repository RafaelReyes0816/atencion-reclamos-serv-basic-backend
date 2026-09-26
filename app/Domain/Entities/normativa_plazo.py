from dataclasses import dataclass, field
from typing import Optional, List
from datetime import date


@dataclass
class NormativaPlazo:
    id_normativa: int
    servicio: str
    categoria: str
    urgencia: str
    plazo_maximo_dias: int
    vigencia_desde: date
    reclamos: Optional[List[object]] = field(default=None)
