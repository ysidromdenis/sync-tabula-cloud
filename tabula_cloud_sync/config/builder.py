"""
Builder de configuración para proyectos Tabula Cloud Sync.
"""

from configparser import ConfigParser
from pathlib import Path

import yaml

from ..build_tools.project_detector import ProjectDetector
from ..utils.directories import tabula_dirs


class ConfigBuilder:
    """Constructor de archivos de configuración para proyectos."""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.config_dir = project_root / "config"
        self.detector = ProjectDetector()

        # Asegurar que existe el directorio de configuración
        self.config_dir.mkdir(exist_ok=True)

    def generate_main_config(self) -> Path:
        """Genera el archivo de configuración principal."""
        config = ConfigParser()

        # Sección de API
        config.add_section("API")
        config.set("API", "base_url", "https://api.tabula.com.py")
        config.set("API", "version", "v1")
        config.set("API", "timeout", "30")
        config.set("API", "api_key", "YOUR_API_KEY_HERE")
        config.set("API", "client_id", "YOUR_CLIENT_ID_HERE")

        # Sección de sincronización
        config.add_section("SYNC")
        config.set("SYNC", "interval", "300")  # 5 minutos
        config.set("SYNC", "batch_size", "100")
        config.set("SYNC", "retry_attempts", "3")
        config.set("SYNC", "retry_delay", "10")
        config.set("SYNC", "auto_start", "true")

        # Sección de base de datos
        db_type = self.detector.detect_database_type()
        config.add_section("DATABASE")

        if db_type == "postgresql":
            config.set("DATABASE", "type", "postgresql")
            config.set("DATABASE", "host", "localhost")
            config.set("DATABASE", "port", "5432")
            config.set("DATABASE", "database", "tabula_sync")
            config.set("DATABASE", "username", "postgres")
            config.set("DATABASE", "password", "YOUR_PASSWORD_HERE")
        elif db_type == "mysql":
            config.set("DATABASE", "type", "mysql")
            config.set("DATABASE", "host", "localhost")
            config.set("DATABASE", "port", "3306")
            config.set("DATABASE", "database", "tabula_sync")
            config.set("DATABASE", "username", "root")
            config.set("DATABASE", "password", "YOUR_PASSWORD_HERE")
        elif db_type == "sqlserver":
            config.set("DATABASE", "type", "sqlserver")
            config.set("DATABASE", "host", "localhost")
            config.set("DATABASE", "port", "1433")
            config.set("DATABASE", "database", "tabula_sync")
            config.set("DATABASE", "username", "sa")
            config.set("DATABASE", "password", "YOUR_PASSWORD_HERE")
        else:
            # SQLite por defecto - usar directorio de datos de platformdirs
            sqlite_path = tabula_dirs.get_data_file_path("tabula_sync.db")
            config.set("DATABASE", "type", "sqlite")
            config.set("DATABASE", "path", str(sqlite_path))

        # Sección de logging - usar directorio de logs de platformdirs
        config.add_section("LOGGING")
        config.set("LOGGING", "level", "INFO")
        log_path = tabula_dirs.get_log_file_path("tabula_service.log")
        config.set("LOGGING", "file", str(log_path))
        config.set("LOGGING", "max_size", "10MB")
        config.set("LOGGING", "backup_count", "5")
        config.set(
            "LOGGING",
            "format",
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        )

        # Sección del servicio
        config.add_section("SERVICE")
        config.set(
            "SERVICE", "name", f"{self.project_root.name}_tabula_service"
        )
        config.set(
            "SERVICE",
            "display_name",
            f"{self.project_root.name.title()} Tabula Service",
        )
        config.set(
            "SERVICE",
            "description",
            "Servicio de sincronización con Tabula Cloud",
        )
        config.set("SERVICE", "run_as_daemon", "true")

        # Guardar configuración
        config_file = self.config_dir / "tabula_config.ini"
        with open(config_file, "w") as f:
            config.write(f)

        return config_file

    def generate_logging_config(self) -> Path:
        """Genera configuración avanzada de logging."""
        # Usar rutas de platformdirs para archivos de log
        main_log_path = tabula_dirs.get_log_file_path("tabula_service.log")
        error_log_path = tabula_dirs.get_log_file_path("sync_errors.log")

        logging_config = {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "detailed": {
                    "format": "%(asctime)s - %(name)s - %(levelname)s - "
                    "%(funcName)s:%(lineno)d - %(message)s"
                },
                "simple": {
                    "format": "%(asctime)s - %(levelname)s - %(message)s"
                },
            },
            "handlers": {
                "file_handler": {
                    "class": "logging.handlers.RotatingFileHandler",
                    "level": "INFO",
                    "formatter": "detailed",
                    "filename": str(main_log_path),
                    "maxBytes": 10485760,  # 10MB
                    "backupCount": 5,
                },
                "error_handler": {
                    "class": "logging.handlers.RotatingFileHandler",
                    "level": "ERROR",
                    "formatter": "detailed",
                    "filename": str(error_log_path),
                    "maxBytes": 5242880,  # 5MB
                    "backupCount": 3,
                },
                "console_handler": {
                    "class": "logging.StreamHandler",
                    "level": "INFO",
                    "formatter": "simple",
                    "stream": "ext://sys.stdout",
                },
            },
            "loggers": {
                "tabula_cloud_sync": {
                    "level": "INFO",
                    "handlers": [
                        "file_handler",
                        "error_handler",
                        "console_handler",
                    ],
                    "propagate": False,
                },
                "root": {"level": "WARNING", "handlers": ["console_handler"]},
            },
        }

        logging_file = self.config_dir / "logging_config.yaml"
        with open(logging_file, "w") as f:
            yaml.dump(logging_config, f, default_flow_style=False)

        return logging_file

    def generate_database_config(self) -> Path:
        """Genera configuración específica de base de datos."""
        db_type = self.detector.detect_database_type() or "sqlite"

        db_config = {
            "default": {
                "type": db_type,
                "pool_size": 5,
                "max_overflow": 10,
                "pool_timeout": 30,
                "pool_recycle": 3600,
                "echo": False,
            }
        }

        if db_type == "postgresql":
            db_config["postgresql"] = {
                "driver": "psycopg2",
                "connection_string_template": (
                    "postgresql+psycopg2://{username}:{password}@{host}:"
                    "{port}/{database}"
                ),
                "default_port": 5432,
                "schema_support": True,
            }
        elif db_type == "mysql":
            db_config["mysql"] = {
                "driver": "pymysql",
                "connection_string_template": (
                    "mysql+pymysql://{username}:{password}@{host}:"
                    "{port}/{database}"
                ),
                "default_port": 3306,
                "charset": "utf8mb4",
            }
        elif db_type == "sqlserver":
            db_config["sqlserver"] = {
                "driver": "pymssql",
                "connection_string_template": (
                    "mssql+pymssql://{username}:{password}@{host}:"
                    "{port}/{database}"
                ),
                "default_port": 1433,
                "schema_support": True,
            }
        else:
            db_config["sqlite"] = {
                "driver": "sqlite",
                "connection_string_template": "sqlite:///{path}",
                "wal_mode": True,
                "foreign_keys": True,
            }

        db_file = self.config_dir / "database_config.yaml"
        with open(db_file, "w") as f:
            yaml.dump(db_config, f, default_flow_style=False)

        return db_file

    def generate_service_config(self) -> Path:
        """Genera configuración específica del servicio."""
        project_type = self.detector.get_project_type()

        service_config = {
            "service": {
                "name": f"{self.project_root.name}_tabula_service",
                "display_name": f"{self.project_root.name.title()} Tabula Service",
                "description": "Servicio de sincronización con Tabula Cloud",
                "project_type": project_type,
                "auto_start": True,
                "restart_on_failure": True,
                "max_restart_attempts": 3,
            },
            "sync": {
                "default_interval": 300,
                "batch_processing": True,
                "parallel_processing": False,
                "error_threshold": 10,
                "cleanup_old_logs": True,
                "log_retention_days": 30,
            },
            "monitoring": {
                "health_check_interval": 60,
                "performance_metrics": True,
                "memory_threshold_mb": 500,
                "cpu_threshold_percent": 80,
            },
        }

        service_file = self.config_dir / "service_config.yaml"
        with open(service_file, "w") as f:
            yaml.dump(service_config, f, default_flow_style=False)

        return service_file

    def generate_environment_config(
        self, environment: str = "development"
    ) -> Path:
        """Genera configuración específica del entorno."""
        env_configs = {
            "development": {
                "debug": True,
                "log_level": "DEBUG",
                "api_base_url": "https://api-dev.tabula.com.py",
                "database_echo": True,
                "sync_interval": 60,
                "cache_enabled": False,
            },
            "testing": {
                "debug": True,
                "log_level": "INFO",
                "api_base_url": "https://api-test.tabula.com.py",
                "database_echo": False,
                "sync_interval": 30,
                "cache_enabled": True,
            },
            "production": {
                "debug": False,
                "log_level": "WARNING",
                "api_base_url": "https://api.tabula.com.py",
                "database_echo": False,
                "sync_interval": 300,
                "cache_enabled": True,
                "ssl_verify": True,
                "connection_pool_size": 20,
            },
        }

        config = env_configs.get(environment, env_configs["development"])

        env_file = self.config_dir / f"environment_{environment}.yaml"
        with open(env_file, "w") as f:
            yaml.dump(config, f, default_flow_style=False)

        return env_file
