from typing import List, Optional
from datetime import date
from app.Domain.Repositories.normativa_plazo_repository import NormativaPlazoRepositoryABC
from app.Domain.Entities.normativa_plazo import NormativaPlazo
from app.Infraestructura.database.models.normativa_plazo import NormativaPlazoORM
from app.Infraestructura.database.models.reclamo import ReclamoORM


class NormativaPlazoRepository(NormativaPlazoRepositoryABC):
    def __init__(self, db):
        self.db = db

    def _to_entity(self, orm: NormativaPlazoORM) -> NormativaPlazo:
        return NormativaPlazo(
            id_normativa=orm.id_normativa,
            servicio=orm.servicio,
            categoria=orm.categoria,
            urgencia=orm.urgencia,
            plazo_maximo_dias=orm.plazo_maximo_dias,
            vigencia_desde=orm.vigencia_desde,
        )

    def get_all(self) -> List[NormativaPlazo]:
        query = self.db.query(NormativaPlazoORM)
        return [self._to_entity(e) for e in query.all()]

    def get_by_id(self, id: int) -> Optional[NormativaPlazo]:
        orm = self.db.query(NormativaPlazoORM).filter(NormativaPlazoORM.id_normativa == id).first()
        return self._to_entity(orm) if orm else None

    def get_vigente(self, servicio: str, categoria: str, urgencia: str, fecha: date) -> Optional[NormativaPlazo]:
        orm = self.db.query(NormativaPlazoORM).filter(
            NormativaPlazoORM.servicio == servicio,
            NormativaPlazoORM.categoria == categoria,
            NormativaPlazoORM.urgencia == urgencia,
            NormativaPlazoORM.vigencia_desde <= fecha,
        ).order_by(NormativaPlazoORM.vigencia_desde.desc()).first()
        return self._to_entity(orm) if orm else None

    def get_filtrados(
        self,
        servicio: Optional[str] = None,
        categoria: Optional[str] = None,
        urgencia: Optional[str] = None,
    ) -> List[NormativaPlazo]:
        query = self.db.query(NormativaPlazoORM)
        if servicio:
            query = query.filter(NormativaPlazoORM.servicio == servicio)
        if categoria:
            query = query.filter(NormativaPlazoORM.categoria == categoria)
        if urgencia:
            query = query.filter(NormativaPlazoORM.urgencia == urgencia)
        query = query.order_by(NormativaPlazoORM.id_normativa.desc())
        return [self._to_entity(e) for e in query.all()]

    def create(self, data: dict) -> NormativaPlazo:
        orm = NormativaPlazoORM(**data)
        self.db.add(orm)
        self.db.commit()
        self.db.refresh(orm)
        return self._to_entity(orm)

    def update(self, entity: NormativaPlazo) -> NormativaPlazo:
        orm = self.db.query(NormativaPlazoORM).filter(
            NormativaPlazoORM.id_normativa == entity.id_normativa
        ).first()
        if orm is None:
            raise ValueError(f"Normativa {entity.id_normativa} no encontrada")
        orm.servicio = entity.servicio
        orm.categoria = entity.categoria
        orm.urgencia = entity.urgencia
        orm.plazo_maximo_dias = entity.plazo_maximo_dias
        orm.vigencia_desde = entity.vigencia_desde
        self.db.commit()
        self.db.refresh(orm)
        return self._to_entity(orm)

    def delete(self, id: int) -> None:
        orm = self.db.query(NormativaPlazoORM).filter(NormativaPlazoORM.id_normativa == id).first()
        if orm is None:
            raise ValueError(f"Normativa {id} no encontrada")
        self.db.query(ReclamoORM).filter(ReclamoORM.id_normativa == id).update(
            {ReclamoORM.id_normativa: None}, synchronize_session=False
        )
        self.db.delete(orm)
        self.db.commit()
