from pydantic import BaseModel
from datetime import date


class AvanceCreate(BaseModel):
    id_orden: int
    fecha_avance: date
    descripcion: str
    estado_parcial: str


class AvanceResponse(BaseModel):
    id_avance: int
    id_orden: int
    fecha_avance: date
    descripcion: str
    estado_parcial: str

    class Config:
        from_attributes = True
