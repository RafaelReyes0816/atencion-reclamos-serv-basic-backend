from typing import List
from app.Domain.Repositories.reporte_repository import ReporteRepositoryABC
from app.Domain.Entities.reporte import Reporte
from app.Infraestructura.database.models.reporte import ReporteORM


class ReporteRepository(ReporteRepositoryABC):
    def __init__(self, db):
        self.db = db

    def _to_entity(self, orm: ReporteORM) -> Reporte:
        return Reporte(
            id_reporte=orm.id_reporte,
            tipo_reporte=orm.tipo_reporte,
            periodo=orm.periodo,
            fecha_generacion=orm.fecha_generacion,
            contenido=orm.contenido,
        )

    def get_all(self) -> List[Reporte]:
        query = self.db.query(ReporteORM)
        return [self._to_entity(e) for e in query.all()]

    def get_by_tipo(self, tipo: str) -> List[Reporte]:
        query = self.db.query(ReporteORM).filter(ReporteORM.tipo_reporte == tipo)
        return [self._to_entity(e) for e in query.all()]

    def create(self, data: dict) -> Reporte:
        orm = ReporteORM(**data)
        self.db.add(orm)
        self.db.commit()
        self.db.refresh(orm)
        return self._to_entity(orm)
