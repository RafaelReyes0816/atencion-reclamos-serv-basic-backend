from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.Infraestructura.database import engine, Base
from app.Infraestructura.tasks.scheduler import init_scheduler, shutdown_scheduler
from app.Presentation.routes import auth, usuarios, reclamos, normativa, cuadrillas, areas_comerciales, seguimiento, plazos, reportes


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    init_scheduler()
    yield
    shutdown_scheduler()


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
app.include_router(reclamos.router)
app.include_router(normativa.router)
app.include_router(cuadrillas.router)
app.include_router(areas_comerciales.router)
app.include_router(seguimiento.router)
app.include_router(plazos.router)
app.include_router(reportes.router)


@app.get("/")
def root():
    return {"message": "Sistema de Atención de Reclamos de Servicios Básicos"}


@app.get("/health")
def health():
    return {"status": "ok"}
