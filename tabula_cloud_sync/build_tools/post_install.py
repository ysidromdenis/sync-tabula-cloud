"""
Post-installation hooks para Tabula Cloud Sync.

Este módulo contiene funciones que se ejecutan automáticamente después
de instalar la librería para configurar el entorno del usuario.
"""

import os
import shutil
import sys
from pathlib import Path
from typing import Dict, List, Optional

from ..config.builder import ConfigBuilder
from ..utils.commons import ensure_directory
from .project_detector import ProjectDetector
from .template_generator import TemplateGenerator


class PostInstallHooks:
    """Hooks de post-instalación para configurar automáticamente el entorno."""

    @staticmethod
    def run_post_install() -> None:
        """
        Ejecuta todos los hooks de post-instalación.

        Este método se llama automáticamente después de instalar la librería.
        """
        try:
            print("🚀 Configurando Tabula Cloud Sync...")

            # Detectar el directorio del proyecto del usuario
            project_root = PostInstallHooks._detect_project_root()

            if project_root:
                print(f"📁 Proyecto detectado en: {project_root}")

                # Crear estructura de directorios
                PostInstallHooks._create_project_structure(project_root)

                # Generar archivos de configuración
                PostInstallHooks._generate_config_files(project_root)

                # Configurar logging
                PostInstallHooks._setup_logging(project_root)

                # Generar templates base
                PostInstallHooks._generate_templates(project_root)

                print("✅ Configuración completada exitosamente!")
                print(
                    "💡 Consulta la documentación en: https://github.com/ysidromdenis/template-sync-tabula-cloud"
                )
            else:
                print(
                    "ℹ️  No se detectó un proyecto Python. La configuración se realizará al importar la librería."
                )

        except Exception as e:
            print(f"⚠️  Error durante la configuración: {e}")
            print(
                "🔧 Puedes ejecutar 'tabula-cli init' manualmente para configurar el proyecto."
            )

    @staticmethod
    def _detect_project_root() -> Optional[Path]:
        """Detecta el directorio raíz del proyecto del usuario."""
        current_dir = Path.cwd()

        # Buscar indicadores de proyecto Python
        project_indicators = [
            "setup.py",
            "pyproject.toml",
            "requirements.txt",
            "main.py",
            "__main__.py",
            ".git",
        ]

        # Buscar hacia arriba hasta encontrar indicadores
        for path in [current_dir] + list(current_dir.parents):
            if any((path / indicator).exists() for indicator in project_indicators):
                return path

        # Si no encuentra, usar directorio actual
        return current_dir

    @staticmethod
    def _create_project_structure(project_root: Path) -> None:
        """Crea la estructura básica de directorios."""
        directories = [
            "logs",
            "config",
            "cache",
            "data",
            "backups",
            "templates",
            "services",
        ]

        for directory in directories:
            dir_path = project_root / directory
            ensure_directory(str(dir_path))

        print("📂 Estructura de directorios creada")

    @staticmethod
    def _generate_config_files(project_root: Path) -> None:
        """Genera archivos de configuración base."""
        config_builder = ConfigBuilder(project_root)

        # Generar config.ini principal
        config_builder.generate_main_config()

        # Generar archivo de configuración de logging
        config_builder.generate_logging_config()

        # Generar archivo de configuración de base de datos
        config_builder.generate_database_config()

        print("⚙️  Archivos de configuración generados")

    @staticmethod
    def _setup_logging(project_root: Path) -> None:
        """Configura el sistema de logging."""
        logs_dir = project_root / "logs"
        ensure_directory(str(logs_dir))

        # Crear archivos de log base
        log_files = ["tabula_service.log", "sync_errors.log", "debug.log"]

        for log_file in log_files:
            log_path = logs_dir / log_file
            if not log_path.exists():
                log_path.touch()

        print("📋 Sistema de logging configurado")

    @staticmethod
    def _generate_templates(project_root: Path) -> None:
        """Genera templates base para el proyecto."""
        template_generator = TemplateGenerator(project_root)

        # Generar servicio base
        template_generator.generate_service_template()

        # Generar modelo base
        template_generator.generate_model_template()

        # Generar configuración de daemon
        template_generator.generate_daemon_template()

        print("📄 Templates base generados")


class ImportTimeHooks:
    """Hooks que se ejecutan al importar la librería."""

    @staticmethod
    def run_import_hooks() -> None:
        """
        Ejecuta hooks al importar la librería.

        Se ejecuta automáticamente cuando se importa tabula_cloud_sync.
        """
        try:
            # Detectar proyecto
            detector = ProjectDetector()

            if detector.is_new_project():
                print("🔍 Nuevo proyecto detectado - Configurando Tabula Cloud Sync...")

                # Configurar proyecto automáticamente
                project_root = detector.get_project_root()
                PostInstallHooks._create_project_structure(project_root)
                PostInstallHooks._generate_config_files(project_root)
                PostInstallHooks._setup_logging(project_root)

                print("✅ Proyecto configurado automáticamente!")

        except Exception as e:
            # Silencioso en import - no interrumpir la importación
            pass
