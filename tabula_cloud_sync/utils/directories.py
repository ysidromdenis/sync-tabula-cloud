"""
Utilidades para el manejo de directorios usando platformdirs.
Proporciona rutas multiplataforma estándar para configuración, datos, logs, cache, etc.
"""

from pathlib import Path
from typing import Optional, Union

from platformdirs import PlatformDirs


class TabulaDirectories:
    """
    Maneja directorios de la aplicación usando platformdirs para
    compatibilidad multiplataforma.
    """

    def __init__(
        self, app_name: str = "TabulaCloudSync", app_author: str = "Tabula"
    ):
        """
        Inicializa el manejador de directorios.

        Args:
            app_name: Nombre de la aplicación
            app_author: Autor/empresa de la aplicación
        """
        self.app_name = app_name
        self.app_author = app_author
        self._dirs = PlatformDirs(
            appname=app_name, appauthor=app_author, ensure_exists=False
        )

    @property
    def user_config_dir(self) -> Path:
        """Directorio de configuración del usuario."""
        path = Path(self._dirs.user_config_dir)
        path.mkdir(parents=True, exist_ok=True)
        return path

    @property
    def user_data_dir(self) -> Path:
        """Directorio de datos del usuario."""
        path = Path(self._dirs.user_data_dir)
        path.mkdir(parents=True, exist_ok=True)
        return path

    @property
    def user_cache_dir(self) -> Path:
        """Directorio de cache del usuario."""
        path = Path(self._dirs.user_cache_dir)
        path.mkdir(parents=True, exist_ok=True)
        return path

    @property
    def user_log_dir(self) -> Path:
        """Directorio de logs del usuario."""
        path = Path(self._dirs.user_log_dir)
        path.mkdir(parents=True, exist_ok=True)
        return path

    @property
    def site_config_dir(self) -> Path:
        """Directorio de configuración del sistema."""
        path = Path(self._dirs.site_config_dir)
        # No crear automáticamente ya que puede requerir permisos admin
        return path

    @property
    def site_data_dir(self) -> Path:
        """Directorio de datos del sistema."""
        path = Path(self._dirs.site_data_dir)
        # No crear automáticamente ya que puede requerir permisos admin
        return path

    def get_config_file_path(self, filename: str = "config.ini") -> Path:
        """
        Obtiene la ruta completa de un archivo de configuración.

        Args:
            filename: Nombre del archivo de configuración

        Returns:
            Path completo al archivo de configuración
        """
        return self.user_config_dir / filename

    def get_log_file_path(self, filename: str = "tabula_service.log") -> Path:
        """
        Obtiene la ruta completa de un archivo de log.

        Args:
            filename: Nombre del archivo de log

        Returns:
            Path completo al archivo de log
        """
        return self.user_log_dir / filename

    def get_data_file_path(self, filename: str) -> Path:
        """
        Obtiene la ruta completa de un archivo de datos.

        Args:
            filename: Nombre del archivo de datos

        Returns:
            Path completo al archivo de datos
        """
        return self.user_data_dir / filename

    def get_cache_file_path(self, filename: str) -> Path:
        """
        Obtiene la ruta completa de un archivo de cache.

        Args:
            filename: Nombre del archivo de cache

        Returns:
            Path completo al archivo de cache
        """
        return self.user_cache_dir / filename

    def get_backup_dir(self) -> Path:
        """Directorio para respaldos dentro del directorio de datos."""
        backup_dir = self.user_data_dir / "backups"
        backup_dir.mkdir(parents=True, exist_ok=True)
        return backup_dir

    def get_templates_dir(self) -> Path:
        """Directorio para templates dentro del directorio de datos."""
        templates_dir = self.user_data_dir / "templates"
        templates_dir.mkdir(parents=True, exist_ok=True)
        return templates_dir

    def get_project_specific_dir(
        self, project_name: str, dir_type: str = "data"
    ) -> Path:
        """
        Obtiene directorio específico para un proyecto.

        Args:
            project_name: Nombre del proyecto
            dir_type: Tipo de directorio (data, config, cache, logs)

        Returns:
            Path al directorio específico del proyecto
        """
        base_dir_map = {
            "data": self.user_data_dir,
            "config": self.user_config_dir,
            "cache": self.user_cache_dir,
            "logs": self.user_log_dir,
        }

        base_dir = base_dir_map.get(dir_type, self.user_data_dir)
        project_dir = base_dir / "projects" / project_name
        project_dir.mkdir(parents=True, exist_ok=True)
        return project_dir

    def ensure_all_directories(self) -> None:
        """Asegura que todos los directorios principales existan."""
        directories = [
            self.user_config_dir,
            self.user_data_dir,
            self.user_cache_dir,
            self.user_log_dir,
            self.get_backup_dir(),
            self.get_templates_dir(),
        ]

        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)

    def clean_cache(self) -> bool:
        """
        Limpia el directorio de cache.

        Returns:
            True si se limpió correctamente, False en caso contrario
        """
        try:
            import shutil

            if self.user_cache_dir.exists():
                shutil.rmtree(self.user_cache_dir)
                self.user_cache_dir.mkdir(parents=True, exist_ok=True)
            return True
        except Exception:
            return False

    def get_directory_info(self) -> dict:
        """
        Obtiene información sobre todos los directorios.

        Returns:
            Diccionario con información de directorios
        """
        return {
            "app_name": self.app_name,
            "app_author": self.app_author,
            "user_config_dir": str(self.user_config_dir),
            "user_data_dir": str(self.user_data_dir),
            "user_cache_dir": str(self.user_cache_dir),
            "user_log_dir": str(self.user_log_dir),
            "site_config_dir": str(self.site_config_dir),
            "site_data_dir": str(self.site_data_dir),
            "backup_dir": str(self.get_backup_dir()),
            "templates_dir": str(self.get_templates_dir()),
        }


