# AGENTS.md

## Layout

- **Backend:** Python, FastAPI, SQLAlchemy, PostgreSQL, JWT (`backend/app/`)
- **Frontend:** React 19, Vite 8, React Router v7, Axios (`frontend/`) — pnpm only, no TypeScript (`.js`/`.jsx`)
- **Two independent git repos** (`backend/`, `frontend/`), both on `master` with a GitHub
  `origin`. There is **no root `.git`**: the root `AGENTS.md`, `docs/`, and `PLAN.md` are untracked
  by both.
- `backend/AGENTS.md` is a tracked near-duplicate of this file. **Update both** or they drift.
- `backend/PLAN.md` is byte-identical to the root `PLAN.md` — edit one and copy.
- Commits are conventional, in Spanish: `feat:`, `fix:`, `docs:`, `refactor:`. Feature work lands
  as a paired backend + frontend commit pair.
- **No CI, no pre-commit, no Python linter/formatter/typechecker.** There is no `pyproject.toml`
  or `setup.py` — deps live only in `backend/requirements.txt`, and `pytest` is the *only*
  automated gate. Don't reach for `ruff`/`black`/`mypy`; they are not configured.

## Commands

```bash
# Backend — deps live in backend/venv, NOT the system python
cd backend && ./venv/bin/python -m pytest          # or: source venv/bin/activate
cd backend && python -m scripts.migrar_esquema     # ALTERs pendientes (idempotente, preserva datos)
cd backend && python -m scripts.seed               # datos de prueba (--reset solo borra lo suyo)
cd backend && uvicorn app.main:app --reload --port 8000

# Frontend
cd frontend && pnpm install
cd frontend && pnpm dev     # http://127.0.0.1:5173
cd frontend && pnpm lint    # oxlint, NOT ESLint
cd frontend && pnpm build
cd frontend && pnpm preview # port 4173, also proxied
```

Swagger: http://localhost:8000/docs. Health: `GET /health`.
Copy `backend/.env.example` → `backend/.env`; `DATABASE_URL`/`SECRET_KEY` are read at **import**
time, so a missing one crashes on startup, not per request.

### Usuarios de prueba (`python -m scripts.seed`)

| rol | documento | contraseña |
|-----|-----------|------------|
| `admin` | `10000001` | `clave123` |
| `supervisor` | `10000002` | `clave123` |
| `tecnico` | `10000003` | `clave123` |
| `ciudadano` | `10000004` | `clave123` |

`seed` is idempotent. `--reset` deletes **only** rows matching the demo name/document filters
(`NOMBRES_CUADRILLA_DEMO`, `DOCUMENTOS_DEMO`, …), never unrelated records.

## Testing: green, but slow — and 70% of the time is one file

- **The suite passes** (246 tests, ~4m40s), but **never run bare `pytest` for a quick check.**
  `tests/test_permisos.py` alone is ~3m14s of that — the other nine files combined are ~80s.
- Cause: `test_matriz_de_permisos` is parametrized **24 endpoints × 4 roles = 96 cases**, and
  `tokens_por_rol` is **function-scoped**, so every case re-hashes and re-verifies 4 bcrypt
  passwords. `pwd_context` sets no explicit rounds, so bcrypt defaults to 12.
- Timings to plan against: `test_auth.py` <1s, `test_medidores.py` ~10s, `test_reclamos.py` ~15s.
  Iterate on one file or narrow with `-k`. Fastest signal is almost always a single file.
- `pytest.ini` already sets `addopts = -q --tb=short` and filters `DeprecationWarning`/`UserWarning`.
- Tests need **no PostgreSQL**. `tests/conftest.py` `setdefault`s `DATABASE_URL` to a temp
  SQLite file and the `db_session` fixture overrides `get_db` with an **in-memory** `sqlite://`
  engine + `StaticPool` + `PRAGMA foreign_keys=ON`.
- Conftest helpers worth reusing instead of rewriting: `headers_admin|supervisor|tecnico|ciudadano`,
  `auth_headers` (alias of admin), `tokens_por_rol`, `reclamo_creado`, `usuario_id`,
  `id_medidor_agua` / `id_medidor_luz`. Use `_crear_usuario_directo` for non-`ciudadano` roles —
  `/auth/register` always forces `ciudadano`.
- In `MATRIZ`, `esperado` is the code when the role *is* allowed, and **`404` is often the correct
  pass**: routes are protected correctly but the fixture resource `9999` doesn't exist. Only a
  `403` expectation that returns `404` signals a real permission gap.
- Naming: `test_<method>_<scenario>_<result>`. Frontend has no test runner (no vitest).

## Architecture (Clean Architecture)

Dependency rule is strict — violations cause import errors:

```
Presentation → Application → Domain ← Infraestructura
```

- `backend/app/Domain/` — dataclasses, ABC repository interfaces, `Exceptions.py`. Imports nothing from the inner layers.
- `backend/app/Application/usecase/<entidad>/` — **directories are singular** (`reclamo/`,
  `usuario/`, `cuadrilla/`, `area_comercial/`, `orden_trabajo/`, `avance/`, `derivacion/`,
  `medidor/`, `normativa/`, `reporte/`; only `plazos/` is plural), while the routers are plural
  (`routes/reclamos.py`). Don't guess the name — `ls` it.
