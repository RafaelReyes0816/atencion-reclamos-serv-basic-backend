# Arquitectura del Sistema — Atención de Reclamos de Servicios Básicos

## Diagrama de Arquitectura General

```mermaid
graph TB
    subgraph "Frontend — React 19 + Vite 8"
        UI[Páginas UI<br/>Login, Dashboard, Reclamos,<br/>Clasificación, Seguimiento,<br/>Administración, Reportes]
        AuthCtx[AuthContext<br/>JWT Token Management]
        AxiosClient[Axios Client<br/>API HTTP]
    end

    subgraph "Backend — FastAPI + Clean Architecture"
        subgraph "Presentation Layer"
            Routes[Routers<br/>auth, usuarios, reclamos,<br/>normativa, cuadrillas,<br/>areas-comerciales,<br/>seguimiento, plazos, reportes,<br/>dashboard]
            Schemas[Pydantic Schemas<br/>Request/Response Validation]
            Dependencies[Dependencies<br/>get_current_user, require_roles<br/>get_service, INTERNO/GESTION/ADMIN]
        end

        subgraph "Application Layer"
            UseCases[Use Cases<br/>gestionar_<entidad>.py /<br/>archivos individuales]
        end

        subgraph "Domain Layer"
            Entities[Entities<br/>10 dataclasses<br/>Usuario, Medidor, Reclamo,<br/>NormativaPlazo,<br/>OrdenTrabajo, Avance,<br/>DerivacionComercial,<br/>Cuadrilla, AreaComercial,<br/>Reporte]
            Interfaces[Repository ABC<br/>10 interfaces]
            Exceptions[Exceptions<br/>DomainError + derivados]
        end

        subgraph "Infrastructure Layer"
            ORM[SQLAlchemy Models<br/>10 tablas]
            Repos[Concrete Repositories<br/>10 implementaciones]
            Security[Security<br/>JWT + bcrypt]
            Scheduler[APScheduler<br/>Tareas Temporales]
        end
    end

    subgraph "Data Layer"
        PostgreSQL[(PostgreSQL<br/>9 tablas)]
        SQLite[(SQLite<br/>Dev Local)]
    end

    subgraph "Scripts Operativos"
        Seeds[scripts/seed.py<br/>Datos demo por rol]
        Migrate[scripts/migrar_esquema.py<br/>ALTER idempotente]
    end

    subgraph "Entidades Externas"
        EE1[EE: Usuario]
        EE2[EE: Cuadrilla Técnica]
        EE3[EE: Área Comercial]
        EE4[EE: Entidad Reguladora]
    end

    subgraph "Background Tasks — P4"
        T1[Detectar Vencimientos<br/>Cada hora]
        T2[Detectar Vencidos<br/>Cada hora]
        T3[Detectar Críticos<br/>Cada 30 min]
    end

    subgraph "Background Tasks — P5"
        T4[Reporte Diario<br/>23:00]
        T5[Reporte Mensual<br/>1er día del mes]
    end

    UI --> AuthCtx
    AuthCtx --> AxiosClient
    AxiosClient -->|HTTP| Routes

    Routes --> Dependencies
    Dependencies --> UseCases
    UseCases --> Interfaces
    Interfaces -.->|Implementa| Repos
    Repos --> ORM
    ORM --> PostgreSQL
    ORM --> SQLite

    Routes --> Schemas
    Dependencies --> Security
    Scheduler --> UseCases

    UseCases -->|lanza| Exceptions
    Exceptions -.->|status_code| Routes

    Seeds --> ORM
    Migrate --> PostgreSQL

    EE1 -->|F1-F4| Routes
    EE2 -->|F5-F6| Routes
    EE3 -->|F7| Routes
    EE4 -->|F8| Routes

    T1 --> PostgreSQL
    T2 --> PostgreSQL
    T3 --> PostgreSQL
    T4 --> PostgreSQL
    T5 --> PostgreSQL

    style UI fill:#3498db,color:#fff
    style Routes fill:#e74c3c,color:#fff
    style UseCases fill:#2ecc71,color:#fff
    style Entities fill:#f39c12,color:#fff
    style Repos fill:#9b59b6,color:#fff
    style PostgreSQL fill:#34495e,color:#fff
    style Security fill:#e67e22,color:#fff
    style Scheduler fill:#1abc9c,color:#fff
    style Exceptions fill:#c0392b,color:#fff
    style Migrate fill:#7f8c8d,color:#fff
    style Seeds fill:#7f8c8d,color:#fff
```

