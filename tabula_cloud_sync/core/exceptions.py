"""
Excepciones personalizadas para Tabula Cloud Sync.

Este módulo define todas las excepciones personalizadas utilizadas
en la librería Tabula Cloud Sync para un mejor manejo de errores
y depuración.
"""

from typing import Any, Dict, Optional


class TabulaCloudException(Exception):
    """Excepción base para todas las excepciones de Tabula Cloud Sync."""

    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        """
        Inicializa la excepción base.

        Args:
            message: Mensaje descriptivo del error
            error_code: Código de error opcional para identificación
            details: Detalles adicionales del error
        """
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.details = details or {}

    def __str__(self) -> str:
        """Representación en string de la excepción."""
        error_str = f"TabulaCloudException: {self.message}"
        if self.error_code:
            error_str += f" (Código: {self.error_code})"
        return error_str

    def to_dict(self) -> Dict[str, Any]:
        """Convierte la excepción a un diccionario para serialización."""
        return {
            "error_type": self.__class__.__name__,
            "message": self.message,
            "error_code": self.error_code,
            "details": self.details,
        }


class AuthenticationException(TabulaCloudException):
    """Excepción para errores de autenticación."""

    def __init__(self, message: str = "Error de autenticación", **kwargs):
        super().__init__(message, error_code="AUTH_ERROR", **kwargs)


class AuthorizationException(TabulaCloudException):
    """Excepción para errores de autorización/permisos."""

    def __init__(self, message: str = "Acceso denegado", **kwargs):
        super().__init__(message, error_code="AUTHORIZATION_ERROR", **kwargs)


class ConnectionException(TabulaCloudException):
    """Excepción para errores de conexión con el servidor."""

    def __init__(
        self, message: str = "Error de conexión con el servidor", **kwargs
    ):
        super().__init__(message, error_code="CONNECTION_ERROR", **kwargs)


class TimeoutException(TabulaCloudException):
    """Excepción para errores de timeout."""

    def __init__(self, message: str = "Tiempo de espera agotado", **kwargs):
        super().__init__(message, error_code="TIMEOUT_ERROR", **kwargs)


class ValidationException(TabulaCloudException):
    """Excepción para errores de validación de datos."""

    def __init__(
        self,
        message: str = "Error de validación de datos",
        field: Optional[str] = None,
        **kwargs,
    ):
        super().__init__(message, error_code="VALIDATION_ERROR", **kwargs)
        self.field = field
        if field:
            self.details["field"] = field

    def __str__(self) -> str:
        error_str = f"ValidationException: {self.message}"
        if self.field:
            error_str += f" (Campo: {self.field})"
        if self.error_code:
            error_str += f" (Código: {self.error_code})"
        return error_str


class ConfigurationException(TabulaCloudException):
    """Excepción para errores de configuración."""

    def __init__(self, message: str = "Error de configuración", **kwargs):
        super().__init__(message, error_code="CONFIG_ERROR", **kwargs)


class ResourceNotFoundException(TabulaCloudException):
    """Excepción cuando un recurso no es encontrado."""

    def __init__(
        self,
        message: str = "Recurso no encontrado",
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        **kwargs,
    ):
        super().__init__(message, error_code="RESOURCE_NOT_FOUND", **kwargs)
        self.resource_type = resource_type
        self.resource_id = resource_id
        if resource_type:
            self.details["resource_type"] = resource_type
        if resource_id:
            self.details["resource_id"] = resource_id


class APIException(TabulaCloudException):
    """Excepción para errores de la API."""

    def __init__(
        self,
        message: str = "Error en la API",
        status_code: Optional[int] = None,
        response_data: Optional[Dict[str, Any]] = None,
        **kwargs,
    ):
        super().__init__(message, error_code="API_ERROR", **kwargs)
        self.status_code = status_code
        self.response_data = response_data or {}
        if status_code:
            self.details["status_code"] = status_code
        if response_data:
            self.details["response_data"] = response_data


class DatabaseException(TabulaCloudException):
    """Excepción para errores de base de datos."""

    def __init__(self, message: str = "Error de base de datos", **kwargs):
        super().__init__(message, error_code="DATABASE_ERROR", **kwargs)


class SyncException(TabulaCloudException):
    """Excepción para errores durante la sincronización."""

    def __init__(
        self,
        message: str = "Error durante la sincronización",
        sync_type: Optional[str] = None,
        **kwargs,
    ):
        super().__init__(message, error_code="SYNC_ERROR", **kwargs)
        self.sync_type = sync_type
        if sync_type:
            self.details["sync_type"] = sync_type


