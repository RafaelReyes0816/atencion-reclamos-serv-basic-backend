from app.Domain.Repositories.usuario_repository import UsuarioRepositoryABC
from app.Domain.Entities.usuario import Usuario
from app.Domain.Entities.catalogos import Rol
from app.Domain.Exceptions import DuplicadoError


class CrearUsuarioUseCase:
    def __init__(self, repository: UsuarioRepositoryABC):
        self.repository = repository

    def execute(self, data: dict, rol: str = Rol.ciudadano.value) -> Usuario:
        data = dict(data)
        if self.repository.get_by_documento(data["documento"]):
            raise DuplicadoError("Ya existe un usuario con ese documento")
        data["direccion"] = data.get("direccion") or ""
        data["rol"] = rol
        return self.repository.create(data)
