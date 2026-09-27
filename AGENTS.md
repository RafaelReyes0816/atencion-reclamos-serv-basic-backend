# AGENTS.md

## Stack

- **Backend:** Python, FastAPI, SQLAlchemy, PostgreSQL, JWT (`app/`)
- **Frontend:** React 19, Vite 8, React Router v7, Axios, pnpm (`frontend/`)
- **Deploy:** Solo local (sin despliegue a producción)
- **Package manager:** pnpm only (no npm/yarn). No TypeScript — files are `.js`/`.jsx`.
- **Repos:** Two independent git repos (`backend/` and `frontend/`), not a monorepo

## Commands

```bash
# Backend
pip install -r requirements.txt
python -m scripts.migrar_esquema   # aplica ALTERs pendientes (idempotente, no borra datos)
python -m scripts.seed             # datos de prueba (--reset para recargar)
uvicorn app.main:app --reload --port 8000

# Frontend
cd frontend && pnpm install
cd frontend && pnpm dev       # Vite dev server, port 5173
cd frontend && pnpm lint      # oxlint (NOT ESLint)
cd frontend && pnpm build     # Production build to dist/
```

Swagger: http://localhost:8000/docs

### Usuarios de prueba (`python -m scripts.seed`)

| rol | documento | contraseña |
|-----|-----------|------------|
| `admin` | `10000001` | `clave123` |
| `supervisor` | `10000002` | `clave123` |
| `tecnico` | `10000003` | `clave123` |
| `ciudadano` | `10000004` | `clave123` |

En PowerShell usar `curl.exe`, no `Invoke-RestMethod` (rompe la `ñ` de la contraseña).

## Roles y permisos

Cuatro roles en `app/Domain/Entities/catalogos.py::Rol`. Se aplican con
`require_roles(*roles)` en `app/Presentation/dependencies/__init__.py`:

```python
from app.Presentation.dependencies import require_roles, INTERNO, GESTION, ADMIN

INTERNO  = (tecnico, supervisor, admin)   # lectura de catalogs + operacion de reclamos
GESTION  = (supervisor, admin)            # escritura de catalogs, cierre, reportes, dashboard
ADMIN    = (admin,)                       # CRUD de usuarios, eliminacion de reclamos
```

`POST /auth/register` es público pero **siempre** asigna `ciudadano`; ignora el `rol` del
body. Solo `POST /usuarios/` (admin) permite crear usuarios con otro rol. Los claims del JWT
se re-consultan contra la BD en cada request, así que cambiar el rol surte efecto de
inmediato. La matriz completa está en `docs/API.md`.

## Architecture (Clean Architecture)

Dependency rule is strict — violations cause import errors:

```
Presentation → Application → Domain ← Infraestructura
```

- `app/Domain/` — pure dataclasses (entities) + ABC interfaces (repositories) + `Exceptions.py`. Never imports from Infraestructura or Presentation.
- `app/Application/usecase/` — use cases. Depends only on Domain.
- `app/Infraestructura/` — SQLAlchemy models, JWT/bcrypt, concrete repositories. Implements what Domain defines.
- `app/Presentation/` — FastAPI app (in `api/`), routes, Pydantic schemas, DI dependencies. Uses Application (use cases).

Key directories:
- `app/Domain/Entities/` — dataclass entities
- `app/Domain/Repositories/` — ABC interfaces
- `app/Domain/Exceptions.py` — `DomainError` y derivados. `Presentation/api/__init__.py` los traduce a HTTP con su `status_code`, así que los use cases lanzan excepciones de dominio, nunca `HTTPException`.
- `app/Infraestructura/database/` — engine, SessionLocal, Base, get_db (setup in `__init__.py`)
- `app/Infraestructura/repositories/` — concrete implementations
- `app/Application/usecase/<entity>/` — use case classes, agrupados por archivo (`gestionar_<entidad>.py`)
- `app/Presentation/api/` — FastAPI app, CORS middleware, router includes, exception handlers, lifespan
- `app/Presentation/routes/` — FastAPI routers
- `app/Presentation/schemas/` — Pydantic schemas
- `app/main.py` — entry point (thin wrapper, imports app from `Presentation/api`)
- `scripts/` — `migrar_esquema.py` y `seed.py`

