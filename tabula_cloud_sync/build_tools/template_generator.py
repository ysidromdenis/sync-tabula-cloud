"""
Generador de templates para proyectos que usan Tabula Cloud Sync.
"""

import os
from pathlib import Path
from typing import Any, Dict

from jinja2 import BaseLoader, DictLoader, Environment, FileSystemLoader


class TemplateGenerator:
    """Genera templates personalizados para proyectos Tabula Cloud Sync."""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.templates_dir = project_root / "templates"
        self.services_dir = project_root / "services"

        # Asegurar que existen los directorios
        self.templates_dir.mkdir(exist_ok=True)
        self.services_dir.mkdir(exist_ok=True)

        # Configurar Jinja2 con templates internos
        self.jinja_env = Environment(loader=DictLoader(self._get_builtin_templates()))

    def _get_builtin_templates(self) -> Dict[str, str]:
        """Retorna templates integrados en la librería."""
        return {
            "service_template.py": '''"""
Servicio personalizado para {{ project_name }}.

Este archivo fue generado automáticamente por Tabula Cloud Sync.
Personaliza los métodos según las necesidades de tu proyecto.
"""

import os
import time
from datetime import datetime
from typing import Dict, Any, Optional

from tabula_cloud_sync import TabulaCloudService


class {{ class_name }}(TabulaCloudService):
    """Servicio personalizado para {{ project_name }}."""

    def __init__(self, config_file: str = "config/tabula_config.ini"):
        """Inicializa el servicio personalizado."""
        super().__init__(config_file)
        
        # Variables específicas del proyecto
        self.records_synced = 0
        self.last_sync_time = None
        self.sync_errors = []

    def on_start(self) -> None:
        """Callback ejecutado al iniciar el servicio."""
        self.logger.info("=== Iniciando {{ project_name }} Service ===")
        
        # Inicialización personalizada aquí
        self._initialize_custom_resources()
        
        self.logger.info("Servicio iniciado correctamente")

    def on_stop(self) -> None:
        """Callback ejecutado al detener el servicio."""
        self.logger.info("=== Deteniendo {{ project_name }} Service ===")
        
        # Limpieza de recursos aquí
        self._cleanup_resources()
        
        self.logger.info("Servicio detenido correctamente")

    def perform_sync(self) -> Dict[str, Any]:
        """
        Implementa la lógica de sincronización personalizada.
        
        Returns:
            Dict con resultados de la sincronización
        """
        try:
            self.logger.info("Iniciando sincronización personalizada...")
            
            # IMPLEMENTAR: Tu lógica de sincronización aquí
            results = self._execute_custom_sync()
            
            self.records_synced += results.get('count', 0)
            self.last_sync_time = datetime.now()
            
            self.logger.info(f"Sincronización completada: {results}")
            return results
            
        except Exception as e:
            self.logger.error(f"Error en sincronización: {e}")
            self.sync_errors.append(str(e))
            raise

    def _initialize_custom_resources(self) -> None:
        """Inicializa recursos específicos del proyecto."""
        # IMPLEMENTAR: Conexiones a DB, APIs, etc.
        pass

    def _cleanup_resources(self) -> None:
        """Limpia recursos al finalizar."""
        # IMPLEMENTAR: Cerrar conexiones, limpiar cache, etc.
        pass

    def _execute_custom_sync(self) -> Dict[str, Any]:
        """
        Ejecuta la lógica de sincronización específica.
        
        Returns:
            Dict con resultados de la operación
        """
        # IMPLEMENTAR: Tu lógica específica de sincronización
        
        # Ejemplo básico:
        return {
            'status': 'success',
            'count': 0,
            'timestamp': datetime.now().isoformat(),
            'details': 'Sincronización básica completada'
        }

    def get_sync_status(self) -> Dict[str, Any]:
        """Retorna el estado actual de sincronización."""
        return {
            'records_synced': self.records_synced,
            'last_sync_time': self.last_sync_time.isoformat() if self.last_sync_time else None,
            'error_count': len(self.sync_errors),
            'is_running': self.running
        }


# Para uso como script independiente
if __name__ == "__main__":
    service = {{ class_name }}()
    service.start()
''',
            "model_template.py": '''"""
Modelo de datos personalizado para {{ project_name }}.

Este archivo fue generado automáticamente por Tabula Cloud Sync.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict, Any


@dataclass
class {{ model_name }}:
    """Modelo de datos para {{ project_name }}."""
    
    id: Optional[int] = None
    name: str = ""
    description: str = ""
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    is_active: bool = True
    metadata: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte el modelo a diccionario."""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'is_active': self.is_active,
            'metadata': self.metadata or {}
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> '{{ model_name }}':
        """Crea una instancia desde un diccionario."""
        return cls(
            id=data.get('id'),
            name=data.get('name', ''),
            description=data.get('description', ''),
            created_at=datetime.fromisoformat(data['created_at']) if data.get('created_at') else None,
            updated_at=datetime.fromisoformat(data['updated_at']) if data.get('updated_at') else None,
            is_active=data.get('is_active', True),
            metadata=data.get('metadata')
        )
    
    def validate(self) -> bool:
        """Valida los datos del modelo."""
        if not self.name or not self.name.strip():
            return False
        return True
''',
            "daemon_template.py": '''"""
Daemon personalizado para {{ project_name }}.

Este archivo fue generado automáticamente por Tabula Cloud Sync.
"""

import sys
import signal
from pathlib import Path

# Agregar el directorio del proyecto al path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from tabula_cloud_sync.service.daemon import TabulaCloudDaemon
from .{{ service_filename }} import {{ class_name }}


class {{ project_name }}Daemon(TabulaCloudDaemon):
    """Daemon personalizado para {{ project_name }}."""
    
    def __init__(self):
        super().__init__(
            service_class={{ class_name }},
            pidfile='/tmp/{{ project_name.lower() }}_daemon.pid'
        )


def signal_handler(signum, frame):
    """Manejador de señales para cerrar el daemon correctamente."""
    print(f"\\nRecibida señal {signum}. Cerrando daemon...")
    daemon.stop()
    sys.exit(0)


if __name__ == "__main__":
    daemon = {{ project_name }}Daemon()
    
    # Configurar manejadores de señales
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    if len(sys.argv) == 2:
        if 'start' == sys.argv[1]:
            daemon.start()
        elif 'stop' == sys.argv[1]:
            daemon.stop()
        elif 'restart' == sys.argv[1]:
            daemon.restart()
        elif 'status' == sys.argv[1]:
            daemon.status()
        else:
            print(f"Comando desconocido: {sys.argv[1]}")
            sys.exit(2)
        sys.exit(0)
    else:
        print(f"Uso: {sys.argv[0]} start|stop|restart|status")
        sys.exit(2)
''',
        }

    def generate_service_template(
        self, service_name: str = None, project_name: str = None
    ) -> Path:
        """Genera un template de servicio personalizado."""
        if not service_name:
            service_name = f"{self.project_root.name.title()}Service"

        if not project_name:
            project_name = (
                self.project_root.name.replace("_", " ").replace("-", " ").title()
            )

        class_name = service_name.replace(" ", "").replace("_", "").replace("-", "")

        template = self.jinja_env.get_template("service_template.py")
        content = template.render(project_name=project_name, class_name=class_name)

        service_file = self.services_dir / f"{service_name.lower()}.py"
        service_file.write_text(content)

        return service_file

    def generate_model_template(self, model_name: str = None) -> Path:
        """Genera un template de modelo de datos."""
        if not model_name:
            model_name = f"{self.project_root.name.title()}Model"

        model_name = model_name.replace(" ", "").replace("_", "").replace("-", "")

        template = self.jinja_env.get_template("model_template.py")
        content = template.render(
            project_name=self.project_root.name, model_name=model_name
        )

        models_dir = self.project_root / "models"
        models_dir.mkdir(exist_ok=True)

        model_file = models_dir / f"{model_name.lower()}.py"
        model_file.write_text(content)

        return model_file

    def generate_daemon_template(self, service_name: str = None) -> Path:
        """Genera un template de daemon."""
        if not service_name:
            service_name = f"{self.project_root.name.title()}Service"

        class_name = service_name.replace(" ", "").replace("_", "").replace("-", "")
        project_name = (
            self.project_root.name.replace("_", " ").replace("-", " ").title()
        )
        service_filename = service_name.lower()

        template = self.jinja_env.get_template("daemon_template.py")
        content = template.render(
            project_name=project_name.replace(" ", ""),
            class_name=class_name,
            service_filename=service_filename,
        )

        daemon_file = self.services_dir / "daemon.py"
        daemon_file.write_text(content)

        return daemon_file

    def generate_custom_template(
        self, template_name: str, output_path: Path, context: Dict[str, Any]
    ) -> Path:
        """Genera un template personalizado."""
        if template_name in self.jinja_env.list_templates():
            template = self.jinja_env.get_template(template_name)
            content = template.render(**context)

            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(content)

            return output_path
        else:
            raise ValueError(f"Template {template_name} no encontrado")
