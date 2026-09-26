from apscheduler.schedulers.background import BackgroundScheduler
from app.Infraestructura.database import SessionLocal
from app.Infraestructura.repositories.reclamo_repository import ReclamoRepository
from app.Infraestructura.repositories.avance_repository import AvanceRepository
from app.Infraestructura.repositories.reporte_repository import ReporteRepository
from app.Application.usecase.plazos.detectar_vencimiento_proximo import DetectarVencimientoProximoUseCase
from app.Application.usecase.plazos.detectar_reclamo_vencido import DetectarReclamoVencidoUseCase
from app.Application.usecase.plazos.detectar_reclamo_critico import DetectarReclamoCriticoUseCase
from app.Application.usecase.reporte.generar_reporte_diario import GenerarReporteDiarioUseCase
from app.Application.usecase.reporte.generar_reporte_mensual import GenerarReporteMensualUseCase
import logging

logger = logging.getLogger(__name__)

scheduler = BackgroundScheduler()


def detectar_vencimientos():
    db = SessionLocal()
    try:
        repo = ReclamoRepository(db)
        use_case = DetectarVencimientoProximoUseCase(repo)
        avisos = use_case.execute()
        if avisos:
            logger.info(f"Vencimientos próximos detectados: {len(avisos)}")
    except Exception as e:
        logger.error(f"Error al detectar vencimientos: {e}")
    finally:
        db.close()


def detectar_vencidos():
    db = SessionLocal()
    try:
        repo = ReclamoRepository(db)
        use_case = DetectarReclamoVencidoUseCase(repo)
        alertas = use_case.execute()
        if alertas:
            logger.info(f"Reclamos vencidos detectados: {len(alertas)}")
    except Exception as e:
        logger.error(f"Error al detectar vencidos: {e}")
    finally:
        db.close()


def detectar_criticos():
    db = SessionLocal()
    try:
        repo = ReclamoRepository(db)
        use_case = DetectarReclamoCriticoUseCase(repo)
        alarmas = use_case.execute()
        if alarmas:
            logger.info(f"Reclamos críticos detectados: {len(alarmas)}")
    except Exception as e:
        logger.error(f"Error al detectar críticos: {e}")
    finally:
        db.close()


def generar_reporte_diario():
    db = SessionLocal()
    try:
        reclamo_repo = ReclamoRepository(db)
        avance_repo = AvanceRepository(db)
        reporte_repo = ReporteRepository(db)
        use_case = GenerarReporteDiarioUseCase(reclamo_repo, avance_repo, reporte_repo)
        resultado = use_case.execute()
        logger.info(f"Reporte diario generado: {resultado.get('id_reporte')}")
    except Exception as e:
        logger.error(f"Error al generar reporte diario: {e}")
    finally:
        db.close()


def generar_reporte_mensual():
    db = SessionLocal()
    try:
        reclamo_repo = ReclamoRepository(db)
        reporte_repo = ReporteRepository(db)
        use_case = GenerarReporteMensualUseCase(reclamo_repo, reporte_repo)
        resultado = use_case.execute()
        logger.info(f"Reporte mensual generado: {resultado.get('id_reporte')}")
    except Exception as e:
        logger.error(f"Error al generar reporte mensual: {e}")
    finally:
        db.close()


def init_scheduler():
    scheduler.add_job(detectar_vencimientos, 'interval', hours=1, id='detectar_vencimientos')
    scheduler.add_job(detectar_vencidos, 'interval', hours=1, id='detectar_vencidos')
    scheduler.add_job(detectar_criticos, 'interval', minutes=30, id='detectar_criticos')
    scheduler.add_job(generar_reporte_diario, 'cron', hour=23, minute=0, id='reporte_diario')
    scheduler.add_job(generar_reporte_mensual, 'cron', day=1, hour=0, minute=0, id='reporte_mensual')
    scheduler.start()
    logger.info("Scheduler iniciado")


def shutdown_scheduler():
    if scheduler.running:
        scheduler.shutdown()
        logger.info("Scheduler detenido")
