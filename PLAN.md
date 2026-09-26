# Plan de Desarrollo — Sistema de Atención de Reclamos de Servicios Básicos

## Información General

- **Proyecto:** Sistema de Atención de Reclamos de Servicios Básicos (Agua y Luz)
- **Stack Backend:** Python, FastAPI, SQLAlchemy, PostgreSQL, JWT, APScheduler
- **Stack Frontend:** React 19, Vite 8, React Router v7, Axios, pnpm
- **Repos:** Repos separados (backend y frontend), pero en la misma carpeta de trabajo
- **Entorno:** Solo local (sin despliegue)

## Repositorios

| Repo | URL |
|------|-----|
| Backend | https://github.com/RafaelReyes0816/atencion-reclamos-serv-basic-backend.git |
| Frontend | https://github.com/RafaelReyes0816/atencion-reclamos-serv-basic-frontend.git |

## Estructura de Carpetas

```
servicio-atencion-serv-basicos/
├── backend/          # Repo separado — FastAPI
│   ├── app/
│   ├── requirements.txt
│   └── ...
├── frontend/         # Repo separado — React + Vite
│   ├── src/
│   ├── package.json
│   └── ...
└── docs/             # Documentación compartida
    ├── Plantilla-FastAPI.md
    ├── SKILLS_PROYECTO.md
    └── PLAN.md       # Este archivo
```

---

## División de Responsabilidades

| Developer | Responsabilidad Principal | Repos |
|-----------|--------------------------|-------|
| **Dev A** | Backend completo + API | `backend/` |
| **Dev B** | Frontend completo + UI | `frontend/` |

### Puntos de Integración

- **Acuerdo 1:** Dev A documenta cada endpoint en un archivo `docs/API.md` dentro del repo backend (method, path, request body, response, auth requerida)
- **Acuerdo 2:** Dev B consume la API usando las especificaciones de `API.md`
- **Acuerdo 3:** Ambos usan el mismo formato de respuesta JSON: `{ "data": ..., "message": "...", "status": "success"|"error" }`
- **Acuerdo 4:** Puerto backend: `8000`, Puerto frontend: `5173`, proxy configurado en `vite.config.js`

---

## Fase 0: Configuración Inicial (Ambos)

### Dev A — Backend

| # | Tarea | Dependencia | Estado |
|---|-------|-------------|--------|
| A.0.1 | Crear repo `backend/` con estructura Clean Architecture | — | ☐ |
| A.0.2 | Crear `requirements.txt` con todas las dependencias | — | ☐ |
| A.0.3 | Crear `.env.example` con DATABASE_URL, SECRET_KEY | — | ☐ |
| A.0.4 | Configurar `app/Infraestructura/database/__init__.py` (engine, SessionLocal, Base, get_db) | A.0.2 | ☐ |
| A.0.5 | Configurar `app/main.py` con FastAPI app, CORS, lifespan | A.0.4 | ☐ |
| A.0.6 | Crear `app/Infraestructura/security/` (JWT + bcrypt helpers) | A.0.2 | ☐ |
| A.0.7 | Verificar que el servidor arranca: `uvicorn app.main:app --reload` | A.0.5 | ☐ |

### Dev B — Frontend

| # | Tarea | Dependencia | Estado |
|---|-------|-------------|--------|
| B.0.1 | Crear repo `frontend/` con Vite + React 19 | — | ☐ |
| B.0.2 | `pnpm create vite frontend -- --template react` | — | ☐ |
| B.0.3 | Instalar dependencias: react-router-dom, axios | B.0.2 | ☐ |
| B.0.4 | Configurar `vite.config.js` con proxy al backend (`/auth`, `/usuarios`, `/reclamos`, etc.) | B.0.2 | ☐ |
| B.0.5 | Configurar ESLint flat config (`eslint.config.js`) | B.0.2 | ☐ |
| B.0.6 | Crear estructura de carpetas: `src/api/`, `src/context/`, `src/pages/`, `src/components/` | B.0.2 | ☐ |
| B.0.7 | Crear `src/api/client.js` con instancia Axios + helper `token()` | B.0.6 | ☐ |
| B.0.8 | Verificar que el dev server arranca: `pnpm dev` | B.0.3 | ☐ |

