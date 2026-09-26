from typing import List, Optional
from datetime import date
from app.Domain.Repositories.normativa_plazo_repository import NormativaPlazoRepositoryABC
from app.Domain.Entities.normativa_plazo import NormativaPlazo
from app.Infraestructura.database.models.normativa_plazo import NormativaPlazoORM


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

    def get_vigente(self, servicio: str, categoria: str, urgencia: str, fecha: date) -> Optional[NormativaPlazo]:
        orm = self.db.query(NormativaPlazoORM).filter(
            NormativaPlazoORM.servicio == servicio,
            NormativaPlazoORM.categoria == categoria,
            NormativaPlazoORM.urgencia == urgencia,
            NormativaPlazoORM.vigencia_desde <= fecha,
        ).order_by(NormativaPlazoORM.vigencia_desde.desc()).first()
        return self._to_entity(orm) if orm else None

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
        if orm:
            orm.servicio = entity.servicio
            orm.categoria = entity.categoria
            orm.urgencia = entity.urgencia
            orm.plazo_maximo_dias = entity.plazo_maximo_dias
            orm.vigencia_desde = entity.vigencia_desde
            self.db.commit()
            self.db.refresh(orm)
        return self._to_entity(orm)
