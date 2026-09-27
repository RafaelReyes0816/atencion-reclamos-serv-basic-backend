# CAMBIOS.md — Backend

Registro técnico de los cambios aplicados al backend (FastAPI + SQLAlchemy + PostgreSQL).

- **Alcance:** 53 archivos modificados, 10 eliminados y 31 creados (93 en total).
- **Balance del diff:** +4842 / −1239 líneas.
- **Estado:** `191 passed` en verde (`pytest`, 202 s, código de salida 0).
- **Arquitectura:** Clean Architecture con la regla de dependencia estricta
  `Presentation → Application → Domain ← Infraestructura`.

---

## 1. Roles y permisos

### `app/Domain/Entities/catalogos.py` (modificado)

Se agregó el enum `Rol` con los cuatro roles del dominio: `ciudadano`, `tecnico`,
`supervisor` y `admin`. Antes el rol era un string libre sin validación en la capa de
dominio.

### `app/Presentation/dependencies/__init__.py` (modificado, +120 líneas)

El archivo pasó de ser un simple `get_db` a ser el **contenedor de dependencias** de la
aplicación:

| Símbolo | Propósito |
|---|---|
| `oauth2_scheme` | `OAuth2PasswordBearer(tokenUrl="auth/login")` |
| `get_current_user` | Valida el token, extrae `sub` y re-consulta el usuario en la BD |
| `require_roles(*roles)` | Fabrica de dependencias; devuelve `403` si el rol no alcanza |
| `get_service` | Contenedor central de use cases (inyección de dependencias) |

Grupos de roles predefinidos:

```python
INTERNO = (Rol.tecnico, Rol.supervisor, Rol.admin)   # catálogos + operación de reclamos
GESTION = (Rol.supervisor, Rol.admin)                # escritura de catálogos, cierre, reportes
ADMIN   = (Rol.admin,)                              # CRUD de usuarios, eliminación de reclamos
```

**Decisión de diseño relevante:** los claims del JWT **no** son la fuente de verdad del
rol. `get_current_user` recupera el usuario desde la base en cada request, así que
cambiar el rol de alguien surte efecto de inmediato, sin necesidad de invalidar tokens.

`get_service` instancia los 9 repositorios una sola vez y expone **48 use cases** en un
diccionario. Las rutas dependen de este dict mediante `Depends(get_service)`; ninguna
instancia repositorios por su cuenta.

---

## 2. Errores de dominio

### `app/Domain/Exceptions.py` (nuevo)

Jerarquía de errores de negocio con su código HTTP asociado:

| Excepción | `status_code` | Uso |
|---|---|---|
| `DomainError` | 400 | Clase base |
| `NoEncontradoError` | 404 | Entidad inexistente |
| `ConflictoError` | 409 | Estado incompatible |
| `DuplicadoError` | 400 | Violación de clave única |
| `ValidacionError` | 422 | Reglas de negocio incumplidas |
| `SinPermisosError` | 403 | Rol insuficiente |

### `app/main.py` (modificado)

Se agregó el manejador global que traduce estas excepciones a respuestas HTTP:

```python
@app.exception_handler(DomainError)
async def manejar_error_dominio(request: Request, exc: DomainError):
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.mensaje})
```

**Qué corrige:** antes los use cases lanzaban `HTTPException` de FastAPI. Eso obligaba a
`Application` a importar de `Presentation` e invertía la regla de dependencia de Clean
Architecture. Ahora los use cases lanzan errores de dominio puros y es `main.py` quien
traduce a HTTP.

---

## 3. Reorganización de use cases

Se aplicó la convención de **una clase por operación, agrupadas por entidad** en un
archivo `gestionar_<entidad>.py`. Esto sustituyó a los use cases sueltos, que además
estaban mal nombrados: `resolver_reclamo_tecnico` y `resolver_reclamo_comercial` se
unificaron en un solo `resolver_reclamo`.

### 9 use cases eliminados

```
app/Application/usecase/reclamo/asignar_cuadrilla.py
app/Application/usecase/reclamo/cerrar_reclamo.py
app/Application/usecase/reclamo/derivar_comercial.py
app/Application/usecase/reclamo/determinar_urgencia.py
app/Application/usecase/reclamo/determinar_via_atencion.py
app/Application/usecase/reclamo/registrar_avance.py
app/Application/usecase/reclamo/resolver_reclamo_comercial.py
app/Application/usecase/reclamo/resolver_reclamo_tecnico.py
app/Application/usecase/reclamo/verificar_cierre.py
```

### 11 use cases nuevos

```
app/Application/usecase/area_comercial/gestionar_area.py
app/Application/usecase/avance/gestionar_avance.py
app/Application/usecase/cuadrilla/gestionar_cuadrilla.py
app/Application/usecase/derivacion/gestionar_derivacion.py
app/Application/usecase/normativa/gestionar_normativa.py
app/Application/usecase/orden_trabajo/gestionar_orden.py
app/Application/usecase/reclamo/actualizar_contacto.py
app/Application/usecase/reclamo/resolver_reclamo.py
app/Application/usecase/reporte/gestionar_reporte.py
app/Application/usecase/reporte/obtener_dashboard.py
app/Application/usecase/usuario/cambiar_contrasena.py
```

