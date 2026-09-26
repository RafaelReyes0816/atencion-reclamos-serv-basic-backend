from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.Infraestructura.database import get_db
from app.Infraestructura.repositories.cuadrilla_repository import CuadrillaRepository
from app.Presentation.schemas.cuadrilla import CuadrillaCreate, CuadrillaUpdate, CuadrillaResponse
from app.Presentation.dependencies import get_current_user
from typing import List

router = APIRouter(prefix="/cuadrillas", tags=["cuadrillas"])


@router.get("/", response_model=List[CuadrillaResponse])
def listar_cuadrillas(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    repo = CuadrillaRepository(db)
    return repo.get_all()


@router.get("/{id}", response_model=CuadrillaResponse)
def obtener_cuadrilla(id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    repo = CuadrillaRepository(db)
    cuadrilla = repo.get_by_id(id)
    if not cuadrilla:
        raise HTTPException(status_code=404, detail="Cuadrilla no encontrada")
    return cuadrilla


@router.get("/disponibles/{especialidad}", response_model=List[CuadrillaResponse])
def obtener_disponibles(especialidad: str, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    repo = CuadrillaRepository(db)
    return repo.get_disponibles(especialidad)


@router.post("/", response_model=CuadrillaResponse)
def crear_cuadrilla(cuadrilla_data: CuadrillaCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    repo = CuadrillaRepository(db)
    return repo.create(cuadrilla_data.model_dump())


@router.put("/{id}", response_model=CuadrillaResponse)
def actualizar_cuadrilla(id: int, cuadrilla_data: CuadrillaUpdate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    repo = CuadrillaRepository(db)
    cuadrilla = repo.get_by_id(id)
    if not cuadrilla:
        raise HTTPException(status_code=404, detail="Cuadrilla no encontrada")
    update_data = cuadrilla_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(cuadrilla, key, value)
    return repo.update(cuadrilla)


@router.delete("/{id}")
def eliminar_cuadrilla(id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    repo = CuadrillaRepository(db)
    repo.delete(id)
    return {"message": "Cuadrilla eliminada", "status": "success"}