---

## Fase 1: Modelado de Datos y Auth (Base)

### Dev A — Backend

| # | Tarea | Dependencia | Estado |
|---|-------|-------------|--------|
| A.1.1 | Crear catálogos enum: `app/Domain/Entities/catalogos.py` | A.0.5 | ☐ |
| A.1.2 | Crear entity `Usuario`: `app/Domain/Entities/usuario.py` | A.1.1 | ☐ |
| A.1.3 | Crear entity `Reclamo`: `app/Domain/Entities/reclamo.py` | A.1.1 | ☐ |
| A.1.4 | Crear entity `NormativaPlazo`: `app/Domain/Entities/normativa_plazo.py` | A.1.1 | ☐ |
| A.1.5 | Crear entity `OrdenTrabajo`: `app/Domain/Entities/orden_trabajo.py` | A.1.1 | ☐ |
| A.1.6 | Crear entity `Avance`: `app/Domain/Entities/avance.py` | A.1.1 | ☐ |
| A.1.7 | Crear entity `DerivacionComercial`: `app/Domain/Entities/derivacion_comercial.py` | A.1.1 | ☐ |
| A.1.8 | Crear entity `Cuadrilla`: `app/Domain/Entities/cuadrilla.py` | A.1.1 | ☐ |
| A.1.9 | Crear entity `AreaComercial`: `app/Domain/Entities/area_comercial.py` | A.1.1 | ☐ |
| A.1.10 | Crear entity `Reporte`: `app/Domain/Entities/reporte.py` | A.1.1 | ☐ |
| A.1.11 | Crear modelos SQLAlchemy: `app/Infraestructura/database/models/` (uno por entidad) | A.1.1–A.1.10 | ☐ |
| A.1.12 | Crear interfaces ABC: `app/Domain/Repositories/` (una por entidad) | A.1.1–A.1.10 | ☐ |
| A.1.13 | Crear repositorios concretos: `app/Infraestructura/repositories/` | A.1.12 | ☐ |
| A.1.14 | Crear schemas Pydantic: `app/Presentation/schemas/` (request + response) | A.1.1–A.1.10 | ☐ |
| A.1.15 | Crear router auth: login + register con JWT | A.0.6, A.1.2 | ☐ |
| A.1.16 | Crear dependencias: `get_current_user`, `get_service(db)` | A.0.6, A.1.13 | ☐ |
| A.1.17 | Crear `docs/API.md` con especificación de auth endpoints | A.1.15 | ☐ |
| A.1.18 | Ejecutar migración inicial (create_all) y verificar tablas | A.1.11 | ☐ |

### Dev B — Frontend

| # | Tarea | Dependencia | Estado |
|---|-------|-------------|--------|
| B.1.1 | Crear `src/context/AuthContext.jsx` (token, login, logout, registrar) | B.0.7 | ☐ |
| B.1.2 | Crear `src/pages/Login.jsx` (formulario email/password) | B.1.1 | ☐ |
| B.1.3 | Configurar `src/App.jsx` con rutas protegidas (React Router) | B.1.1 | ☐ |
| B.1.4 | Crear componente `ProtectedRoute.jsx` (verifica token, redirige a /) | B.1.1 | ☐ |
| B.1.5 | Crear `src/main.jsx` con AuthProvider envolviendo la app | B.1.1, B.1.3 | ☐ |
| B.1.6 | Estilos base en `src/index.css` (fuentes, colores, layout) | B.0.2 | ☐ |
| B.1.7 | Verificar login funcional contra backend (cuando A.1.15 esté listo) | B.1.2, A.1.15 | ☐ |

---

## Fase 2: P1 — Registrar y Consultar Reclamos

### Dev A — Backend

