# API Documentation — Sistema de Atención de Reclamos de Servicios Básicos

**Base URL:** `http://127.0.0.1:8000`

**Documentación interactiva (Swagger):** `http://127.0.0.1:8000/docs`

**Formato de respuesta:** los endpoints de recurso devuelven el objeto directamente.
Los endpoints de acción y eliminación devuelven `{ "message": ..., "status": "success" }`.

**Autenticación:** JWT Bearer token en header `Authorization: Bearer {token}`

**Códigos de estado usados:**

| Código | Significado |
|--------|-------------|
| `200` | Operación exitosa |
| `201` | Recurso creado |
| `400` | Regla de negocio (documento duplicado) |
| `401` | Sin token, token inválido o credenciales incorrectas |
| `403` | Autenticado pero sin permisos para esa operación |
| `404` | Recurso no encontrado |
| `409` | Conflicto de estado (estado inválido para la transición) |
| `422` | Validación de datos o de catálogos |

**Catálogos validados:** todos los campos de catálogo son rechazados con `422` si el valor
no pertenece a su enum. Ver [Catálogos](#catálogos).

---

## Máquina de estados del reclamo

El `estado` de un reclamo transiciona automáticamente según la acción ejecutada:

```
registrado ──PUT /clasificar──> clasificado
clasificado ──PUT /asignar-plazo──> clasificado (con fecha_tope)
clasificado ──POST /seguimiento/ordenes──> en_atencion_tecnica
clasificado ──POST /seguimiento/derivaciones──> en_atencion_comercial
en_atencion_tecnica ──PUT /seguimiento/ordenes/{id} (estado_orden: resuelta)──> resuelto
en_atencion_comercial ──PUT /seguimiento/derivaciones/{id} (estado_derivacion: resuelta)──> resuelto
resuelto ──PUT /cerrar──> cerrado
cualquiera (no cerrado) ──scheduler vencidos──> escalado
```

**Transiciones importantes:**
- **Crear orden de trabajo** (`POST /seguimiento/ordenes`) cambia el reclamo a `en_atencion_tecnica`.
- **Crear derivación comercial** (`POST /seguimiento/derivaciones`) cambia el reclamo a `en_atencion_comercial`.
- **Marcar orden como resuelta** (`PUT /seguimiento/ordenes/{id}` con `estado_orden: "resuelta"`) cambia el reclamo a `resuelto`.
- **Marcar derivación como resuelta** (`PUT /seguimiento/derivaciones/{id}` con `estado_derivacion: "resuelta"`) cambia el reclamo a `resuelto`.
- **Resolver** (`PUT /reclamos/{id}/resolver`) requiere que el reclamo NO esté en `registrado` ni `cerrado`.
- **Cerrar** (`PUT /reclamos/{id}/cerrar`) requiere que el reclamo esté en `resuelto`.

---

## Roles y permisos

Cada usuario tiene un `rol`. El registro público (`/auth/register`) **siempre** asigna
`ciudadano`; solo un `admin` puede crear usuarios con otro rol.

| Rol | Puede hacer |
|-----|-------------|
| `ciudadano` | Registrar y consultar **sus propios** reclamos, ver y editar su propio perfil, cambiar su contraseña, consultar el estado de su reclamo por documento |
| `tecnico` | Lo de `ciudadano` + lectura de normativa/cuadrillas/áreas/órdenes, registrar avances, clasificar, asignar plazos y resolver reclamos |
| `supervisor` | Lo de `tecnico` + listar usuarios, escribir normativa/cuadrillas/áreas, cerrar reclamos, eliminar órdenes, reportes, dashboard, verificación de plazos |
| `admin` | Todo, incluyendo crear/eliminar usuarios y eliminar reclamos |

**Matriz por endpoint:**

| Endpoint | ciudadano | tecnico | supervisor | admin |
|----------|:---------:|:-------:|:----------:|:-----:|
| `GET /usuarios/` | | | ✅ | ✅ |
| `POST /usuarios/` | | | | ✅ |
| `GET /usuarios/{id}` | solo el suyo | ✅ | ✅ | ✅ |
| `PUT /usuarios/{id}` | solo el suyo, sin `rol` | | | ✅ |
| `PUT /usuarios/{id}/contrasena` | solo el suyo | solo el suyo | solo el suyo | solo el suyo |
| `DELETE /usuarios/{id}` | | | | ✅ |
| `GET /reclamos/` | solo los suyos | ✅ | ✅ | ✅ |
| `POST /reclamos/` | solo a su nombre | ✅ | ✅ | ✅ |
| `GET /reclamos/{id}` | solo los suyos | ✅ | ✅ | ✅ |
| `PUT /reclamos/{id}` | | ✅ | ✅ | ✅ |
| `PUT /reclamos/{id}/clasificar` | | ✅ | ✅ | ✅ |
| `PUT /reclamos/{id}/asignar-plazo` | | ✅ | ✅ | ✅ |
| `PUT /reclamos/{id}/resolver` | | ✅ | ✅ | ✅ |
| `PUT /reclamos/{id}/cerrar` | | | ✅ | ✅ |
| `DELETE /reclamos/{id}` | | | | ✅ |
| `GET /normativa/` `GET /cuadrillas/` `GET /areas-comerciales/` | | ✅ | ✅ | ✅ |
| `POST/PUT/DELETE` de normativa, cuadrillas y áreas | | | ✅ | ✅ |
| `GET/POST/PUT` de seguimiento (órdenes, avances, derivaciones) | | ✅ | ✅ | ✅ |
| `DELETE /seguimiento/ordenes/{id}` | | | ✅ | ✅ |
| `GET /reportes/` `POST /reportes/*` `GET /dashboard/` `POST /plazos/*` | | | ✅ | ✅ |

Un `403` significa token válido pero rol insuficiente. Un `401` significa token ausente,
expirado o credenciales incorrectas.

---

## Auth

### POST `/auth/login`
Iniciar sesión. OAuth2 `application/x-www-form-urlencoded` (no JSON).

**Request:**
```
username: documento
password: contraseña
```

**Response:** `200`
```json
{
  "access_token": "eyJ...",
  "token_type": "bearer",
  "rol": "ciudadano",
  "id_usuario": 13,
  "nombre": "Ciudadano Demo"
}
```

> En PowerShell usar `curl.exe` y no `Invoke-RestMethod`: este último rompe la `ñ` de la contraseña.

### POST `/auth/register`
Registrar nuevo usuario. **Sin auth.** El `rol` enviado en el body se **ignora**: siempre
se crea como `ciudadano`.

**Request Body:** `UsuarioCreate`
```json
{
  "nombre": "Juan Pérez",
  "documento": "12345678",
  "telefono": "555-0100",
  "contraseña": "clave123",
  "email": "juan@correo.com",
  "direccion": "Av. Principal 123"
}
```

**Response:** `201` `UsuarioResponse` — `400` si el documento ya existe

---

## Usuarios

> Todos los endpoints de esta sección requieren un rol de **gestión** (`supervisor` o `admin`),
> excepto donde se indica lo contrario.

### GET `/usuarios/`
Listar todos los usuarios. **Requiere `supervisor` o `admin`.**

**Response:** `200` `List[UsuarioResponse]`

### POST `/usuarios/`
Crear usuario. **Requiere `admin`.** Es la única forma de crear un usuario con un rol
distinto de `ciudadano`.

**Request Body:** `UsuarioCreate`
```json
{
  "nombre": "Supervisor Pérez",
  "documento": "12345679",
  "telefono": "555-0100",
  "contraseña": "clave123",
  "email": "sup@correo.com",
  "direccion": "Calle 1",
  "rol": "supervisor"
}
```

**Response:** `201` `UsuarioResponse` — `400` si el documento ya existe

### GET `/usuarios/documento/{documento}`
Obtener usuario por documento. **Requiere auth.** Un `ciudadano` solo puede consultar su
propio documento.

**Response:** `200` `UsuarioResponse` — `403` si se consulta el documento de otro usuario

### GET `/usuarios/{id}`
Obtener usuario por ID. **Requiere auth.** Un `ciudadano` solo puede consultarse a sí mismo.

**Response:** `200` `UsuarioResponse`

### PUT `/usuarios/{id}`
Actualizar usuario. **Requiere auth.** Solo se modifican los campos enviados.
Un `ciudadano` solo puede editarse a sí mismo y el campo `rol` se **ignora** para él.

**Request Body:** `UsuarioUpdate` (todos opcionales)
```json
{
  "nombre": "Juan Pérez Soto",
  "telefono": "555-0199",
  "email": "nuevo@correo.com",
  "direccion": "Calle 45 #12-34",
  "rol": "tecnico"
}
```

**Response:** `200` `UsuarioResponse`

### PUT `/usuarios/{id}/contrasena`
Cambiar la contraseña. **Requiere auth** y solo puede usarse sobre el propio usuario
(`403` en caso contrario, incluso para un `admin`).

**Request Body:**
```json
{
  "contrasena_actual": "clave123",
  "contrasena_nueva": "nuevaClave123"
}
```

**Response:** `200`
```json
{ "message": "Contraseña actualizada correctamente", "status": "success" }
```

`422` si `contrasena_actual` no coincide o si la nueva es igual a la actual.

### DELETE `/usuarios/{id}`
Eliminar usuario. **Requiere `admin`.** `409` si tiene reclamos asociados.

**Response:** `200`
```json
{ "message": "Usuario eliminado", "status": "success" }
```

---

## Reclamos

### GET `/reclamos/`
Listar reclamos con filtros opcionales. **Requiere auth.** Un `ciudadano` solo recibe los suyos (el filtro `id_usuario` se sobrescribe); el personal interno ve todos.

**Query Parameters (todos opcionales):**

| Param | Valores |
|-------|---------|
| `estado` | `registrado`, `clasificado`, `en_atencion_tecnica`, `en_atencion_comercial`, `resuelto`, `cerrado`, `escalado` |
| `servicio` | `agua`, `luz` |
| `categoria` | `corte`, `facturacion`, `fuga`, `falla_tecnica` |
| `urgencia` | `programada`, `normal`, `alta`, `critica` |
| `canal` | `presencial`, `telefonico`, `web` |
| `id_usuario` | entero > 0 |

Los resultados vienen ordenados por `id_reclamo` descendente.

**Ejemplo:** `GET /reclamos/?servicio=agua&estado=clasificado`

**Response:** `200` `List[ReclamoResponse]`

### POST `/reclamos/`
Crear nuevo reclamo. **Requiere auth.** `404` si `id_usuario` no existe. Un `ciudadano` solo puede registrar reclamos a su propio nombre (`403` en caso contrario).

**Request Body:**
```json
{
  "id_usuario": 1,
  "canal": "web",
  "servicio": "agua",
  "categoria": "fuga",
  "urgencia": "alta",
  "descripcion": "Fuga en tubería principal"
}
```

**Response:** `201` `ReclamoResponse` (con `estado: "registrado"` y `fecha_recepcion` asignados)

### GET `/reclamos/estado/{id_o_doc}`
Consultar estado. **Público — sin auth.** (tracking del ciudadano)

Acepta el **ID del reclamo** o el **documento del usuario** (numérico o alfanumérico).
Si es documento, devuelve el reclamo más reciente del usuario.

**Response:** `200`
```json
{ "id_reclamo": 1, "estado": "clasificado", "fecha_tope": "2026-10-10" }
```

`404` si no hay coincidencia o el usuario no tiene reclamos.

### GET `/reclamos/{id}`
Obtener reclamo por ID. **Requiere auth.** Un `ciudadano` solo accede a sus propios reclamos (`403` en caso contrario).

**Response:** `200` `ReclamoResponse`

### PUT `/reclamos/{id}`
Actualizar reclamo. **Requiere rol interno** (`tecnico`, `supervisor` o `admin`). `409` si el reclamo está `cerrado`.

**Request Body:** `ReclamoUpdate` (todos opcionales)
```json
{
  "canal": "web",
  "servicio": "agua",
  "categoria": "fuga",
  "urgencia": "alta",
  "descripcion": "Descripción actualizada",
  "id_normativa": 1,
  "fecha_tope": "2026-10-15",
  "resultado": "resuelto"
}
```

**Response:** `200` `ReclamoResponse`

### PUT `/reclamos/{id}/clasificar`
Clasificar reclamo. **Requiere rol interno.** `409` si está `resuelto` o `cerrado`.

**Request Body:**
```json
{ "servicio": "agua", "categoria": "fuga", "urgencia": "critica" }
```

**Response:** `200` `ReclamoResponse` (con `estado: "clasificado"`)

### PUT `/reclamos/{id}/asignar-plazo`
Asignar plazo regulatorio. **Requiere rol interno.** `404` si la normativa no existe, `409` si está cerrado.

**Request Body:**
```json
{ "id_normativa": 1, "fecha_tope": "2026-10-15" }
```

**Response:** `200` `ReclamoResponse`

### PUT `/reclamos/{id}/resolver`
Resolver reclamo. **Requiere rol interno.** `409` si está `cerrado` o `registrado`.

**Request Body:**
```json
{ "resultado": "resuelto", "detalle": "Reparado" }
```

**Response:** `200` `ReclamoResponse` (con `estado: "resuelto"`)

### PUT `/reclamos/{id}/cerrar`
Cerrar reclamo. **Requiere `supervisor` o `admin`.** **`409` si el estado actual no es `resuelto`** —
primero hay que resolver.

**Request Body:**
```json
{ "resultado": "resuelto" }
```

**Response:** `200` `ReclamoResponse` (con `estado: "cerrado"` y `fecha_cierre`)

### GET `/reclamos/{id}/comprobante`
Obtener comprobante. **Requiere auth.** Un `ciudadano` solo obtiene los de sus propios reclamos.

**Response:** `200`
```json
{
  "id_reclamo": 1,
  "fecha_recepcion": "2026-09-26",
  "canal": "web",
  "servicio": "agua",
  "categoria": "fuga",
  "descripcion": "Fuga en tubería principal",
  "fecha_tope": "2026-10-10"
}
```

### PUT `/reclamos/{id}/contacto`
Actualizar datos de contacto del reclamante. **Requiere auth.** Un `ciudadano` solo puede
actualizar el contacto de sus propios reclamos.

**Request Body:**
```json
{ "telefono": "555-0100", "email": "nuevo@correo.com" }
```

**Response:** `200`
```json
{ "message": "Contacto actualizado", "status": "success" }
```

### DELETE `/reclamos/{id}`
Eliminar reclamo. **Requiere `admin`.** Elimina en cascada su orden de trabajo,
avances y derivación.

**Response:** `200`
```json
{ "message": "Reclamo eliminado", "status": "success" }
```

---

## Normativa

### GET `/normativa/vigente`
Normativa vigente para una combinación. **Requiere rol interno.** `404` si no hay match.

**Query Parameters (obligatorios):** `servicio`, `categoria`, `urgencia`

**Response:** `200` `NormativaResponse`

### GET `/normativa/`
Listar normativa. **Requiere rol interno.** Filtros opcionales: `servicio`, `categoria`, `urgencia`.

**Response:** `200` `List[NormativaResponse]`

### POST `/normativa/`
Crear normativa. **Requiere `supervisor` o `admin`.**

**Request Body:**
```json
{
  "servicio": "agua",
  "categoria": "fuga",
  "urgencia": "critica",
  "plazo_maximo_dias": 3,
  "vigencia_desde": "2026-01-01"
}
```

**Response:** `201` `NormativaResponse`

### GET `/normativa/{id}`
Obtener normativa por ID. **Requiere rol interno.**

**Response:** `200` `NormativaResponse`

### PUT `/normativa/{id}`
Actualizar normativa. **Requiere `supervisor` o `admin`.** Solo se modifican los campos enviados;
los demás conservan su valor.

**Request Body:** `NormativaUpdate` (todos opcionales)

**Response:** `200` `NormativaResponse`

### DELETE `/normativa/{id}`
Eliminar normativa. **Requiere `supervisor` o `admin`.** Los reclamos que la referencian quedan con
`id_normativa: null`.

**Response:** `200`
```json
{ "message": "Normativa eliminada", "status": "success" }
```

---

## Cuadrillas

### GET `/cuadrillas/disponibles/{especialidad}`
Cuadrillas por especialidad. **Requiere rol interno.** `especialidad`: `agua` | `luz`.

**Response:** `200` `List[CuadrillaResponse]`

### GET `/cuadrillas/`
Listar cuadrillas. **Requiere rol interno.**

**Response:** `200` `List[CuadrillaResponse]`

### POST `/cuadrillas/`
Crear cuadrilla. **Requiere `supervisor` o `admin`.**

**Request Body:**
```json
{ "nombre": "Cuadrilla Alpha", "especialidad": "agua", "capacidad": 3, "contacto": "555-0101" }
```

**Response:** `201` `CuadrillaResponse`

### GET `/cuadrillas/{id}`
**Requiere rol interno.**

**Response:** `200` `CuadrillaResponse`

### PUT `/cuadrillas/{id}`
Actualizar cuadrilla. **Requiere `supervisor` o `admin`.** Solo se modifican los campos enviados.

**Response:** `200` `CuadrillaResponse`

### DELETE `/cuadrillas/{id}`
**Requiere `supervisor` o `admin`.**

**Response:** `200`
```json
{ "message": "Cuadrilla eliminada", "status": "success" }
```

---

## Áreas Comerciales

### GET `/areas-comerciales/`
**Requiere rol interno.** → `200` `List[AreaComercialResponse]`

### POST `/areas-comerciales/`
**Requiere `supervisor` o `admin`.**
```json
{ "nombre": "Facturación Central", "tipo": "facturacion", "contacto": "555-0202" }
```
`tipo`: `facturacion` | `cobranza`

**Response:** `201` `AreaComercialResponse`

### GET `/areas-comerciales/{id}`
**Requiere rol interno.** → `200` `AreaComercialResponse`

### PUT `/areas-comerciales/{id}`
**Requiere `supervisor` o `admin`.** → `200` `AreaComercialResponse`

### DELETE `/areas-comerciales/{id}`
**Requiere `supervisor` o `admin`.** → `200` `{ "message": "Área comercial eliminada", "status": "success" }`

---

## Seguimiento

### GET `/seguimiento/ordenes`
Listar órdenes de trabajo. **Requiere rol interno.** → `200` `List[OrdenTrabajoResponse]`

### GET `/seguimiento/ordenes/reclamo/{id_reclamo}`
Orden de un reclamo. **Requiere rol interno.** `404` si no tiene orden.

**Response:** `200` `OrdenTrabajoResponse`

### POST `/seguimiento/ordenes`
Crear orden. **Requiere rol interno.** `404` si el reclamo no existe, `409` si ya tiene orden.
**Cambia el estado del reclamo a `en_atencion_tecnica`.**

**Request Body:**
```json
{ "id_reclamo": 1, "cuadrilla": "Cuadrilla Alpha", "fecha_asignacion": "2026-09-26" }
```

**Response:** `201` `OrdenTrabajoResponse` (con `estado_orden: "asignada"`)

### GET `/seguimiento/ordenes/{id}`
**Requiere rol interno.** → `200` `OrdenTrabajoResponse`

### PUT `/seguimiento/ordenes/{id}`
Actualizar orden. **Requiere rol interno.** Solo los campos enviados.
`estado_orden`: `asignada` | `en_curso` | `resuelta`
**Si se cambia a `resuelta`, el reclamo asociado pasa a `resuelto`.**

**Request Body:**
```json
{ "cuadrilla": "Cuadrilla Beta", "fecha_asignacion": "2026-09-27", "estado_orden": "en_curso" }
```

**Response:** `200` `OrdenTrabajoResponse`

### DELETE `/seguimiento/ordenes/{id}`
**Requiere `supervisor` o `admin`.** Elimina también sus avances.

**Response:** `200` `{ "message": "Orden de trabajo eliminada", "status": "success" }`

### GET `/seguimiento/avances/{id_orden}`
Listar avances de una orden. **Requiere rol interno.** `404` si la orden no existe.

**Response:** `200` `List[AvanceResponse]`

### POST `/seguimiento/avances`
Registrar avance. **Requiere rol interno.** `404` si la orden no existe,
`409` si la orden está `resuelta`.

**Request Body:**
```json
{
  "id_orden": 1,
  "fecha_avance": "2026-09-26",
  "descripcion": "Se localizó la fuga",
  "estado_parcial": "iniciado"
}
```
`estado_parcial`: `iniciado` | `en_proceso` | `verificado`

**Response:** `201` `AvanceResponse`

### GET `/seguimiento/derivaciones/reclamo/{id_reclamo}`
Derivación de un reclamo. **Requiere rol interno.** `404` si no tiene derivación.

**Response:** `200` `DerivacionResponse`

### GET `/seguimiento/derivaciones/{id}`
Derivación por su ID. **Requiere rol interno.**

**Response:** `200` `DerivacionResponse`

### POST `/seguimiento/derivaciones`
Crear derivación. **Requiere rol interno.** `404` si el reclamo no existe, `409` si ya tiene derivación.
**Cambia el estado del reclamo a `en_atencion_comercial`.**
`area_comercial`: `facturacion` | `cobranza`

**Request Body:**
```json
{ "id_reclamo": 1, "fecha_derivacion": "2026-09-26", "area_comercial": "facturacion" }
```

**Response:** `201` `DerivacionResponse` (con `estado_derivacion: "derivada"`)

### PUT `/seguimiento/derivaciones/{id}`
Actualizar derivación. **Requiere rol interno.** `estado_derivacion`: `derivada` | `resuelta`
**Si se cambia a `resuelta`, el reclamo asociado pasa a `resuelto`.**

**Request Body:**
```json
{ "area_comercial": "cobranza", "fecha_derivacion": "2026-09-27", "estado_derivacion": "resuelta" }
```

**Response:** `200` `DerivacionResponse`

---

## Plazos (P4 — Vigilancia)

Los tres endpoints son `POST` y requieren auth. Também los ejecuta APScheduler
cada hora (críticos: cada 30 min).

### POST `/plazos/verificar-vencimientos`
```json
{ "avisos": [{ "id_reclamo": 1, "fecha_tope": "2026-10-01", "dias_restantes": 5 }], "total": 1 }
```

### POST `/plazos/verificar-vencidos`
```json
{ "alertas": [{ "id_reclamo": 2, "fecha_tope": "2026-09-20", "exceso_dias": 6 }], "total": 1 }
```

### POST `/plazos/verificar-criticos`
```json
{ "alarmas": [{ "id_reclamo": 3, "servicio": "agua", "categoria": "fuga", "urgencia": "critica" }], "total": 1 }
```

---

## Reportes (P5)

### GET `/reportes/`
Listar reportes (más reciente primero). **Requiere `supervisor` o `admin`.** → `200` `List[ReporteResponse]`

### POST `/reportes/diario`
Generar reporte operativo diario. **Requiere `supervisor` o `admin`.**

**Response:** `201` `{ "message": "Reporte diario generado", "id_reporte": 1 }`

### POST `/reportes/mensual`
Generar reporte regulatorio mensual (período anterior). **Requiere `supervisor` o `admin`.**

**Response:** `201` `{ "message": "Reporte mensual generado", "id_reporte": 2 }`

### GET `/reportes/{id}`
Reporte con el JSON de `contenido` ya parseado. **Requiere `supervisor` o `admin`.**

**Response:** `200`
```json
{
  "id_reporte": 1,
  "tipo_reporte": "operativo_diario",
  "periodo": "2026-09-26",
  "fecha_generacion": "2026-09-26T23:00:00",
  "datos": { "fecha": "2026-09-26", "ingresados": 4, "en_atencion": 2, "vencidos": 1, "criticos": 0 }
}
```

### GET `/reportes/{id}/excel`
Descargar el reporte como `.xlsx`. **Requiere `supervisor` o `admin`.**

**Response:** `200`
- `Content-Type: application/vnd.openxmlformats-officedocument.spreadsheetml.sheet`
- `Content-Disposition: attachment; filename="reporte_operativo_diario_2026-09-26.xlsx"`

---

## Dashboard

### GET `/dashboard/`
Métricas agregadas y alertas. **Requiere `supervisor` o `admin`.**

**Response:** `200`
```json
{
  "total_reclamos": 12,
  "total_usuarios": 5,
  "por_estado": { "registrado": 2, "clasificado": 3, "cerrado": 7 },
  "por_servicio": [{ "servicio": "agua", "total": 7 }, { "servicio": "luz", "total": 5 }],
  "por_categoria": { "fuga": 4, "corte": 8 },
  "por_urgencia": { "alta": 9, "critica": 3 },
  "en_atencion": 0,
  "resueltos": 0,
  "cerrados": 7,
  "pendientes": 5,
  "criticos": 2,
  "vencidos": 1,
  "proximos_vencer": 1,
  "cumplidos_en_plazo": 6,
  "cerrados_en_plazo": 7,
  "porcentaje_cumplimiento": 85.71,
  "alertas_vencidos": [{ "id_reclamo": 4, "estado": "clasificado", "fecha_tope": "2026-09-20", "dias_restantes": -6 }],
  "alertas_vencimiento_proximo": [{ "id_reclamo": 9, "estado": "clasificado", "fecha_tope": "2026-09-28", "dias_restantes": 2 }],
  "alertas_criticas": [{ "id_reclamo": 2, "servicio": "agua", "categoria": "fuga", "urgencia": "critica", "estado": "clasificado" }]
}
```

`dias_restantes` negativo significa días de atraso.

---

## Salud

### GET `/`
`{ "message": "Sistema de Atención de Reclamos de Servicios Básicos" }`

### GET `/health`
`{ "status": "ok" }`

---

## Catálogos

Un valor fuera de estos catálogos se rechaza con `422`.

| Catálogo | Valores |
|----------|---------|
| `Rol` | `ciudadano`, `tecnico`, `supervisor`, `admin` |
| `Canal` | `presencial`, `telefonico`, `web` |
| `Servicio` | `agua`, `luz` |
| `Categoria` | `corte`, `facturacion`, `fuga`, `falla_tecnica` |
| `Urgencia` | `programada`, `normal`, `alta`, `critica` |
| `EstadoReclamo` | `registrado`, `clasificado`, `en_atencion_tecnica`, `en_atencion_comercial`, `resuelto`, `cerrado`, `escalado` |
| `Resultado` | `resuelto`, `descartado`, `derivado` |
| `EstadoOrden` | `asignada`, `en_curso`, `resuelta` |
| `EstadoParcial` | `iniciado`, `en_proceso`, `verificado` |
| `TipoAreaComercial` | `facturacion`, `cobranza` |
| `EstadoDerivacion` | `derivada`, `resuelta` |
| `ViaAtencion` | `tecnica`, `comercial` |
| `ResultadoComercial` | `anulacion_factura`, `ajuste_factura`, `reclamacion_infundada`, `otro` |
| `TipoReporte` | `operativo_diario`, `regulatorio_mensual` |

---

## Schemas

### UsuarioResponse
```json
{
  "id_usuario": 1,
  "nombre": "Juan Pérez",
  "documento": "12345678",
  "telefono": "555-0100",
  "email": "juan@correo.com",
  "direccion": "Av. Principal 123",
  "rol": "ciudadano"
}
```

### ReclamoResponse
```json
{
  "id_reclamo": 1,
  "id_usuario": 1,
  "fecha_recepcion": "2026-09-26",
  "canal": "web",
  "servicio": "agua",
  "categoria": "fuga",
  "urgencia": "alta",
  "descripcion": "Fuga en tubería",
  "estado": "clasificado",
  "id_normativa": 1,
  "fecha_tope": "2026-10-10",
  "fecha_cierre": null,
  "resultado": null
}
```

### NormativaResponse
```json
{
  "id_normativa": 1,
  "servicio": "agua",
  "categoria": "fuga",
  "urgencia": "alta",
  "plazo_maximo_dias": 7,
  "vigencia_desde": "2026-01-01"
}
```

### CuadrillaResponse
```json
{ "id_cuadrilla": 1, "nombre": "Cuadrilla Alpha", "especialidad": "agua", "capacidad": 3, "contacto": "555-0101" }
```

### AreaComercialResponse
```json
{ "id_area": 1, "nombre": "Facturación Central", "tipo": "facturacion", "contacto": "555-0202" }
```

### OrdenTrabajoResponse
```json
{ "id_orden": 1, "id_reclamo": 1, "cuadrilla": "Cuadrilla Alpha", "fecha_asignacion": "2026-09-26", "estado_orden": "asignada" }
```

### AvanceResponse
```json
{ "id_avance": 1, "id_orden": 1, "fecha_avance": "2026-09-26", "descripcion": "Se localizó la fuga", "estado_parcial": "iniciado" }
```

### DerivacionResponse
```json
{ "id_derivacion": 1, "id_reclamo": 1, "fecha_derivacion": "2026-09-26", "area_comercial": "facturacion", "estado_derivacion": "derivada" }
```

### ReporteResponse
```json
{
  "id_reporte": 1,
  "tipo_reporte": "operativo_diario",
  "periodo": "2026-09-26",
  "fecha_generacion": "2026-09-26T23:00:00",
  "contenido": "{...}"
}
```
