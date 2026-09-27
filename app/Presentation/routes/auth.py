from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.Infraestructura.database import get_db
from app.Infraestructura.security import verify_password, create_access_token
from app.Infraestructura.repositories.usuario_repository import UsuarioRepository
from app.Presentation.schemas.usuario import UsuarioCreate, UsuarioResponse
from app.Presentation.dependencies import get_service
from app.Domain.Entities.catalogos import Rol

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
    access_token = create_access_token(data={"sub": str(orm.id_usuario), "rol": orm.rol})
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "rol": orm.rol,
        "id_usuario": orm.id_usuario,
        "nombre": orm.nombre,
    }


@router.post("/register", response_model=UsuarioResponse, status_code=status.HTTP_201_CREATED)
def register(usuario_data: UsuarioCreate, servicio=Depends(get_service)):
    """Registro público. Siempre crea un usuario con rol `ciudadano`."""
    data = usuario_data.model_dump(exclude={"rol"})
    return servicio["crear_usuario"].execute(data, rol=Rol.ciudadano.value)