class ServiceUnavailableException(TabulaCloudException):
    """Excepción cuando el servicio no está disponible."""

    def __init__(self, message: str = "Servicio no disponible", **kwargs):
        super().__init__(message, error_code="SERVICE_UNAVAILABLE", **kwargs)


class RateLimitException(TabulaCloudException):
    """Excepción para errores de límite de tasa."""

    def __init__(
        self,
        message: str = "Límite de tasa excedido",
        retry_after: Optional[int] = None,
        **kwargs,
    ):
        super().__init__(message, error_code="RATE_LIMIT_ERROR", **kwargs)
        self.retry_after = retry_after
        if retry_after:
            self.details["retry_after"] = retry_after


class ModelValidationException(ValidationException):
    """Excepción específica para errores de validación de modelos."""

    def __init__(
        self,
        message: str = "Error de validación del modelo",
        model_name: Optional[str] = None,
        **kwargs,
    ):
        super().__init__(message, **kwargs)
        self.model_name = model_name
        if model_name:
            self.details["model_name"] = model_name


class BusinessLogicException(TabulaCloudException):
    """Excepción para errores de lógica de negocio."""

    def __init__(self, message: str = "Error de lógica de negocio", **kwargs):
        super().__init__(message, error_code="BUSINESS_LOGIC_ERROR", **kwargs)


# Funciones de utilidad para manejo de excepciones
def handle_api_error(
    status_code: int, response_data: Optional[Dict[str, Any]] = None
) -> APIException:
    """
    Crea una excepción API apropiada basada en el código de estado.

    Args:
        status_code: Código de estado HTTP
        response_data: Datos de respuesta opcionales

    Returns:
        Excepción API apropiada
    """
    error_messages = {
        400: "Solicitud incorrecta. Verifica los datos proporcionados",
        401: "Acceso denegado. Usuario o contraseña inválida",
        403: "Acceso denegado. No tienes permisos para este recurso",
        404: "Recurso no encontrado",
        405: "Método no permitido",
        408: "Tiempo de espera de la solicitud agotado",
        429: "Demasiadas solicitudes. Inténtalo de nuevo más tarde",
        500: "Error interno del servidor",
        502: "Puerta de enlace incorrecta",
        503: "Servicio no disponible",
        504: "Tiempo de espera de la puerta de enlace agotado",
    }

    message = error_messages.get(status_code, f"Error HTTP: {status_code}")

    # Crear excepción específica según el código de estado
    if status_code == 401:
        return AuthenticationException(
            message, details={"status_code": status_code}
        )
    elif status_code == 403:
        return AuthorizationException(
            message, details={"status_code": status_code}
        )
    elif status_code == 404:
        return ResourceNotFoundException(
            message, details={"status_code": status_code}
        )
    elif status_code == 429:
        return RateLimitException(
            message, details={"status_code": status_code}
        )
    elif status_code >= 500:
        return ServiceUnavailableException(
            message, details={"status_code": status_code}
        )
    else:
        return APIException(
            message, status_code=status_code, response_data=response_data
        )


def wrap_requests_exception(exc: Exception) -> TabulaCloudException:
    """
    Convierte excepciones de requests en excepciones personalizadas.

    Args:
        exc: Excepción de requests

    Returns:
        Excepción personalizada apropiada
    """
    import requests

    if isinstance(exc, requests.exceptions.ConnectionError):
        return ConnectionException(f"Error de conexión: {str(exc)}")
    elif isinstance(exc, requests.exceptions.Timeout):
        return TimeoutException(f"Tiempo de espera agotado: {str(exc)}")
    elif isinstance(exc, requests.exceptions.HTTPError):
        if hasattr(exc, "response") and exc.response is not None:
            return handle_api_error(exc.response.status_code)
        return APIException(f"Error HTTP: {str(exc)}")
    elif isinstance(exc, requests.exceptions.TooManyRedirects):
        return APIException(f"Demasiados redireccionamientos: {str(exc)}")
    elif isinstance(exc, requests.exceptions.SSLError):
        return ConnectionException(f"Error SSL: {str(exc)}")
    elif isinstance(exc, requests.exceptions.ProxyError):
        return ConnectionException(f"Error del proxy: {str(exc)}")
    elif isinstance(exc, requests.exceptions.RequestException):
        return APIException(f"Error de solicitud: {str(exc)}")
    else:
        return TabulaCloudException(f"Error desconocido: {str(exc)}")
