from typing import Optional
from app.Domain.Repositories.derivacion_comercial_repository import DerivacionComercialRepositoryABC
from app.Domain.Entities.derivacion_comercial import DerivacionComercial
from app.Infraestructura.database.models.derivacion_comercial import DerivacionComercialORM


class DerivacionComercialRepository(DerivacionComercialRepositoryABC):
    def __init__(self, db):
        self.db = db

    def _to_entity(self, orm: DerivacionComercialORM) -> DerivacionComercial:
        return DerivacionComercial(
            id_derivacion=orm.id_derivacion,
            id_reclamo=orm.id_reclamo,
            fecha_derivacion=orm.fecha_derivacion,
            area_comercial=orm.area_comercial,
            estado_derivacion=orm.estado_derivacion,
            reclamo=orm.reclamo,
        )

    def get_by_id(self, id: int) -> Optional[DerivacionComercial]:
        orm = self.db.query(DerivacionComercialORM).filter(
            DerivacionComercialORM.id_derivacion == id
        ).first()
        return self._to_entity(orm) if orm else None

    def get_by_reclamo(self, id_reclamo: int) -> Optional[DerivacionComercial]:
        orm = self.db.query(DerivacionComercialORM).filter(
            DerivacionComercialORM.id_reclamo == id_reclamo
        ).first()
        return self._to_entity(orm) if orm else None

    def create(self, data: dict) -> DerivacionComercial:
        orm = DerivacionComercialORM(**data)
        self.db.add(orm)
        self.db.commit()
        self.db.refresh(orm)
        return self._to_entity(orm)

    def update(self, entity: DerivacionComercial) -> DerivacionComercial:
        orm = self.db.query(DerivacionComercialORM).filter(
            DerivacionComercialORM.id_derivacion == entity.id_derivacion
        ).first()
        if orm is None:
            raise ValueError(f"Derivación {entity.id_derivacion} no encontrada")
        orm.id_reclamo = entity.id_reclamo
        orm.fecha_derivacion = entity.fecha_derivacion
        orm.area_comercial = entity.area_comercial
        orm.estado_derivacion = entity.estado_derivacion
        self.db.commit()
        self.db.refresh(orm)
        return self._to_entity(orm)
