from typing import Optional
from app.Domain.Repositories.reclamo_repository import ReclamoRepositoryABC
from app.Domain.Entities.reclamo import Reclamo


class ObtenerReclamoUseCase:
    def __init__(self, repository: ReclamoRepositoryABC):
        self.repository = repository

    def execute(self, id: int) -> Optional[Reclamo]:
        return self.repository.get_by_id(id)
