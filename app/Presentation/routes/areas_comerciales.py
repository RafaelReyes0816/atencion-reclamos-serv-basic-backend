from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.Infraestructura.database import get_db
from app.Infraestructura.repositories.area_comercial_repository import AreaComercialRepository
from app.Presentation.schemas.area_comercial import AreaComercialCreate, AreaComercialUpdate, AreaComercialResponse
from app.Presentation.dependencies import get_current_user
from typing import List

router = APIRouter(prefix="/areas-comerciales", tags=["areas-comerciales"])


@router.get("/", response_model=List[AreaComercialResponse])
def listar_areas(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    repo = AreaComercialRepository(db)
    return repo.get_all()


@router.get("/{id}", response_model=AreaComercialResponse)
def obtener_area(id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    repo = AreaComercialRepository(db)
    area = repo.get_by_id(id)
    if not area:
        raise HTTPException(status_code=404, detail="Área comercial no encontrada")
    return area


@router.post("/", response_model=AreaComercialResponse)
def crear_area(area_data: AreaComercialCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    repo = AreaComercialRepository(db)
    return repo.create(area_data.model_dump())


@router.put("/{id}", response_model=AreaComercialResponse)
def actualizar_area(id: int, area_data: AreaComercialUpdate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    repo = AreaComercialRepository(db)
    area = repo.get_by_id(id)
    if not area:
        raise HTTPException(status_code=404, detail="Área comercial no encontrada")
    update_data = area_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(area, key, value)
    return repo.update(area)


@router.delete("/{id}")
def eliminar_area(id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    repo = AreaComercialRepository(db)
    repo.delete(id)
    return {"message": "Área comercial eliminada", "status": "success"}
