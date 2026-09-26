from typing import Optional
from app.Domain.Repositories.usuario_repository import UsuarioRepositoryABC
from app.Domain.Entities.usuario import Usuario


class ObtenerUsuarioUseCase:
    def __init__(self, repository: UsuarioRepositoryABC):
        self.repository = repository

    def execute(self, id: int) -> Optional[Usuario]:
        return self.repository.get_by_id(id)
