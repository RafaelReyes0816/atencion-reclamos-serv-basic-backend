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

**Estado final de la base:** 4 usuarios (los del seed), 13 reclamos, 2 ordenes de
trabajo, 1 derivacion comercial.

> Los 4 usuarios del seed (`10000001` a `10000004`) se conservan intencionalmente: son
> las únicas cuentas con las que se puede iniciar sesión en una base limpia.

---

## 15. Maquina de estados del reclamo (transiciones automaticas)

### `app/Application/usecase/orden_trabajo/gestionar_orden.py` (modificado)

- `CrearOrdenUseCase`: ahora cambia el estado del reclamo a `en_atencion_tecnica` al crear la orden.
- `ActualizarOrdenUseCase`: ahora cambia el estado del reclamo a `resuelto` al marcar la orden como `resuelta`.

### `app/Application/usecase/derivacion/gestionar_derivacion.py` (modificado)

- `CrearDerivacionUseCase`: ahora cambia el estado del reclamo a `en_atencion_comercial` al crear la derivacion.
- `ActualizarDerivacionUseCase`: ahora cambia el estado del reclamo a `resuelto` al marcar la derivacion como `resuelta`. Recibe `reclamo_repo` como dependencia.

### `app/Application/usecase/reclamo/resolver_reclamo.py` (modificado)

- `ResolverReclamoUseCase`: ahora bloquea resolver desde estado `registrado` (debe clasificarse primero).

### `app/Presentation/dependencies/__init__.py` (modificado)

- `ActualizarOrdenUseCase` y `ActualizarDerivacionUseCase` ahora reciben `reclamo_repo` para poder cambiar el estado del reclamo.

### `app/Presentation/routes/reclamos.py` (modificado)

- `asignar_plazo`: cambio de permiso de `GESTION` a `INTERNO` (el tecnico ahora puede asignar plazos).

---

## 16. Restructuracion: Presentation/api/

### `app/Presentation/api/__init__.py` (nuevo)

Se extrajo toda la configuracion de FastAPI de `main.py` a esta carpeta, siguiendo la
estructura de Clean Architecture:

```
Presentation/
  api/            ← FastAPI app, CORS, routers, exception handler, lifespan
  routes/
  schemas/
  dependencies/
```

El archivo contiene:
- Creacion de `app = FastAPI(...)` con titulo, descripcion, version y lifespan
- Configuracion de CORS middleware
- Include de los 10 routers
- Exception handler global para `DomainError`
- Endpoints de salud (`/` y `/health`)

### `app/main.py` (modificado)

Se redujo a un thin wrapper:
```python
from app.Presentation.api import app  # noqa: F401
```

El entry point para uvicorn sigue siendo `app.main:app` (sin cambios en el comando
de arranque). `conftest.py` tambien sigue importando de `app.main`.

---

## 17. Medidores

Nueva entidad del dominio, con repositorio, casos de uso, rutas y permisos. Cada cuenta
tiene **exactamente un medidor de agua y uno de luz**.

### Archivos nuevos

```
app/Domain/Entities/medidor.py
app/Domain/Repositories/medidor_repository.py
app/Application/usecase/medidor/gestionar_medidor.py
app/Application/usecase/reclamo/validar_medidor.py
app/Infraestructura/database/models/medidor.py
app/Infraestructura/repositories/medidor_repository.py
app/Presentation/routes/medidores.py
app/Presentation/schemas/medidor.py
tests/test_medidores.py
```

### `app/Infraestructura/database/models/medidor.py` (nuevo)

Dos restricciones de unicidad, cada una con una razon distinta:

```python
__table_args__ = (
    UniqueConstraint("id_usuario", "servicio", name="uq_medidor_usuario_servicio"),
    UniqueConstraint("numero", name="uq_medidor_numero"),
)
```

La primera es la que permite que el ciudadano solo tenga que **seleccionar** su medidor y
nunca escriba un numero. La segunda evita que dos suministros compartan codigo, que para
la cuadrilla seria indistinguible.

`reclamos.id_medidor` es nullable a proposito: los reclamos anteriores a esta tabla se
conservan sin medidor en lugar de quedar invalidos.

### `app/Application/usecase/medidor/gestionar_medidor.py` (nuevo)

| Caso de uso | Que hace |
|---|---|
| `ListarMedidoresUseCase` | Filtra por `id_usuario` si se indica |
| `ListarMedidoresDeCiudadanosUseCase` | Aplana ciudadano + medidores, para el rol interno |
| `ObtenerMedidorUseCase` | Busca por `id_medidor` |
| `CrearMedidorUseCase` | Valida que el usuario exista y que no haya otro del mismo servicio |
| `ActualizarMedidorUseCase` | Actualiza el numero |
| `EliminarMedidorUseCase` | Borra |
| `AsignarMedidoresPorDefectoUseCase` | Da de alta el de agua y el de luz, idempotente |

### `app/Application/usecase/reclamo/validar_medidor.py` (nuevo)

`ValidarMedidorReclamoUseCase` es la unica fuente de las tres reglas que-compiten: el
medidor tiene que pertenecer al cliente, su `servicio` tiene que coincidir con el del
reclamo y tiene que estar activo. Se invoca desde `CrearReclamoUseCase`,
`ActualizarReclamoUseCase` y `ClasificarReclamoUseCase`.

> Al reclasificar un reclamo a otro servicio, el medidor queda **desasociado**
> (`id_medidor = NULL`), no cambiado de medidor. Elegir el medidor correcto es una
> decision del operador, no un efecto colateral de cambiar la categoria.

### `app/Presentation/routes/medidores.py` (nuevo)

