# AGENTS.md

## Stack

- **Backend:** Python, FastAPI, SQLAlchemy, PostgreSQL, JWT (`app/`)
- **Frontend:** React 19, Vite 8, React Router v7, Axios, pnpm (`frontend/`)
- **Deploy:** Solo local (sin despliegue a producción)
- **Package manager:** pnpm only (no npm/yarn). No TypeScript — files are `.js`/`.jsx`.
- **Repos:** Backend y frontend en repos separados dentro de la misma carpeta

## Commands

```bash
# Backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

# Frontend
cd frontend && pnpm install
cd frontend && pnpm dev       # Vite dev server, port 5173
cd frontend && pnpm lint      # ESLint flat config
cd frontend && pnpm build     # Production build to dist/
```

## Architecture (Clean Architecture)

Dependency rule is strict — violations cause import errors:

```
Presentation → Application → Domain ← Infraestructura
```

- `app/Domain/` — pure dataclasses (entities) + ABC interfaces (repositories). Never imports from Infraestructura or Presentation.
- `app/Application/usecase/` — one class per CRUD operation. Depends only on Domain.
- `app/Infraestructura/` — SQLAlchemy models, JWT/bcrypt, concrete repositories. Implements what Domain defines.
- `app/Presentation/` — FastAPI app, routes, Pydantic schemas, DI dependencies. Uses Application (use cases).

Key directories:
- `app/Domain/Entities/` — dataclass entities
- `app/Domain/Repositories/` — ABC interfaces
- `app/Infraestructura/database/` — engine, SessionLocal, Base, get_db (setup in `__init__.py`)
- `app/Infraestructura/repositories/` — concrete implementations
- `app/Application/usecase/<entity>/` — use case classes
- `app/Presentation/routes/` — FastAPI routers
- `app/Presentation/schemas/` — Pydantic schemas

## Gotchas

- **bcrypt version:** Must use `bcrypt==4.0.1` — newer versions (5.x) break passlib compatibility. See `requirements.txt`.
- **Entity relations:** Always include `Optional[object]` for relationships in entity dataclasses, otherwise Pydantic throws `Field required` on serialization.
- **joinedload:** Use `joinedload()` in `get_all` and `get_by_id` on every relationship. Without it, related objects are `None` and Pydantic fails.
- **DATABASE_URL dialect:** Use `postgresql+psycopg://` (not `postgresql://`). See `app/Infraestructura/database/__init__.py`.
- **SQLite support:** `database/__init__.py` auto-detects SQLite and disables `pool_pre_ping`. Use `sqlite:///./test.db` for local dev.
- **API proxy:** Frontend uses relative URLs. Vite proxies to backend via `vite.config.js` server.proxy. Add new routes there when adding endpoints. Don't hardcode `VITE_API_URL` in axios.
- **Login format:** OAuth2 `application/x-www-form-urlencoded` (not JSON) — matches FastAPI's `OAuth2PasswordRequestForm`. `username` = documento.
- **Password field:** User entity has `contraseña` (plain) in request, `contraseña_hash` (bcrypt) in DB. Never expose hash in API responses.
- **DI pattern:** Routes use `get_service(db)` with `Depends()` to inject repositories and use cases.
- **Table recreation:** If DB schema changes (new columns), drop and recreate tables: `Base.metadata.drop_all()` then `Base.metadata.create_all()`.

## Conventions

- UI in Spanish (variables, labels, error messages).
- One use case class per CRUD operation (e.g., `ListarProductosUseCase`).
- Entity ↔ ORM conversion inline in each concrete repository.
- Routes pattern: `router = APIRouter(prefix="/entities", tags=["entities"])`.

## Testing

```bash
# Backend
pytest  # pytest + httpx (async) or FastAPI TestClient

# Frontend
cd frontend && pnpm vitest  # Vitest + React Testing Library (not configured by default)
```

- Naming: `test_<method>_<scenario>_<result>`

## Deployment Notes

- Backend: Solo local, sin Docker ni plataforma externa.
- Frontend: Solo local, sin Vercel ni plataforma externa.
- Secrets en `.env` (nunca en el repo).

## Reference

- Template guide: `docs/Plantilla-FastAPI.md`
- Plan de desarrollo: `PLAN.md`
