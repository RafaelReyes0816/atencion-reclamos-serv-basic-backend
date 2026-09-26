from sqlalchemy import Column, Integer, String, Date, ForeignKey
from sqlalchemy.orm import relationship
from app.Infraestructura.database import Base


class OrdenTrabajoORM(Base):
    __tablename__ = "ordenes_trabajo"

    id_orden = Column(Integer, primary_key=True, index=True)
    id_reclamo = Column(Integer, ForeignKey("reclamos.id_reclamo"), nullable=False)
    cuadrilla = Column(String, nullable=False)
    fecha_asignacion = Column(Date, nullable=False)
    estado_orden = Column(String, nullable=False, default="asignada")

    reclamo = relationship("ReclamoORM", back_populates="orden_trabajo")
    avances = relationship("AvanceORM", back_populates="orden")
