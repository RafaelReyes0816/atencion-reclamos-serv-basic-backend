from enum import Enum


class Rol(str, Enum):
    ciudadano = "ciudadano"
    tecnico = "tecnico"
    supervisor = "supervisor"
    admin = "admin"


class Canal(str, Enum):
    presencial = "presencial"
    telefonico = "telefonico"
    web = "web"


class Servicio(str, Enum):
    agua = "agua"
    luz = "luz"


class Categoria(str, Enum):
    corte = "corte"
    facturacion = "facturacion"
    fuga = "fuga"
    falla_tecnica = "falla_tecnica"


class Urgencia(str, Enum):
    programada = "programada"
    normal = "normal"
    alta = "alta"
    critica = "critica"


class EstadoReclamo(str, Enum):
    registrado = "registrado"
    clasificado = "clasificado"
    en_atencion_tecnica = "en_atencion_tecnica"
    en_atencion_comercial = "en_atencion_comercial"
    resuelto = "resuelto"
    cerrado = "cerrado"
    escalado = "escalado"


class Resultado(str, Enum):
    resuelto = "resuelto"
    descartado = "descartado"
    derivado = "derivado"


class EstadoOrden(str, Enum):
    asignada = "asignada"
    en_curso = "en_curso"
    resuelta = "resuelta"


class EstadoParcial(str, Enum):
    iniciado = "iniciado"
    en_proceso = "en_proceso"
    verificado = "verificado"


class ViaAtencion(str, Enum):
    tecnica = "tecnica"
    comercial = "comercial"


class TipoAreaComercial(str, Enum):
    facturacion = "facturacion"
    cobranza = "cobranza"


class EstadoDerivacion(str, Enum):
    derivada = "derivada"
    resuelta = "resuelta"


class ResultadoComercial(str, Enum):
    anulacion_factura = "anulacion_factura"
    ajuste_factura = "ajuste_factura"
    reclamacion_infundada = "reclamacion_infundada"
    otro = "otro"


class TipoReporte(str, Enum):
    operativo_diario = "operativo_diario"
    regulatorio_mensual = "regulatorio_mensual"
