from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ReporteResponse(BaseModel):
    id_reporte: int
    tipo_reporte: str
    periodo: str
    fecha_generacion: datetime
    contenido: str

    class Config:
        from_attributes = True