| # | Tarea | Dependencia | Estado |
|---|-------|-------------|--------|
| A.2.1 | Use Case: `ValidarReclamoUseCase` (P1.1.1) | A.1.12 | ☐ |
| A.2.2 | Use Case: `RegistrarReclamoUseCase` (P1.1.2 + P1.1.3) | A.2.1 | ☐ |
| A.2.3 | Use Case: `EmitirComprobanteUseCase` (P1.2) | A.2.2 | ☐ |
| A.2.4 | Use Case: `ConsultarEstadoUseCase` (P1.3) | A.1.13 | ☐ |
| A.2.5 | Use Case: `ActualizarContactoUseCase` (P1.4) | A.1.13 | ☐ |
| A.2.6 | Router reclamos: POST `/reclamos` (crear) | A.2.2 | ☐ |
| A.2.7 | Router reclamos: GET `/reclamos` (listar con filtros) | A.1.13 | ☐ |
| A.2.8 | Router reclamos: GET `/reclamos/{id}` (detalle) | A.1.13 | ☐ |
| A.2.9 | Router reclamos: GET `/reclamos/{id}/comprobante` | A.2.3 | ☐ |
| A.2.10 | Router reclamos: GET `/reclamos/estado/{id_o_doc}` | A.2.4 | ☐ |
| A.2.11 | Router reclamos: PUT `/reclamos/{id}/contacto` | A.2.5 | ☐ |
| A.2.12 | Documentar endpoints P1 en `docs/API.md` | A.2.6–A.2.11 | ☐ |

### Dev B — Frontend

| # | Tarea | Dependencia | Estado |
|---|-------|-------------|--------|
| B.2.1 | Página `NuevoReclamo.jsx`: formulario con validación | B.1.3 | ☐ |
| B.2.2 | Página `ListaReclamos.jsx`: tabla con paginación y filtros | B.1.3 | ☐ |
| B.2.3 | Página `DetalleReclamo.jsx`: vista completa del reclamo | B.1.3 | ☐ |
| B.2.4 | Página `ConsultaEstado.jsx`: búsqueda por id o documento | B.1.3 | ☐ |
| B.2.5 | Servicio `reclamos.js` en `src/api/` (CRUD + comprobante) | B.0.7 | ☐ |
| B.2.6 | Navegación principal (sidebar o navbar) | B.1.6 | ☐ |
| B.2.7 | Integrar con backend (cuando A.2.6–A.2.11 estén listos) | B.2.1–B.2.6, A.2.6–A.2.11 | ☐ |

---

## Fase 3: P2 — Clasificar y Asignar Reclamos

### Dev A — Backend

| # | Tarea | Dependencia | Estado |
|---|-------|-------------|--------|
| A.3.1 | Use Case: `DeterminarUrgenciaUseCase` (P2.1.2 — matriz) | A.1.12 | ☐ |
| A.3.2 | Use Case: `DeterminarViaAtencionUseCase` (P2.1.3) | A.3.1 | ☐ |
| A.3.3 | Use Case: `AsignarPlazoUseCase` (P2.2.1 + P2.2.2 + P2.2.3) | A.3.1 | ☐ |
| A.3.4 | Use Case: `AsignarCuadrillaUseCase` (P2.3) | A.3.3 | ☐ |
| A.3.5 | Use Case: `DerivarComercialUseCase` (P2.4) | A.3.3 | ☐ |
| A.3.6 | Router normativa: CRUD completo | A.1.13 | ☐ |
| A.3.7 | Router cuadrillas: CRUD completo | A.1.13 | ☐ |
| A.3.8 | Router áreas comerciales: CRUD completo | A.1.13 | ☐ |
| A.3.9 | Router reclamos: PUT `/reclamos/{id}/clasificar` | A.3.1–A.3.5 | ☐ |
| A.3.10 | Router reclamos: PUT `/reclamos/{id}/asignar-plazo` | A.3.3 | ☐ |
| A.3.11 | Router ordenes-trabajo: CRUD completo | A.1.13 | ☐ |
| A.3.12 | Router derivaciones: POST + GET | A.1.13 | ☐ |
| A.3.13 | Documentar endpoints P2 en `docs/API.md` | A.3.6–A.3.12 | ☐ |

### Dev B — Frontend

