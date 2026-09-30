from typing import List, Optional
from sqlalchemy import func
from sqlalchemy.orm import joinedload
from app.Domain.Entities.catalogos import EstadoOrden
from app.Domain.Repositories.orden_trabajo_repository import OrdenTrabajoRepositoryABC
from app.Domain.Entities.orden_trabajo import OrdenTrabajo
from app.Infraestructura.database.models.orden_trabajo import OrdenTrabajoORM
from app.Infraestructura.database.models.avance import AvanceORM

# Estados que ocupan a la cuadrilla. Se listan uno por uno en vez de "todo lo
# que no sea resuelta" para que un estado nuevo no empiece a contar sin que
# nadie lo decida a proposito.
ESTADOS_OCUPAN_CUPO = (EstadoOrden.asignada.value, EstadoOrden.en_curso.value)


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
            id_cuadrilla=orm.id_cuadrilla,
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

    def contar_activas_por_cuadrilla(self, excluir_id_orden: int | None = None) -> dict:
        """Un solo GROUP BY para todas las cuadrillas: la lista de reportes y
        la validacion de capacidad comparten el mismo conteo.
        """
        query = self.db.query(
            OrdenTrabajoORM.id_cuadrilla, func.count(OrdenTrabajoORM.id_orden)
        ).filter(
            OrdenTrabajoORM.estado_orden.in_(ESTADOS_OCUPAN_CUPO),
            OrdenTrabajoORM.id_cuadrilla.isnot(None),
        )
        if excluir_id_orden is not None:
            query = query.filter(OrdenTrabajoORM.id_orden != excluir_id_orden)
        return {id_cuadrilla: total for id_cuadrilla, total in query.group_by(
            OrdenTrabajoORM.id_cuadrilla
        ).all()}

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
        if orm is None:
            raise ValueError(f"Orden de trabajo {entity.id_orden} no encontrada")
        orm.id_reclamo = entity.id_reclamo
        orm.id_cuadrilla = entity.id_cuadrilla
        orm.cuadrilla = entity.cuadrilla
        orm.fecha_asignacion = entity.fecha_asignacion
        orm.estado_orden = entity.estado_orden
        self.db.commit()
        self.db.refresh(orm)
        return self._to_entity(orm)

    def delete(self, id: int) -> None:
        orm = self.db.query(OrdenTrabajoORM).filter(OrdenTrabajoORM.id_orden == id).first()
        if orm is None:
            raise ValueError(f"Orden de trabajo {id} no encontrada")
        self.db.query(AvanceORM).filter(AvanceORM.id_orden == id).delete(synchronize_session=False)
        self.db.delete(orm)
        self.db.commit()
