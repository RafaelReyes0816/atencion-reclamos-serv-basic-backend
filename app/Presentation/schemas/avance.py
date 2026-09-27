from pydantic import BaseModel, ConfigDict, Field
from typing import Optional
from datetime import date
from app.Domain.Entities.catalogos import EstadoParcial


class BaseCatalogo(BaseModel):
    model_config = ConfigDict(use_enum_values=True)


class AvanceCreate(BaseCatalogo):
    id_orden: int = Field(gt=0)
    fecha_avance: date
    descripcion: str = Field(min_length=5, max_length=1000)
    estado_parcial: EstadoParcial


class AvanceResponse(BaseModel):
    id_avance: int
    id_orden: int
    fecha_avance: date
    descripcion: str
    estado_parcial: str

    model_config = ConfigDict(from_attributes=True)