---

## Diagrama de Dependencias — Clean Architecture

```mermaid
graph LR
    subgraph "Presentation"
        P[Routers + Schemas]
    end

    subgraph "Application"
        A[Use Cases]
    end

    subgraph "Domain"
        D[Entities + ABC Interfaces]
    end

    subgraph "Infrastructure"
        I[ORM + Repos + Security]
    end

    P --> A
    A --> D
    I -.->|Implementa| D

    style P fill:#e74c3c,color:#fff
    style A fill:#2ecc71,color:#fff
    style D fill:#f39c12,color:#fff
    style I fill:#9b59b6,color:#fff
```

> **Regla estricta:** Las dependencias van de Presentation → Application → Domain ← Infrastructure. Domain **nunca** importa de Infrastructure ni Presentation.

### Errores de dominio

Los use cases lanzan `DomainError` (o sus derivados) desde `app/Domain/Exceptions.py`, nunca
`HTTPException`. `app/Presentation/api/__init__.py` registra un handler que traduce cada excepción a su
`status_code`:

| Excepción | HTTP | Cuándo |
|-----------|------|--------|
| `NoEncontradoError` | 404 | El recurso no existe |
| `DuplicadoError` | 400 | Documento ya registrado |
| `ConflictoError` | 409 | Transición de estado inválida |

### Invariante: una atención técnica culmina con avances

Una orden de trabajo no puede pasar a `resuelta` sin al menos un avance registrado, y un
reclamo con orden tampoco puede resolverse por `PUT /reclamos/{id}/resolver`. Ambas reglas
viven en la capa Application, no en las rutas:

- `ActualizarOrdenUseCase` — valida solo cuando el payload pide `estado_orden: "resuelta"`,
  antes de mutar, y deja la orden en su estado anterior si rechaza.
- `ResolverReclamoUseCase` — carga la orden del reclamo y aplica el mismo criterio.

Ambas comparten la constante `SIN_AVANCES` de `gestionar_orden.py`. Un reclamo **sin**
orden se resuelve sin restricciones adicionales, porque no hay avances que exigir.
La UI replica la guarda en `AvancesTrabajo.jsx`, pero la garantía real es del backend.

### `nombre_cuenta` y `direccion` viven en el reclamo

Son la identificación de la **cuenta del servicio**, no del reclamante. `Usuario.direccion`
existe aparte y sigue siendo la dirección de la persona. Por eso `PUT /reclamos/{id}/contacto`
escribe en dos tablas según el campo: `telefono`/`email` en `usuarios`,
`nombre_cuenta`/`direccion` en `reclamos`.

Ambos son obligatorios al crear (`ReclamoCreate`) y opcionales al actualizar
(`ReclamoUpdate`, `ReclamoContactoUpdate`). En la entidad y el ORM son `Optional` y las
columnas allow-null para tolerar filas anteriores a la migración; `scripts/migrar_esquema.py`
las agrega y las backfillea desde `usuarios.nombre` y `usuarios.direccion`.
| `ValidacionError` | 422 | Valor fuera de catálogo o regla de negocio |
| `SinPermisosError` | 403 | Rol insuficiente |

---

## Seguridad y Roles

Cada usuario tiene un `rol` en `usuarios.rol` (`Rol` en `app/Domain/Entities/catalogos.py`).
El token JWT lleva el rol, pero `get_current_user` **re-consulta la BD en cada request**, así
que cambiar el rol de un usuario surte efecto inmediato sin esperar que expire el token.

```python
INTERNO = (Rol.tecnico, Rol.supervisor, Rol.admin)   # catálogos + operación de reclamos
GESTION = (Rol.supervisor, Rol.admin)                # escritura, cierre, reportes, dashboard
ADMIN   = (Rol.admin,)                               # CRUD de usuarios, borrado de reclamos
```

`POST /auth/register` es público pero siempre asigna `ciudadano`. Solo `POST /usuarios/`
(admin) crea usuarios con otro rol. Los ciudadanos están acotados a sus propios reclamos y
su propio perfil: el filtro `id_usuario` se sobrescribe con el del token y cualquier
reclamo ajeno devuelve `403`. La matriz completa por endpoint está en `docs/API.md`.

