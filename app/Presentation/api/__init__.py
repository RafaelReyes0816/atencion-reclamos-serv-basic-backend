from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import app.Infraestructura.database.models  # noqa: F401  registra todos los ORM en Base.metadata
from app.Infraestructura.database import engine, Base
from app.Infraestructura.tasks import scheduler as scheduler_module
from app.Domain.Exceptions import DomainError
from app.Presentation.routes import auth, usuarios, reclamos, normativa, cuadrillas, areas_comerciales, seguimiento, plazos, reportes, dashboard, medidores


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    scheduler_module.init_scheduler()
    yield
    scheduler_module.shutdown_scheduler()


app = FastAPI(
    title="Sistema de Atención de Reclamos de Servicios Básicos",
    description="API para gestión de reclamos de agua y luz",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(usuarios.router)
app.include_router(medidores.router)
app.include_router(reclamos.router)
app.include_router(normativa.router)
app.include_router(cuadrillas.router)
app.include_router(areas_comerciales.router)
app.include_router(seguimiento.router)
app.include_router(plazos.router)
app.include_router(reportes.router)
app.include_router(dashboard.router)


@app.exception_handler(DomainError)
async def manejar_error_dominio(request: Request, exc: DomainError):
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.mensaje})


@app.get("/")
def root():
    return {"message": "Sistema de Atención de Reclamos de Servicios Básicos"}


@app.get("/health")
def health():
    return {"status": "ok"}
