"""
Ejemplo de uso de las excepciones personalizadas de Tabula Cloud Sync.

Este archivo muestra cómo usar las excepciones personalizadas para un mejor
manejo de errores y depuración en tu aplicación.
"""

# Importar las excepciones personalizadas
from tabula_cloud_sync import (
    APIException,
    AuthenticationException,
    AuthorizationException,
    BusinessLogicException,
    ConfigurationException,
    ConnectionException,
    DatabaseException,
    ModelValidationException,
    RateLimitException,
    ResourceNotFoundException,
    ServiceUnavailableException,
    Session,
    SyncException,
    TabulaCloudException,
    TimeoutException,
    ValidationException,
)


def ejemplo_basico_manejo_excepciones():
    """Ejemplo básico de manejo de excepciones."""

    try:
        # Intentar crear una sesión con token inválido
        session = Session("token_invalido")
        response = session.get("api/v1/contacts/")

    except AuthenticationException as e:
        print(f"Error de autenticación: {e.message}")
        print(f"Código de error: {e.error_code}")
        print(f"Detalles: {e.details}")

    except ConnectionException as e:
        print(f"Error de conexión: {e.message}")
        # Implementar lógica de reintento

    except TimeoutException as e:
        print(f"Timeout: {e.message}")
        # Implementar lógica de reintento con timeout mayor

    except TabulaCloudException as e:
        # Captura cualquier otra excepción personalizada
        print(f"Error de Tabula Cloud: {e.message}")
        print(f"Tipo: {e.__class__.__name__}")

    except Exception as e:
        # Captura errores no esperados
        print(f"Error inesperado: {str(e)}")


def ejemplo_validacion_datos():
    """Ejemplo de validación de datos con excepciones personalizadas."""

    def validar_contacto(data):
        """Valida datos de contacto."""
        if not data.get("nombre"):
            raise ValidationException(
                "El nombre es requerido",
                field="nombre",
                details={"provided_data": data},
            )

        if not data.get("numedocu"):
            raise ValidationException(
                "El número de documento es requerido",
                field="numedocu",
                details={"provided_data": data},
            )

        # Validaciones de negocio específicas
        if len(data.get("numedocu", "")) < 3:
            raise BusinessLogicException(
                "El número de documento debe tener al menos 3 caracteres",
                details={"field": "numedocu", "value": data.get("numedocu")},
            )

    # Datos de prueba inválidos
    datos_invalidos = {"nombre": ""}

    try:
        validar_contacto(datos_invalidos)
    except ValidationException as e:
        print(f"Error de validación en campo '{e.field}': {e.message}")
        return False
    except BusinessLogicException as e:
        print(f"Error de lógica de negocio: {e.message}")
        return False

    return True


def ejemplo_manejo_api():
    """Ejemplo de manejo de errores de API."""

    def procesar_respuesta_api(session, endpoint):
        """Procesa una respuesta de API con manejo de errores."""
        try:
            response = session.get(endpoint)
            return response.json()

        except AuthenticationException:
            print("Token expirado o inválido. Renovando autenticación...")
            # Lógica para renovar token
            return None

        except AuthorizationException:
            print("No tienes permisos para acceder a este recurso.")
            return None

        except ResourceNotFoundException as e:
            print(f"Recurso no encontrado: {e.message}")
            if e.resource_type:
                print(f"Tipo de recurso: {e.resource_type}")
            return None

        except RateLimitException as e:
            print(f"Límite de tasa excedido: {e.message}")
            if e.retry_after:
                print(f"Reintentar después de {e.retry_after} segundos")
            return None

        except ServiceUnavailableException:
            print("Servicio temporalmente no disponible. Reintentando...")
            # Implementar lógica de reintento exponencial
            return None

        except APIException as e:
            print(f"Error de API: {e.message}")
            if e.status_code:
                print(f"Código de estado HTTP: {e.status_code}")
            return None

    # Ejemplo de uso
    try:
        session = Session("mi_token")
        datos = procesar_respuesta_api(session, "api/v1/contacts/123/")
        if datos:
            print("Datos obtenidos exitosamente")
    except Exception as e:
        print(f"Error inesperado: {str(e)}")


