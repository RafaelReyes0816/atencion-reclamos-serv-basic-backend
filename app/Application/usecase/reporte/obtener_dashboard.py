from datetime import date
from collections import Counter
from app.Domain.Repositories.reclamo_repository import ReclamoRepositoryABC
from app.Domain.Repositories.usuario_repository import UsuarioRepositoryABC

DIAS_ALERTA_VENCIMIENTO = 3
_ESTADOS_EN_ATENCION = ("en_atencion_tecnica", "en_atencion_comercial")


class ObtenerDashboardUseCase:
    def __init__(self, reclamo_repo: ReclamoRepositoryABC, usuario_repo: UsuarioRepositoryABC):
        self.reclamo_repo = reclamo_repo
        self.usuario_repo = usuario_repo

    def execute(self) -> dict:
        reclamos = self.reclamo_repo.get_all()
        hoy = date.today()

        por_estado = Counter(r.estado for r in reclamos)
        por_servicio = Counter(r.servicio for r in reclamos)
        por_categoria = Counter(r.categoria for r in reclamos)
        por_urgencia = Counter(r.urgencia for r in reclamos)

        cerrados = [r for r in reclamos if r.estado == "cerrado"]
        cerrados_en_plazo = [
            r for r in cerrados
            if r.fecha_tope and r.fecha_cierre and r.fecha_cierre <= r.fecha_tope
        ]
        porcentaje_cumplimiento = (
            round(len(cerrados_en_plazo) / len(cerrados) * 100, 2) if cerrados else 0.0
        )

        vencidos = self.reclamo_repo.get_vencidos(hoy)
        por_vencer = [
            r for r in self.reclamo_repo.get_por_vencer(hoy)
            if r.fecha_tope and 0 <= (r.fecha_tope - hoy).days <= DIAS_ALERTA_VENCIMIENTO
        ]
        criticos = self.reclamo_repo.get_criticos()

        return {
            "total_reclamos": len(reclamos),
            "total_usuarios": len(self.usuario_repo.get_all()),
            "por_estado": dict(por_estado),
            "por_servicio": [{"servicio": k, "total": v} for k, v in sorted(por_servicio.items())],
            "por_categoria": dict(por_categoria),
            "por_urgencia": dict(por_urgencia),
            "en_atencion": sum(por_estado.get(e, 0) for e in _ESTADOS_EN_ATENCION),
            "resueltos": por_estado.get("resuelto", 0),
            "cerrados": por_estado.get("cerrado", 0),
            "pendientes": por_estado.get("registrado", 0) + por_estado.get("clasificado", 0),
            "criticos": len(criticos),
            "vencidos": len(vencidos),
            "proximos_vencer": len(por_vencer),
            "cumplidos_en_plazo": len(cerrados_en_plazo),
            "cerrados_en_plazo": len(cerrados),
            "porcentaje_cumplimiento": porcentaje_cumplimiento,
            "alertas_vencidos": [self._alerta_plazo(r, hoy) for r in vencidos],
            "alertas_vencimiento_proximo": [self._alerta_plazo(r, hoy) for r in por_vencer],
            "alertas_criticas": [
                {
                    "id_reclamo": r.id_reclamo,
                    "servicio": r.servicio,
                    "categoria": r.categoria,
                    "urgencia": r.urgencia,
                    "estado": r.estado,
                }
                for r in criticos
            ],
        }

    @staticmethod
    def _alerta_plazo(reclamo, hoy) -> dict:
        return {
            "id_reclamo": reclamo.id_reclamo,
            "estado": reclamo.estado,
            "fecha_tope": reclamo.fecha_tope.isoformat(),
            "dias_restantes": (reclamo.fecha_tope - hoy).days,
        }
