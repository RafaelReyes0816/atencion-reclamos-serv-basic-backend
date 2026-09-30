from pydantic import BaseModel, ConfigDict, Field
from typing import Optional
from datetime import date
from app.Domain.Entities.catalogos import EstadoOrden


class BaseCatalogo(BaseModel):
    model_config = ConfigDict(use_enum_values=True)


class OrdenTrabajoCreate(BaseCatalogo):
    id_reclamo: int = Field(gt=0)
    # La cuadrilla se elige por id, no por nombre: es lo unico que permite
    # validar la capacidad. El nombre lo responde el servidor, y por eso no
    # se acepta en la entrada (habria dos fuentes de verdad).
    id_cuadrilla: int = Field(gt=0)
    fecha_asignacion: date


class OrdenTrabajoUpdate(BaseCatalogo):
    id_cuadrilla: Optional[int] = Field(default=None, gt=0)
    fecha_asignacion: Optional[date] = None
    estado_orden: Optional[EstadoOrden] = None


class OrdenTrabajoResponse(BaseModel):
    id_orden: int
    id_reclamo: int
    id_cuadrilla: Optional[int] = None
    cuadrilla: str
    fecha_asignacion: date
    estado_orden: str

    model_config = ConfigDict(from_attributes=True)
