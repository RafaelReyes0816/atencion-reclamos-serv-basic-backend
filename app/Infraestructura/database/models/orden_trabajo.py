from sqlalchemy import Column, Integer, String, Date, ForeignKey
from sqlalchemy.orm import relationship
from app.Infraestructura.database import Base


class OrdenTrabajoORM(Base):
    __tablename__ = "ordenes_trabajo"

    id_orden = Column(Integer, primary_key=True, index=True)
    id_reclamo = Column(Integer, ForeignKey("reclamos.id_reclamo"), nullable=False)
    # Nullable a proposito: las ordenes anteriores a esta columna no tienen
    # cuadrilla que las respalde y se conservan con el nombre en `cuadrilla`.
    id_cuadrilla = Column(Integer, ForeignKey("cuadrillas.id_cuadrilla"), nullable=True)
    # Nombre desnormalizado. Es la copia del nombre en el momento de la
    # asignacion, para que la orden muestre lo que se asigno aunque la
    # cuadrilla se renombre despues. La verdad sobre la capacidad esta en la
    # FK, no aqui.
    cuadrilla = Column(String, nullable=False)
    fecha_asignacion = Column(Date, nullable=False)
    estado_orden = Column(String, nullable=False, default="asignada")

    reclamo = relationship("ReclamoORM", back_populates="orden_trabajo")
    avances = relationship("AvanceORM", back_populates="orden")
