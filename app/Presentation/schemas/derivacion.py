from pydantic import BaseModel
from typing import Optional
from datetime import date


class DerivacionCreate(BaseModel):
    id_reclamo: int
    fecha_derivacion: date
    area_comercial: str


class DerivacionUpdate(BaseModel):
    estado_derivacion: Optional[str] = None


class DerivacionResponse(BaseModel):
    id_derivacion: int
    id_reclamo: int
    fecha_derivacion: date
    area_comercial: str
    estado_derivacion: str

    class Config:
        from_attributes = True
