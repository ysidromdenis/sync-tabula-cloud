"""
Tests para las excepciones personalizadas de Tabula Cloud Sync.
"""

from unittest.mock import Mock

import pytest
import requests

from tabula_cloud_sync.core.exceptions import (
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


class TestTabulaCloudException:
    """Test para la excepción base."""

    def test_excepcion_basica(self):
        """Test de la excepción básica con mensaje."""
        exc = TabulaCloudException("Error de prueba")
        assert exc.message == "Error de prueba"
        assert exc.error_code is None
        assert exc.details == {}

    def test_excepcion_completa(self):
        """Test de la excepción con todos los parámetros."""
        details = {"field": "test", "value": 123}
        exc = TabulaCloudException(
            "Error completo", error_code="TEST_ERROR", details=details
        )
        assert exc.message == "Error completo"
        assert exc.error_code == "TEST_ERROR"
        assert exc.details == details

    def test_to_dict(self):
        """Test de conversión a diccionario."""
        exc = TabulaCloudException(
            "Error de prueba",
            error_code="TEST_ERROR",
            details={"key": "value"},
        )
        result = exc.to_dict()
        expected = {
            "error_type": "TabulaCloudException",
            "message": "Error de prueba",
            "error_code": "TEST_ERROR",
            "details": {"key": "value"},
        }
        assert result == expected

    def test_str_representation(self):
        """Test de representación en string."""
        exc = TabulaCloudException("Test error", error_code="TEST_001")
        assert (
            str(exc) == "TabulaCloudException: Test error (Código: TEST_001)"
        )

        exc_no_code = TabulaCloudException("Test error")
        assert str(exc_no_code) == "TabulaCloudException: Test error"


class TestExcepcionesEspecificas:
    """Test para excepciones específicas."""

    def test_authentication_exception(self):
        """Test de AuthenticationException."""
        exc = AuthenticationException("Token inválido")
        assert exc.message == "Token inválido"
        assert exc.error_code == "AUTH_ERROR"
        assert isinstance(exc, TabulaCloudException)

    def test_validation_exception_con_campo(self):
        """Test de ValidationException con campo."""
        exc = ValidationException("Campo inválido", field="nombre")
        assert exc.message == "Campo inválido"
        assert exc.field == "nombre"
        assert exc.details["field"] == "nombre"
        assert "nombre" in str(exc)

    def test_resource_not_found_exception(self):
        """Test de ResourceNotFoundException."""
        exc = ResourceNotFoundException(
            "Contacto no encontrado",
            resource_type="Contact",
            resource_id="123",
        )
        assert exc.resource_type == "Contact"
        assert exc.resource_id == "123"
        assert exc.details["resource_type"] == "Contact"
        assert exc.details["resource_id"] == "123"

    def test_api_exception(self):
        """Test de APIException."""
        response_data = {"error": "Bad request"}
        exc = APIException(
            "Error en la API", status_code=400, response_data=response_data
        )
        assert exc.status_code == 400
        assert exc.response_data == response_data
        assert exc.details["status_code"] == 400
        assert exc.details["response_data"] == response_data

    def test_rate_limit_exception(self):
        """Test de RateLimitException."""
        exc = RateLimitException("Límite excedido", retry_after=60)
        assert exc.retry_after == 60
        assert exc.details["retry_after"] == 60

    def test_sync_exception(self):
        """Test de SyncException."""
        exc = SyncException("Error de sync", sync_type="contacts")
        assert exc.sync_type == "contacts"
        assert exc.details["sync_type"] == "contacts"

    def test_model_validation_exception(self):
        """Test de ModelValidationException."""
        exc = ModelValidationException(
            "Error de modelo", model_name="Contact", field="email"
        )
        assert exc.model_name == "Contact"
        assert exc.field == "email"
        assert exc.details["model_name"] == "Contact"


class TestHandleApiError:
    """Test para la función handle_api_error."""

    def test_error_401_authentication(self):
        """Test de error 401 -> AuthenticationException."""
        exc = handle_api_error(401)
        assert isinstance(exc, AuthenticationException)
        assert exc.details["status_code"] == 401

    def test_error_403_authorization(self):
        """Test de error 403 -> AuthorizationException."""
        exc = handle_api_error(403)
        assert isinstance(exc, AuthorizationException)
        assert exc.details["status_code"] == 403

    def test_error_404_resource_not_found(self):
        """Test de error 404 -> ResourceNotFoundException."""
        exc = handle_api_error(404)
        assert isinstance(exc, ResourceNotFoundException)
        assert exc.details["status_code"] == 404

    def test_error_429_rate_limit(self):
        """Test de error 429 -> RateLimitException."""
        exc = handle_api_error(429)
        assert isinstance(exc, RateLimitException)
        assert exc.details["status_code"] == 429

    def test_error_500_service_unavailable(self):
        """Test de error 500 -> ServiceUnavailableException."""
        exc = handle_api_error(500)
        assert isinstance(exc, ServiceUnavailableException)
        assert exc.details["status_code"] == 500

    def test_error_generico_api_exception(self):
        """Test de error genérico -> APIException."""
        response_data = {"error": "Bad request"}
        exc = handle_api_error(400, response_data)
        assert isinstance(exc, APIException)
        assert exc.status_code == 400
        assert exc.response_data == response_data


class TestWrapRequestsException:
    """Test para la función wrap_requests_exception."""

    def test_connection_error(self):
        """Test de ConnectionError -> ConnectionException."""
        original_exc = requests.exceptions.ConnectionError("Connection failed")
        exc = wrap_requests_exception(original_exc)
        assert isinstance(exc, ConnectionException)
        assert "Connection failed" in exc.message

    def test_timeout_error(self):
        """Test de Timeout -> TimeoutException."""
        original_exc = requests.exceptions.Timeout("Request timeout")
        exc = wrap_requests_exception(original_exc)
        assert isinstance(exc, TimeoutException)
        assert "Request timeout" in exc.message

    def test_http_error_con_response(self):
        """Test de HTTPError con response -> handle_api_error."""
        mock_response = Mock()
        mock_response.status_code = 404

        original_exc = requests.exceptions.HTTPError("Not found")
        original_exc.response = mock_response

        exc = wrap_requests_exception(original_exc)
        assert isinstance(exc, ResourceNotFoundException)

    def test_ssl_error(self):
        """Test de SSLError -> ConnectionException."""
        original_exc = requests.exceptions.SSLError("SSL verification failed")
        exc = wrap_requests_exception(original_exc)
        assert isinstance(exc, ConnectionException)
        assert "SSL verification failed" in exc.message

    def test_proxy_error(self):
        """Test de ProxyError -> ConnectionException."""
        original_exc = requests.exceptions.ProxyError("Proxy failed")
        exc = wrap_requests_exception(original_exc)
        assert isinstance(exc, ConnectionException)
        assert "Proxy failed" in exc.message

    def test_too_many_redirects(self):
        """Test de TooManyRedirects -> APIException."""
        original_exc = requests.exceptions.TooManyRedirects(
            "Too many redirects"
        )
        exc = wrap_requests_exception(original_exc)
        assert isinstance(exc, APIException)
        assert "Too many redirects" in exc.message

    def test_request_exception_generico(self):
        """Test de RequestException genérico -> APIException."""
        original_exc = requests.exceptions.RequestException("Generic error")
        exc = wrap_requests_exception(original_exc)
        assert isinstance(exc, APIException)
        assert "Generic error" in exc.message

    def test_excepcion_no_requests(self):
        """Test de excepción que no es de requests -> TabulaCloudException."""
        original_exc = ValueError("Not a requests exception")
        exc = wrap_requests_exception(original_exc)
        assert isinstance(exc, TabulaCloudException)
        assert "Not a requests exception" in exc.message


class TestJerarquiaExcepciones:
    """Test para verificar la jerarquía de excepciones."""

    def test_todas_heredan_de_tabula_cloud_exception(self):
        """Verifica que todas las excepciones heredan de TabulaCloudException."""
        excepciones = [
            AuthenticationException,
            AuthorizationException,
            ConnectionException,
            TimeoutException,
            ValidationException,
            ConfigurationException,
            ResourceNotFoundException,
            APIException,
            DatabaseException,
            SyncException,
            ServiceUnavailableException,
            RateLimitException,
            ModelValidationException,
            BusinessLogicException,
        ]

        for exc_class in excepciones:
            exc = exc_class("Test message")
            assert isinstance(exc, TabulaCloudException)
            assert isinstance(exc, Exception)

    def test_model_validation_hereda_de_validation(self):
        """Verifica que ModelValidationException hereda de ValidationException."""
        exc = ModelValidationException("Test", model_name="Test")
        assert isinstance(exc, ValidationException)
        assert isinstance(exc, TabulaCloudException)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
