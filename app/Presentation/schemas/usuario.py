from pydantic import BaseModel, ConfigDict, EmailStr, Field
from typing import Optional
from app.Domain.Entities.catalogos import Rol


class UsuarioCreate(BaseModel):
    nombre: str = Field(min_length=3, max_length=150)
    documento: str = Field(min_length=5, max_length=30)
    telefono: str = Field(min_length=6, max_length=30)
    contraseña: str = Field(min_length=6, max_length=128)
    email: Optional[EmailStr] = None
    direccion: str = Field(default="", max_length=200)
    rol: Rol = Rol.ciudadano


class UsuarioUpdate(BaseModel):
    nombre: Optional[str] = Field(default=None, min_length=3, max_length=150)
    telefono: Optional[str] = Field(default=None, min_length=6, max_length=30)
    email: Optional[EmailStr] = None
    direccion: Optional[str] = Field(default=None, max_length=200)
    rol: Optional[Rol] = None


class UsuarioCambioContrasena(BaseModel):
    contrasena_actual: str = Field(min_length=1, max_length=128)
    contrasena_nueva: str = Field(min_length=6, max_length=128)


class UsuarioResponse(BaseModel):
    id_usuario: int
    nombre: str
    documento: str
    telefono: str
    email: Optional[str] = None
    direccion: str
    rol: str

    model_config = ConfigDict(from_attributes=True)