- **File layout inside a usecase dir is not uniform.** `reclamo/` and `usuario/` use one file
  per operation (`crear_reclamo.py`, `asignar_plazo.py`, `resolver_reclamo.py`, …); the rest use
  one `gestionar_<entidad>.py` holding several use cases. Follow the sibling dir you land in.
- `backend/app/Infraestructura/` — ORM models, JWT/bcrypt, concrete repositories. Entity ↔ ORM conversion is inline in each repository.
- `backend/app/Presentation/` — `api/` (app, CORS, routers, exception handlers, lifespan), `routes/`, `schemas/`, `dependencies/`.
- `backend/app/main.py` is a thin wrapper over `Presentation/api/__init__.py`.

### Wiring facts that are easy to get wrong

- **Router registration is manual.** Adding `app/Presentation/routes/<x>.py` requires editing the
  `app.include_router(...)` list in `Presentation/api/__init__.py` **and** the import on its
  line 9. There are 11 routers today. Same for ORM models: the module must be reachable from
  `import app.Infraestructura.database.models` (that import on `api/__init__.py:5` is what
  registers them in `Base.metadata`).
- **Exceptions:** use cases raise `DomainError` subclasses from `Domain/Exceptions.py` (each carries
  its own `status_code`: 400/403/404/409/422). The handler in `Presentation/api/__init__.py` maps
  them to HTTP. **Never raise `HTTPException` from a use case** — but routes and `dependencies/`
  do use it (401/403), and that is fine.
- **DI:** routes take `servicio = Depends(get_service)`, and `get_service()`
  (`Presentation/dependencies/__init__.py:111`) is one function returning a **single dict literal**
  of pre-built use cases. New use cases must be added to that dict, or `servicio["..."]` KeyErrors.
  Do not instantiate repositories in a route, and do not put business logic there.
- `dependencies/__init__.py` defines `INTERNO` (tecnico, supervisor, admin), `GESTION` (supervisor,
  admin), `ADMIN` (admin). Four roles live in `Domain/Entities/catalogos.py::Rol`.

## Gotchas

- **`scripts/migrar_esquema.py` is a hand-maintained allowlist, not an auto-migrator.** Its `main()`
  calls `agregar_columna_si_falta(...)` for exactly four columns (`usuarios.rol`,
  `reclamos.nombre_cuenta`, `reclamos.direccion`, `reclamos.id_medidor`) and also runs
  `crear_tablas_faltantes()`, `agregar_indice_unico_si_falta()` (for the `medidores` unique
  indexes), `completar_medidores_existentes()` and `renumerar_medidores_placeholder()`.
  `Base.metadata.create_all()` creates *new tables* but
  never alters existing ones, so **adding a column to an ORM requires adding a matching
  `agregar_columna_si_falta(...)` call to `main()`** or the column is silently missing. Never
  `drop_all` unless you intend to lose data.
- **Scheduler runs on app startup.** `lifespan` calls `init_scheduler()`, which starts a real
  `BackgroundScheduler` with 5 jobs (interval 1h ×2, 30min, cron daily 23:00, cron monthly 1st).
  It opens its **own** `SessionLocal()`, bypassing `get_db` overrides. `api/__init__.py` imports it as a
  module (`from ... import scheduler as scheduler_module`) on purpose — `conftest.py` monkeypatches
  attributes on that module. Import `init_scheduler` directly and the patch silently fails, the
  real scheduler starts, and it writes to the real DB. `conftest.py` asserts
  `not scheduler.scheduler.running` to catch this.
- **`bcrypt==4.0.1` is pinned** in `requirements.txt`; 5.x breaks passlib.
- **`DATABASE_URL` must use `postgresql+psycopg://`**, not `postgresql://`. Missing `DATABASE_URL`
  or `SECRET_KEY` raises at import time, not at request time. `database/__init__.py` branches on a
  `sqlite` prefix to skip `pool_pre_ping`.
- **Entity dataclasses need `Optional[...]` defaults on every relationship**, or Pydantic raises
  `Field required` on serialization.
- **`ReclamoRepository.update()` copies fields explicitly**, so a new reclamo column is silently
  dropped on update unless it is added to that method too — the ORM and the update path drift apart.
- **A work order cannot be closed without progress.** `estado_orden: "resuelta"` via
  `PUT /seguimiento/ordenes/{id}` and `PUT /reclamos/{id}/resolver` both raise `ConflictoError`
  (409) when the order has no avances. The check lives in `ActualizarOrdenUseCase` /
  `ResolverReclamoUseCase` (shared `SIN_AVANCES` constant in
  `usecase/orden_trabajo/gestionar_orden.py:10`), not in the routes. Resolving a reclamo with
  **no** order is still allowed.
- **`POST /reclamos/` requires `id_medidor`** (`ReclamoCreate.id_medidor: int = Field(gt=0)`,
  `schemas/reclamo.py:19`); it is `Optional` on update and on the response. A hand-rolled reclamo
  payload without it gets a 422 — use the `reclamo_creado` or `id_medidor_agua` fixtures.
