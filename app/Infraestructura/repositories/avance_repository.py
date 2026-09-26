from typing import List
from app.Domain.Repositories.avance_repository import AvanceRepositoryABC
from app.Domain.Entities.avance import Avance
from app.Infraestructura.database.models.avance import AvanceORM


class AvanceRepository(AvanceRepositoryABC):
    def __init__(self, db):
        self.db = db

    def _to_entity(self, orm: AvanceORM) -> Avance:
        return Avance(
            id_avance=orm.id_avance,
            id_orden=orm.id_orden,
            fecha_avance=orm.fecha_avance,
            descripcion=orm.descripcion,
            estado_parcial=orm.estado_parcial,
            orden=orm.orden,
        )

    def get_by_orden(self, id_orden: int) -> List[Avance]:
        query = self.db.query(AvanceORM).filter(AvanceORM.id_orden == id_orden)
        return [self._to_entity(e) for e in query.all()]

    def create(self, data: dict) -> Avance:
        orm = AvanceORM(**data)
        self.db.add(orm)
        self.db.commit()
        self.db.refresh(orm)
        return self._to_entity(orm)
