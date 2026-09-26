from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.Infraestructura.database import get_db
from app.Infraestructura.repositories.usuario_repository import UsuarioRepository
from app.Presentation.schemas.usuario import UsuarioCreate, UsuarioUpdate, UsuarioResponse
from app.Presentation.dependencies import get_current_user
from typing import List

router = APIRouter(prefix="/usuarios", tags=["usuarios"])


@router.get("/", response_model=List[UsuarioResponse])
def listar_usuarios(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    repo = UsuarioRepository(db)
    return repo.get_all()


@router.get("/{id}", response_model=UsuarioResponse)
def obtener_usuario(id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    repo = UsuarioRepository(db)
    usuario = repo.get_by_id(id)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return usuario


@router.get("/documento/{documento}", response_model=UsuarioResponse)
def obtener_por_documento(documento: str, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    repo = UsuarioRepository(db)
    usuario = repo.get_by_documento(documento)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return usuario


@router.post("/", response_model=UsuarioResponse)
def crear_usuario(usuario_data: UsuarioCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    repo = UsuarioRepository(db)
    existing = repo.get_by_documento(usuario_data.documento)
    if existing:
        raise HTTPException(status_code=400, detail="Ya existe un usuario con ese documento")
    data = usuario_data.model_dump()
    data["direccion"] = data.get("direccion", "")
    return repo.create(data)


@router.put("/{id}", response_model=UsuarioResponse)
def actualizar_usuario(id: int, usuario_data: UsuarioUpdate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    repo = UsuarioRepository(db)
    usuario = repo.get_by_id(id)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    update_data = usuario_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(usuario, key, value)
    return repo.update(usuario)
