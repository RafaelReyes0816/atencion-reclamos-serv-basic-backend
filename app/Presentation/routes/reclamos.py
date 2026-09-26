from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.Infraestructura.database import get_db
from app.Infraestructura.repositories.reclamo_repository import ReclamoRepository
from app.Infraestructura.repositories.usuario_repository import UsuarioRepository
from app.Presentation.schemas.reclamo import (
    ReclamoCreate, ReclamoUpdate, ReclamoClasificar,
    ReclamoAsignarPlazo, ReclamoResolver, ReclamoCerrar,
    ReclamoContactoUpdate, ReclamoResponse, ComprobanteResponse
)
from app.Presentation.dependencies import get_current_user
from typing import List
from datetime import date

router = APIRouter(prefix="/reclamos", tags=["reclamos"])


@router.get("/", response_model=List[ReclamoResponse])
def listar_reclamos(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    repo = ReclamoRepository(db)
    return repo.get_all()


@router.get("/{id}", response_model=ReclamoResponse)
def obtener_reclamo(id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    repo = ReclamoRepository(db)
    reclamo = repo.get_by_id(id)
    if not reclamo:
        raise HTTPException(status_code=404, detail="Reclamo no encontrado")
    return reclamo


@router.post("/", response_model=ReclamoResponse)
def crear_reclamo(reclamo_data: ReclamoCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    repo = ReclamoRepository(db)
    data = reclamo_data.model_dump()
    data["fecha_recepcion"] = date.today()
    data["estado"] = "registrado"
    return repo.create(data)


@router.put("/{id}", response_model=ReclamoResponse)
def actualizar_reclamo(id: int, reclamo_data: ReclamoUpdate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    repo = ReclamoRepository(db)
    reclamo = repo.get_by_id(id)
    if not reclamo:
        raise HTTPException(status_code=404, detail="Reclamo no encontrado")
    update_data = reclamo_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(reclamo, key, value)
    return repo.update(reclamo)


@router.put("/{id}/clasificar", response_model=ReclamoResponse)
def clasificar_reclamo(id: int, clasificacion: ReclamoClasificar, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    repo = ReclamoRepository(db)
    reclamo = repo.get_by_id(id)
    if not reclamo:
        raise HTTPException(status_code=404, detail="Reclamo no encontrado")
    reclamo.servicio = clasificacion.servicio
    reclamo.categoria = clasificacion.categoria
    reclamo.urgencia = clasificacion.urgencia
    reclamo.estado = "clasificado"
    return repo.update(reclamo)


@router.put("/{id}/asignar-plazo", response_model=ReclamoResponse)
def asignar_plazo(id: int, plazo: ReclamoAsignarPlazo, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    repo = ReclamoRepository(db)
    reclamo = repo.get_by_id(id)
    if not reclamo:
        raise HTTPException(status_code=404, detail="Reclamo no encontrado")
    reclamo.id_normativa = plazo.id_normativa
    reclamo.fecha_tope = plazo.fecha_tope
    return repo.update(reclamo)


@router.put("/{id}/resolver", response_model=ReclamoResponse)
def resolver_reclamo(id: int, resolucion: ReclamoResolver, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    repo = ReclamoRepository(db)
    reclamo = repo.get_by_id(id)
    if not reclamo:
        raise HTTPException(status_code=404, detail="Reclamo no encontrado")
    reclamo.estado = "resuelto"
    reclamo.resultado = resolucion.resultado
    return repo.update(reclamo)


@router.put("/{id}/cerrar", response_model=ReclamoResponse)
def cerrar_reclamo(id: int, cierre: ReclamoCerrar, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    repo = ReclamoRepository(db)
    reclamo = repo.get_by_id(id)
    if not reclamo:
        raise HTTPException(status_code=404, detail="Reclamo no encontrado")
    reclamo.estado = "cerrado"
    reclamo.fecha_cierre = date.today()
    reclamo.resultado = cierre.resultado
    return repo.update(reclamo)


@router.get("/{id}/comprobante", response_model=ComprobanteResponse)
def obtener_comprobante(id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    repo = ReclamoRepository(db)
    reclamo = repo.get_by_id(id)
    if not reclamo:
        raise HTTPException(status_code=404, detail="Reclamo no encontrado")
    return reclamo


@router.get("/estado/{id_o_doc}")
def consultar_estado(id_o_doc: str, db: Session = Depends(get_db)):
    repo = ReclamoRepository(db)
    try:
        id_reclamo = int(id_o_doc)
        reclamo = repo.get_by_id(id_reclamo)
    except ValueError:
        usuario_repo = UsuarioRepository(db)
        usuario = usuario_repo.get_by_documento(id_o_doc)
        if not usuario:
            raise HTTPException(status_code=404, detail="No encontrado")
        reclamos = [r for r in repo.get_all() if r.id_usuario == usuario.id_usuario]
        reclamo = reclamos[-1] if reclamos else None
    if not reclamo:
        raise HTTPException(status_code=404, detail="Reclamo no encontrado")
    return {
        "id_reclamo": reclamo.id_reclamo,
        "estado": reclamo.estado,
        "fecha_tope": reclamo.fecha_tope,
    }


@router.put("/{id}/contacto")
def actualizar_contacto(id: int, contacto: ReclamoContactoUpdate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    reclamo_repo = ReclamoRepository(db)
    reclamo = reclamo_repo.get_by_id(id)
    if not reclamo:
        raise HTTPException(status_code=404, detail="Reclamo no encontrado")
    usuario_repo = UsuarioRepository(db)
    usuario = usuario_repo.get_by_id(reclamo.id_usuario)
    if usuario:
        usuario.telefono = contacto.telefono
        usuario.email = contacto.email
        usuario_repo.update(usuario)
    return {"message": "Contacto actualizado", "status": "success"}
