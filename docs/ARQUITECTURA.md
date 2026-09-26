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
            Routes[Routers<br/>auth, usuarios, reclamos,<br/>normativa, cuadrillas,<br/>areas-comerciales,<br/>seguimiento, plazos, reportes]
            Schemas[Pydantic Schemas<br/>Request/Response Validation]
            Dependencies[Dependencies<br/>get_current_user<br/>get_service]
        end

        subgraph "Application Layer"
            UseCases[Use Cases<br/>25+ clases<br/>1 por operación CRUD]
        end

        subgraph "Domain Layer"
            Entities[Entities<br/>9 dataclasses<br/>Usuario, Reclamo,<br/>NormativaPlazo,<br/>OrdenTrabajo, Avance,<br/>DerivacionComercial,<br/>Cuadrilla, AreaComercial,<br/>Reporte]
            Interfaces[Repository ABC<br/>9 interfaces]
        end

        subgraph "Infrastructure Layer"
            ORM[SQLAlchemy Models<br/>9 tablas]
            Repos[Concrete Repositories<br/>9 implementaciones]
            Security[Security<br/>JWT + bcrypt]
            Scheduler[APScheduler<br/>Tareas Temporales]
        end
    end

    subgraph "Data Layer"
        PostgreSQL[(PostgreSQL<br/>9 tablas)]
        SQLite[(SQLite<br/>Dev Local)]
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
    }

    RECLAMO {
        int id_reclamo PK
        int id_usuario FK
        int id_normativa FK
        date fecha_recepcion
        string canal
        string servicio
        string categoria
        string urgencia
        string descripcion
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

| Método | Ruta | Descripción | Auth |
|--------|------|-------------|------|
| POST | `/auth/login` | Iniciar sesión | No |
| POST | `/auth/register` | Registrar usuario | No |
| GET | `/usuarios/` | Listar usuarios | Sí |
| POST | `/reclamos/` | Crear reclamo | Sí |
| PUT | `/reclamos/{id}/clasificar` | Clasificar reclamo | Sí |
| PUT | `/reclamos/{id}/resolver` | Resolver reclamo | Sí |
| PUT | `/reclamos/{id}/cerrar` | Cerrar reclamo | Sí |
| POST | `/plazos/verificar-vencimientos` | Verificar plazos | Sí |
| POST | `/reportes/diario` | Generar reporte | Sí |
