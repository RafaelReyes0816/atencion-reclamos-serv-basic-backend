from dataclasses import dataclass, field
from typing import Optional, List


@dataclass
class Usuario:
    id_usuario: int
    nombre: str
    documento: str
    telefono: str
    email: Optional[str] = None
    direccion: str = ""
    reclamos: Optional[List[object]] = field(default=None)