El hash de contraseña nunca sale por la API. `UsuarioRepository.update()` no escribe el hash;
para contraseñas existe `actualizar_contrasena()`, expuesto en
`PUT /usuarios/{id}/contrasena`.

---

## Medidores

Cada cuenta tiene **exactamente un medidor de agua y uno de luz**. El número lo sortea
el sistema al crear la cuenta (`AG-XXXXXXXX` / `LUZ-XXXXXXXX`, 8 caracteres alfanuméricos
sin vocales ni dígitos que se confundan al dictarlos) y el cliente lo corrige desde su
perfil si la empresa le entrega otro. `UniqueConstraint(id_usuario, servicio)` impide un
segundo medidor del mismo servicio y `UniqueConstraint(numero)` impide que dos suministros
compartan código.

El código no depende del documento: se genera con `secrets` y se verifica contra la base
antes de usarlo, así que un cliente no puede deducir ni el de otro. `AsignarMedidoresPorDefectoUseCase`
es idempotente, y `scripts/migrar_esquema.py` renumera los `AG-{documento}` que dejó la
versión anterior.

Consecuencia de diseño: el reclamo **nunca** guarda un número escrito por el usuario,
sino una `id_medidor` (nullable, para no invalidar los reclamos anteriores a esta tabla).
El número que ve el ciudadano es un campo derivado (`Reclamo.medidor.numero`).

`ValidarMedidorReclamoUseCase` (`app/Application/usecase/reclamo/validar_medidor.py`) es
donde vive la regla, y se aplica en los tres caminos que tocan el medidor:

| Camino | Qué hace |
|--------|----------|
| `CrearReclamoUseCase` | Exige `id_medidor` del propio cliente y del mismo `servicio` |
| `ActualizarReclamoUseCase` | Valida `id_medidor` y `servicio` **juntos** si se envía alguno |
| `ClasificarReclamoUseCase` | Si el nuevo `servicio` no corresponde, suelta el medidor (`NULL`) |

Los roles internos registran por ventanilla con `GET /medidores/ciudadanos`, que devuelve
ciudadanos con sus medidores para elegirlos de una sola vez.

---

## Diagrama de Flujo — Ciclo de Vida de un Reclamo

```mermaid
sequenceDiagram
    participant U as EE: Usuario
    participant P1 as P1: Registrar
    participant P2 as P2: Clasificar
    participant P4 as P4: Vigilar Plazos
    participant P3 as P3: Seguir/Cerrar
    participant P5 as P5: Reportes

    U->>P1: F1: Solicitud de Reclamo
    P1->>P1: Validar datos
    P1->>P1: Registrar usuario + reclamo
    P1->>P1: Asignar carátula
    P1-->>U: Comprobante

    P1->>P2: Reclamo registrado
    P2->>P2: Determinar servicio/categoría
    P2->>P2: Asignar urgencia
    P2->>P2: Determinar vía (técnica/comercial)
    P2->>P2: Consultar normativa
    P2->>P2: Calcular fecha_tope

    alt Vía Técnica
        P2->>P3: Asignar a cuadrilla
    else Vía Comercial
        P2->>P3: Derivar a área comercial
    end

    loop P4: Cada hora
        P4->>P4: Detectar vencimientos/vencidos/críticos
    end

    P3->>P3: Registrar avances
    P3->>P3: Registrar resolución
    P3->>P3: Verificar cierre
    P3->>P3: Cerrar reclamo
    P3-->>U: Notificación de resolución

    loop P5: Diario/Mensual
        P5->>P5: Generar reportes
    end
```

---

## Modelo de Datos — DER

