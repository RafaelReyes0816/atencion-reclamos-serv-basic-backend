from sqlalchemy import Column, Integer, String, Date, ForeignKey
from sqlalchemy.orm import relationship
from app.Infraestructura.database import Base


class DerivacionComercialORM(Base):
    __tablename__ = "derivaciones_comerciales"

    id_derivacion = Column(Integer, primary_key=True, index=True)
    id_reclamo = Column(Integer, ForeignKey("reclamos.id_reclamo"), nullable=False)
    fecha_derivacion = Column(Date, nullable=False)
    area_comercial = Column(String, nullable=False)
    estado_derivacion = Column(String, nullable=False, default="derivada")

    reclamo = relationship("ReclamoORM", back_populates="derivacion_comercial")
