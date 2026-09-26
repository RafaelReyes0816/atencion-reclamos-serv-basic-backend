from pydantic import BaseModel
from typing import Optional


class AreaComercialCreate(BaseModel):
    nombre: str
    tipo: str
    contacto: str


class AreaComercialUpdate(BaseModel):
    nombre: Optional[str] = None
    tipo: Optional[str] = None
    contacto: Optional[str] = None


class AreaComercialResponse(BaseModel):
    id_area: int
    nombre: str
    tipo: str
    contacto: str

    class Config:
        from_attributes = True
