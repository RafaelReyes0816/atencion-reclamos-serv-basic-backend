from pydantic import BaseModel
from typing import Optional
from datetime import date


class UsuarioCreate(BaseModel):
    nombre: str
    documento: str
    telefono: str
    email: Optional[str] = None
    direccion: str


class UsuarioUpdate(BaseModel):
    nombre: Optional[str] = None
    telefono: Optional[str] = None
    email: Optional[str] = None
    direccion: Optional[str] = None


class UsuarioResponse(BaseModel):
    id_usuario: int
    nombre: str
    documento: str
    telefono: str
    email: Optional[str] = None
    direccion: str

    class Config:
        from_attributes = True
