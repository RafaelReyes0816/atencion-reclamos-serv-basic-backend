from sqlalchemy import Column, Integer, String, Date, ForeignKey
from sqlalchemy.orm import relationship
from app.Infraestructura.database import Base


class AvanceORM(Base):
    __tablename__ = "avances"

    id_avance = Column(Integer, primary_key=True, index=True)
    id_orden = Column(Integer, ForeignKey("ordenes_trabajo.id_orden"), nullable=False)
    fecha_avance = Column(Date, nullable=False)
    descripcion = Column(String, nullable=False)
    estado_parcial = Column(String, nullable=False)

    orden = relationship("OrdenTrabajoORM", back_populates="avances")
