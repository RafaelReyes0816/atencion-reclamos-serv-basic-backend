from typing import List
from app.Domain.Repositories.usuario_repository import UsuarioRepositoryABC
from app.Domain.Entities.usuario import Usuario


class ListarUsuariosUseCase:
    def __init__(self, repository: UsuarioRepositoryABC):
        self.repository = repository

    def execute(self) -> List[Usuario]:
        return self.repository.get_all()
