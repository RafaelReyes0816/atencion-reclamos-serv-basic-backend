from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime


@dataclass
class Reporte:
    id_reporte: int
    tipo_reporte: str
    periodo: str
    fecha_generacion: datetime
    contenido: str