## Gotchas

- **bcrypt version:** Must use `bcrypt==4.0.1` — newer versions (5.x) break passlib compatibility. See `requirements.txt`.
- **Entity relations:** Always include `Optional[object]` for relationships in entity dataclasses, otherwise Pydantic throws `Field required` on serialization.
- **joinedload:** Use `joinedload()` in `get_all` and `get_by_id` on every relationship. Without it, related objects are `None` and Pydantic fails.
- **DATABASE_URL dialect:** Use `postgresql+psycopg://` (not `postgresql://`). See `app/Infraestructura/database/__init__.py`.
- **SQLite support:** `database/__init__.py` auto-detects SQLite and disables `pool_pre_ping`. Use `sqlite:///./test.db` for local dev.
- **API proxy:** Frontend uses relative URLs. Vite proxies to backend via `vite.config.js` server.proxy. Add new routes there when adding endpoints. Don't hardcode `VITE_API_URL` in axios.
- **Vite 8 host:** `vite.config.js` sets `host: '127.0.0.1'` — without this, Vite 8 only binds `[::1]` and `http://127.0.0.1:5173` doesn't respond.
- **Preview proxy:** `pnpm preview` (port 4173) also needs the proxy config; without it the app loads but all API calls fail silently.
- **CORS:** `Presentation/api/__init__.py` allows `http://localhost:5173`. Update if frontend port changes.
- **Login format:** OAuth2 `application/x-www-form-urlencoded` (not JSON) — matches FastAPI's `OAuth2PasswordRequestForm`. `username` = documento.
- **Password field:** User entity has `contraseña` (plain) in request, `contraseña_hash` (bcrypt) in DB. Never expose hash in API responses. `UsuarioRepository.update()` nunca escribe el hash: para contraseñas usar `actualizar_contrasena()`.
- **DI pattern:** Routes usan `use_cases = Depends(get_service)` — un dict de use cases. **No instanciar repositorios directamente en las rutas**; la lógica de negocio va en `app/Application/usecase/`, no en el route.
- **Schema changes:** `Base.metadata.create_all()` **no altera** tablas existentes. Ejecutar `python -m scripts.migrar_esquema` (ALTER idempotente, preserva datos). No usar `drop_all` salvo que quieras perder todo.
- **Scheduler en tests:** `Presentation/api/__init__.py` importa el módulo con `from app.Infraestructura.tasks import scheduler` y llama `scheduler_module.init_scheduler()`, no `from ... import init_scheduler`. Si se importa la función directamente, el monkeypatch de `conftest.py` deja de funcionar y el `BackgroundScheduler` real arranca contra la BD real.
- **403 vs 401:** `401` = token ausente/inválido. `403` = token válido pero rol insuficiente. El frontend debe distinguir ambos.

## Conventions

- UI in Spanish (variables, labels, error messages).
- One use case class per CRUD operation (e.g., `ListarProductosUseCase`).
- Entity ↔ ORM conversion inline in each concrete repository.
- Routes pattern: `router = APIRouter(prefix="/entities", tags=["entities"])`.

## Testing

```bash
# Backend (from backend/)
cd backend && pytest  # pytest + httpx (async) or FastAPI TestClient
```

- Naming: `test_<method>_<scenario>_<result>`
- Frontend testing not configured (vitest not in devDependencies)

## Deployment Notes

- Backend: Solo local, sin Docker ni plataforma externa.
- Frontend: Solo local, sin Vercel ni plataforma externa.
- Secrets en `.env` (nunca en el repo).

## Reference

- Template guide: `docs/Plantilla-FastAPI.md`
- Architecture docs: `docs/ARQUITECTURA.md`
- Plan de desarrollo: `PLAN.md`