```mermaid
erDiagram
    USUARIO {
        int id_usuario PK
        string nombre
        string documento
        string telefono
        string contraseña_hash
        string email
        string direccion
        string rol
    }

    MEDIDOR {
        int id_medidor PK
        int id_usuario FK
        string servicio
        string numero
        string direccion
        bool activo
    }

    RECLAMO {
        int id_reclamo PK
        int id_usuario FK
        int id_normativa FK
        int id_medidor FK
        date fecha_recepcion
        string canal
        string servicio
        string categoria
        string urgencia
        string descripcion
        string nombre_cuenta
        string direccion
        string estado
        date fecha_tope
        date fecha_cierre
        string resultado
    }

    NORMATIVA_PLAZO {
        int id_normativa PK
        string servicio
        string categoria
        string urgencia
        int plazo_maximo_dias
        date vigencia_desde
    }

    ORDEN_TRABAJO {
        int id_orden PK
        int id_reclamo FK
        string cuadrilla
        date fecha_asignacion
        string estado_orden
    }

    AVANCE {
        int id_avance PK
        int id_orden FK
        date fecha_avance
        string descripcion
        string estado_parcial
    }

    DERIVACION_COMERCIAL {
        int id_derivacion PK
        int id_reclamo FK
        date fecha_derivacion
        string area_comercial
        string estado_derivacion
    }

    CUADRILLA {
        int id_cuadrilla PK
        string nombre
        string especialidad
        int capacidad
        string contacto
    }

    AREA_COMERCIAL {
        int id_area PK
        string nombre
        string tipo
        string contacto
    }

    REPORTE {
        int id_reporte PK
        string tipo_reporte
        string periodo
        datetime fecha_generacion
        string contenido
    }

    USUARIO ||--o{ RECLAMO : presenta
    USUARIO ||--o{ MEDIDOR : tiene
    MEDIDOR o|--o{ RECLAMO : sustenta
    NORMATIVA_PLAZO ||--o{ RECLAMO : establece_plazo
    RECLAMO o|--o| ORDEN_TRABAJO : genera
    RECLAMO o|--o| DERIVACION_COMERCIAL : deriva
    ORDEN_TRABAJO ||--o{ AVANCE : registra
```

---

## Subsistemas — DFD Nivel 1

```mermaid
graph LR
    subgraph "P1: Registrar y Consultar"
        P1_1[Validar Datos]
        P1_2[Registrar Usuario]
        P1_3[Asignar Carátula]
        P1_4[Emitir Comprobante]
        P1_5[Consultar Estado]
        P1_6[Actualizar Contacto]
    end

    subgraph "P2: Clasificar y Asignar"
        P2_1[Determinar Servicio/Categoría]
        P2_2[Asignar Urgencia]
        P2_3[Determinar Vía]
        P2_4[Consultar Normativa]
        P2_5[Calcular Plazo]
        P2_6[Asignar Cuadrilla]
        P2_7[Derivar Comercial]
    end

    subgraph "P3: Seguir y Cerrar"
        P3_1[Registrar Avance]
        P3_2[Resolver Técnico]
        P3_3[Resolver Comercial]
        P3_4[Verificar Cierre]
        P3_5[Cerrar Reclamo]
        P3_6[Notificar Usuario]
    end

    subgraph "P4: Vigilar Plazos"
        P4_1[Detectar Vencimientos]
        P4_2[Detectar Vencidos]
        P4_3[Detectar Críticos]
    end

    subgraph "P5: Generar Reportes"
        P5_1[Reporte Diario]
        P5_2[Reporte Mensual]
    end

    P1_1 --> P1_2 --> P1_3 --> P1_4
    P2_1 --> P2_2 --> P2_3
    P2_3 --> P2_6
    P2_3 --> P2_7
    P2_4 --> P2_5
    P3_1 --> P3_2
    P3_2 --> P3_4 --> P3_5 --> P3_6
    P3_3 --> P3_4

    style P1_1 fill:#3498db,color:#fff
    style P2_1 fill:#e74c3c,color:#fff
    style P3_1 fill:#2ecc71,color:#fff
    style P4_1 fill:#f39c12,color:#fff
    style P5_1 fill:#9b59b6,color:#fff
```

---

## API Endpoints

