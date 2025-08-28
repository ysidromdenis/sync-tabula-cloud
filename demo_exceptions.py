#!/usr/bin/env python3
"""
Script de demostración del sistema de excepciones personalizadas de Tabula Cloud Sync.

Este script muestra cómo las nuevas excepciones funcionan en diferentes escenarios.
"""

import sys
import traceback

from tabula_cloud_sync.core.exceptions import *
from tabula_cloud_sync.core.session import Session


def demo_excepciones_basicas():
    """Demuestra el uso básico de las excepciones personalizadas."""
    print("🔍 Demo: Excepciones Básicas")
    print("=" * 50)

    # 1. TabulaCloudException básica
    try:
        raise TabulaCloudException(
            "Error de demostración",
            error_code="DEMO_001",
            details={"tipo": "demo", "nivel": "info"},
        )
    except TabulaCloudException as e:
        print(f"✅ TabulaCloudException capturada:")
        print(f"   Mensaje: {e.message}")
        print(f"   Código: {e.error_code}")
        print(f"   Detalles: {e.details}")
        print(f"   String: {str(e)}")
        print(f"   Dict: {e.to_dict()}")

    print()

    # 2. ValidationException con campo
    try:
        raise ValidationException(
            "El email no es válido",
            field="email",
            details={
                "value": "email_invalido",
                "expected_format": "user@domain.com",
            },
        )
    except ValidationException as e:
        print(f"✅ ValidationException capturada:")
        print(f"   Mensaje: {e.message}")
        print(f"   Campo: {e.field}")
        print(f"   String: {str(e)}")

    print()


def demo_handle_api_error():
    """Demuestra la función handle_api_error."""
    print("🌐 Demo: Manejo de Errores de API")
    print("=" * 50)

    codigos_test = [400, 401, 403, 404, 429, 500, 502]

    for codigo in codigos_test:
        try:
            exc = handle_api_error(codigo)
            raise exc
        except TabulaCloudException as e:
            print(f"✅ Código {codigo} -> {e.__class__.__name__}: {e.message}")

    print()


def demo_wrap_requests_exception():
    """Demuestra la conversión de excepciones de requests."""
    print("🔄 Demo: Conversión de Excepciones de Requests")
    print("=" * 50)

    from unittest.mock import Mock

    import requests

    # Simular diferentes tipos de excepciones de requests
    excepciones_test = [
        requests.exceptions.ConnectionError("No se pudo conectar"),
        requests.exceptions.Timeout("Tiempo de espera agotado"),
        requests.exceptions.SSLError("Error de certificado SSL"),
        requests.exceptions.ProxyError("Error del proxy"),
        requests.exceptions.TooManyRedirects("Demasiados redireccionamientos"),
    ]

    for exc_original in excepciones_test:
        try:
            exc_convertida = wrap_requests_exception(exc_original)
            raise exc_convertida
        except TabulaCloudException as e:
            print(
                f"✅ {exc_original.__class__.__name__} -> {e.__class__.__name__}"
            )
            print(f"   Original: {str(exc_original)}")
            print(f"   Convertida: {e.message}")

    print()


def demo_session_con_excepciones():
    """Demuestra cómo la clase Session usa las nuevas excepciones."""
    print("💾 Demo: Session con Excepciones Personalizadas")
    print("=" * 50)

    # Crear una sesión de prueba
    session = Session("token-de-prueba")
    print(f"✅ Sesión creada correctamente")
    print(f"   Headers: {session.headers}")

    # Demostrar el manejo de excepciones (sin hacer requests reales)
    print("✅ La sesión está configurada para usar excepciones personalizadas")
    print("   - Los errores HTTP se convierten automáticamente")
    print("   - Los errores de red usan ConnectionException/TimeoutException")
    print("   - Los errores de autenticación usan AuthenticationException")

    print()


def demo_validacion_modelos():
    """Demuestra las excepciones en validación de modelos."""
    print("📋 Demo: Validación de Modelos")
    print("=" * 50)

    # Test con modelo Currency del módulo base
    try:
        from tabula_cloud_sync.models.base import Currency

        # Intentar crear un Currency con decimal inválido
        try:
            currency = Currency(
                id="USD",
                nombre="Dólar",
                simbolo="$",
                decimal=15,  # Inválido: debe estar entre 0 y 8
            )
        except ValidationException as e:
            print(f"✅ ValidationException en modelo Currency:")
            print(f"   Campo: {e.field}")
            print(f"   Mensaje: {e.message}")
        except Exception as e:
            # Pydantic podría envolver nuestra excepción
            print(f"✅ Excepción capturada en validación: {type(e).__name__}")
            print(f"   Mensaje: {str(e)}")

    except ImportError as e:
        print(f"ℹ️  Modelo Currency no disponible: {e}")

    print()


def demo_manejo_jerarquico():
    """Demuestra el manejo jerárquico de excepciones."""
    print("🌳 Demo: Manejo Jerárquico de Excepciones")
    print("=" * 50)

    excepciones_test = [
        AuthenticationException("Token inválido"),
        ValidationException("Campo requerido", field="nombre"),
        BusinessLogicException("Regla de negocio violada"),
        ConnectionException("No se pudo conectar al servidor"),
    ]

    for exc in excepciones_test:
        try:
            raise exc
        except AuthenticationException:
            print(f"✅ Manejo específico para autenticación: {exc.message}")
        except ValidationException as e:
            print(
                f"✅ Manejo específico para validación: {e.message} (campo: {e.field})"
            )
        except TabulaCloudException as e:
            print(
                f"✅ Manejo genérico para Tabula Cloud: {e.__class__.__name__} - {e.message}"
            )
        except Exception as e:
            print(f"✅ Manejo genérico: {type(e).__name__} - {str(e)}")

    print()


def demo_logging_estructurado():
    """Demuestra cómo hacer logging estructurado con las excepciones."""
    print("📝 Demo: Logging Estructurado")
    print("=" * 50)

    import json

    try:
        raise APIException(
            "Error en la API de contactos",
            status_code=422,
            response_data={"error": "Validation failed", "field": "email"},
        )
    except APIException as e:
        # Convertir a dict para logging estructurado
        error_dict = e.to_dict()
        print("✅ Error convertido a diccionario para logging:")
        print(json.dumps(error_dict, indent=2, ensure_ascii=False))

    print()


def main():
    """Ejecuta todas las demostraciones."""
    print("🚀 DEMOSTRACIÓN DEL SISTEMA DE EXCEPCIONES PERSONALIZADAS")
    print("🚀 Tabula Cloud Sync - Excepciones Personalizadas")
    print("=" * 80)
    print()

    demos = [
        demo_excepciones_basicas,
        demo_handle_api_error,
        demo_wrap_requests_exception,
        demo_session_con_excepciones,
        demo_validacion_modelos,
        demo_manejo_jerarquico,
        demo_logging_estructurado,
    ]

    for demo in demos:
        try:
            demo()
        except Exception as e:
            print(f"❌ Error en {demo.__name__}: {e}")
            traceback.print_exc()
            print()

    print("🎉 DEMOSTRACIÓN COMPLETADA")
    print("=" * 80)
    print()
    print("📚 Para más información, consulta:")
    print("   - docs/EXCEPTIONS.md")
    print("   - examples/exceptions_usage.py")
    print("   - tests/test_exceptions.py")


if __name__ == "__main__":
    main()
