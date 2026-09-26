# API Documentation — Sistema de Atención de Reclamos de Servicios Básicos

**Base URL:** `http://127.0.0.1:8000`

**Formato de respuesta estándar:**
```json
{
  "data": {},
  "message": "mensaje descriptivo",
  "status": "success|error"
}
```

**Autenticación:** JWT Bearer token en header `Authorization: Bearer {token}`

---

## Auth

### POST `/auth/login`
Iniciar sesión. OAuth2 `application/x-www-form-urlencoded`.

**Request:**
```
username: documento
password: contraseña
```

**Response:**
```json
{
  "access_token": "eyJ...",
  "token_type": "bearer"
}
```

### POST `/auth/register`
Registrar nuevo usuario.

**Request Body:**
```json
{
  "nombre": "string",
  "documento": "string",
  "telefono": "string",
  "email": "string|null",
  "direccion": "string"
}
```

**Response:** `UsuarioResponse`

---

## Usuarios

### GET `/usuarios/`
Listar todos los usuarios. **Requiere auth.**

**Response:** `List[UsuarioResponse]`

### GET `/usuarios/{id}`
Obtener usuario por ID. **Requiere auth.**

**Response:** `UsuarioResponse`

### GET `/usuarios/documento/{documento}`
Obtener usuario por documento. **Requiere auth.**

**Response:** `UsuarioResponse`

### POST `/usuarios/`
Crear usuario. **Requiere auth.**

**Request Body:** `UsuarioCreate`

**Response:** `UsuarioResponse`

### PUT `/usuarios/{id}`
Actualizar usuario. **Requiere auth.**

**Request Body:** `UsuarioUpdate` (campos opcionales)

**Response:** `UsuarioResponse`

---

## Reclamos

### GET `/reclamos/`
Listar todos los reclamos. **Requiere auth.**

**Response:** `List[ReclamoResponse]`

### GET `/reclamos/{id}`
Obtener reclamo por ID. **Requiere auth.**

**Response:** `ReclamoResponse`

### POST `/reclamos/`
Crear nuevo reclamo. **Requiere auth.**

**Request Body:**
```json
{
  "id_usuario": 1,
  "canal": "presencial|telefonico|web",
  "servicio": "agua|luz",
  "categoria": "corte|facturacion|fuga|falla_tecnica",
  "urgencia": "programada|normal|alta|critica",
  "descripcion": "string"
}
```

**Response:** `ReclamoResponse`

### PUT `/reclamos/{id}`
Actualizar reclamo. **Requiere auth.**

**Request Body:** `ReclamoUpdate` (campos opcionales)

**Response:** `ReclamoResponse`

### PUT `/reclamos/{id}/clasificar`
Clasificar reclamo (servicio, categoría, urgencia). **Requiere auth.**

**Request Body:**
```json
{
  "servicio": "agua|luz",
  "categoria": "corte|facturacion|fuga|falla_tecnica",
  "urgencia": "programada|normal|alta|critica"
}
```

**Response:** `ReclamoResponse`

### PUT `/reclamos/{id}/asignar-plazo`
Asignar plazo regulatorio. **Requiere auth.**

**Request Body:**
```json
{
  "id_normativa": 1,
  "fecha_tope": "2026-10-15"
}
```

**Response:** `ReclamoResponse`

### PUT `/reclamos/{id}/resolver`
Resolver reclamo. **Requiere auth.**

**Request Body:**
```json
{
  "resultado": "resuelto|descartado|derivado",
  "detalle": "string|null"
}
```

**Response:** `ReclamoResponse`

### PUT `/reclamos/{id}/cerrar`
Cerrar reclamo. **Requiere auth.**

**Request Body:**
```json
{
  "resultado": "resuelto|descartado|derivado"
}
```

**Response:** `ReclamoResponse`

### GET `/reclamos/{id}/comprobante`
Obtener comprobante del reclamo. **Requiere auth.**

**Response:**
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

### GET `/reclamos/estado/{id_o_doc}`
Consultar estado del reclamo (público, sin auth).

**Path Parameter:** `id_o_doc` — ID del reclamo o documento del usuario

**Response:**
```json
{
  "id_reclamo": 1,
  "estado": "en_atencion_tecnica",
  "fecha_tope": "2026-10-10"
}
```

