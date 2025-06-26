# Esquema de Funcionamiento - Módulo Sincronizador

## 📋 Descripción General

El **Sincronizador** es un servicio daemon que gestiona la sincronización de documentos electrónicos (Facturas, Notas de Crédito, Nota de Débito, Autofactura y Nota de Remisión) entre una base de datos local (MySQL, PostgreSQL, etc.) y la API externa de Tabula. Opera en un bucle continuo verificando diferentes estados de los documentos y manteniendo la sincronización con el sistema de facturación electrónica.

## 🏗️ Arquitectura del Sistema

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│   Base Datos    │────▶│  Sincronizador   │────▶│   API Tabula    │
│      Local      │     │     (Daemon)     │     │   (Externa)     │
└─────────────────┘     └──────────────────┘     └─────────────────┘
                                │
                                ▼
                        ┌──────────────────┐
                        │   SET Sistema    │
                        │   Tributario     │
                        └──────────────────┘
```

## 🔄 Flujo Principal del Proceso

### 1. **Inicialización del Sistema**

```python
# Carga de configuración
config = configparser.ConfigParser()
config.read('config.ini')
token = config_sincronizador.get('token', None)
intervalo = int(config_sincronizador.get('intervalo', 10)) * 60

# Establecimiento de sesión HTTP
session = Session(token=token)
```

### 2. **Bucle Principal de Sincronización**

El sistema ejecuta las siguientes funciones en orden secuencial:
1. `check_timbrados(conn)` - Verifica estado de los timbrados y punto de expedición habilitado
2. `check_fe_estado(conn)` - Verificar estados de Facturas Electrónicas
2. `check_nce_estado(conn)` - Verificar estados de Notas de Crédito
3. `check_factura_pendiente(conn)` - Procesar documentos pendientes
4. `check_documento_error(conn)` - Reenviar documentos con errores

## 🧩 Componentes y Funciones Detalladas

### 🔧 **Funciones Auxiliares**

#### `round_ext(num, decimales=0)`

- **Propósito**: Función de redondeo personalizada para cálculos financieros
- **Lógica**: Redondeo tradicional (0.5 hacia arriba)
- **Uso**: Cálculos de descuentos y totales de documentos

#### `verificar_datos_contactos(conn, contacto_id)`

```python
# Flujo de verificación de contactos
contacto_local = queries.get_dato_contacto(conn, contacto_id)
contacto_api = session.get(CONTACTO_ID.format(id=contacto_id))

if contacto_api.status_code == 200:
    # Actualizar contacto existente
    session.put(CONTACTO_ID.format(id=contacto_id), json_data=contacto_local)
elif contacto_api.status_code == 404:
    # Crear nuevo contacto
    session.post(CONTACTO, json_data=contacto_local)
```

**Validaciones que realiza:**

- Consulta datos contra SET (Sistema Tributario)
- Determina tipo de documento (RUC/CI)
- Calcula dígito verificador para RUC
- Establece tipo de persona (JURÍDICO/FÍSICO)

#### `verificar_datos_items(lista_items)`

```python
# Proceso de sincronización de items
for item in lista_items:
    # Verificar existencia en API
    response = session.get(ITEM_SECUENCIA.format(secuencia=item['idArticulo']))

    if response.status_code == 200:
        # Actualizar item existente
        session.put(ITEM_ID.format(id=data['id']), json_data=item_dicc)
    elif response.status_code == 404:
        # Crear nuevo item
        session.post(ITEM, json_data=item_dicc)
```

**Retorna**: Diccionario de mapeo `{id_local: id_api}`

## 📊 Estados y Tipos de Documentos

### 🔄 **Ciclo de Vida de Documentos**

```
[PENDIENTE] ──envío──▶ [ENVIADO] ──verificación──▶ [APROBADO/RECHAZADO]
     ▲                                                      │
     └──────────────── regeneración ◀────── [ERROR] ◀──────┘
