from typing import List
from app.Domain.Repositories.reclamo_repository import ReclamoRepositoryABC
from app.Domain.Entities.reclamo import Reclamo


class ListarReclamosUseCase:
    def __init__(self, repository: ReclamoRepositoryABC):
        self.repository = repository

    def execute(self, **filtros) -> List[Reclamo]:
        return self.repository.get_filtrados(**filtros)
