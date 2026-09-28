from sqlalchemy import Column, Integer, String, Date, ForeignKey
from sqlalchemy.orm import relationship
from app.Infraestructura.database import Base


class ReclamoORM(Base):
    __tablename__ = "reclamos"

    id_reclamo = Column(Integer, primary_key=True, index=True)
    id_usuario = Column(Integer, ForeignKey("usuarios.id_usuario"), nullable=False)
    id_normativa = Column(Integer, ForeignKey("normativa_plazos.id_normativa"), nullable=True)
    fecha_recepcion = Column(Date, nullable=False)
    canal = Column(String, nullable=False)
    servicio = Column(String, nullable=False)
    categoria = Column(String, nullable=False)
    urgencia = Column(String, nullable=False)
    descripcion = Column(String, nullable=False)
    # Titular de la cuenta donde ocurre el problema. NO es necesariamente el
    #Usuario del reclamo: un interno puede registrarlo a nombre de un
    #ciudadano sobre una cuenta de un tercero. Nullable solo por legado.
    nombre_cuenta = Column(String(120), nullable=True)
    direccion = Column(String(255), nullable=True)
    estado = Column(String, nullable=False, default="registrado")
    fecha_tope = Column(Date, nullable=True)
    fecha_cierre = Column(Date, nullable=True)
    resultado = Column(String, nullable=True)

    usuario = relationship("UsuarioORM", back_populates="reclamos")
    normativa = relationship("NormativaPlazoORM", back_populates="reclamos")
    orden_trabajo = relationship("OrdenTrabajoORM", back_populates="reclamo", uselist=False)
    derivacion_comercial = relationship("DerivacionComercialORM", back_populates="reclamo", uselist=False)
