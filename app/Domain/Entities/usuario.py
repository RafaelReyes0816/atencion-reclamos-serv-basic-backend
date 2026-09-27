from dataclasses import dataclass, field
from typing import Optional, List
from app.Domain.Entities.catalogos import Rol


@dataclass
class Usuario:
    id_usuario: int
    nombre: str
    documento: str
    telefono: str
    contraseña: str = ""
    email: Optional[str] = None
    direccion: str = ""
    rol: str = Rol.ciudadano.value
    reclamos: Optional[List[object]] = field(default=None)