| Endpoint | Permiso |
|---|---|
| `GET /medidores/` | Cualquier autenticado; `?id_usuario=` de otra cuenta da `403` al ciudadano |
| `GET /medidores/ciudadanos` | `INTERNO` |
| `POST /medidores/` | `ADMIN` |
| `PUT /medidores/{id}` | El dueno o un rol interno |
| `DELETE /medidores/{id}` | `ADMIN` |

---

## 18. Codigo de medidor generado por el sistema

### `generar_numero_medidor(servicio)`

El codigo se sortea con `secrets` y **no se deriva del documento**:

```python
CONFUSOS = set("OILSBZ")
ALFABETO = "".join(c for c in string.ascii_uppercase + string.digits if c not in CONFUSOS)
LARGO_SUFIJO = 8
```

El alfabeto excluye vocales y los digitos que se confunden al dictar por radio
(`0/O`, `1/I/L`, `5/S`, `8/B`, `2/Z`). El resultado es `AG-XXXXXXXX` o `LUZ-XXXXXXXX`.

`numero_medidor_aleatorio(servicio, medidor_repo)` envuelve al generador y reintenta
hasta 20 veces consultando `get_by_numero`, para no depender solo de la restriccion de
base de datos.

**Por que no `AG-{documento}`:** la version provisional derivaba el codigo del documento,
lo que hacia que un cliente pudiera deducir el numero de otro y decia que el medidor era
"provisional". El codigo aleatorio no depende de ningun dato personal y es opaco.

### `AsignarMedidoresPorDefectoUseCase.execute(id_usuario)`

La firma ya **no recibe `documento`**. Se invoca desde `CrearUsuarioUseCase`, asi que
tanto `POST /auth/register` (publico) como `POST /usuarios/` (admin) dan de alta los dos
medidores por el mismo camino. Sigue siendo idempotente: si el cliente ya tiene el
medidor de un servicio, no lo duplica.

### `scripts/migrar_esquema.py` (modificado)

Tres pasos nuevos, todos idempotentes:

| Funcion | Que hace |
|---|---|
| `agregar_indice_unico_si_falta` | `ALTER TABLE ... ADD CONSTRAINT uq_medidor_numero UNIQUE (numero)` |
| `completar_medidores_existentes` | Da de alta los medidores de las cuentas anteriores a la tabla |
| `renumerar_medidores_placeholder` | Sustituye los `AG-{documento}` de la version anterior por codigos generados |

> `create_all()` no puede agregar una restriccion a una tabla que ya existe, por eso el
> indice unico necesita su propio `ALTER` en el script de migracion.

`renumerar_medidores_placeholder` solo toca los medidores cuyo numero coincide
exactamente con el formato viejo, asi que nunca pisa un numero que la empresa haya
cargado a mano. Imprime el antes y el despues de cada cambio.

### `scripts/seed.py` (modificado)

- El seed crea los medidores de las cuatro cuentas demo y los reclamos referencian
  `id_medidor` en vez de un numero de texto.
- **Bug corregido:** `seed_medidores` guardaba en el diccionario solo los medidores
  *nuevos* que devolvia el caso de uso. Al reejecutar el seed **sin** `--reset` sobre una
  base ya sembrada, `por_cliente` quedaba vacio y los reclamos no encontraban su
  medidor. Ahora lee de `repo.get_by_usuario(id_usuario)`, que devuelve lo que quedo en la
  base, no solo lo creado en esa corrida.
- **Bug corregido en `--reset`:** al borrar los usuarios demo, los reclamos de los
  usuarios que no son demo quedaban apuntando a una norma que el script si eliminaba.
  Ahora se les pone `id_normativa = NULL` antes de borrar las normativas.

---

## 19. Verificacion de esta tanda

| Check | Resultado |
|---|---|
| `pytest` | **234 passed** (191 previos + 43 de medidores), salida 0, 208 s |
| `python -m scripts.migrar_esquema` | 13 cambios la primera vez, "No hacia falta ningun cambio" la segunda |
| Altas reales por HTTP | `POST /auth/register` devuelve los dos medidores (`AG-15HT395A`, `LUZ-MWXHPKV4`) |
| Filtro por estado para ciudadano | 13 reclamos, particionados: 2 registrado, 3 clasificado, 2 en atencion tecnica, 3 cerrado |
| Base de datos | 6 usuarios, 12 medidores, 0 medidores con servicio incorrecto |

### Tests agregados en `tests/test_medidores.py`

| Test | Que cubre |
|---|---|
| `test_registro_crea_medidor_de_agua_y_luz` | El alta publica da los dos medidores con codigo generado |
| `test_codigos_de_medidor_no_se_repiten_entre_clientes` | 4 clientes x 2 medidores = 8 codigos distintos |
| `test_numero_aleatorio_no_deriva_del_documento` | 50 codigos casi todos distintos y con el formato esperado |

> Los medidores que crea `conftest.py` van con numero fijo a proposito: es una base
> comparable para los tests de reclamos, que comparan contra `AG-10000001`. En produccion
> el numero es aleatorio.

---

## 20. Pendientes conocidos

- **No hay pantalla de registro publico en el frontend.** `POST /auth/register` existe y
  `AuthContext.registro` esta implementado, pero ninguna pagina lo invoca.
- **`Plantilla-FastAPI.md` sigue sin trackear** en la raiz, mientras `AGENTS.md` y
  `PLAN.md` lo referencian como `docs/Plantilla-FastAPI.md`. Hay que decidir si se mueve
  a `docs/` o se corrige la referencia. No se incluyo en el commit por no ser parte de
  estos cambios.
- **Los 24 warnings de oxlint del frontend** son `react(set-state-in-effect)`:
  algunos `useEffect` llaman `setState` de forma sincrona. No son errores, pero un
  refactor a derivar estado durante el render los eliminaria.