| # | Tarea | Dependencia | Estado |
|---|-------|-------------|--------|
| B.3.1 | Página `ClasificarReclamo.jsx`: formulario servicio/categoría/urgencia | B.1.3 | ☐ |
| B.3.2 | Página `Cuadrillas.jsx`: CRUD de cuadrillas | B.1.3 | ☐ |
| B.3.3 | Página `AreasComerciales.jsx`: CRUD de áreas | B.1.3 | ☐ |
| B.3.4 | Página `Normativa.jsx`: CRUD de normativa de plazos | B.1.3 | ☐ |
| B.3.5 | Servicios API: `clasificacion.js`, `cuadrillas.js`, `areasComerciales.js`, `normativa.js` | B.0.7 | ☐ |
| B.3.6 | Integrar clasificación en DetalleReclamo (botón "Clasificar") | B.2.3, A.3.9 | ☐ |
| B.3.7 | Integrar CRUD de administración en navegación | B.2.6, B.3.2–B.3.4 | ☐ |

---

## Fase 4: P3 — Seguir y Cerrar Reclamos

### Dev A — Backend

| # | Tarea | Dependencia | Estado |
|---|-------|-------------|--------|
| A.4.1 | Use Case: `RegistrarAvanceUseCase` (P3.1) | A.1.12 | ☐ |
| A.4.2 | Use Case: `ResolverReclamoTecnicoUseCase` (P3.2) | A.4.1 | ☐ |
| A.4.3 | Use Case: `ResolverReclamoComercialUseCase` (P3.3) | A.1.13 | ☐ |
| A.4.4 | Use Case: `VerificarCierreUseCase` (P3.4.1) | A.4.2, A.4.3 | ☐ |
| A.4.5 | Use Case: `CerrarReclamoUseCase` (P3.4.2) | A.4.4 | ☐ |
| A.4.6 | Use Case: `NotificarUsuarioUseCase` (P3.5) | A.4.5 | ☐ |
| A.4.7 | Router avances: GET `/{id_orden}`, POST `/` | A.4.1 | ☐ |
| A.4.8 | Router ordenes-trabajo: PUT `/{id}` (actualizar estado) | A.4.2 | ☐ |
| A.4.9 | Router derivaciones: PUT `/{id}` (resolver) | A.4.3 | ☐ |
| A.4.10 | Router reclamos: PUT `/{id}/resolver` (técnico/comercial) | A.4.2, A.4.3 | ☐ |
| A.4.11 | Router reclamos: PUT `/{id}/cerrar` | A.4.5 | ☐ |
| A.4.12 | Documentar endpoints P3 en `docs/API.md` | A.4.7–A.4.11 | ☐ |

### Dev B — Frontend

| # | Tarea | Dependencia | Estado |
|---|-------|-------------|--------|
| B.4.1 | Página `AvancesTrabajo.jsx`: formulario de avances por orden | B.1.3 | ☐ |
| B.4.2 | Página `ResolverReclamo.jsx`: formulario resolución técnica/comercial | B.1.3 | ☐ |
| B.4.3 | Agregar botón "Registrar Avance" en DetalleReclamo (si es técnico) | B.2.3 | ☐ |
| B.4.4 | Agregar botón "Resolver" en DetalleReclamo (si está en atención) | B.2.3 | ☐ |
| B.4.5 | Agregar botón "Cerrar" en DetalleReclamo (si está resuelto) | B.2.3 | ☐ |
| B.4.6 | Servicios API: `avances.js`, `segimiento.js` | B.0.7 | ☐ |
| B.4.7 | Integrar con backend (cuando A.4.7–A.4.11 estén listos) | B.4.1–B.4.6, A.4.7–A.4.11 | ☐ |

---

## Fase 5: P4 — Vigilar Plazos Regulatorios

### Dev A — Backend

| # | Tarea | Dependencia | Estado |
|---|-------|-------------|--------|
| A.5.1 | Use Case: `DetectarVencimientoProximoUseCase` (P4.1) | A.1.12 | ☐ |
| A.5.2 | Use Case: `DetectarReclamoVencidoUseCase` (P4.2) | A.1.12 | ☐ |
| A.5.3 | Use Case: `DetectarReclamoCriticoUseCase` (P4.3) | A.1.12 | ☐ |
| A.5.4 | Configurar APScheduler en `app/Infraestructura/tasks/scheduler.py` | A.5.1–A.5.3 | ☐ |
| A.5.5 | Integrar scheduler en `main.py` (lifespan) | A.5.4 | ☐ |
| A.5.6 | Router plazos: POST triggers manuales (verificar-vencimientos, vencidos, críticos) | A.5.1–A.5.3 | ☐ |
| A.5.7 | Documentar endpoints P4 en `docs/API.md` | A.5.6 | ☐ |

