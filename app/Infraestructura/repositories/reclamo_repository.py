from typing import List, Optional
from datetime import date
from sqlalchemy.orm import joinedload
from app.Domain.Repositories.reclamo_repository import ReclamoRepositoryABC
from app.Domain.Entities.reclamo import Reclamo
from app.Infraestructura.database.models.reclamo import ReclamoORM


class ReclamoRepository(ReclamoRepositoryABC):
    def __init__(self, db):
        self.db = db

    def _to_entity(self, orm: ReclamoORM) -> Reclamo:
        return Reclamo(
            id_reclamo=orm.id_reclamo,
            id_usuario=orm.id_usuario,
            fecha_recepcion=orm.fecha_recepcion,
            canal=orm.canal,
            servicio=orm.servicio,
            categoria=orm.categoria,
            urgencia=orm.urgencia,
            descripcion=orm.descripcion,
            estado=orm.estado,
            id_normativa=orm.id_normativa,
            fecha_tope=orm.fecha_tope,
            fecha_cierre=orm.fecha_cierre,
            resultado=orm.resultado,
            usuario=orm.usuario,
            normativa=orm.normativa,
            orden_trabajo=orm.orden_trabajo,
            derivacion_comercial=orm.derivacion_comercial,
        )

    def get_all(self) -> List[Reclamo]:
        query = self.db.query(ReclamoORM).options(
            joinedload(ReclamoORM.usuario),
            joinedload(ReclamoORM.normativa),
            joinedload(ReclamoORM.orden_trabajo),
            joinedload(ReclamoORM.derivacion_comercial),
        )
        return [self._to_entity(e) for e in query.all()]

    def get_by_id(self, id: int) -> Optional[Reclamo]:
        query = self.db.query(ReclamoORM).options(
            joinedload(ReclamoORM.usuario),
            joinedload(ReclamoORM.normativa),
            joinedload(ReclamoORM.orden_trabajo),
            joinedload(ReclamoORM.derivacion_comercial),
        ).filter(ReclamoORM.id_reclamo == id)
        orm = query.first()
        return self._to_entity(orm) if orm else None

    def get_by_estado(self, estado: str) -> List[Reclamo]:
        query = self.db.query(ReclamoORM).options(
            joinedload(ReclamoORM.usuario),
        ).filter(ReclamoORM.estado == estado)
        return [self._to_entity(e) for e in query.all()]

    def get_por_vencer(self, fecha_actual: date) -> List[Reclamo]:
        query = self.db.query(ReclamoORM).options(
            joinedload(ReclamoORM.usuario),
        ).filter(
            ReclamoORM.fecha_tope >= fecha_actual,
            ReclamoORM.estado.notin_(["cerrado", "registrado"]),
        )
        return [self._to_entity(e) for e in query.all()]

    def get_vencidos(self, fecha_actual: date) -> List[Reclamo]:
        query = self.db.query(ReclamoORM).options(
            joinedload(ReclamoORM.usuario),
        ).filter(
            ReclamoORM.fecha_tope < fecha_actual,
            ReclamoORM.estado.notin_(["cerrado"]),
        )
        return [self._to_entity(e) for e in query.all()]

    def get_criticos(self) -> List[Reclamo]:
        query = self.db.query(ReclamoORM).options(
            joinedload(ReclamoORM.usuario),
        ).filter(
            ReclamoORM.urgencia == "critica",
            ReclamoORM.estado.notin_(["cerrado", "resuelto"]),
        )
        return [self._to_entity(e) for e in query.all()]

    def create(self, data: dict) -> Reclamo:
        orm = ReclamoORM(**data)
        self.db.add(orm)
        self.db.commit()
        self.db.refresh(orm)
        return self._to_entity(orm)

    def update(self, entity: Reclamo) -> Reclamo:
        orm = self.db.query(ReclamoORM).filter(ReclamoORM.id_reclamo == entity.id_reclamo).first()
        if orm:
            orm.id_normativa = entity.id_normativa
            orm.estado = entity.estado
            orm.fecha_tope = entity.fecha_tope
            orm.fecha_cierre = entity.fecha_cierre
            orm.resultado = entity.resultado
            self.db.commit()
            self.db.refresh(orm)
        return self._to_entity(orm)

    def update_estado(self, id: int, estado: str) -> None:
        orm = self.db.query(ReclamoORM).filter(ReclamoORM.id_reclamo == id).first()
        if orm:
            orm.estado = estado
            self.db.commit()
