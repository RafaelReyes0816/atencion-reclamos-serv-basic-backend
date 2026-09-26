from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.Infraestructura.database import get_db
from app.Infraestructura.repositories.orden_trabajo_repository import OrdenTrabajoRepository
from app.Infraestructura.repositories.avance_repository import AvanceRepository
from app.Infraestructura.repositories.derivacion_comercial_repository import DerivacionComercialRepository
from app.Presentation.schemas.orden_trabajo import OrdenTrabajoCreate, OrdenTrabajoUpdate, OrdenTrabajoResponse
from app.Presentation.schemas.avance import AvanceCreate, AvanceResponse
from app.Presentation.schemas.derivacion import DerivacionCreate, DerivacionUpdate, DerivacionResponse
from app.Presentation.dependencies import get_current_user
from typing import List

router = APIRouter(prefix="/seguimiento", tags=["seguimiento"])


@router.get("/ordenes", response_model=List[OrdenTrabajoResponse])
def listar_ordenes(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    repo = OrdenTrabajoRepository(db)
    return repo.get_all()


@router.get("/ordenes/{id}", response_model=OrdenTrabajoResponse)
def obtener_orden(id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    repo = OrdenTrabajoRepository(db)
    orden = repo.get_by_id(id)
    if not orden:
        raise HTTPException(status_code=404, detail="Orden no encontrada")
    return orden


@router.get("/ordenes/reclamo/{id_reclamo}", response_model=OrdenTrabajoResponse)
def obtener_por_reclamo(id_reclamo: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    repo = OrdenTrabajoRepository(db)
    orden = repo.get_by_reclamo(id_reclamo)
    if not orden:
        raise HTTPException(status_code=404, detail="No hay orden para este reclamo")
    return orden


@router.post("/ordenes", response_model=OrdenTrabajoResponse)
def crear_orden(orden_data: OrdenTrabajoCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    repo = OrdenTrabajoRepository(db)
    data = orden_data.model_dump()
    data["estado_orden"] = "asignada"
    return repo.create(data)


@router.put("/ordenes/{id}", response_model=OrdenTrabajoResponse)
def actualizar_orden(id: int, orden_data: OrdenTrabajoUpdate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    repo = OrdenTrabajoRepository(db)
    orden = repo.get_by_id(id)
    if not orden:
        raise HTTPException(status_code=404, detail="Orden no encontrada")
    update_data = orden_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(orden, key, value)
    return repo.update(orden)


@router.get("/avances/{id_orden}", response_model=List[AvanceResponse])
def listar_avances(id_orden: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    repo = AvanceRepository(db)
    return repo.get_by_orden(id_orden)


@router.post("/avances", response_model=AvanceResponse)
def crear_avance(avance_data: AvanceCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    repo = AvanceRepository(db)
    return repo.create(avance_data.model_dump())


@router.get("/derivaciones/{id_reclamo}", response_model=DerivacionResponse)
def obtener_derivacion(id_reclamo: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    repo = DerivacionComercialRepository(db)
    derivacion = repo.get_by_reclamo(id_reclamo)
    if not derivacion:
        raise HTTPException(status_code=404, detail="No hay derivación para este reclamo")
    return derivacion


@router.post("/derivaciones", response_model=DerivacionResponse)
def crear_derivacion(derivacion_data: DerivacionCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    repo = DerivacionComercialRepository(db)
    data = derivacion_data.model_dump()
    data["estado_derivacion"] = "derivada"
    return repo.create(data)


@router.put("/derivaciones/{id}", response_model=DerivacionResponse)
def actualizar_derivacion(id: int, derivacion_data: DerivacionUpdate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    repo = DerivacionComercialRepository(db)
    derivacion = repo.get_by_reclamo(id)
    if not derivacion:
        raise HTTPException(status_code=404, detail="Derivación no encontrada")
    update_data = derivacion_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(derivacion, key, value)
    return repo.update(derivacion)
