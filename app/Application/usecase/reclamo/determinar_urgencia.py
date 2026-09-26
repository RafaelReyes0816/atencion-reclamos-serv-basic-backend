from app.Domain.Entities.catalogos import Urgencia


class DeterminarUrgenciaUseCase:
    def execute(self, servicio: str, categoria: str, contexto: dict = None) -> str:
        if servicio == "agua" and categoria == "fuga":
            if contexto and contexto.get("caudal_alto"):
                return Urgencia.critica.value
            return Urgencia.normal.value
        if servicio == "luz" and categoria == "corte":
            if contexto and contexto.get("prolongado"):
                return Urgencia.critica.value
            return Urgencia.programada.value
        if servicio == "agua" and categoria == "corte":
            return Urgencia.alta.value
        if servicio == "luz" and categoria == "falla_tecnica":
            if contexto and contexto.get("falla_general"):
                return Urgencia.alta.value
            return Urgencia.normal.value
        if categoria == "facturacion":
            return Urgencia.normal.value
        return Urgencia.normal.value
