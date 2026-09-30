from pydantic import BaseModel, ConfigDict, Field
from typing import Optional
from app.Domain.Entities.catalogos import Servicio


class BaseCatalogo(BaseModel):
    model_config = ConfigDict(use_enum_values=True)


class CuadrillaCreate(BaseCatalogo):
    nombre: str = Field(min_length=2, max_length=120)
    especialidad: Servicio
    capacidad: int = Field(gt=0, le=999)
    contacto: str = Field(min_length=6, max_length=30)


class CuadrillaUpdate(BaseCatalogo):
    nombre: Optional[str] = Field(default=None, min_length=2, max_length=120)
    especialidad: Optional[Servicio] = None
    capacidad: Optional[int] = Field(default=None, gt=0, le=999)
    contacto: Optional[str] = Field(default=None, min_length=6, max_length=30)


class CuadrillaResponse(BaseModel):
    id_cuadrilla: int
    nombre: str
    especialidad: str
    # `capacidad` es el tope de ordenes activas; `ordenes_activas` es la carga
    # actual y `disponible` si todavia cabe una mas. Vienen calculados en la
    # lectura, no almacenados.
    capacidad: int
    ordenes_activas: int = 0
    disponible: bool = True
    contacto: str

    model_config = ConfigDict(from_attributes=True)