### `app/Application/__init__.py` (nuevo)

Falta hacer que `Application` sea un paquete importable. Sin este archivo los imports de
los use cases fallaban de forma intermitente según el directorio de trabajo.

---

## 4. Endpoint nuevo: dashboard

### `app/Presentation/routes/dashboard.py` (nuevo)

`GET /dashboard/` responde con `DashboardResponse` y está restringido a `GESTION`
(supervisor y admin). Agrega en una sola llamada las métricas que la aplicación necesita:
totales de reclamos por estado, conteo de usuarios, cumplimiento de plazos y alertas de
vencimiento.

**Estos números son la fuente de verdad del panel.** El frontend los muestra como
tarjetas y, al pulsarlas, lleva a la lista de reclamos con el filtro equivalente, de
modo que el valor de la tarjeta y el número de filas siempre coinciden. Los criterios
exactos son:

| Métrica | Cálculo |
|---|---|
| `pendientes` | `por_estado["registrado"] + por_estado["clasificado"]` |
| `en_atencion` | `por_estado["en_atencion_tecnica"] + por_estado["en_atencion_comercial"]` |
| `resueltos` | `por_estado["resuelto"]` |
| `cerrados` | `por_estado["cerrado"]` |
| `vencidos` | `get_vencidos(hoy)`: `fecha_tope < hoy AND estado != "cerrado"` |
| `proximos_vencer` | `get_por_vencer(hoy)`: `fecha_tope >= hoy AND estado NOT IN ("cerrado", "registrado")` |
| `criticos` | `get_criticos()`: `urgencia == "critica" AND estado NOT IN ("cerrado", "resuelto")` |

> Si se cambia alguno de estos criterios hay que actualizarlos también en
> `src/pages/Dashboard.jsx` y `src/pages/Reclamos/ListaReclamos.jsx` del frontend, o el
> panel mostrará una cifra y la lista otra.

### `app/Presentation/schemas/dashboard.py` (nuevo)

Contratos Pydantic de entrada y salida, siguiendo el estilo del resto de schemas
(separación `XxxCreate` / `XxxResponse`).

---

## 5. Cambio de contraseña

### `app/Application/usecase/usuario/cambiar_contrasena.py` (nuevo)

`CambiarContrasenaUseCase` valida `contrasena_actual` antes de permitir el cambio y
lanza `ValidacionError` si no coincide.

### `app/Infraestructura/repositories/usuario_repository.py` (modificado, +44 líneas)

Se agregó `actualizar_contrasena()`, que sí escribe `contraseña_hash`.

> **Regla importante:** `UsuarioRepository.update()` **nunca** escribe el hash. Si se
> pasa `contraseña` en un `PUT /usuarios/{id}`, el campo se ignora. El hash solo cambia
> por `PUT /usuarios/{id}/contrasena`. Esto evita que un hash bcrypt se regenere por
> accidente en cada actualización de perfil.

---

## 6. Migración de esquema y seed

Ambos scripts son **idempotentes** y se pueden ejecutar tantas veces como haga falta.

### `scripts/migrar_esquema.py` (nuevo)

`Base.metadata.create_all()` **no altera tablas que ya existen**, así que agregar una
columna al ORM no se refleja en una base ya creada. Este script aplica los `ALTER TABLE`
pendientes:

```python
agregar_columna_si_falta("usuarios", "rol", "rol VARCHAR(20) NOT NULL DEFAULT 'ciudadano'")
```

Verifica primero si la tabla y la columna existen, y solo entonces aplica el `ALTER`.
**Nunca usa `drop_all`**, por lo que preserva los datos.

### `scripts/seed.py` (nuevo, 10.3 KB)

Carga datos de prueba: 4 usuarios (uno por rol), 6 normas de plazo, 3 cuadrillas,
2 áreas comerciales y 5 reclamos.

```bash
python -m scripts.seed            # crea solo lo que falte
python -m scripts.seed --reset    # borra SOLO lo de este script y recarga
```

El `--reset` identifica sus propios registros por valores conocidos (documentos
`1000000X`, nombres de cuadrilla y de área) y **nunca toca registros ajenos**, de modo
que es seguro incluso en una base con datos reales.

---

## 7. Suite de tests

### `tests/` (nuevo) — 10 archivos, 191 tests

```
conftest.py                            fixtures, cliente de test, monkeypatch
test_auth.py                           login, registro, token
test_usuarios.py                       CRUD, roles, cambio de contraseña
test_permisos.py                       matriz 401/403 por rol
test_reclamos.py                       ciclo de vida completo del reclamo
test_seguimiento.py                    órdenes, avances, derivaciones
test_normativa.py                      CRUD y búsqueda de norma vigente
test_cuadrillas_areas.py               catálogos operativos
test_reportes_plazos_dashboard.py      reportes, .xlsx, agregados del dashboard
test_configuracion.py                  health, raíz, CORS
```