# Instancia global para uso fácil
tabula_dirs = TabulaDirectories()


def get_default_config_path() -> Path:
    """Obtiene la ruta por defecto del archivo de configuración."""
    return tabula_dirs.get_config_file_path()


def get_default_log_path() -> Path:
    """Obtiene la ruta por defecto del archivo de log."""
    return tabula_dirs.get_log_file_path()


def get_default_data_dir() -> Path:
    """Obtiene el directorio por defecto de datos."""
    return tabula_dirs.user_data_dir


def get_default_cache_dir() -> Path:
    """Obtiene el directorio por defecto de cache."""
    return tabula_dirs.user_cache_dir


def ensure_directory(path: Union[str, Path]) -> Path:
    """
    Asegura que un directorio existe, creándolo si es necesario.
    Versión mejorada de la función original con mejor manejo de errores.

    Args:
        path: Ruta del directorio

    Returns:
        Path object del directorio
    """
    dir_path = Path(path)
    try:
        dir_path.mkdir(parents=True, exist_ok=True)
    except PermissionError:
        # Si no se pueden crear en la ubicación especificada,
        # intentar en el directorio de datos del usuario
        fallback_dir = tabula_dirs.user_data_dir / dir_path.name
        fallback_dir.mkdir(parents=True, exist_ok=True)
        return fallback_dir
    except Exception:
        # Como último recurso, usar directorio temporal
        import tempfile

        temp_dir = (
            Path(tempfile.gettempdir()) / "tabula_cloud_sync" / dir_path.name
        )
        temp_dir.mkdir(parents=True, exist_ok=True)
        return temp_dir

    return dir_path


def get_appropriate_config_path(
    local_config: Optional[Union[str, Path]] = None,
) -> Path:
    """
    Determina la ruta de configuración más apropiada.

    Prioridad:
    1. Archivo local especificado
    2. config.ini en directorio actual
    3. Archivo en directorio de configuración del usuario
    4. Archivo en directorio de configuración del sistema

    Args:
        local_config: Ruta a archivo de configuración local

    Returns:
        Path al archivo de configuración a usar
    """
    # 1. Archivo especificado explícitamente
    if local_config:
        local_path = Path(local_config)
        if local_path.exists():
            return local_path

    # 2. config.ini en directorio actual
    current_config = Path.cwd() / "config.ini"
    if current_config.exists():
        return current_config

    # 3. Archivo en directorio de usuario
    user_config = tabula_dirs.get_config_file_path()
    if user_config.exists():
        return user_config

    # 4. Archivo en directorio del sistema (solo verificar si es accesible)
    try:
        site_config = tabula_dirs.site_config_dir / "config.ini"
        if site_config.exists():
            return site_config
    except (PermissionError, OSError):
        # Si no se puede acceder al directorio del sistema, ignorar
        pass

    # 5. Por defecto, retornar la ruta del usuario (se creará si es necesario)
    return user_config


def get_appropriate_log_dir() -> Path:
    """
    Determina el directorio de logs más apropiado.

    Returns:
        Path al directorio de logs a usar
    """
    # Intentar usar directorio local primero
    local_log_dir = Path.cwd() / "logs"
    try:
        local_log_dir.mkdir(exist_ok=True)
        # Verificar que se puede escribir
        test_file = local_log_dir / ".write_test"
        test_file.touch()
        test_file.unlink()
        return local_log_dir
    except (PermissionError, OSError):
        # Si no se puede usar local, usar directorio del usuario
        return tabula_dirs.user_log_dir