| Método | Ruta | Descripción | Rol mínimo |
|--------|------|-------------|:----------:|
| POST | `/auth/login` | Iniciar sesión | Público |
| POST | `/auth/register` | Registrar usuario (siempre `ciudadano`) | Público |
| GET | `/reclamos/estado/{id_o_doc}` | Tracking del reclamo | Público |
| PUT | `/usuarios/{id}/contrasena` | Cambiar contraseña | Propio usuario |
| GET | `/usuarios/documento/{documento}` | Buscar usuario por documento | Propio o interno |
| GET | `/usuarios/` | Listar usuarios | `supervisor` |
| POST | `/usuarios/` | Crear usuario con rol | `admin` |
| DELETE | `/usuarios/{id}` | Eliminar usuario | `admin` |
| GET | `/usuarios/{id}` | Ver usuario | Propio o interno |
| PUT | `/usuarios/{id}` | Actualizar usuario | Propio (sin `rol`) o `admin` |
| GET | `/reclamos/` | Listar reclamos | `ciudadano` ve los suyos, `tecnico` todos |
| POST | `/reclamos/` | Crear reclamo | `ciudadano` solo a su nombre |
| GET | `/reclamos/{id}` | Ver reclamo | Propietario o `tecnico` |
| PUT | `/reclamos/{id}` | Editar reclamo | `tecnico` |
| PUT | `/reclamos/{id}/clasificar` | Clasificar reclamo | `tecnico` |
| PUT | `/reclamos/{id}/asignar-plazo` | Asignar plazo | `supervisor` |
| PUT | `/reclamos/{id}/resolver` | Resolver reclamo | `tecnico` |
| PUT | `/reclamos/{id}/cerrar` | Cerrar reclamo | `supervisor` |
| DELETE | `/reclamos/{id}` | Eliminar reclamo | `admin` |
| GET | `/normativa/` `GET /cuadrillas/` `GET /areas-comerciales/` | Leer catálogos | `tecnico` |
| GET | `/normativa/vigente` | Normativa vigente por combinación | `tecnico` |
| POST/PUT/DELETE | de normativa, cuadrillas y áreas | Escribir catálogos | `supervisor` |
| GET/POST/PUT | `/seguimiento/*` | Órdenes, avances, derivaciones | `tecnico` |
| DELETE | `/seguimiento/ordenes/{id}` | Eliminar orden | `supervisor` |
| POST | `/plazos/*` | Verificar vencimientos/vencidos/críticos | `supervisor` |
| GET/POST | `/reportes/*` | Reportes y export Excel | `supervisor` |
| GET | `/dashboard/` | Indicadores | `supervisor` |

> `supervisor` y `admin` heredan todo lo de `tecnico`. Detalle completo en `docs/API.md`.

---

## Esquema y Datos de Prueba

`Base.metadata.create_all()` **no altera tablas que ya existen**: si se agrega una columna al
ORM sobre una base viva, la columna no aparece. Por eso existe `scripts/migrar_esquema.py`,
que aplica `ALTER TABLE ... ADD COLUMN IF NOT EXISTS` de forma idempotente y preserva los
datos. Se ejecuta una vez tras cada cambio de esquema.

`scripts/seed.py` carga un usuario por rol (documentos `10000001`–`10000004`, contraseña
`clave123`), normativa, cuadrillas, áreas comerciales y reclamos de ejemplo. Es idempotente.
`--reset` borra únicamente lo que el propio script creó —se identifica por documento, nombre
y tuplas de catálogo, nunca "todo lo que hay en la tabla"— y vuelve a insertarlo.

---

## Suite de Pruebas

Ubicación: `tests/`. Se ejecuta con `pytest` (desde `backend/`).

```bash
cd backend && pytest                  # todos
cd backend && pytest tests/test_reclamos.py  # un archivo
cd backend && pytest -k "test_crear"  # por nombre
```

| Archivo | Cubre |
|---------|-------|
| `conftest.py` | Fixtures: cliente HTTP, usuario admin/tecnico/ciudadano, datos de prueba |
| `test_auth.py` | Login, register, JWT |
| `test_usuarios.py` | CRUD de usuarios, permisos por rol |
| `test_permisos.py` | Matriz completa de 403 por rol × endpoint |
| `test_reclamos.py` | Crear, listar, clasificar, resolver, cerrar, eliminar |
| `test_normativa.py` | CRUD de normativa, consulta vigente |
| `test_cuadrillas_areas.py` | CRUD de cuadrillas y áreas comerciales |
| `test_seguimiento.py` | Órdenes, avances, derivaciones |
| `test_reportes_plazos_dashboard.py` | Reportes, plazos, dashboard |
| `test_configuracion.py` | Configuración del sistema |

Naming: `test_<method>_<scenario>_<result>`. La suite usa httpx async para llamadas
a la API y `conftest.py` configura la BD de prueba (SQLite en memoria).
