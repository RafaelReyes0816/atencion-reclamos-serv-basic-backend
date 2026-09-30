from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.Infraestructura.database import Base


class MedidorORM(Base):
    __tablename__ = "medidores"
    # Un unico medidor por servicio y por cliente: es lo que permite que el ciudadano
    # # solo tenga que seleccionar el suyo y nunca escribir el numero.
    # El numero tambien es unico en toda la tabla: el sistema lo genera al azar, y
    # dos clientes con el mismo codigo seria indistinguibles para la cuadrilla.
    __table_args__ = (
        UniqueConstraint("id_usuario", "servicio", name="uq_medidor_usuario_servicio"),
        UniqueConstraint("numero", name="uq_medidor_numero"),
    )

    id_medidor = Column(Integer, primary_key=True, index=True)
    id_usuario = Column(Integer, ForeignKey("usuarios.id_usuario"), nullable=False, index=True)
    servicio = Column(String, nullable=False)
    numero = Column(String, nullable=False)
    direccion = Column(String, nullable=True)
    activo = Column(Boolean, nullable=False, default=True)

    usuario = relationship("UsuarioORM", back_populates="medidores")
    reclamos = relationship("ReclamoORM", back_populates="medidor")
