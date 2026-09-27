from typing import Optional
from app.Domain.Repositories.usuario_repository import UsuarioRepositoryABC
from app.Domain.Entities.usuario import Usuario
from app.Domain.Exceptions import NoEncontradoError


class ActualizarUsuarioUseCase:
    def __init__(self, repository: UsuarioRepositoryABC):
        self.repository = repository

    def execute(self, id: int, cambios: dict) -> Usuario:
        usuario = self.repository.get_by_id(id)
        if usuario is None:
            raise NoEncontradoError("Usuario no encontrado")
        for campo, valor in cambios.items():
            if valor is not None and hasattr(usuario, campo):
                setattr(usuario, campo, valor)
        return self.repository.update(usuario)
