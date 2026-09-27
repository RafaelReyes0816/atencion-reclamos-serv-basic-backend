from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Any, Dict


class ReporteResponse(BaseModel):
    id_reporte: int
    tipo_reporte: str
    periodo: str
    fecha_generacion: datetime
    contenido: str

    model_config = ConfigDict(from_attributes=True)


class ReporteGeneradoResponse(BaseModel):
    message: str
    id_reporte: int


class ReporteContenidoResponse(BaseModel):
    id_reporte: int
    tipo_reporte: str
    periodo: str
    fecha_generacion: datetime
    datos: Dict[str, Any]
