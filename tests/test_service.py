"""Tests básicos para el servicio Tabula Cloud Sync."""

import os
import tempfile
import unittest
from unittest.mock import Mock, patch

from service.base_service import TabulaCloudService


class TestTabulaCloudService(unittest.TestCase):
    """Tests para la clase base del servicio."""

    def setUp(self):
        """Configurar tests."""
        # Crear archivo de configuración temporal
        self.temp_config = tempfile.NamedTemporaryFile(
            mode="w", suffix=".ini", delete=False
        )

        config_content = """
[sincronizador]
token = test_token
interval = 5
url = test.tabula.com.py

[servicio]
log_level = INFO
max_retries = 3
timeout = 30
"""
        self.temp_config.write(config_content)
        self.temp_config.close()

        self.service = TabulaCloudService(self.temp_config.name)

    def tearDown(self):
        """Limpiar después de tests."""
        os.unlink(self.temp_config.name)

    def test_load_config(self):
        """Test cargar configuración."""
        self.service.load_config()

        self.assertEqual(self.service.config["sincronizador"]["token"], "test_token")
        self.assertEqual(self.service.sync_interval, 5)

    @patch("service.base_service.Session")
    def test_initialize_session(self, mock_session):
        """Test inicializar sesión."""
        self.service.load_config()
        self.service.initialize_session()

        mock_session.assert_called_once_with("test_token")
        self.assertIsNotNone(self.service.session)

    def test_get_status(self):
        """Test obtener estado."""
        status = self.service.get_status()

        self.assertIn("running", status)
        self.assertIn("config_file", status)
        self.assertIn("sync_interval", status)
        self.assertFalse(status["running"])

    def test_health_check_without_session(self):
        """Test health check sin sesión."""
        self.assertFalse(self.service.health_check())

    @patch("service.base_service.Session")
    def test_health_check_with_session(self, mock_session):
        """Test health check con sesión."""
        self.service.load_config()
        self.service.initialize_session()
        self.service.running = True

        self.assertTrue(self.service.health_check())


class TestServiceIntegration(unittest.TestCase):
    """Tests de integración para el servicio."""

    def setUp(self):
        """Configurar tests de integración."""
        self.temp_config = tempfile.NamedTemporaryFile(
            mode="w", suffix=".ini", delete=False
        )

        config_content = """
[sincronizador]
token = integration_test_token
interval = 1
url = test.tabula.com.py
"""
        self.temp_config.write(config_content)
        self.temp_config.close()

    def tearDown(self):
        """Limpiar tests de integración."""
        os.unlink(self.temp_config.name)

    def test_service_lifecycle(self):
        """Test ciclo de vida completo del servicio."""

        class TestService(TabulaCloudService):
            def __init__(self, config_file):
                super().__init__(config_file)
                self.sync_count = 0

            def perform_sync(self):
                self.sync_count += 1

        service = TestService(self.temp_config.name)

        # Test estado inicial
        status = service.get_status()
        self.assertFalse(status["running"])

        # Test configuración
        service.load_config()
        self.assertEqual(service.sync_interval, 1)

        # Test health check inicial
        self.assertFalse(service.health_check())


if __name__ == "__main__":
    unittest.main()