```

### 📋 **Tipos de Documentos Soportados**

| Tipo                              | Código | Operación | Comprobante | Formulario |
| --------------------------------- | ------ | --------- | ----------- | ---------- |
| Factura Electrónica (FE)          | 16     | 1         | 16          | 302        |
| Nota de Crédito Electrónica (NCE) | 17     | 11        | 17          | 302        |

## 🔍 Procesos Detallados

### 1. **`check_fe_estado(conn)`**

- **Propósito**: Verificar estado de facturas ya enviadas a la API
- **Consulta**: `queries.get_fe_enviado(conn)`
- **Proceso**:
  ```python
  for documento in de_enviado:
      response = session.get(DOCUMENTO_VERIFICAR_ESTADO.format(referencia=documento['referencia_fe']))
      if response.status_code == 200:
          queries.update_fe_db_estado(conn, documento, respuesta)
  ```

### 2. **`check_nce_estado(conn)`**

- **Propósito**: Verificar estado de notas de crédito ya enviadas
- **Consulta**: `queries.get_nce_enviado(conn)`
- **Proceso**: Similar a FE pero con referencia NCE

### 3. **`check_factura_pendiente(conn)`**

- **Propósito**: Procesar y enviar documentos pendientes
- **Consultas**:
  - `queries.get_fe_pendiente(conn)` - Facturas pendientes
  - `queries.get_nce_pendiente(conn)` - Notas de crédito pendientes

#### **Proceso para Facturas Electrónicas:**

```python
# 1. Validar contacto
contacto = verificar_datos_contactos(conn, documento['idcliente'])

# 2. Crear documento base
_temp_documento = Documento(
    sucursal=sucursal_id,
    formulario=302,
    operacion=1,
    comprobante=16,
    # ... otros campos
)

# 3. Procesar detalles
lista_detalles = queries.get_detalle_fe(conn, ...)
dicc_key_items = verificar_datos_items(lista_detalles)

# 4. Crear detalles del documento
for row_item in lista_detalles:
    detalle_item = DocumentoDetalle(
        documento=_temp_documento,
        item=dicc_key_items[row_item['idArticulo']],
        cantidad=row_item['Cantidad'],
        precio=row_item['Precio'],
        # ... otros campos
    )
    _temp_documento.detalles.append(detalle_item)

# 5. Calcular totales y enviar
_temp_documento.set_calcular_totales()
response = session.post(DOCUMENTO, json_data=datos)
```

#### **Proceso para Notas de Crédito:**

Similar al proceso de facturas pero con:

- `operacion=11`, `comprobante=17`
- Manejo de `DocumentoAsociado` (documento de referencia)
- Cálculo diferente de descuentos

### 4. **`check_documento_error(conn)`**

- **Propósito**: Reenviar documentos que tuvieron errores
- **Consultas**:
  - `queries.get_fe_reenviar(conn)`
  - `queries.get_nce_reenviar(conn)`

**Proceso:**

```python
# 1. Validar contacto nuevamente
contacto = verificar_datos_contactos(conn, documento['idcliente'])

# 2. Regenerar XML del documento
response = session.post(DOCUMENTO_REGENERAR_XML.format(referencia=referencia))

# 3. Actualizar estado si es exitoso
if response.status_code == 200:
    queries.update_fe_db_reenviado(conn, documento)

# 4. Generar lote
session.post(GENERAR_LOTES_DE)
```

## 📋 Estructura de Datos

### **Documento Base**

```python
{
    "sucursal": int,
    "formulario": 302,
    "cdc": str,
    "cds": str,
    "contacto": int,
    "fecha_documento": date,
    "hora_documento": time,
    "establecimiento": str(3),  # Zero-padded
    "punto_expedicion": str(3), # Zero-padded
    "numero_documento": int,
    "numero_comprobante": str,  # "XXX-XXX-XXXXXXX"
    "operacion": int,
    "comprobante": int,
    "timbrado": int,
    "moneda": "PYG",
    "tasa_cambio": Decimal("1.0"),
    "detalles": [DocumentoDetalle],
    "documentos_asociados": [DocumentoAsociado]  # Solo NCE
}
```

### **DocumentoDetalle**

```python
{
    "documento": Documento,
    "orden": int,
    "item_tipo": "P",
    "centro_costo": 1,
    "item_gtin": str,  # Código de barras validado
    "moneda": "PYG",
    "item": int,  # ID del item en API
    "item_secuencia": int,  # ID local del item
    "item_nombre": str,
    "cantidad": decimal,
    "precio": decimal,
    "descuento": decimal,
    "porcentaje_descuento": decimal,
    "tasa_iva": decimal,
    "afectacion_iva": 1,
    "proporcion_iva": 100
}
```

### **DocumentoAsociado** (Solo NCE)

```python
{
    "tipo_documento": int,  # 1=CDC, 2=Manual
    "cdc": str,  # Si tipo_documento=1
    "timbrado": int,
    "numero_comprobante": str,
    "tipo_documento_asociado": 1,
    "fecha_documento": date
}
```

## ⚙️ Configuración del Sistema

### **config.ini**

```ini
[mysql]
host = 192.168.0.190
user = root
password = password
database = distpro
port = 3306

