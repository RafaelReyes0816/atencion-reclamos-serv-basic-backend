from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.Infraestructura.database import get_db
from app.Infraestructura.repositories.normativa_plazo_repository import NormativaPlazoRepository
from app.Presentation.schemas.normativa import NormativaCreate, NormativaUpdate, NormativaResponse
from app.Presentation.dependencies import get_current_user
from typing import List

router = APIRouter(prefix="/normativa", tags=["normativa"])


@router.get("/", response_model=List[NormativaResponse])
def listar_normativa(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    repo = NormativaPlazoRepository(db)
    return repo.get_all()


@router.get("/vigente", response_model=NormativaResponse)
def obtener_vigente(servicio: str, categoria: str, urgencia: str, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    repo = NormativaPlazoRepository(db)
    from datetime import date
    normativa = repo.get_vigente(servicio, categoria, urgencia, date.today())
    if not normativa:
        raise HTTPException(status_code=404, detail="No hay normativa vigente para esta combinación")
    return normativa


@router.post("/", response_model=NormativaResponse)
def crear_normativa(normativa_data: NormativaCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    repo = NormativaPlazoRepository(db)
    return repo.create(normativa_data.model_dump())


@router.put("/{id}", response_model=NormativaResponse)
def actualizar_normativa(id: int, normativa_data: NormativaUpdate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    repo = NormativaPlazoRepository(db)
    normativa = repo.get_vigente("a", "b", "c", date.today())
    from app.Domain.Entities.normativa_plazo import NormativaPlazo
    existing = NormativaPlazo(id_normativa=id, servicio="", categoria="", urgencia="", plazo_maximo_dias=0, vigencia_desde=date.today())
    update_data = normativa_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(existing, key, value)
    return repo.update(existing)