Convención de nombres: `test_<método>_<escenario>_<resultado>`.

### `pytest.ini` (nuevo)

```ini
[pytest]
testpaths = tests
addopts = -q --tb=short
filterwarnings =
    ignore::DeprecationWarning
    ignore::UserWarning
```

### `requirements.txt` (modificado)

Se agregaron las dependencias de testing: `pytest` y `httpx`.

---

## 8. Scheduler aislado

### `app/main.py` (modificado)

El scheduler se importa **como módulo**, no como función:

```python
from app.Infraestructura.tasks import scheduler as scheduler_module

@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    scheduler_module.init_scheduler()
    yield
    scheduler_module.shutdown_scheduler()
```

**Por qué importa tanto:** si se escribiera `from ... import init_scheduler`, el
monkeypatch de `conftest.py` dejaría de funcionar y el `BackgroundScheduler` real
arrancaría durante los tests, leyendo y escribiendo en la base de datos de desarrollo.
Al patchear el atributo del módulo, el test intercepta la llamada sin efectos
colaterales.

---

## 9. CORS

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

> **Atención:** el origen permitido es `http://localhost:5173`, **no**
> `http://127.0.0.1:5173`; para el navegador son orígenes distintos. Por eso el frontend
> debe consumir la API **a través del proxy de Vite** con URLs relativas, y nunca llamar
> al backend en el puerto `8000` directamente. Ver `CAMBIOS.md` del frontend, sección
> "Bugs corregidos".

---

## 10. Dependencias y secretos

### `requirements.txt`

```diff
 pydantic
+pydantic[email]
+email-validator
```

Los schemas usan `EmailStr`, que requiere el extra de pydantic y `email-validator`.

> `bcrypt==4.0.1` está pineado a propósito: las versiones 5.x rompen la compatibilidad
> con `passlib`.

### `.gitignore` (modificado, +2 líneas)

Se añadió `.env` para que el archivo de secretos nunca entre al repositorio.

### `.env.example` (modificado, +41 líneas)

Plantilla ampliada y saneada: sin valores reales, con la lista de variables necesarias y
comentarios de uso.

### `SECRET_KEY`

Rotada. La anterior estaba en el historial de git, por lo que cualquier token emitido
con ella era comprometible.

---

## 11. Repositorios

Archivos modificados: `reclamo`, `usuario`, `normativa_plazo`, `orden_trabajo`,
`derivacion_comercial`, `cuadrilla`, `area_comercial` y `reporte`.

Cambios recurrentes aplicados:

- **`joinedload()` en todas las relaciones** de `get_all` y `get_by_id`. Sin esto,
  SQLAlchemy no carga las relaciones y los objetos llegan como `None`, lo que hace que
  Pydantic falle al serializar.
- **Filtros por rol** en `listar_reclamos`: un `ciudadano` solo ve sus propios reclamos;
  los roles internos ven todos.
- **`actualizar_contrasena()`** separado de `update()` (ver sección 5).
- **`Optional[object]`** en las relaciones de las entidades dataclass del dominio, para
  que Pydantic no exija el campo al serializar.

---

## 12. Documentación

| Archivo | Cambio |
|---|---|
| `docs/API.md` | Reescrito: +435 / −289 líneas. Matriz de permisos por endpoint, esquemas y ejemplos |
| `docs/ARQUITECTURA.md` | +97 / −12 líneas: capa de errores, DI, reorganización de use cases |
| `AGENTS.md` | +43 / −6 líneas: comandos, gotchas de bcrypt, scheduler, `joinedload`, migraciones |

---

## 13. Archivos eliminados

| Archivo | Motivo |
|---|---|
| `app/Presentation/api/__init__.py` | Paquete vacío sin ningún módulo importable |
| 9 use cases sueltos de reclamo | Reemplazados por la agrupación `gestionar_*.py` (sección 3) |

---

## 14. Limpieza de datos de prueba

Se eliminaron de la base de datos los registros sobrantes de pruebas E2E que no
pertenecían al seed:

- **6 usuarios** `ciudadano` de prueba: `Usuario Demo`, `Tecnico Prueba`, dos
  `E2E Usuario`, `Usuario Prueba` y otro.
- **2 reclamos** derivados de ellos, con sus **2 órdenes de trabajo**, **1 avance** y
  **1 derivación comercial**.

El borrado se hizo en el orden inverso de la cadena de dependencias verificada en el
esquema: `avances` → `ordenes_trabajo` → `derivaciones_comerciales` → `reclamos` →
`usuarios`.

**Estado final de la base:** 4 usuarios (los del seed), 5 reclamos, 0 órdenes de
trabajo.

> Los 4 usuarios del seed (`10000001` a `10000004`) se conservan intencionalmente: son
> las únicas cuentas con las que se puede iniciar sesión en una base limpia.
