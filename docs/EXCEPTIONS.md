# Excepciones Personalizadas de Tabula Cloud Sync

Este documento describe el sistema de excepciones personalizadas implementado en la librería Tabula Cloud Sync para un mejor manejo de errores y depuración.

## Estructura de Excepciones

### Excepción Base

**`TabulaCloudException`** - Excepción base para todas las excepciones de la librería.

```python
from tabula_cloud_sync import TabulaCloudException

try:
    # código que puede fallar
    pass
except TabulaCloudException as e:
    print(f"Error: {e.message}")
    print(f"Código: {e.error_code}")
    print(f"Detalles: {e.details}")
    # Convertir a diccionario para logging
    error_dict = e.to_dict()
```

### Excepciones de Autenticación y Autorización

#### `AuthenticationException`

Para errores de autenticación (credenciales inválidas, token expirado, etc.).

```python
from tabula_cloud_sync import AuthenticationException

try:
    session = Session("token_invalido")
except AuthenticationException as e:
    print("Renovar token de autenticación")
```

#### `AuthorizationException`

Para errores de autorización (permisos insuficientes).

```python
from tabula_cloud_sync import AuthorizationException

try:
    # operación que requiere permisos especiales
    pass
except AuthorizationException as e:
    print("Usuario sin permisos suficientes")
```

### Excepciones de Conectividad

#### `ConnectionException`

Para errores de conexión con el servidor.

```python
from tabula_cloud_sync import ConnectionException

try:
    response = session.get("api/endpoint/")
except ConnectionException as e:
    print("Problemas de conectividad - implementar reintento")
```

#### `TimeoutException`

Para errores de timeout en las solicitudes.

```python
from tabula_cloud_sync import TimeoutException

try:
    response = session.get("api/endpoint/", timeout=5)
except TimeoutException as e:
    print("Solicitud tomó demasiado tiempo")
```

### Excepciones de Validación

#### `ValidationException`

Para errores de validación de datos generales.

```python
from tabula_cloud_sync import ValidationException

def validar_contacto(data):
    if not data.get("nombre"):
        raise ValidationException(
            "El nombre es requerido",
            field="nombre",
            details={"provided_data": data}
        )

try:
    validar_contacto({"nombre": ""})
except ValidationException as e:
    print(f"Campo inválido: {e.field}")
```

#### `ModelValidationException`

Para errores específicos de validación de modelos.

```python
from tabula_cloud_sync import ModelValidationException

try:
    # validación de modelo Pydantic
    pass
except ModelValidationException as e:
    print(f"Error en modelo {e.model_name}: {e.message}")
```

### Excepciones de API

#### `APIException`

Para errores generales de la API.

```python
from tabula_cloud_sync import APIException

try:
    response = session.post("api/endpoint/", json_data=data)
except APIException as e:
    print(f"Error API: {e.status_code} - {e.message}")
    print(f"Respuesta: {e.response_data}")
```

#### `ResourceNotFoundException`

Para cuando un recurso no es encontrado.

```python
from tabula_cloud_sync import ResourceNotFoundException

try:
    contact = session.get("api/contacts/999999/")
except ResourceNotFoundException as e:
    print(f"Recurso no encontrado: {e.resource_type} ID: {e.resource_id}")
```

#### `RateLimitException`

Para errores de límite de tasa.

```python
from tabula_cloud_sync import RateLimitException

try:
    response = session.get("api/endpoint/")
except RateLimitException as e:
    if e.retry_after:
        print(f"Esperar {e.retry_after} segundos antes de reintentar")
```

#### `ServiceUnavailableException`

Para cuando el servicio no está disponible.

```python
from tabula_cloud_sync import ServiceUnavailableException

try:
    response = session.get("api/endpoint/")
except ServiceUnavailableException as e:
    print("Servicio temporalmente no disponible")
    # Implementar lógica de reintento exponencial
```

### Excepciones de Negocio

#### `BusinessLogicException`

Para errores de lógica de negocio.

```python
from tabula_cloud_sync import BusinessLogicException

def procesar_venta(items):
    if not items:
        raise BusinessLogicException(
            "No se puede procesar una venta sin items",
            details={"items_count": len(items)}
        )
```

#### `SyncException`

Para errores durante procesos de sincronización.

