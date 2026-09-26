from sqlalchemy import Column, Integer, String, Date
from sqlalchemy.orm import relationship
from app.Infraestructura.database import Base


class NormativaPlazoORM(Base):
    __tablename__ = "normativa_plazos"

    id_normativa = Column(Integer, primary_key=True, index=True)
    servicio = Column(String, nullable=False)
    categoria = Column(String, nullable=False)
    urgencia = Column(String, nullable=False)
    plazo_maximo_dias = Column(Integer, nullable=False)
    vigencia_desde = Column(Date, nullable=False)

    reclamos = relationship("ReclamoORM", back_populates="normativa")