### PUT `/reclamos/{id}/contacto`
Actualizar datos de contacto del reclamante. **Requiere auth.**

**Request Body:**
```json
{
  "telefono": "string",
  "email": "string|null"
}
```

**Response:**
```json
{
  "message": "Contacto actualizado",
  "status": "success"
}
```

---

## Normativa

### GET `/normativa/`
Listar toda la normativa. **Requiere auth.**

**Response:** `List[NormativaResponse]`

### GET `/normativa/vigente?servicio=X&categoria=Y&urgencia=Z`
Obtener normativa vigente. **Requiere auth.**

**Query Parameters:**
- `servicio`: agua|luz
- `categoria`: corte|facturacion|fuga|falla_tecnica
- `urgencia`: programada|normal|alta|critica

**Response:** `NormativaResponse`

### POST `/normativa/`
Crear normativa. **Requiere auth.**

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

**Response:** `NormativaResponse`

### PUT `/normativa/{id}`
Actualizar normativa. **Requiere auth.**

**Request Body:** Campos opcionales de `NormativaCreate`

**Response:** `NormativaResponse`

---

## Cuadrillas

### GET `/cuadrillas/`
Listar cuadrillas. **Requiere auth.**

**Response:** `List[CuadrillaResponse]`

### GET `/cuadrillas/{id}`
Obtener cuadrilla. **Requiere auth.**

**Response:** `CuadrillaResponse`

### GET `/cuadrillas/disponibles/{especialidad}`
Obtener cuadrillas disponibles por especialidad. **Requiere auth.**

**Response:** `List[CuadrillaResponse]`

### POST `/cuadrillas/`
Crear cuadrilla. **Requiere auth.**

**Request Body:**
```json
{
  "nombre": "Cuadrilla Alpha",
  "especialidad": "agua",
  "capacidad": 3,
  "contacto": "555-0101"
}
```

**Response:** `CuadrillaResponse`

### PUT `/cuadrillas/{id}`
Actualizar cuadrilla. **Requiere auth.**

**Request Body:** Campos opcionales

**Response:** `CuadrillaResponse`

### DELETE `/cuadrillas/{id}`
Eliminar cuadrilla. **Requiere auth.**

**Response:**
```json
{
  "message": "Cuadrilla eliminada",
  "status": "success"
}
```

---

## Áreas Comerciales

### GET `/areas-comerciales/`
Listar áreas. **Requiere auth.**

**Response:** `List[AreaComercialResponse]`

### GET `/areas-comerciales/{id}`
Obtener área. **Requiere auth.**

**Response:** `AreaComercialResponse`

### POST `/areas-comerciales/`
Crear área. **Requiere auth.**

**Request Body:**
```json
{
  "nombre": "Facturación Central",
  "tipo": "facturacion|cobranza",
  "contacto": "555-0202"
}
```

**Response:** `AreaComercialResponse`

### PUT `/areas-comerciales/{id}`
Actualizar área. **Requiere auth.**

**Request Body:** Campos opcionales

**Response:** `AreaComercialResponse`

### DELETE `/areas-comerciales/{id}`
Eliminar área. **Requiere auth.**

**Response:**
```json
{
  "message": "Área comercial eliminada",
  "status": "success"
}
```

---

## Seguimiento

### GET `/seguimiento/ordenes`
Listar órdenes de trabajo. **Requiere auth.**

**Response:** `List[OrdenTrabajoResponse]`

### GET `/seguimiento/ordenes/{id}`
Obtener orden. **Requiere auth.**

**Response:** `OrdenTrabajoResponse`

### GET `/seguimiento/ordenes/reclamo/{id_reclamo}`
Obtener orden por reclamo. **Requiere auth.**

**Response:** `OrdenTrabajoResponse`

### POST `/seguimiento/ordenes`
Crear orden de trabajo. **Requiere auth.**

**Request Body:**
```json
{
  "id_reclamo": 1,
  "cuadrilla": "Cuadrilla Alpha",
  "fecha_asignacion": "2026-09-26"
}
```

**Response:** `OrdenTrabajoResponse`

### PUT `/seguimiento/ordenes/{id}`
Actualizar orden. **Requiere auth.**