def ejemplo_sincronizacion():
    """Ejemplo de manejo de errores durante sincronización."""

    def sincronizar_datos(source, target):
        """Sincroniza datos entre dos fuentes."""
        try:
            # Simular proceso de sincronización
            print("Iniciando sincronización...")

            # Simular diferentes tipos de errores
            import random

            error_type = random.choice(
                ["database", "validation", "connection", "business", "success"]
            )

            if error_type == "database":
                raise DatabaseException(
                    "Error al conectar con la base de datos",
                    details={"database": "tabula_local", "source": source},
                )
            elif error_type == "validation":
                raise ModelValidationException(
                    "Datos inválidos encontrados durante la sincronización",
                    model_name="Contact",
                    details={"invalid_records": 5},
                )
            elif error_type == "connection":
                raise ConnectionException(
                    "Pérdida de conexión durante la sincronización"
                )
            elif error_type == "business":
                raise BusinessLogicException(
                    "Regla de negocio violada: No se pueden sincronizar "
                    "contactos duplicados"
                )
            else:
                print("Sincronización completada exitosamente")
                return True

        except DatabaseException as e:
            print(f"Error de base de datos: {e.message}")
            # Implementar lógica de reconexión
            return False

        except ModelValidationException as e:
            print(
                f"Error de validación del modelo {e.model_name}: {e.message}"
            )
            # Log de registros inválidos para revisión manual
            return False

        except SyncException as e:
            print(f"Error durante la sincronización: {e.message}")
            if e.sync_type:
                print(f"Tipo de sincronización: {e.sync_type}")
            return False

        except TabulaCloudException as e:
            print(f"Error de Tabula Cloud: {e.message}")
            # Convertir a diccionario para logging
            error_dict = e.to_dict()
            print(f"Detalles del error: {error_dict}")
            return False

    # Ejemplo de uso
    resultado = sincronizar_datos("local_db", "tabula_cloud")
    if resultado:
        print("Sincronización exitosa")
    else:
        print("Sincronización falló")


def ejemplo_configuracion():
    """Ejemplo de manejo de errores de configuración."""

    def cargar_configuracion(config_path):
        """Carga configuración con manejo de errores."""
        try:
            # Simular carga de configuración
            import os

            if not os.path.exists(config_path):
                raise ConfigurationException(
                    f"Archivo de configuración no encontrado: {config_path}",
                    details={"config_path": config_path},
                )

            # Simular configuración inválida
            raise ConfigurationException(
                "Configuración de API incompleta",
                details={
                    "missing_fields": ["api_token", "base_url"],
                    "config_file": config_path,
                },
            )

        except ConfigurationException as e:
            print(f"Error de configuración: {e.message}")
            print(f"Detalles: {e.details}")
            # Implementar configuración por defecto o solicitar al usuario
            return None

    # Ejemplo de uso
    config = cargar_configuracion("/path/to/config.json")


if __name__ == "__main__":
    print(
        "=== Ejemplos de Excepciones Personalizadas de Tabula Cloud Sync ===\n"
    )

    print("1. Ejemplo básico de manejo de excepciones:")
    ejemplo_basico_manejo_excepciones()
    print()

    print("2. Ejemplo de validación de datos:")
    ejemplo_validacion_datos()
    print()

    print("3. Ejemplo de manejo de API:")
    ejemplo_manejo_api()
    print()

    print("4. Ejemplo de sincronización:")
    ejemplo_sincronizacion()
    print()

    print("5. Ejemplo de configuración:")
    ejemplo_configuracion()
    print()

    print("=== Fin de ejemplos ===")
