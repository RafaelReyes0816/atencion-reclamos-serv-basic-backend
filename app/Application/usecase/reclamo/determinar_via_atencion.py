from app.Domain.Entities.catalogos import ViaAtencion


class DeterminarViaAtencionUseCase:
    def execute(self, categoria: str) -> str:
        via_tecnica = ["corte", "fuga", "falla_tecnica"]
        via_comercial = ["facturacion"]
        if categoria in via_tecnica:
            return ViaAtencion.tecnica.value
        if categoria in via_comercial:
            return ViaAtencion.comercial.value
        return ViaAtencion.tecnica.value