- **`medidores` carries two unique constraints** — `(id_usuario, servicio)` and `numero` — so a
  client has at most one meter per service and `numero` is server-generated, never client-supplied.
  Inserting a duplicate in a test fails at the DB level, not in a use case.
- **Two different fields are both called `direccion` in the medidor schemas.** In
  `MedidorCiudadanoResponse` it is `usuarios.direccion` (the account holder's address, a string,
  `""` if unregistered) and is what the ventanilla form prefills. In `MedidorResponse` it is the
  supply's address and **no use case writes it**, so it is always `null`. Don't conflate them.
- **`nombre_cuenta`/`direccion` identify the service account, not the person.** They live on
  `reclamos`, while `telefono`/`email` in `PUT /reclamos/{id}/contacto` are written to
  `usuarios`. Required on create, optional on update, `Optional` in the entity/ORM for
  legacy rows.
- **Repositories must `joinedload()` every relationship** in `get_all` and `get_by_id`; lazy loading
  is off and Pydantic gets `None`.
- **Passwords:** `contraseña` (plain) in requests, `contraseña_hash` (bcrypt) in the DB. Never expose
  the hash. `UsuarioRepository.update()` never writes it — use `actualizar_contrasena()`.
- **Login is OAuth2 form-encoded**, not JSON: `POST /auth/login` with
  `data={"username": <documento>, "password": ...}`. `username` is the *documento*, not an email.
- **`POST /auth/register` is public and always forces `Rol.ciudadano`**, ignoring any `rol` in the
  body. Only `POST /usuarios/` (admin) can mint another role. JWT claims are re-read from the DB on
  every request, so role changes apply immediately.
- **401 vs 403:** 401 = missing/invalid token, 403 = valid token, insufficient role. The frontend
  interceptor (`frontend/src/api/client.js`) clears the token and hard-redirects to `/ingresar` on
  401, and deliberately does *not* log out on 403.

## Frontend specifics

- **The Vite proxy is an explicit allowlist.** `vite.config.js` `RUTAS_API` lists 11 prefixes
  (`/auth`, `/usuarios`, `/medidores`, `/reclamos`, `/normativa`, `/cuadrillas`,
  `/areas-comerciales`, `/seguimiento`, `/plazos`, `/reportes`, `/dashboard`). A new backend
  router is **unreachable** from the frontend until you add it there — there is no catch-all.
  Requests use relative URLs; do not hardcode a base URL in axios.
- `corregirLocation` rewrites absolute `Location` headers back to relative. FastAPI 307-redirects
  `/x` → `/x/`; without this the browser follows it cross-origin and CORS blocks it. Keep it if you
  touch the proxy config.
- `host: '127.0.0.1'` is required in both `server` and `preview` — Vite 8 otherwise binds only
  `[::1]` and `127.0.0.1:5173` refuses connections.
- CORS in `Presentation/api/__init__.py` allows only `http://localhost:5173`. Update both if the
  port changes.
- **Frontend route names deliberately differ from the backend**: login is `/ingresar` (not
  `/login`), and everything authenticated is nested under `/panel/*` with
  `administracion/*` for the CRUD screens. Route guards are the
  `Protegida` / `SoloVisitante` wrappers in `src/App.jsx`; role failures render
  `pages/NoAutorizado.jsx` rather than redirecting. Adding a page means editing the `<Routes>` tree
  in `App.jsx` (there is no file-based routing).
- `pnpm lint` currently exits 0 with **27 pre-existing warnings** (`set-state-in-effect` ×16,
  `only-export-components` ×11). Don't try to zero them out as part of unrelated work. But
  `.oxlintrc.json` sets `react/rules-of-hooks` to **error**, so a real hook violation fails the build.
- **`src/components/Autocompletado.jsx` is the shared search-with-suggestions input** (props:
  `id`, `etiqueta`, `opciones`, `valor`, `onCambiar`, `onElegir`, `maximo`). It is purely
  presentational — the page supplies the options. Reuse it instead of writing another typeahead.
- `dist/` is gitignored. Auth state lives in `localStorage` under `token` and `sesion` (the full
  session JSON, written by `AuthContext.jsx`); the last error uses `error-global` (`client.js`).
  The two files declare these key constants separately — change both if you rename one.

## Reference

- `backend/docs/API.md` — endpoint and permission matrix (964 lines; the authoritative one).
- `backend/docs/ARQUITECTURA.md` — current architecture doc. The root `docs/ARQUITECTURA.md` is a
  35-line older stub; prefer the backend one.
- `frontend/README.md` — fuller frontend walkthrough. `backend/CAMBIOS.md` and
  `frontend/CAMBIOS.md` are change logs of the last big feature pass.
- `docs/SKILLS_PROYECTO.md` (910 lines of generic Kubernetes/malware/red-team skills) and
  `docs/informe-indice.md` / `docs/informe-indices.md` (empty course-report template) are **not
  project guidance**; don't mine them for conventions.
