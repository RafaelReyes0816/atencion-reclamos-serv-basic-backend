from pydantic import BaseModel
from typing import Optional
from datetime import date


class OrdenTrabajoCreate(BaseModel):
    id_reclamo: int
    cuadrilla: str
    fecha_asignacion: date


class OrdenTrabajoUpdate(BaseModel):
    estado_orden: Optional[str] = None


class OrdenTrabajoResponse(BaseModel):
    id_orden: int
    id_reclamo: int
    cuadrilla: str
    fecha_asignacion: date
    estado_orden: str

    class Config:
        from_attributes = True
