from typing import List, Optional
from sqlalchemy.orm import joinedload
from app.Domain.Repositories.orden_trabajo_repository import OrdenTrabajoRepositoryABC
from app.Domain.Entities.orden_trabajo import OrdenTrabajo
from app.Infraestructura.database.models.orden_trabajo import OrdenTrabajoORM


class OrdenTrabajoRepository(OrdenTrabajoRepositoryABC):
    def __init__(self, db):
        self.db = db

    def _to_entity(self, orm: OrdenTrabajoORM) -> OrdenTrabajo:
        return OrdenTrabajo(
            id_orden=orm.id_orden,
            id_reclamo=orm.id_reclamo,
            cuadrilla=orm.cuadrilla,
            fecha_asignacion=orm.fecha_asignacion,
            estado_orden=orm.estado_orden,
            avances=orm.avances,
            reclamo=orm.reclamo,
        )

    def get_all(self) -> List[OrdenTrabajo]:
        query = self.db.query(OrdenTrabajoORM).options(
            joinedload(OrdenTrabajoORM.avances),
            joinedload(OrdenTrabajoORM.reclamo),
        )
        return [self._to_entity(e) for e in query.all()]

    def get_by_id(self, id: int) -> Optional[OrdenTrabajo]:
        query = self.db.query(OrdenTrabajoORM).options(
            joinedload(OrdenTrabajoORM.avances),
            joinedload(OrdenTrabajoORM.reclamo),
        ).filter(OrdenTrabajoORM.id_orden == id)
        orm = query.first()
        return self._to_entity(orm) if orm else None

    def get_by_reclamo(self, id_reclamo: int) -> Optional[OrdenTrabajo]:
        query = self.db.query(OrdenTrabajoORM).options(
            joinedload(OrdenTrabajoORM.avances),
        ).filter(OrdenTrabajoORM.id_reclamo == id_reclamo)
        orm = query.first()
        return self._to_entity(orm) if orm else None

    def create(self, data: dict) -> OrdenTrabajo:
        orm = OrdenTrabajoORM(**data)
        self.db.add(orm)
        self.db.commit()
        self.db.refresh(orm)
        return self._to_entity(orm)

    def update(self, entity: OrdenTrabajo) -> OrdenTrabajo:
        orm = self.db.query(OrdenTrabajoORM).filter(
            OrdenTrabajoORM.id_orden == entity.id_orden
        ).first()
        if orm:
            orm.estado_orden = entity.estado_orden
            self.db.commit()
            self.db.refresh(orm)
        return self._to_entity(orm)