### Dev B — Frontend

| # | Tarea | Dependencia | Estado |
|---|-------|-------------|--------|
| B.5.1 | Página `Plazos.jsx`: botones trigger + historial de alertas | B.1.3 | ☐ |
| B.5.2 | Dashboard: alertas de vencimiento próximo, vencidos, críticos | B.1.3 | ☐ |
| B.5.3 | Servicio API: `plazos.js` | B.0.7 | ☐ |
| B.5.4 | Integrar con backend (cuando A.5.6 esté listo) | B.5.1–B.5.3, A.5.6 | ☐ |

---

## Fase 6: P5 — Generar Reportes

### Dev A — Backend

| # | Tarea | Dependencia | Estado |
|---|-------|-------------|--------|
| A.6.1 | Use Case: `GenerarReporteDiarioUseCase` (P5.1) | A.1.12 | ☐ |
| A.6.2 | Use Case: `GenerarReporteMensualUseCase` (P5.2) | A.1.12 | ☐ |
| A.6.3 | Función de exportación Excel con `openpyxl` | A.6.1, A.6.2 | ☐ |
| A.6.4 | Router reportes: GET `/reportes`, POST `/reportes/diario`, POST `/reportes/mensual`, GET `/reportes/{id}/excel` | A.6.1–A.6.3 | ☐ |
| A.6.5 | Integrar reportes en APScheduler (cron diario + mensual) | A.5.4, A.6.1, A.6.2 | ☐ |
| A.6.6 | Documentar endpoints P5 en `docs/API.md` | A.6.4 | ☐ |

### Dev B — Frontend

| # | Tarea | Dependencia | Estado |
|---|-------|-------------|--------|
| B.6.1 | Página `Reportes.jsx`: botones generar + tabla de reportes | B.1.3 | ☐ |
| B.6.2 | Botón "Descargar Excel" para cada reporte | B.6.1 | ☐ |
| B.6.3 | Servicio API: `reportes.js` | B.0.7 | ☐ |
| B.6.4 | Integrar con backend (cuando A.6.4 esté listo) | B.6.1–B.6.3, A.6.4 | ☐ |

---

## Fase 7: Dashboard y Pulido Final (Ambos)

### Dev A — Backend

| # | Tarea | Dependencia | Estado |
|---|-------|-------------|--------|
| A.7.1 | Router dashboard: GET `/dashboard` (resumen de métricas) | A.2.7 | ☐ |
| A.7.2 | Documentar todos los endpoints finales en `docs/API.md` | Todas | ☐ |
| A.7.3 | Verificar que todos los use cases tienen cobertura | Todas | ☐ |
| A.7.4 | Revisar manejo de errores y validaciones | Todas | ☐ |

### Dev B — Frontend

| # | Tarea | Dependencia | Estado |
|---|-------|-------------|--------|
| B.7.1 | Página `Dashboard.jsx`: métricas, gráficos, alertas | B.1.3 | ☐ |
| B.7.2 | Pulido de estilos y responsive | B.1.6 | ☐ |
| B.7.3 | Verificar que toda la navegación funciona | Todas | ☐ |
| B.7.4 | Verificar que no hay errores en consola | Todas | ☐ |
| B.7.5 | Ejecutar `pnpm lint` y corregir warnings | Todas | ☐ |

---

## Fase 8: Pruebas y Validación (Ambos)

### Dev A — Backend

| # | Tarea | Dependencia | Estado |
|---|-------|-------------|--------|
| A.8.1 | Probar flujo completo: registro → clasificación → asignación → avances → resolución → cierre | Todas | ☐ |
| A.8.2 | Probar P4: verificar que scheduler detecta vencimientos/vencidos/críticos | A.5.5 | ☐ |
| A.8.3 | Probar P5: generar reporte diario y mensual, descargar Excel | A.6.4 | ☐ |
| A.8.4 | Probar autenticación: login, token, endpoints protegidos | A.1.15 | ☐ |
| A.8.5 | Probar validaciones: datos faltantes, catálogos inválidos, estados incorrectos | Todas | ☐ |

