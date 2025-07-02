"""
Tabula Cloud Sync - Librería reutilizable para sincronización con Tabula Cloud.

Esta librería proporciona una base sólida para crear servicios de sincronización
personalizados que se integren con la API de Tabula Cloud.

Características principales:
- Auto-configuración al instalar/importar
- Sistema de templates personalizables
- Soporte para múltiples bases de datos
- CLI integrado para gestión de proyectos
- Build tools automáticos
- Sistema de logging avanzado
- Compatibilidad multiplataforma

Uso básico:
    from tabula_cloud_sync import TabulaCloudService

    class MiServicio(TabulaCloudService):
        def perform_sync(self):
            # Tu lógica de sincronización aquí
            pass
"""

__version__ = "1.0.0"
__author__ = "Ysidro Denis"
__email__ = "contacto@tabula.com.py"
__license__ = "MIT"

from .core.session import Session
# Imports principales
from .service.base_service import TabulaCloudService
from .service.daemon import TabulaCloudDaemon
from .utils.commons import *

# Import hooks - ejecutar configuración automática
try:
    from .build_tools.post_install import ImportTimeHooks

    ImportTimeHooks.run_import_hooks()
except Exception:
    # Si hay error en hooks, no interrumpir la importación
    pass

# Exports públicos
__all__ = [
    "TabulaCloudService",
    "TabulaCloudDaemon",
    "Session",
    # Utilidades comunes se exportan con *
]