```python
from tabula_cloud_sync import SyncException

try:
    sincronizar_contactos()
except SyncException as e:
    print(f"Error en sincronización {e.sync_type}: {e.message}")
```

### Excepciones de Sistema

#### `ConfigurationException`

Para errores de configuración.

```python
from tabula_cloud_sync import ConfigurationException

def cargar_config():
    if not config_existe():
        raise ConfigurationException(
            "Archivo de configuración no encontrado",
            details={"config_path": "/path/to/config"}
        )
```

#### `DatabaseException`

Para errores de base de datos.

```python
from tabula_cloud_sync import DatabaseException

try:
    # operación de base de datos
    pass
except DatabaseException as e:
    print("Error de base de datos - verificar conexión")
```

## Funciones de Utilidad

### `handle_api_error(status_code, response_data=None)`

Convierte códigos de estado HTTP en excepciones apropiadas.

```python
from tabula_cloud_sync import handle_api_error

try:
    # Cuando recibes un error HTTP
    if response.status_code != 200:
        raise handle_api_error(response.status_code, response.json())
except Exception as e:
    # Se convertirá en la excepción apropiada
    print(f"Error: {e}")
```

### `wrap_requests_exception(exc)`

Convierte excepciones de la librería `requests` en excepciones personalizadas.

```python
from tabula_cloud_sync import wrap_requests_exception
import requests

try:
    response = requests.get("https://api.ejemplo.com")
except requests.RequestException as e:
    raise wrap_requests_exception(e)
```

## Mejores Prácticas

### 1. Manejo Específico por Tipo

```python
try:
    # operación
    pass
except AuthenticationException:
    # renovar token
    pass
except ConnectionException:
    # reintento con backoff
    pass
except ValidationException as e:
    # logging de errores de validación
    logger.warning(f"Validación falló: {e.field} - {e.message}")
except TabulaCloudException as e:
    # manejo genérico para otras excepciones de la librería
    logger.error(e.to_dict())
except Exception as e:
    # errores inesperados
    logger.critical(f"Error inesperado: {str(e)}")
```

### 2. Logging Estructurado

```python
import logging

try:
    # operación
    pass
except TabulaCloudException as e:
    logging.error("Error de Tabula Cloud", extra=e.to_dict())
```

### 3. Retry Logic

```python
import time
from tabula_cloud_sync import TimeoutException, RateLimitException

def operacion_con_retry(max_retries=3):
    for attempt in range(max_retries):
        try:
            return realizar_operacion()
        except (TimeoutException, RateLimitException) as e:
            if attempt == max_retries - 1:
                raise

            wait_time = 2 ** attempt  # Backoff exponencial
            if isinstance(e, RateLimitException) and e.retry_after:
                wait_time = e.retry_after

            time.sleep(wait_time)
```

### 4. Contexto de Error Enriquecido

```python
try:
    procesar_contacto(contacto_data)
except ValidationException as e:
    # Agregar contexto adicional
    e.details.update({
        "user_id": current_user.id,
        "timestamp": datetime.now().isoformat(),
        "operation": "procesar_contacto"
    })
    raise
```

## Migración desde ValueError

Si tienes código existente que usa `ValueError`, puedes migrarlo gradualmente:

### Antes:

```python
try:
    response = session.get("api/endpoint/")
except ValueError as e:
    print(f"Error: {str(e)}")
```

### Después:

```python
try:
    response = session.get("api/endpoint/")
except (TabulaCloudException, ValueError) as e:
    if isinstance(e, TabulaCloudException):
        print(f"Error específico: {e.message} (Código: {e.error_code})")
    else:
        print(f"Error genérico: {str(e)}")
```

## Integración con FastAPI

```python
from fastapi import HTTPException
from tabula_cloud_sync import TabulaCloudException, AuthenticationException

@app.get("/api/contacts/")
async def get_contacts():
    try:
        # lógica de la API
        pass
    except AuthenticationException:
        raise HTTPException(status_code=401, detail="Token inválido")
    except TabulaCloudException as e:
        raise HTTPException(
            status_code=500,
            detail={"error": e.message, "code": e.error_code}
        )
```

## Testing

```python
import pytest
from tabula_cloud_sync import ValidationException

def test_validacion_contacto():
    with pytest.raises(ValidationException) as exc_info:
        validar_contacto({"nombre": ""})

    assert exc_info.value.field == "nombre"
    assert "requerido" in exc_info.value.message
```
