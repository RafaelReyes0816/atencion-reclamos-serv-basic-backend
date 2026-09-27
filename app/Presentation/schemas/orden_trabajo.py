from pydantic import BaseModel, ConfigDict, Field
from typing import Optional
from datetime import date
from app.Domain.Entities.catalogos import EstadoOrden


class BaseCatalogo(BaseModel):
    model_config = ConfigDict(use_enum_values=True)


class OrdenTrabajoCreate(BaseCatalogo):
    id_reclamo: int = Field(gt=0)
    cuadrilla: str = Field(min_length=2, max_length=120)
    fecha_asignacion: date


class OrdenTrabajoUpdate(BaseCatalogo):
    cuadrilla: Optional[str] = Field(default=None, min_length=2, max_length=120)
    fecha_asignacion: Optional[date] = None
    estado_orden: Optional[EstadoOrden] = None


class OrdenTrabajoResponse(BaseModel):
    id_orden: int
    id_reclamo: int
    cuadrilla: str
    fecha_asignacion: date
    estado_orden: str

    model_config = ConfigDict(from_attributes=True)