### Dev B — Frontend

| # | Tarea | Dependencia | Estado |
|---|-------|-------------|--------|
| B.8.1 | Probar flujo completo desde la UI: crear reclamo → clasificar → asignar → avances → cerrar | Todas | ☐ |
| B.8.2 | Probar que el dashboard muestra métricas correctas | B.7.1 | ☐ |
| B.8.3 | Probar reportes: generar y descargar Excel | B.6.1 | ☐ |
| B.8.4 | Probar navegación: todas las rutas accesibles | B.7.3 | ☐ |
| B.8.5 | Probar autenticación: login, redirección, logout | B.1.2 | ☐ |

---

## Cronograma Estimado

| Fase | Dev A (Backend) | Dev B (Frontend) | Días |
|------|-----------------|-------------------|------|
| Fase 0 | Configuración inicial | Configuración inicial | 1 |
| Fase 1 | Modelado + Auth | Auth UI | 2 |
| Fase 2 | P1: Registrar/Consultar | P1: Formularios UI | 2 |
| Fase 3 | P2: Clasificar/Asignar | P2: Clasificación + Admin UI | 2 |
| Fase 4 | P3: Seguir/Cerrar | P3: Seguimiento UI | 2 |
| Fase 5 | P4: Vigilar Plazos | P4: Plazos UI | 1 |
| Fase 6 | P5: Reportes | P5: Reportes UI | 1 |
| Fase 7 | Dashboard + Pulido | Dashboard + Pulido | 1 |
| Fase 8 | Pruebas | Pruebas | 1 |
| **Total** | | | **~13 días** |

---

## Dependencias Críticas

```
A.0.5 (main.py) → B.0.4 (proxy config)
A.1.15 (auth router) → B.1.7 (login funcional)
A.1.17 (API.md auth) → B.2.5 (servicios API)
A.2.6–A.2.11 (P1 endpoints) → B.2.7 (integración P1)
A.3.6–A.3.12 (P2 endpoints) → B.3.7 (integración P2)
A.4.7–A.4.11 (P3 endpoints) → B.4.7 (integración P3)
A.5.6 (P4 endpoints) → B.5.4 (integración P4)
A.6.4 (P5 endpoints) → B.6.4 (integración P5)
```

---

## Comunicación

- **Reunión diaria:** 15 min al inicio del día para sincronizar avances
- **Bloqueos:** Si un dev depende de algo del otro, levantar inmediatamente
- **Integration points:** Cada fase tiene un punto de integración claro donde ambos deben coordinarse
- **API.md:** Dev A lo mantiene actualizado; Dev B lo usa como fuente de verdad

---

## Correciones Realizadas

| Fecha | Corrección | Detalle |
|-------|------------|---------|
| 2026-09-26 | Campo contraseña | Se agregó `contraseña` (plain) en request y `contraseña_hash` (bcrypt) en DB |
| 2026-09-26 | bcrypt version | Fijar `bcrypt==4.0.1` — versiones 5.x rompen compatibilidad con passlib |
| 2026-09-26 | SQLite support | `database/__init__.py` detecta SQLite y desactiva `pool_pre_ping` |
| 2026-09-26 | Login username | `username` en login = campo `documento` del usuario |
| 2026-09-26 | Tablas DB | Si cambia schema, ejecutar `Base.metadata.drop_all()` + `create_all()` |

---

## Checklist Final

- [ ] Backend: Todos los endpoints documentados en `docs/API.md`
- [ ] Backend: Flujo completo funciona (registro → cierre)
- [ ] Backend: P4 ejecuta correctamente (scheduler + manual)
- [ ] Backend: P5 genera reportes Excel/CSV
- [ ] Frontend: Todas las páginas navegables
- [ ] Frontend: CRUD de administración funcional
- [ ] Frontend: Dashboard muestra métricas
- [ ] Frontend: Sin errores en consola
- [ ] Frontend: `pnpm lint` sin warnings
- [ ] Ambos: Integración verificada end-to-end
