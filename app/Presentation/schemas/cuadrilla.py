from pydantic import BaseModel
from typing import Optional


class CuadrillaCreate(BaseModel):
    nombre: str
    especialidad: str
    capacidad: int
    contacto: str


class CuadrillaUpdate(BaseModel):
    nombre: Optional[str] = None
    especialidad: Optional[str] = None
    capacidad: Optional[int] = None
    contacto: Optional[str] = None


class CuadrillaResponse(BaseModel):
    id_cuadrilla: int
    nombre: str
    especialidad: str
    capacidad: int
    contacto: str

    class Config:
        from_attributes = True