**Request Body:** `{"estado_orden": "asignada|en_curso|resuelta"}`

**Response:** `OrdenTrabajoResponse`

### GET `/seguimiento/avances/{id_orden}`
Listar avances de una orden. **Requiere auth.**

**Response:** `List[AvanceResponse]`

### POST `/seguimiento/avances`
Registrar avance. **Requiere auth.**

**Request Body:**
```json
{
  "id_orden": 1,
  "fecha_avance": "2026-09-26",
  "descripcion": "Se localizó la fuga",
  "estado_parcial": "iniciado|en_proceso|verificado"
}
```

**Response:** `AvanceResponse`

### GET `/seguimiento/derivaciones/{id_reclamo}`
Obtener derivación de un reclamo. **Requiere auth.**

**Response:** `DerivacionResponse`

### POST `/seguimiento/derivaciones`
Crear derivación comercial. **Requiere auth.**

**Request Body:**
```json
{
  "id_reclamo": 1,
  "fecha_derivacion": "2026-09-26",
  "area_comercial": "facturacion|cobranza"
}
```

**Response:** `DerivacionResponse`

### PUT `/seguimiento/derivaciones/{id}`
Actualizar derivación. **Requiere auth.**

**Request Body:** `{"estado_derivacion": "derivada|resuelta"}`

**Response:** `DerivacionResponse`

---

## Plazos (P4 — Vigilancia)

### POST `/plazos/verificar-vencimientos`
Detectar reclamos próximos a vencer. **Requiere auth.**

**Response:**
```json
{
  "avisos": [
    {"id_reclamo": 1, "fecha_tope": "2026-10-01", "dias_restantes": 5}
  ],
  "total": 1
}
```

### POST `/plazos/verificar-vencidos`
Detectar reclamos vencidos. **Requiere auth.**

**Response:**
```json
{
  "alertas": [
    {"id_reclamo": 2, "fecha_tope": "2026-09-20", "exceso_dias": 6}
  ],
  "total": 1
}
```

### POST `/plazos/verificar-criticos`
Detectar reclamos críticos. **Requiere auth.**

**Response:**
```json
{
  "alarmas": [
    {"id_reclamo": 3, "servicio": "agua", "categoria": "fuga", "urgencia": "critica"}
  ],
  "total": 1
}
```

---

## Reportes (P5)

### GET `/reportes/`
Listar reportes generados. **Requiere auth.**

**Response:** `List[ReporteResponse]`

### POST `/reportes/diario`
Generar reporte operativo diario. **Requiere auth.**

**Response:**
```json
{
  "message": "Reporte diario generado",
  "id_reporte": 1
}
```

### POST `/reportes/mensual`
Generar reporte regulatorio mensual. **Requiere auth.**

**Response:**
```json
{
  "message": "Reporte mensual generado",
  "id_reporte": 2
}
```

---

## Schemas

### UsuarioResponse
```json
{
  "id_usuario": 1,
  "nombre": "Juan Pérez",
  "documento": "12345678",
  "telefono": "555-0100",
  "email": "juan@email.com",
  "direccion": "Av. Principal 123"
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
  "id_normativa": null,
  "fecha_tope": null,
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
{
  "id_cuadrilla": 1,
  "nombre": "Cuadrilla Alpha",
  "especialidad": "agua",
  "capacidad": 3,
  "contacto": "555-0101"
}
```

### AreaComercialResponse
```json
{
  "id_area": 1,
  "nombre": "Facturación Central",
  "tipo": "facturacion",
  "contacto": "555-0202"
}
```

### OrdenTrabajoResponse
```json
{
  "id_orden": 1,
  "id_reclamo": 1,
  "cuadrilla": "Cuadrilla Alpha",
  "fecha_asignacion": "2026-09-26",
  "estado_orden": "asignada"
}
```

### AvanceResponse
```json
{
  "id_avance": 1,
  "id_orden": 1,
  "fecha_avance": "2026-09-26",
  "descripcion": "Se localizó la fuga",
  "estado_parcial": "iniciado"
}
```

### DerivacionResponse
```json
{
  "id_derivacion": 1,
  "id_reclamo": 1,
  "fecha_derivacion": "2026-09-26",
  "area_comercial": "facturacion",
  "estado_derivacion": "derivada"
}
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