[sincronizador]
debug = True
token = d522ce261c6d857428a6c535a3e04b744fba9dcc
intervalo = 1  # minutos
```

### **URLs de API (core/urls.py)**

```python
# Items
ITEM_SECUENCIA = 'api/items/v1/items/secuencia/{secuencia}/'
ITEM_ID = 'api/items/v1/items/{id}/'
ITEM = 'api/items/v1/items/'

# Contactos
CONTACTO = 'api/contacts/v1/contacts/'
CONTACTO_ID = 'api/contacts/v1/contacts/{id}/'
CONTACTO_BUSCAR_SET = 'api/contacts/v1/buscarset/{documento}/'

# Documentos
DOCUMENTO = 'api/documents/v1/documentos/'
DOCUMENTO_VERIFICAR_ESTADO = 'api/documents/v1/documentos/{referencia}/verificar-estado-de/'
DOCUMENTO_REGENERAR_XML = 'api/documents/v1/documentos/{referencia}/regenerar-xml/'
GENERAR_LOTES_DE = 'api/sifen/generar-lote/'
```

## 📝 Logging y Monitoreo

### **Eventos Registrados**

- ✅ **Conexión exitosa**: "Conexión a la base de datos exitosa."
- 📤 **Documento enviado**: "Factura informada: {numero_comprobante}"
- 🔄 **Estado actualizado**: "Documento {referencia} actualizado"
- ❌ **Errores de API**: Status code y texto de respuesta
- 🔁 **Regeneración**: "Documento regenerado"
- 📦 **Lotes generados**: "Lote de Factura Generado..."

### **Manejo de Errores**

- **Errores de conexión BD**: Log error + sleep + reintento
- **Errores de API 400**: Log detallado + continúa
- **Errores de API otros**: Log + continúa
- **KeyboardInterrupt**: Salida limpia
- **Excepciones no controladas**: Log traceback + continúa

## 🚨 Puntos Críticos y Mejoras Identificadas

### **Problemas Actuales**

1. **Duplicación de código**: Validación de código de barras GTIN repetida en líneas 247-249 y 252-253
2. **Manejo de None**: Funciones pueden retornar None sin manejo adecuado
3. **Timeouts hardcodeados**: timeout=20 en requests

### **Validaciones Importantes**

- **Código de barras**: Usa `validar_gtin()` antes de asignar
- **Contactos SET**: Valida contra sistema tributario paraguayo
- **Formato de comprobante**: "XXX-XXX-XXXXXXX" (establecimiento-punto-numero)
- **CDC**: 44 caracteres para documentos electrónicos

### **Flujo de Datos Crítico**

```
BD Local → Validar Contacto → SET → API Tabula → Generar Lote → Verificar Estado → Actualizar BD
```

## 🔧 Dependencias Principales

- **core.session.Session**: Cliente HTTP con autenticación
- **queries**: Módulo de consultas SQL
- **models.documentos**: Modelos Pydantic para documentos
- **utils.commons**: Funciones utilitarias (get_dv, validar_gtin)
- **db.Database**: Conexión a MySQL

## 📊 Métricas y Rendimiento

- **Intervalo por defecto**: 10 minutos
- **Timeout requests**: 20 segundos
- **Procesamiento**: Secuencial (un documento a la vez)
- **Conexión BD**: Nueva conexión por ciclo
- **Persistencia**: Session HTTP reutilizada

---

**Última actualización**: 26 de junio de 2025
**Versión del documento**: 1.0
