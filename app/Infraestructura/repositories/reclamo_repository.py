from typing import List, Optional
from datetime import date
from sqlalchemy.orm import joinedload
from app.Domain.Repositories.reclamo_repository import ReclamoRepositoryABC
from app.Domain.Entities.reclamo import Reclamo
from app.Infraestructura.database.models.reclamo import ReclamoORM
from app.Infraestructura.database.models.orden_trabajo import OrdenTrabajoORM
from app.Infraestructura.database.models.avance import AvanceORM
from app.Infraestructura.database.models.derivacion_comercial import DerivacionComercialORM


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
            nombre_cuenta=orm.nombre_cuenta,
            direccion=orm.direccion,
            usuario=orm.usuario,
            normativa=orm.normativa,
            orden_trabajo=orm.orden_trabajo,
            derivacion_comercial=orm.derivacion_comercial,
        )

    def _base_query(self):
        return self.db.query(ReclamoORM).options(
            joinedload(ReclamoORM.usuario),
            joinedload(ReclamoORM.normativa),
            joinedload(ReclamoORM.orden_trabajo),
            joinedload(ReclamoORM.derivacion_comercial),
        )

    def get_all(self) -> List[Reclamo]:
        return [self._to_entity(e) for e in self._base_query().all()]

    def get_by_id(self, id: int) -> Optional[Reclamo]:
        orm = self._base_query().filter(ReclamoORM.id_reclamo == id).first()
        return self._to_entity(orm) if orm else None

    def get_by_usuario(self, id_usuario: int) -> List[Reclamo]:
        query = self._base_query().filter(ReclamoORM.id_usuario == id_usuario)
        return [self._to_entity(e) for e in query.all()]

    def get_by_estado(self, estado: str) -> List[Reclamo]:
        query = self._base_query().filter(ReclamoORM.estado == estado)
        return [self._to_entity(e) for e in query.all()]

    def get_filtrados(
        self,
        estado: Optional[str] = None,
        servicio: Optional[str] = None,
        categoria: Optional[str] = None,
        urgencia: Optional[str] = None,
        canal: Optional[str] = None,
        id_usuario: Optional[int] = None,
    ) -> List[Reclamo]:
        query = self._base_query()
        if estado:
            query = query.filter(ReclamoORM.estado == estado)
        if servicio:
            query = query.filter(ReclamoORM.servicio == servicio)
        if categoria:
            query = query.filter(ReclamoORM.categoria == categoria)
        if urgencia:
            query = query.filter(ReclamoORM.urgencia == urgencia)
        if canal:
            query = query.filter(ReclamoORM.canal == canal)
        if id_usuario:
            query = query.filter(ReclamoORM.id_usuario == id_usuario)
        query = query.order_by(ReclamoORM.id_reclamo.desc())
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
        if orm is None:
            raise ValueError(f"Reclamo {entity.id_reclamo} no encontrado")
        orm.id_usuario = entity.id_usuario
        orm.id_normativa = entity.id_normativa
        orm.canal = entity.canal
        orm.servicio = entity.servicio
        orm.categoria = entity.categoria
        orm.urgencia = entity.urgencia
        orm.descripcion = entity.descripcion
        orm.estado = entity.estado
        orm.fecha_tope = entity.fecha_tope
        orm.fecha_cierre = entity.fecha_cierre
        orm.resultado = entity.resultado
        # Ojo: esta copia es campo por campo. Un campo nuevo en la entidad que
        # no se agregue aqui se pierde en la BD sin error.
        orm.nombre_cuenta = entity.nombre_cuenta
        orm.direccion = entity.direccion
        self.db.commit()
        self.db.refresh(orm)
        return self._to_entity(orm)

    def delete(self, id: int) -> None:
        orm = self.db.query(ReclamoORM).filter(ReclamoORM.id_reclamo == id).first()
        if orm is None:
            raise ValueError(f"Reclamo {id} no encontrado")
        orden_ids = [
            orden_id
            for (orden_id,) in self.db.query(OrdenTrabajoORM.id_orden)
            .filter(OrdenTrabajoORM.id_reclamo == id)
            .all()
        ]
        if orden_ids:
            self.db.query(AvanceORM).filter(AvanceORM.id_orden.in_(orden_ids)).delete(
                synchronize_session=False
            )
        self.db.query(OrdenTrabajoORM).filter(OrdenTrabajoORM.id_reclamo == id).delete(synchronize_session=False)
        self.db.query(DerivacionComercialORM).filter(DerivacionComercialORM.id_reclamo == id).delete(synchronize_session=False)
        self.db.delete(orm)
        self.db.commit()

    def update_estado(self, id: int, estado: str) -> None:
        orm = self.db.query(ReclamoORM).filter(ReclamoORM.id_reclamo == id).first()
        if orm:
            orm.estado = estado
            self.db.commit()
