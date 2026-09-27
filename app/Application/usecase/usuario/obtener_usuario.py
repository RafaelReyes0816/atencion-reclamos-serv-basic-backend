from typing import Optional
from app.Domain.Repositories.usuario_repository import UsuarioRepositoryABC
from app.Domain.Entities.usuario import Usuario
from app.Domain.Exceptions import NoEncontradoError, ConflictoError


class ObtenerUsuarioUseCase:
    def __init__(self, repository: UsuarioRepositoryABC):
        self.repository = repository

    def execute(self, id: int) -> Usuario:
        usuario = self.repository.get_by_id(id)
        if usuario is None:
            raise NoEncontradoError("Usuario no encontrado")
        return usuario

    def execute_por_documento(self, documento: str) -> Usuario:
        usuario = self.repository.get_by_documento(documento)
        if usuario is None:
            raise NoEncontradoError("Usuario no encontrado")
        return usuario


class EliminarUsuarioUseCase:
    def __init__(self, repository: UsuarioRepositoryABC):
        self.repository = repository

    def execute(self, id: int) -> None:
        try:
            self.repository.delete(id)
        except ValueError as e:
            if "no encontrado" in str(e):
                raise NoEncontradoError(str(e))
            raise ConflictoError(str(e))
