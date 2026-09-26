from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.Infraestructura.database import get_db
from app.Infraestructura.security import verify_password, get_password_hash, create_access_token
from app.Infraestructura.repositories.usuario_repository import UsuarioRepository
from app.Presentation.schemas.usuario import UsuarioCreate, UsuarioResponse

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    repo = UsuarioRepository(db)
    orm = repo.get_orm_by_documento(form_data.username)
    if not orm or not verify_password(form_data.password, orm.contraseña_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Documento o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": orm.id_usuario})
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/register", response_model=UsuarioResponse)
def register(usuario_data: UsuarioCreate, db: Session = Depends(get_db)):
    repo = UsuarioRepository(db)
    existing = repo.get_by_documento(usuario_data.documento)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ya existe un usuario con ese documento",
        )
    data = usuario_data.model_dump()
    data["direccion"] = data.get("direccion", "")
    return repo.create(data)
