"""Core modules para Tabula Cloud Sync."""

from .exceptions import (
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
    SyncException,
    TabulaCloudException,
    TimeoutException,
    ValidationException,
    handle_api_error,
    wrap_requests_exception,
)
from .session import Session

__version__ = "1.0.0"
__all__ = [
    "Session",
    "TabulaCloudException",
    "AuthenticationException",
    "AuthorizationException",
    "ConnectionException",
    "TimeoutException",
    "ValidationException",
    "ConfigurationException",
    "ResourceNotFoundException",
    "APIException",
    "DatabaseException",
    "SyncException",
    "ServiceUnavailableException",
    "RateLimitException",
    "ModelValidationException",
    "BusinessLogicException",
    "handle_api_error",
    "wrap_requests_exception",
]
