"""
Detector de proyectos para identificar automáticamente proyectos que usan Tabula Cloud Sync.
"""

import os
import sys
from pathlib import Path
from typing import List, Optional


class ProjectDetector:
    """Detecta y analiza proyectos que utilizan Tabula Cloud Sync."""

    def __init__(self):
        self.project_root = self._find_project_root()
        self.project_markers_file = self.project_root / ".tabula_markers"

    def _find_project_root(self) -> Path:
        """Encuentra la raíz del proyecto actual."""
        # Comenzar desde el directorio donde se está ejecutando el script
        if hasattr(sys, "_getframe"):
            caller_frame = sys._getframe(2)
            caller_file = caller_frame.f_code.co_filename
            start_dir = Path(caller_file).parent
        else:
            start_dir = Path.cwd()

        # Indicadores de proyecto Python
        project_indicators = [
            "setup.py",
            "pyproject.toml",
            "requirements.txt",
            "main.py",
            "__main__.py",
            ".git",
            "manage.py",  # Django
            "app.py",  # Flask
        ]

        # Buscar hacia arriba
        current = start_dir.resolve()
        while current != current.parent:
            if any(
                (current / indicator).exists()
                for indicator in project_indicators
            ):
                return current
            current = current.parent

        # Si no encuentra, usar directorio actual
        return Path.cwd()

    def is_new_project(self) -> bool:
        """
        Determina si este es un proyecto nuevo que nunca ha usado Tabula Cloud Sync.
        """
        # Verificar si existe el archivo de marcadores
        if self.project_markers_file.exists():
            return False

        # Verificar si ya existe configuración de Tabula
        config_indicators = [
            self.project_root / "config" / "tabula_config.ini",
            self.project_root / "config.ini",
            self.project_root / "tabula_config.ini",
        ]

        if any(indicator.exists() for indicator in config_indicators):
            return False

        # Verificar si hay servicios que heredan de TabulaCloudService
        if self._has_tabula_services():
            return False

        return True

    def _has_tabula_services(self) -> bool:
        """Verifica si el proyecto ya tiene servicios de Tabula Cloud."""
        python_files = list(self.project_root.rglob("*.py"))

        for py_file in python_files:
            try:
                with open(py_file, "r", encoding="utf-8") as f:
                    content = f.read()
                    if "TabulaCloudService" in content and "class" in content:
                        return True
            except (UnicodeDecodeError, PermissionError):
                continue

        return False

    def mark_as_configured(self) -> None:
        """Marca el proyecto como configurado."""
        with open(self.project_markers_file, "w") as f:
            f.write(f"configured_at={Path.cwd()}\n")
            f.write(f"version=1.0.0\n")

    def get_project_root(self) -> Path:
        """Retorna la raíz del proyecto."""
        return self.project_root

    def get_project_type(self) -> str:
        """Detecta el tipo de proyecto Python."""
        if (self.project_root / "manage.py").exists():
            return "django"
        elif (self.project_root / "app.py").exists():
            return "flask"
        elif (self.project_root / "setup.py").exists():
            return "package"
        elif (self.project_root / "pyproject.toml").exists():
            return "modern_package"
        elif (self.project_root / "main.py").exists():
            return "script"
        else:
            return "generic"

    def detect_database_type(self) -> Optional[str]:
        """Detecta el tipo de base de datos utilizada en el proyecto."""
        requirements_files = [
            self.project_root / "requirements.txt",
            self.project_root / "pyproject.toml",
            self.project_root / "setup.py",
        ]

        db_indicators = {
            "postgresql": ["psycopg2", "asyncpg", "pg8000"],
            "mysql": ["pymysql", "mysqlclient", "mysql-connector"],
            "sqlite": ["sqlite3"],
            "sqlserver": ["pymssql", "pyodbc"],
            "mongodb": ["pymongo", "mongoengine"],
            "oracle": ["cx_Oracle", "oracledb"],
        }

        for req_file in requirements_files:
            if req_file.exists():
                try:
                    content = req_file.read_text().lower()
                    for db_type, packages in db_indicators.items():
                        if any(
                            package.lower() in content for package in packages
                        ):
                            return db_type
                except Exception:
                    continue

        return None

    def get_existing_services(self) -> List[Path]:
        """Encuentra servicios existentes que usan TabulaCloudService."""
        services = []
        python_files = list(self.project_root.rglob("*.py"))

        for py_file in python_files:
            try:
                with open(py_file, "r", encoding="utf-8") as f:
                    content = f.read()
                    if (
                        "class" in content
                        and "TabulaCloudService" in content
                        and "def perform_sync" in content
                    ):
                        services.append(py_file)
            except (UnicodeDecodeError, PermissionError):
                continue

        return services
