"""
Generador de templates para Tabula Cloud Sync.

Proporciona funcionalidad para generar archivos de código base
como servicios, modelos y daemons para proyectos nuevos.
"""

import logging
from pathlib import Path
from typing import Optional

from ..utils.directories import ensure_directory

logger = logging.getLogger(__name__)


class TemplateGenerator:
    """
    Generador de templates de código para proyectos Tabula Cloud Sync.

    Crea archivos base de servicios, modelos y daemons con estructura
    predefinida y mejores prácticas incluidas.
    """

    def __init__(self, project_root: Path):
        """
        Inicializa el generador de templates.

        Args:
            project_root: Directorio raíz del proyecto
        """
        self.project_root = Path(project_root)
        self.services_dir = self.project_root / "services"
        self.models_dir = self.project_root / "models"

    def generate_service_template(
        self,
        service_name: str,
        project_name: str,
        output_dir: Optional[Path] = None,
    ) -> Path:
        """
        Genera un template de servicio base.

        Args:
            service_name: Nombre del servicio a crear
            project_name: Nombre del proyecto
            output_dir: Directorio de salida personalizado

        Returns:
            Path al archivo generado
        """
        output_dir = output_dir or self.services_dir
        ensure_directory(output_dir)

        # Limpiar nombre del servicio
        clean_service_name = service_name.replace("Service", "").replace(
            "service", ""
        )
        service_class_name = f"{clean_service_name}Service"
        filename = f"{clean_service_name.lower()}_service.py"

        template_content = f'''"""
Servicio de sincronización para {project_name}.

Este servicio maneja la sincronización de datos entre la aplicación local
y Tabula Cloud, implementando la lógica de negocio específica del proyecto.
"""

import logging
from typing import Any, Dict, List, Optional
from datetime import datetime

from tabula_cloud_sync.service.base_service import BaseService


logger = logging.getLogger(__name__)


class {service_class_name}(BaseService):
    """
    Servicio de sincronización para {project_name}.
    
    Implementa la lógica específica de sincronización de datos
    entre la aplicación local y Tabula Cloud.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Inicializa el servicio de sincronización.
        
        Args:
            config_path: Ruta al archivo de configuración
        """
        # Usar config_path o valor por defecto
        config_file = config_path or "config.ini"
        super().__init__(config_file)
        self.service_name = "{clean_service_name}"
        
    def process_sync_data(self, data: List[Dict[str, Any]]) -> bool:
        """
        Procesa los datos para sincronización.
        
        Args:
            data: Lista de datos a sincronizar
            
        Returns:
            bool: True si el procesamiento fue exitoso
        """
        try:
            logger.info(f"Procesando {{len(data)}} registros para sincronización")
            
            for record in data:
                # TODO: Implementar lógica específica de procesamiento
                self._process_single_record(record)
                
            logger.info("Procesamiento completado exitosamente")
            return True
            
        except Exception as e:
            logger.error(f"Error procesando datos: {{e}}")
            return False
    
    def _process_single_record(self, record: Dict[str, Any]) -> None:
        """
        Procesa un registro individual.
        
        Args:
            record: Datos del registro a procesar
        """
        # TODO: Implementar lógica específica por registro
        # Ejemplo de procesamiento básico:
        
        # 1. Validar datos
        if not self._validate_record(record):
            record_id = record.get('id', 'unknown')
            logger.warning(f"Registro inválido ignorado: {{record_id}}")
            return
            
        # 2. Transformar datos si es necesario
        transformed_data = self._transform_record(record)
        
        # 3. Preparar para envío a Tabula Cloud
        self._prepare_for_sync(transformed_data)
        
    def _validate_record(self, record: Dict[str, Any]) -> bool:
        """
        Valida un registro antes del procesamiento.
        
        Args:
            record: Datos del registro
            
        Returns:
            bool: True si el registro es válido
        """
        # TODO: Implementar validaciones específicas
        required_fields = ['id']  # Definir campos requeridos
        
        for field in required_fields:
            if field not in record or record[field] is None:
                return False
                
        return True
    
    def _transform_record(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """
        Transforma un registro al formato requerido.
        
        Args:
            record: Datos originales del registro
            
        Returns:
            Dict con datos transformados
        """
        # TODO: Implementar transformaciones específicas
        transformed = record.copy()
        
        # Ejemplo de transformaciones comunes:
        if 'timestamp' not in transformed:
            transformed['timestamp'] = datetime.now().isoformat()
            
        return transformed
    
    def _prepare_for_sync(self, record: Dict[str, Any]) -> None:
        """
        Prepara un registro para sincronización con Tabula Cloud.
        
        Args:
            record: Datos del registro transformado
        """
        # TODO: Implementar preparación para sincronización
        # Esto podría incluir:
        # - Agregar a cola de sincronización
        # - Marcar como pendiente en base de datos local
        # - Aplicar reglas de negocio específicas
        
        logger.debug(f"Registro preparado para sync: {{record.get('id')}}")
    
    def get_pending_records(self) -> List[Dict[str, Any]]:
        """
        Obtiene registros pendientes de sincronización.
        
        Returns:
            Lista de registros pendientes
        """
        # TODO: Implementar consulta a base de datos local
        # para obtener registros pendientes de sincronización
        
        logger.info("Obteniendo registros pendientes...")
        return []
    
    def mark_as_synced(self, record_id: str) -> bool:
        """
        Marca un registro como sincronizado.
        
        Args:
            record_id: ID del registro sincronizado
            
        Returns:
            bool: True si se marcó exitosamente
        """
        try:
            # TODO: Implementar actualización en base de datos local
            logger.info(f"Registro {{record_id}} marcado como sincronizado")
            return True
            
        except Exception as e:
            logger.error(f"Error marcando registro como sincronizado: {{e}}")
            return False
    
    def get_service_status(self) -> Dict[str, Any]:
        """
        Obtiene el estado actual del servicio.
        
        Returns:
            Dict con información de estado
        """
        pending_count = len(self.get_pending_records())
        
        return {{
            'service_name': self.service_name,
            'status': 'running' if self.running else 'stopped',
            'pending_records': pending_count,
            'last_sync': self.last_sync_time.isoformat() if self.last_sync_time else None,
            'config_valid': self.config is not None
        }}
    
    def perform_sync(self) -> Dict[str, Any]:
        """
        Implementa la sincronización con Tabula Cloud.
        
        Este método es requerido por la clase base abstracta BaseService.
        Implementa la lógica específica de sincronización para este servicio.
        
        Returns:
            Dict con resultados de la sincronización
        """
        try:
            logger.info(f"Iniciando sincronización para {{self.service_name}}")
            
            # 1. Obtener registros pendientes de sincronización
            pending_records = self.get_pending_records()
            
            if not pending_records:
                logger.info("No hay registros pendientes para sincronizar")
                return {{
                    'status': 'success',
                    'message': 'No hay datos pendientes',
                    'records_processed': 0,
                    'timestamp': datetime.now().isoformat()
                }}
            
            logger.info(f"Encontrados {{len(pending_records)}} registros pendientes")
            
            # 2. Procesar registros para sincronización
            if not self.process_sync_data(pending_records):
                raise Exception("Error procesando datos para sincronización")
            
            # 3. Enviar datos a Tabula Cloud
            sync_result = self._send_to_tabula_cloud(pending_records)
            
            # 4. Marcar registros como sincronizados
            synced_count = 0
            for record in pending_records:
                record_id = record.get('id', 'unknown')
                if self.mark_as_synced(record_id):
                    synced_count += 1
            
            total_records = len(pending_records)
            logger.info(
                f"Sync completado: {{synced_count}}/{{total_records}} registros"
            )
            
            return {{
                'status': 'success',
                'message': f'Sincronización completada exitosamente',
                'records_processed': len(pending_records),
                'records_synced': synced_count,
                'timestamp': datetime.now().isoformat(),
                'sync_details': sync_result
            }}
            
        except Exception as e:
            logger.error(f"Error en sincronización: {{e}}")
            return {{
                'status': 'error',
                'message': f'Error en sincronización: {{str(e)}}',
                'records_processed': 0,
                'timestamp': datetime.now().isoformat()
            }}
    
    def _send_to_tabula_cloud(self, records: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Envía los registros a Tabula Cloud.
        
        Args:
            records: Lista de registros a enviar
            
        Returns:
            Dict con resultado del envío
        """
        try:
            if not self.session:
                raise Exception("Sesión no inicializada")
            
            logger.info(f"Enviando {{len(records)}} registros a Tabula Cloud")
            
            # TODO: Implementar lógica específica de envío según la API de Tabula Cloud
            # Ejemplo de estructura básica:
            
            payload = {{
                'service_name': self.service_name,
                'timestamp': datetime.now().isoformat(),
                'data': records,
                'metadata': {{
                    'count': len(records),
                    'source': 'sync_service'
                }}
            }}
            
            # Simular envío exitoso (reemplazar con llamada real a la API)
            # response = self.session.post('/api/sync', json=payload)
            # response.raise_for_status()
            
            logger.info("Datos enviados exitosamente a Tabula Cloud")
            
            return {{
                'sent_records': len(records),
                'api_response': 'success',  # response.json() en implementación real
                'endpoint': '/api/sync'
            }}
            
        except Exception as e:
            logger.error(f"Error enviando datos a Tabula Cloud: {{e}}")
            raise


# Función de conveniencia para crear instancia del servicio
def create_service(config_path: Optional[str] = None) -> {service_class_name}:
    """
    Crea una instancia del servicio de sincronización.
    
    Args:
        config_path: Ruta al archivo de configuración
        
    Returns:
        Instancia del servicio configurada
    """
    return {service_class_name}(config_path)


if __name__ == "__main__":
    # Script de prueba del servicio
    import sys
    
    # Configurar logging básico
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    try:
        # Crear servicio
        service = create_service()
        
        # Mostrar estado
        status = service.get_service_status()
        print(f"Estado del servicio: {{status}}")
        
        # Datos de prueba
        test_data = [
            {{'id': '1', 'name': 'Test Record 1', 'value': 100}},
            {{'id': '2', 'name': 'Test Record 2', 'value': 200}}
        ]
        
        # Procesar datos de prueba
        if service.process_sync_data(test_data):
            print("✅ Procesamiento de prueba exitoso")
        else:
            print("❌ Error en procesamiento de prueba")
            
    except Exception as e:
        print(f"❌ Error ejecutando servicio: {{e}}")
        sys.exit(1)
'''

        output_file = output_dir / filename
        output_file.write_text(template_content)

        logger.info(f"Template de servicio generado: {output_file}")
        return output_file

    def generate_model_template(
        self, model_name: str, output_dir: Optional[Path] = None
    ) -> Path:
        """
        Genera un template de modelo base.

        Args:
            model_name: Nombre del modelo a crear
            output_dir: Directorio de salida personalizado

        Returns:
            Path al archivo generado
        """
        output_dir = output_dir or self.models_dir
        ensure_directory(output_dir)

        # Limpiar nombre del modelo
        clean_model_name = model_name.replace("Model", "").replace("model", "")
        model_class_name = f"{clean_model_name}Model"
        filename = f"{clean_model_name.lower()}_model.py"

        template_content = f'''"""
Modelo de datos para {clean_model_name}.

Define la estructura y comportamiento de los datos {clean_model_name}
para sincronización con Tabula Cloud.
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field

from tabula_cloud_sync.models.base_model import BaseModel


logger = logging.getLogger(__name__)


@dataclass
class {model_class_name}(BaseModel):
    """
    Modelo de datos para {clean_model_name}.
    
    Representa la estructura de datos que se sincronizará
    con Tabula Cloud para entidades {clean_model_name}.
    """
    
    # Campos básicos (personalizar según necesidades)
    id: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    
    # Campos de auditoría
    created_at: Optional[datetime] = field(default_factory=datetime.now)
    updated_at: Optional[datetime] = field(default_factory=datetime.now)
    
    # Estado de sincronización
    sync_status: str = "pending"  # pending, synced, failed
    sync_errors: List[str] = field(default_factory=list)
    
    # Metadatos adicionales
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Inicialización posterior a la creación del objeto."""
        super().__post_init__()
        
        # Validaciones automáticas
        self.validate()
        
    def validate(self) -> bool:
        """
        Valida los datos del modelo.
        
        Returns:
            bool: True si los datos son válidos
            
        Raises:
            ValueError: Si los datos no son válidos
        """
        errors = []
        
        # Validaciones básicas (personalizar según necesidades)
        if not self.id:
            errors.append("ID es requerido")
            
        if not self.name or len(self.name.strip()) == 0:
            errors.append("Nombre es requerido")
            
        # TODO: Agregar más validaciones específicas
        
        if errors:
            error_msg = f"Errores de validación en {{self.__class__.__name__}}: {{', '.join(errors)}}"
            logger.error(error_msg)
            raise ValueError(error_msg)
            
        return True
    
    def to_sync_format(self) -> Dict[str, Any]:
        """
        Convierte el modelo al formato requerido para sincronización.
        
        Returns:
            Dict con datos en formato de sincronización
        """
        # Formato base para Tabula Cloud
        sync_data = {{
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'metadata': self.metadata
        }}
        
        # TODO: Personalizar formato según requirements de Tabula Cloud
        
        # Filtrar valores None
        return {{k: v for k, v in sync_data.items() if v is not None}}
    
    @classmethod
    def from_sync_data(cls, data: Dict[str, Any]) -> '{model_class_name}':
        """
        Crea una instancia del modelo desde datos de sincronización.
        
        Args:
            data: Datos recibidos de Tabula Cloud
            
        Returns:
            Instancia del modelo
        """
        # Convertir timestamps si están presentes
        created_at = None
        updated_at = None
        
        if 'created_at' in data and data['created_at']:
            try:
                created_at = datetime.fromisoformat(data['created_at'])
            except ValueError:
                logger.warning(f"Formato de fecha inválido para created_at: {{data['created_at']}}")
                
        if 'updated_at' in data and data['updated_at']:
            try:
                updated_at = datetime.fromisoformat(data['updated_at'])
            except ValueError:
                logger.warning(f"Formato de fecha inválido para updated_at: {{data['updated_at']}}")
        
        return cls(
            id=data.get('id'),
            name=data.get('name'),
            description=data.get('description'),
            created_at=created_at,
            updated_at=updated_at,
            metadata=data.get('metadata', {{}})
        )
    
    def mark_as_synced(self) -> None:
        """Marca el modelo como sincronizado exitosamente."""
        self.sync_status = "synced"
        self.sync_errors.clear()
        self.updated_at = datetime.now()
        
    def mark_sync_failed(self, error: str) -> None:
        """
        Marca el modelo como fallido en sincronización.
        
        Args:
            error: Descripción del error
        """
        self.sync_status = "failed"
        self.sync_errors.append(f"{{datetime.now().isoformat()}}: {{error}}")
        self.updated_at = datetime.now()
        
    def is_sync_pending(self) -> bool:
        """
        Verifica si el modelo está pendiente de sincronización.
        
        Returns:
            bool: True si está pendiente
        """
        return self.sync_status == "pending"
    
    def get_sync_summary(self) -> Dict[str, Any]:
        """
        Obtiene un resumen del estado de sincronización.
        
        Returns:
            Dict con información de sincronización
        """
        return {{
            'id': self.id,
            'name': self.name,
            'sync_status': self.sync_status,
            'last_updated': self.updated_at.isoformat() if self.updated_at else None,
            'error_count': len(self.sync_errors),
            'last_error': self.sync_errors[-1] if self.sync_errors else None
        }}


class {model_class_name}Repository:
    """
    Repositorio para manejar operaciones de datos del modelo {model_class_name}.
    
    Proporciona métodos para CRUD y operaciones de sincronización.
    """
    
    def __init__(self, db_connection=None):
        """
        Inicializa el repositorio.
        
        Args:
            db_connection: Conexión a la base de datos
        """
        self.db = db_connection
        
    def save(self, model: {model_class_name}) -> bool:
        """
        Guarda un modelo en la base de datos.
        
        Args:
            model: Instancia del modelo a guardar
            
        Returns:
            bool: True si se guardó exitosamente
        """
        try:
            # TODO: Implementar persistencia en base de datos
            logger.info(f"Guardando modelo {{model.id}}")
            
            # Validar antes de guardar
            model.validate()
            
            # Actualizar timestamp
            model.updated_at = datetime.now()
            
            # TODO: Ejecutar INSERT/UPDATE en base de datos
            
            return True
            
        except Exception as e:
            logger.error(f"Error guardando modelo: {{e}}")
            return False
    
    def find_by_id(self, model_id: str) -> Optional[{model_class_name}]:
        """
        Busca un modelo por ID.
        
        Args:
            model_id: ID del modelo a buscar
            
        Returns:
            Instancia del modelo o None si no se encuentra
        """
        try:
            # TODO: Implementar consulta a base de datos
            logger.info(f"Buscando modelo con ID: {{model_id}}")
            
            # Placeholder - implementar consulta real
            return None
            
        except Exception as e:
            logger.error(f"Error buscando modelo: {{e}}")
            return None
    
    def find_pending_sync(self) -> List[{model_class_name}]:
        """
        Obtiene todos los modelos pendientes de sincronización.
        
        Returns:
            Lista de modelos pendientes
        """
        try:
            # TODO: Implementar consulta a base de datos
            logger.info("Obteniendo modelos pendientes de sincronización")
            
            # Placeholder - implementar consulta real
            return []
            
        except Exception as e:
            logger.error(f"Error obteniendo modelos pendientes: {{e}}")
            return []
    
    def delete(self, model_id: str) -> bool:
        """
        Elimina un modelo por ID.
        
        Args:
            model_id: ID del modelo a eliminar
            
        Returns:
            bool: True si se eliminó exitosamente
        """
        try:
            # TODO: Implementar eliminación en base de datos
            logger.info(f"Eliminando modelo {{model_id}}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error eliminando modelo: {{e}}")
            return False


# Funciones de conveniencia
def create_model(data: Dict[str, Any]) -> {model_class_name}:
    """
    Crea una instancia del modelo desde datos.
    
    Args:
        data: Datos para crear el modelo
        
    Returns:
        Instancia del modelo
    """
    return {model_class_name}.from_sync_data(data)


def create_repository(db_connection=None) -> {model_class_name}Repository:
    """
    Crea una instancia del repositorio.
    
    Args:
        db_connection: Conexión a la base de datos
        
    Returns:
        Instancia del repositorio
    """
    return {model_class_name}Repository(db_connection)


if __name__ == "__main__":
    # Script de prueba del modelo
    import json
    
    # Configurar logging básico
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    try:
        # Crear modelo de prueba
        test_data = {{
            'id': 'test-001',
            'name': 'Modelo de Prueba',
            'description': 'Este es un modelo de prueba',
            'metadata': {{'test': True, 'version': '1.0'}}
        }}
        
        model = create_model(test_data)
        print(f"✅ Modelo creado: {{model.name}}")
        
        # Probar conversión a formato de sync
        sync_format = model.to_sync_format()
        print(f"📤 Formato de sync: {{json.dumps(sync_format, indent=2)}}")
        
        # Probar validación
        model.validate()
        print("✅ Validación exitosa")
        
        # Probar estados de sync
        model.mark_as_synced()
        print(f"📊 Estado después de sync: {{model.get_sync_summary()}}")
        
    except Exception as e:
        print(f"❌ Error en prueba del modelo: {{e}}")
        import traceback
        traceback.print_exc()
'''

        output_file = output_dir / filename
        output_file.write_text(template_content)

        logger.info(f"Template de modelo generado: {output_file}")
        return output_file

    def generate_daemon_template(
        self, service_name: str, output_dir: Optional[Path] = None
    ) -> Path:
        """
        Genera un template de daemon base.

        Args:
            service_name: Nombre del servicio para el daemon
            output_dir: Directorio de salida personalizado

        Returns:
            Path al archivo generado
        """
        output_dir = output_dir or self.services_dir
        ensure_directory(output_dir)

        # Limpiar nombre del servicio
        clean_service_name = service_name.replace("Service", "").replace(
            "service", ""
        )
        daemon_class_name = f"{clean_service_name}Daemon"
        filename = f"{clean_service_name.lower()}_daemon.py"

        template_content = f'''"""
Daemon de sincronización para {clean_service_name}.

Ejecuta el servicio de sincronización como un proceso daemon,
manejando el ciclo de vida del servicio y la sincronización automática.
"""

import logging
import signal
import sys
import time
from pathlib import Path
from typing import Optional
from threading import Event, Thread

from tabula_cloud_sync.service.daemon import BaseDaemon


logger = logging.getLogger(__name__)


class {daemon_class_name}(BaseDaemon):
    """
    Daemon para ejecutar el servicio de sincronización {clean_service_name}.
    
    Maneja la ejecución continua del servicio, incluyendo:
    - Inicio/parada del servicio
    - Sincronización periódica
    - Manejo de señales del sistema
    - Logging y monitoreo
    """
    
    def __init__(
        self, 
        config_path: Optional[str] = None,
        sync_interval: int = 60,
        max_retries: int = 3
    ):
        """
        Inicializa el daemon.
        
        Args:
            config_path: Ruta al archivo de configuración
            sync_interval: Intervalo de sincronización en segundos
            max_retries: Número máximo de reintentos en caso de error
        """
        super().__init__(config_path)
        
        self.service_name = "{clean_service_name}"
        self.sync_interval = sync_interval
        self.max_retries = max_retries
        
        # Control de ejecución
        self._stop_event = Event()
        self._sync_thread: Optional[Thread] = None
        
        # Estadísticas
        self.sync_count = 0
        self.error_count = 0
        self.last_sync_time: Optional[float] = None
        
        # Configurar manejo de señales
        self._setup_signal_handlers()
        
    def _setup_signal_handlers(self):
        """Configura los manejadores de señales del sistema."""
        signal.signal(signal.SIGTERM, self._signal_handler)
        signal.signal(signal.SIGINT, self._signal_handler)
        
        if hasattr(signal, 'SIGHUP'):
            signal.signal(signal.SIGHUP, self._signal_handler)
            
    def _signal_handler(self, signum, frame):
        """
        Maneja señales del sistema.
        
        Args:
            signum: Número de la señal
            frame: Frame actual
        """
        signal_names = {{
            signal.SIGTERM: 'SIGTERM',
            signal.SIGINT: 'SIGINT'
        }}
        
        if hasattr(signal, 'SIGHUP'):
            signal_names[signal.SIGHUP] = 'SIGHUP'
            
        signal_name = signal_names.get(signum, f'Signal {{signum}}')
        logger.info(f"Recibida señal {{signal_name}}, iniciando parada...")
        
        if signum == getattr(signal, 'SIGHUP', None):
            # SIGHUP - recargar configuración
            self._reload_config()
        else:
            # SIGTERM/SIGINT - parar daemon
            self.stop()
    
    def start(self) -> bool:
        """
        Inicia el daemon de sincronización.
        
        Returns:
            bool: True si se inició exitosamente
        """
        try:
            logger.info(f"Iniciando daemon {{self.service_name}}...")
            
            # Verificar configuración
            if not self.config:
                logger.error("No se pudo cargar la configuración")
                return False
            
            # Inicializar servicio
            if not self._initialize_service():
                logger.error("Error inicializando servicio")
                return False
            
            # Iniciar hilo de sincronización
            self._sync_thread = Thread(target=self._sync_loop, daemon=True)
            self._sync_thread.start()
            
            logger.info(f"Daemon {{self.service_name}} iniciado exitosamente")
            logger.info(f"Intervalo de sincronización: {{self.sync_interval}} segundos")
            
            return True
            
        except Exception as e:
            logger.error(f"Error iniciando daemon: {{e}}")
            return False
    
    def stop(self) -> None:
        """Detiene el daemon de sincronización."""
        logger.info(f"Deteniendo daemon {{self.service_name}}...")
        
        # Señalar parada
        self._stop_event.set()
        
        # Esperar a que termine el hilo de sincronización
        if self._sync_thread and self._sync_thread.is_alive():
            logger.info("Esperando que termine la sincronización...")
            self._sync_thread.join(timeout=30)
            
            if self._sync_thread.is_alive():
                logger.warning("El hilo de sincronización no terminó en tiempo esperado")
        
        # Limpiar recursos
        self._cleanup_resources()
        
        logger.info(f"Daemon {{self.service_name}} detenido")
    
    def _initialize_service(self) -> bool:
        """
        Inicializa el servicio de sincronización.
        
        Returns:
            bool: True si se inicializó exitosamente
        """
        try:
            # TODO: Importar e inicializar el servicio específico
            # from .{clean_service_name.lower()}_service import create_service
            # self.service = create_service(self.config_path)
            
            logger.info("Servicio inicializado exitosamente")
            return True
            
        except Exception as e:
            logger.error(f"Error inicializando servicio: {{e}}")
            return False
    
    def _sync_loop(self) -> None:
        """Bucle principal de sincronización."""
        logger.info("Iniciando bucle de sincronización...")
        
        while not self._stop_event.is_set():
            try:
                start_time = time.time()
                
                # Ejecutar sincronización
                if self._perform_sync():
                    self.sync_count += 1
                    self.last_sync_time = start_time
                    logger.debug(f"Sincronización {{self.sync_count}} completada")
                else:
                    self.error_count += 1
                    logger.warning(f"Error en sincronización {{self.sync_count + 1}}")
                
                # Esperar hasta el próximo ciclo
                elapsed = time.time() - start_time
                wait_time = max(0, self.sync_interval - elapsed)
                
                if wait_time > 0:
                    self._stop_event.wait(wait_time)
                    
            except Exception as e:
                self.error_count += 1
                logger.error(f"Error inesperado en bucle de sincronización: {{e}}")
                
                # Esperar antes de reintentar
                self._stop_event.wait(min(self.sync_interval, 30))
        
        logger.info("Bucle de sincronización terminado")
    
    def _perform_sync(self) -> bool:
        """
        Ejecuta una sincronización.
        
        Returns:
            bool: True si la sincronización fue exitosa
        """
        try:
            # TODO: Implementar lógica de sincronización específica
            # Ejemplo de estructura:
            
            # 1. Obtener datos pendientes
            # pending_data = self.service.get_pending_records()
            
            # 2. Procesar datos
            # if pending_data:
            #     success = self.service.process_sync_data(pending_data)
            #     return success
            
            # Placeholder - simular sincronización exitosa
            logger.debug("Ejecutando sincronización...")
            time.sleep(0.1)  # Simular trabajo
            
            return True
            
        except Exception as e:
            logger.error(f"Error en sincronización: {{e}}")
            return False
    
    def _reload_config(self) -> None:
        """Recarga la configuración del daemon."""
        try:
            logger.info("Recargando configuración...")
            
            # TODO: Implementar recarga de configuración
            # self.load_config()
            
            logger.info("Configuración recargada exitosamente")
            
        except Exception as e:
            logger.error(f"Error recargando configuración: {{e}}")
    
    def _cleanup_resources(self) -> None:
        """Limpia recursos utilizados por el daemon."""
        try:
            # TODO: Limpiar recursos específicos del servicio
            pass
            
        except Exception as e:
            logger.error(f"Error limpiando recursos: {{e}}")
    
    def get_status(self) -> dict:
        """
        Obtiene el estado actual del daemon.
        
        Returns:
            Dict con información de estado
        """
        is_running = self._sync_thread and self._sync_thread.is_alive()
        
        return {{
            'service_name': self.service_name,
            'is_running': is_running,
            'sync_interval': self.sync_interval,
            'sync_count': self.sync_count,
            'error_count': self.error_count,
            'last_sync_time': self.last_sync_time,
            'uptime': time.time() - self.start_time if hasattr(self, 'start_time') else 0
        }}
    
    def run_forever(self) -> None:
        """
        Ejecuta el daemon indefinidamente hasta recibir señal de parada.
        
        Método principal para ejecutar como servicio del sistema.
        """
        try:
            # Marcar tiempo de inicio
            self.start_time = time.time()
            
            # Iniciar daemon
            if not self.start():
                logger.error("No se pudo iniciar el daemon")
                sys.exit(1)
            
            # Ejecutar hasta recibir señal de parada
            logger.info("Daemon ejecutándose... (Ctrl+C para detener)")
            
            try:
                while not self._stop_event.is_set():
                    self._stop_event.wait(1)
                    
            except KeyboardInterrupt:
                logger.info("Interrupción por teclado recibida")
            
            # Detener daemon
            self.stop()
            
        except Exception as e:
            logger.error(f"Error ejecutando daemon: {{e}}")
            sys.exit(1)


def create_daemon(
    config_path: Optional[str] = None,
    sync_interval: int = 60,
    max_retries: int = 3
) -> {daemon_class_name}:
    """
    Crea una instancia del daemon.
    
    Args:
        config_path: Ruta al archivo de configuración
        sync_interval: Intervalo de sincronización en segundos
        max_retries: Número máximo de reintentos
        
    Returns:
        Instancia del daemon configurada
    """
    return {daemon_class_name}(config_path, sync_interval, max_retries)


def main():
    """Función principal para ejecutar el daemon desde línea de comandos."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description=f'Daemon de sincronización {clean_service_name}'
    )
    parser.add_argument(
        '--config', 
        help='Archivo de configuración',
        default=None
    )
    parser.add_argument(
        '--interval',
        type=int,
        help='Intervalo de sincronización en segundos',
        default=60
    )
    parser.add_argument(
        '--log-level',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        help='Nivel de logging',
        default='INFO'
    )
    
    args = parser.parse_args()
    
    # Configurar logging
    logging.basicConfig(
        level=getattr(logging, args.log_level),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            # TODO: Agregar handler para archivo de log
        ]
    )
    
    # Crear y ejecutar daemon
    daemon = create_daemon(
        config_path=args.config,
        sync_interval=args.interval
    )
    
    daemon.run_forever()


if __name__ == "__main__":
    main()
'''

        output_file = output_dir / filename
        output_file.write_text(template_content)

        logger.info(f"Template de daemon generado: {output_file}")
        return output_file

    def generate_database_structure(
        self, project_name: str = "Project"
    ) -> None:
        """
        Genera la estructura completa de database con queries organizados.

        Crea directorios y archivos base para organizar queries SQL
        de forma limpia y mantenible, sin migraciones.

        Args:
            project_name: Nombre del proyecto para personalizar archivos
        """
        database_dir = self.project_root / "database"
        queries_dir = database_dir / "queries"

        # Crear directorios
        ensure_directory(str(database_dir))
        ensure_directory(str(queries_dir))

        # Crear archivos __init__.py
        self._create_init_files(database_dir, queries_dir)

        # Crear archivos principales
        self._create_connection_file(database_dir)
        self._create_select_queries_file(queries_dir, project_name)
        self._create_update_queries_file(queries_dir, project_name)
        self._create_repository_file(database_dir, project_name)
        self._create_custom_queries_file(queries_dir, project_name)

        logger.info(f"Estructura de database creada para {project_name}")

    def _create_init_files(
        self, database_dir: Path, queries_dir: Path
    ) -> None:
        """Crea archivos __init__.py para los packages."""
        database_init = (
            '"""Database package para queries y conexiones MySQL."""\n'
        )
        queries_init = (
            '"""Queries package para consultas SQL organizadas."""\n'
        )

        (database_dir / "__init__.py").write_text(database_init)
        (queries_dir / "__init__.py").write_text(queries_init)

    def _create_connection_file(self, database_dir: Path) -> None:
        """Crea el archivo connection.py con gestor de conexiones MySQL."""
        connection_content = '''"""
Gestor de conexiones MySQL.

Maneja conexiones seguras y eficientes a la base de datos
con soporte para transacciones y pooling de conexiones.
"""

import logging
import mysql.connector
from mysql.connector import Error, pooling
from contextlib import contextmanager
from typing import Dict, Any, List, Optional, Tuple
import configparser

logger = logging.getLogger(__name__)


class DatabaseConnection:
    """
    Gestor de conexiones MySQL con pool de conexiones.
    
    Proporciona métodos seguros para ejecutar queries SQL
    con manejo automático de conexiones y transacciones.
    """
    
    def __init__(self, config_file: str = "config/config.ini"):
        """
        Inicializa el gestor de conexiones.
        
        Args:
            config_file: Ruta al archivo de configuración
        """
        self.config_file = config_file
        self.connection_config = self._load_config()
        self._connection_pool = None
        
    def _load_config(self) -> Dict[str, Any]:
        """Carga la configuración de MySQL desde el archivo."""
        try:
            config = configparser.ConfigParser()
            config.read(self.config_file)
            
            if 'mysql' not in config:
                raise ValueError("Sección [mysql] no encontrada")
            
            mysql_config = dict(config['mysql'])
            
            # Convertir puerto a entero
            if 'port' in mysql_config:
                mysql_config['port'] = int(mysql_config['port'])
                
            # Configuraciones adicionales
            mysql_config.update({
                'autocommit': False,
                'charset': 'utf8mb4',
                'collation': 'utf8mb4_unicode_ci',
                'use_unicode': True,
                'raise_on_warnings': True
            })
            
            logger.info("Configuración MySQL cargada exitosamente")
            return mysql_config
            
        except Exception as e:
            logger.error(f"Error cargando configuración: {e}")
            raise
    
    @contextmanager
    def get_connection(self):
        """
        Context manager para obtener conexión MySQL.
        
        Yields:
            mysql.connector.MySQLConnection: Conexión activa
        """
        connection = None
        try:
            connection = mysql.connector.connect(**self.connection_config)
            logger.debug("Conexión MySQL establecida")
            yield connection
            
        except Error as e:
            logger.error(f"Error de conexión MySQL: {e}")
            if connection:
                connection.rollback()
            raise
            
        finally:
            if connection and connection.is_connected():
                connection.close()
                logger.debug("Conexión MySQL cerrada")
    
    def execute_query(self, query: str, params: Optional[Tuple] = None):
        """
        Ejecuta consulta SELECT y retorna resultados.
        
        Args:
            query: Query SQL a ejecutar
            params: Parámetros para el query
            
        Returns:
            Lista de diccionarios con resultados
        """
        try:
            with self.get_connection() as connection:
                cursor = connection.cursor(dictionary=True)
                
                logger.debug(f"Ejecutando query: {query}")
                cursor.execute(query, params or ())
                results = cursor.fetchall()
                
                logger.debug(f"Query exitoso. Filas: {len(results)}")
                return results
                
        except Error as e:
            logger.error(f"Error en query: {e}")
            raise
        finally:
            if 'cursor' in locals():
                cursor.close()
    
    def execute_update(self, query: str, params: Optional[Tuple] = None):
        """
        Ejecuta consulta UPDATE/INSERT/DELETE.
        
        Args:
            query: Query SQL a ejecutar
            params: Parámetros para el query
            
        Returns:
            Número de filas afectadas
        """
        try:
            with self.get_connection() as connection:
                cursor = connection.cursor()
                
                logger.debug(f"Ejecutando update: {query}")
                cursor.execute(query, params or ())
                connection.commit()
                
                affected_rows = cursor.rowcount
                logger.debug(f"Update exitoso. Filas afectadas: {affected_rows}")
                return affected_rows
                
        except Error as e:
            logger.error(f"Error en update: {e}")
            raise
        finally:
            if 'cursor' in locals():
                cursor.close()
    
    def execute_batch(self, query: str, params_list: List[Tuple]):
        """
        Ejecuta múltiples queries en lote.
        
        Args:
            query: Query SQL a ejecutar
            params_list: Lista de parámetros para cada ejecución
            
        Returns:
            Total de filas afectadas
        """
        if not params_list:
            return 0
            
        try:
            with self.get_connection() as connection:
                cursor = connection.cursor()
                
                logger.debug(f"Ejecutando batch: {len(params_list)} items")
                cursor.executemany(query, params_list)
                connection.commit()
                
                total_affected = cursor.rowcount
                logger.debug(f"Batch exitoso: {total_affected} filas")
                return total_affected
                
        except Error as e:
            logger.error(f"Error en batch: {e}")
            raise
        finally:
            if 'cursor' in locals():
                cursor.close()
    
    def test_connection(self) -> bool:
        """
        Prueba la conexión a la base de datos.
        
        Returns:
            bool: True si la conexión es exitosa
        """
        try:
            with self.get_connection() as connection:
                cursor = connection.cursor()
                cursor.execute("SELECT 1")
                result = cursor.fetchone()
                cursor.close()
                
                logger.info("Prueba de conexión exitosa")
                return result is not None
                
        except Exception as e:
            logger.error(f"Prueba de conexión falló: {e}")
            return False


# Instancia global para reutilizar
_db_instance = None

def get_db_connection(config_file: str = "config/config.ini"):
    """
    Obtiene instancia singleton de DatabaseConnection.
    
    Args:
        config_file: Archivo de configuración
        
    Returns:
        Instancia de DatabaseConnection
    """
    global _db_instance
    
    if _db_instance is None:
        _db_instance = DatabaseConnection(config_file)
        
    return _db_instance
'''

        (database_dir / "connection.py").write_text(connection_content)
        logger.debug("Archivo connection.py creado")

    def _create_select_queries_file(
        self, queries_dir: Path, project_name: str
    ) -> None:
        """Crea el archivo select_queries.py con consultas SELECT."""
        select_content = f'''"""
Queries de consulta (SELECT) para {project_name}.

Organiza todas las consultas SELECT por funcionalidad
para facilitar mantenimiento y reutilización.
"""

from typing import Dict, Any, List, Optional
from ..connection import get_db_connection


class SelectQueries:
    """
    Queries para consultar datos de la base de datos.
    
    Organiza consultas SELECT por categorías de funcionalidad.
    """
    
    def __init__(self, config_file: str = "config/config.ini"):
        """
        Inicializa las queries de consulta.
        
        Args:
            config_file: Archivo de configuración de la BD
        """
        self.db = get_db_connection(config_file)
    
    # =================================================================
    # QUERIES GENERALES - Para cualquier tabla
    # =================================================================
    
    def get_all_records(self, table_name: str):
        """
        Obtiene todos los registros de una tabla.
        
        Args:
            table_name: Nombre de la tabla
            
        Returns:
            Lista de registros
        """
        query = f"SELECT * FROM {{table_name}}"
        return self.db.execute_query(query)
    
    def get_record_by_id(self, table_name: str, record_id):
        """
        Obtiene un registro por ID.
        
        Args:
            table_name: Nombre de la tabla
            record_id: ID del registro
            
        Returns:
            Registro encontrado o None
        """
        query = f"SELECT * FROM {{table_name}} WHERE id = %s"
        results = self.db.execute_query(query, (record_id,))
        return results[0] if results else None
    
    def count_records(self, table_name: str, where_condition: str = None):
        """
        Cuenta registros en una tabla.
        
        Args:
            table_name: Nombre de la tabla
            where_condition: Condición WHERE opcional
            
        Returns:
            Número de registros
        """
        query = f"SELECT COUNT(*) as total FROM {{table_name}}"
        if where_condition:
            query += f" WHERE {{where_condition}}"
        
        result = self.db.execute_query(query)
        return result[0]['total'] if result else 0
    
    # =================================================================
    # QUERIES PARA SINCRONIZACIÓN - Datos pendientes
    # =================================================================
    
    def get_pending_sync_records(self, table_name: str, limit: int = 100):
        """
        Obtiene registros pendientes de sincronización.
        
        Args:
            table_name: Nombre de la tabla
            limit: Límite de registros
            
        Returns:
            Lista de registros pendientes
        """
        query = f"""
        SELECT * FROM {{table_name}} 
        WHERE sync_status = 'pending' 
        ORDER BY created_at ASC 
        LIMIT %s
        """
        return self.db.execute_query(query, (limit,))
    
    def get_failed_sync_records(self, table_name: str, max_retries: int = 3):
        """
        Obtiene registros que fallaron en sincronización.
        
        Args:
            table_name: Nombre de la tabla
            max_retries: Máximo número de reintentos
            
        Returns:
            Lista de registros con errores
        """
        query = f"""
        SELECT * FROM {{table_name}} 
        WHERE sync_status = 'failed' 
        AND sync_retries < %s
        ORDER BY last_sync_attempt ASC
        """
        return self.db.execute_query(query, (max_retries,))
    
    def get_records_modified_after(self, table_name: str, timestamp: str):
        """
        Obtiene registros modificados después de una fecha.
        
        Args:
            table_name: Nombre de la tabla
            timestamp: Fecha/hora de referencia
            
        Returns:
            Lista de registros modificados
        """
        query = f"""
        SELECT * FROM {{table_name}} 
        WHERE updated_at > %s 
        ORDER BY updated_at ASC
        """
        return self.db.execute_query(query, (timestamp,))
    
    # =================================================================
    # QUERIES ESPECÍFICAS PARA {project_name.upper()} - Personalizar según negocio
    # =================================================================
    
    def get_active_records(self):
        """Obtiene registros activos."""
        query = "SELECT * FROM main_table WHERE active = 1"
        return self.db.execute_query(query)
    
    def get_records_by_date_range(self, start_date: str, end_date: str):
        """Obtiene registros por rango de fechas."""
        query = """
        SELECT * FROM main_table 
        WHERE DATE(created_at) BETWEEN %s AND %s
        ORDER BY created_at DESC
        """
        return self.db.execute_query(query, (start_date, end_date))
    
    # TODO: Agregar queries específicas para {project_name}
    # Ejemplos:
    # - get_productos_con_stock_bajo()
    # - get_facturas_del_mes()
    # - get_clientes_activos()
    # - get_ventas_por_periodo()
    
    # =================================================================
    # QUERIES DE CONFIGURACIÓN
    # =================================================================
    
    def get_config_value(self, config_key: str):
        """
        Obtiene un valor de configuración.
        
        Args:
            config_key: Clave de configuración
            
        Returns:
            Valor de configuración o None
        """
        query = "SELECT config_value FROM configuraciones WHERE config_key = %s"
        results = self.db.execute_query(query, (config_key,))
        return results[0]['config_value'] if results else None
    
    def get_all_configs(self):
        """Obtiene todas las configuraciones como diccionario."""
        query = "SELECT config_key, config_value FROM configuraciones"
        results = self.db.execute_query(query)
        return {{row['config_key']: row['config_value'] for row in results}}


# Instancia global para reutilizar
_select_queries = None

def get_select_queries(config_file: str = "config/config.ini"):
    """Obtiene instancia singleton de SelectQueries."""
    global _select_queries
    
    if _select_queries is None:
        _select_queries = SelectQueries(config_file)
        
    return _select_queries
'''

        (queries_dir / "select_queries.py").write_text(select_content)
        logger.debug("Archivo select_queries.py creado")

    def _create_update_queries_file(
        self, queries_dir: Path, project_name: str
    ) -> None:
        """Crea el archivo update_queries.py con consultas de actualización."""
        update_content = f'''"""
Queries de actualización (UPDATE/INSERT) para {project_name}.

Organiza todas las consultas para modificar y agregar datos
en la base de datos local.
"""

from typing import Dict, Any, List, Tuple
from datetime import datetime
from ..connection import get_db_connection


class UpdateQueries:
    """
    Queries para actualizar y insertar datos en la base de datos.
    
    Organiza consultas de modificación por funcionalidad.
    """
    
    def __init__(self, config_file: str = "config/config.ini"):
        """
        Inicializa las queries de actualización.
        
        Args:
            config_file: Archivo de configuración de la BD
        """
        self.db = get_db_connection(config_file)
    
    # =================================================================
    # QUERIES GENERALES - Para cualquier tabla
    # =================================================================
    
    def update_record_by_id(self, table_name: str, record_id, data: Dict[str, Any]):
        """
        Actualiza un registro por ID.
        
        Args:
            table_name: Nombre de la tabla
            record_id: ID del registro
            data: Datos a actualizar
            
        Returns:
            Número de filas afectadas
        """
        if not data:
            return 0
            
        set_clause = ", ".join([f"{{key}} = %s" for key in data.keys()])
        query = f"UPDATE {{table_name}} SET {{set_clause}} WHERE id = %s"
        params = tuple(data.values()) + (record_id,)
        
        return self.db.execute_update(query, params)
    
    def insert_record(self, table_name: str, data: Dict[str, Any]):
        """
        Inserta un nuevo registro.
        
        Args:
            table_name: Nombre de la tabla
            data: Datos a insertar
            
        Returns:
            Número de filas afectadas
        """
        if not data:
            return 0
            
        columns = ", ".join(data.keys())
        placeholders = ", ".join(["%s"] * len(data))
        query = f"INSERT INTO {{table_name}} ({{columns}}) VALUES ({{placeholders}})"
        
        return self.db.execute_update(query, tuple(data.values()))
    
    def upsert_record(self, table_name: str, data: Dict[str, Any], key_col: str = "id"):
        """
        Inserta o actualiza un registro (UPSERT).
        
        Args:
            table_name: Nombre de la tabla
            data: Datos a insertar/actualizar
            key_col: Columna clave para conflicto
            
        Returns:
            Número de filas afectadas
        """
        if not data:
            return 0
            
        columns = ", ".join(data.keys())
        placeholders = ", ".join(["%s"] * len(data))
        
        update_clause = ", ".join([
            f"{{key}} = VALUES({{key}})" for key in data.keys() 
            if key != key_col
        ])
        
        query = f"""
        INSERT INTO {{table_name}} ({{columns}}) 
        VALUES ({{placeholders}})
        ON DUPLICATE KEY UPDATE {{update_clause}}
        """
        
        return self.db.execute_update(query, tuple(data.values()))
    
    # =================================================================
    # QUERIES PARA SINCRONIZACIÓN - Control de estados
    # =================================================================
    
    def mark_as_synced(self, table_name: str, record_id):
        """
        Marca un registro como sincronizado.
        
        Args:
            table_name: Nombre de la tabla
            record_id: ID del registro
            
        Returns:
            Número de filas afectadas
        """
        query = f"""
        UPDATE {{table_name}} 
        SET sync_status = 'synced', 
            last_sync_at = NOW(),
            sync_retries = 0,
            sync_error = NULL
        WHERE id = %s
        """
        return self.db.execute_update(query, (record_id,))
    
    def mark_sync_failed(self, table_name: str, record_id, error_message: str):
        """
        Marca un registro como fallido en sincronización.
        
        Args:
            table_name: Nombre de la tabla
            record_id: ID del registro
            error_message: Mensaje de error
            
        Returns:
            Número de filas afectadas
        """
        query = f"""
        UPDATE {{table_name}} 
        SET sync_status = 'failed',
            sync_retries = sync_retries + 1,
            sync_error = %s,
            last_sync_attempt = NOW()
        WHERE id = %s
        """
        return self.db.execute_update(query, (error_message, record_id))
    
    def mark_for_sync(self, table_name: str, record_id):
        """
        Marca un registro como pendiente de sincronización.
        
        Args:
            table_name: Nombre de la tabla
            record_id: ID del registro
            
        Returns:
            Número de filas afectadas
        """
        query = f"""
        UPDATE {{table_name}} 
        SET sync_status = 'pending',
            updated_at = NOW()
        WHERE id = %s
        """
        return self.db.execute_update(query, (record_id,))
    
    # =================================================================
    # QUERIES ESPECÍFICAS PARA {project_name.upper()} - Tu lógica de negocio
    # =================================================================
    
    def update_status(self, record_id, new_status: str):
        """Actualiza el estado de un registro."""
        query = "UPDATE main_table SET status = %s WHERE id = %s"
        return self.db.execute_update(query, (new_status, record_id))
    
    # TODO: Agregar queries específicas para {project_name}
    # Ejemplos:
    # - actualizar_stock_producto()
    # - crear_nueva_factura()
    # - actualizar_saldo_cliente()
    # - completar_pedido()
    
    # =================================================================
    # QUERIES EN LOTE - Para operaciones masivas
    # =================================================================
    
    def update_multiple_records(self, table_name: str, updates: List[Tuple]):
        """
        Actualiza múltiples registros en lote.
        
        Args:
            table_name: Nombre de la tabla
            updates: Lista de tuplas (nuevo_valor, id)
            
        Returns:
            Total de filas afectadas
        """
        if not updates:
            return 0
            
        query = f"UPDATE {{table_name}} SET status = %s WHERE id = %s"
        return self.db.execute_batch(query, updates)
    
    def insert_multiple_records(self, table_name: str, records: List[Dict[str, Any]]):
        """
        Inserta múltiples registros en lote.
        
        Args:
            table_name: Nombre de la tabla
            records: Lista de diccionarios con datos
            
        Returns:
            Total de filas afectadas
        """
        if not records:
            return 0
            
        columns = list(records[0].keys())
        columns_str = ", ".join(columns)
        placeholders = ", ".join(["%s"] * len(columns))
        
        query = f"INSERT INTO {{table_name}} ({{columns_str}}) VALUES ({{placeholders}})"
        values_list = [tuple(rec[col] for col in columns) for rec in records]
        
        return self.db.execute_batch(query, values_list)
    
    # =================================================================
    # QUERIES DE CONFIGURACIÓN
    # =================================================================
    
    def set_config_value(self, config_key: str, config_value: str):
        """
        Establece un valor de configuración.
        
        Args:
            config_key: Clave de configuración
            config_value: Valor de configuración
            
        Returns:
            Número de filas afectadas
        """
        query = """
        INSERT INTO configuraciones (config_key, config_value, updated_at)
        VALUES (%s, %s, NOW())
        ON DUPLICATE KEY UPDATE 
        config_value = VALUES(config_value),
        updated_at = NOW()
        """
        return self.db.execute_update(query, (config_key, config_value))


# Instancia global para reutilizar
_update_queries = None

def get_update_queries(config_file: str = "config/config.ini"):
    """Obtiene instancia singleton de UpdateQueries."""
    global _update_queries
    
    if _update_queries is None:
        _update_queries = UpdateQueries(config_file)
        
    return _update_queries
'''

        (queries_dir / "update_queries.py").write_text(update_content)
        logger.debug("Archivo update_queries.py creado")

    def _create_repository_file(
        self, database_dir: Path, project_name: str
    ) -> None:
        """Crea el archivo repository.py con patrón Repository."""
        repository_content = f'''"""
Repository pattern para {project_name}.

Combina SelectQueries y UpdateQueries en una interfaz unificada
para facilitar el acceso a datos de forma organizada.
"""

from typing import Dict, Any, List, Optional
from .queries.select_queries import get_select_queries
from .queries.update_queries import get_update_queries


class {project_name.title()}Repository:
    """
    Repository unificado para acceso a datos de {project_name}.
    
    Combina queries de consulta y actualización en una sola interfaz
    organizada por entidades de negocio.
    """
    
    def __init__(self, config_file: str = "config/config.ini"):
        """
        Inicializa el repository.
        
        Args:
            config_file: Archivo de configuración de la BD
        """
        self.select = get_select_queries(config_file)
        self.update = get_update_queries(config_file)
    
    # =================================================================
    # MÉTODOS GENERALES - Para cualquier entidad
    # =================================================================
    
    def get_by_id(self, table_name: str, record_id):
        """Obtiene un registro por ID de cualquier tabla."""
        return self.select.get_record_by_id(table_name, record_id)
    
    def update_by_id(self, table_name: str, record_id, data: Dict[str, Any]):
        """Actualiza un registro por ID en cualquier tabla."""
        return self.update.update_record_by_id(table_name, record_id, data)
    
    def create_record(self, table_name: str, data: Dict[str, Any]):
        """Crea un nuevo registro en cualquier tabla."""
        return self.update.insert_record(table_name, data)
    
    def count_records(self, table_name: str, where_condition: str = None):
        """Cuenta registros en una tabla."""
        return self.select.count_records(table_name, where_condition)
    
    # =================================================================
    # MÉTODOS DE SINCRONIZACIÓN - Para control de sync
    # =================================================================
    
    def get_pending_sync(self, table_name: str, limit: int = 100):
        """Obtiene registros pendientes de sincronización."""
        return self.select.get_pending_sync_records(table_name, limit)
    
    def mark_synced(self, table_name: str, record_id):
        """Marca un registro como sincronizado."""
        return self.update.mark_as_synced(table_name, record_id)
    
    def mark_sync_failed(self, table_name: str, record_id, error: str):
        """Marca un registro como fallido en sincronización."""
        return self.update.mark_sync_failed(table_name, record_id, error)
    
    def get_failed_sync_records(self, table_name: str, max_retries: int = 3):
        """Obtiene registros que fallaron en sincronización."""
        return self.select.get_failed_sync_records(table_name, max_retries)
    
    # =================================================================
    # MÉTODOS ESPECÍFICOS PARA {project_name.upper()} - Personalizar según negocio
    # =================================================================
    
    def get_active_records(self):
        """Obtiene registros activos."""
        return self.select.get_active_records()
    
    def update_record_status(self, record_id, new_status: str):
        """Actualiza el estado de un registro."""
        return self.update.update_status(record_id, new_status)
    
    def get_records_by_date_range(self, start_date: str, end_date: str):
        """Obtiene registros por rango de fechas."""
        return self.select.get_records_by_date_range(start_date, end_date)
    
    # TODO: Agregar métodos específicos para {project_name}
    # Ejemplos para diferentes tipos de negocio:
    # 
    # PARA E-COMMERCE:
    # - get_productos_stock_bajo()
    # - actualizar_inventario()
    # - get_pedidos_pendientes()
    # - procesar_pago()
    #
    # PARA FACTURACIÓN:
    # - get_facturas_del_mes()
    # - crear_factura()
    # - anular_documento()
    # - get_clientes_morosos()
    #
    # PARA CRM:
    # - get_clientes_activos()
    # - actualizar_contacto()
    # - get_oportunidades_abiertas()
    # - crear_actividad()
    
    # =================================================================
    # MÉTODOS DE CONFIGURACIÓN
    # =================================================================
    
    def get_config(self, key: str):
        """Obtiene un valor de configuración."""
        return self.select.get_config_value(key)
    
    def set_config(self, key: str, value: str):
        """Establece un valor de configuración."""
        return self.update.set_config_value(key, value)
    
    def get_all_configs(self):
        """Obtiene todas las configuraciones."""
        return self.select.get_all_configs()


# Instancia global para reutilizar
_repository = None

def get_repository(config_file: str = "config/config.ini"):
    """
    Obtiene una instancia singleton del Repository.
    
    Args:
        config_file: Archivo de configuración
        
    Returns:
        Instancia de {project_name.title()}Repository
    """
    global _repository
    
    if _repository is None:
        _repository = {project_name.title()}Repository(config_file)
        
    return _repository
'''

        (database_dir / "repository.py").write_text(repository_content)
        logger.debug("Archivo repository.py creado")

    def _create_custom_queries_file(
        self, queries_dir: Path, project_name: str
    ) -> None:
        """Crea archivo custom_queries.py para queries específicos del proyecto."""
        custom_content = f'''"""
Queries personalizadas para {project_name}.

Contiene consultas específicas del dominio de negocio
que no encajan en las categorías generales.
"""

from ..connection import get_db_connection


class {project_name.title()}CustomQueries:
    """
    Queries específicas para el dominio de {project_name}.
    
    Implementa consultas complejas y específicas del negocio
    que requieren lógica particular.
    """
    
    def __init__(self, config_file: str = "config/config.ini"):
        """
        Inicializa las queries personalizadas.
        
        Args:
            config_file: Archivo de configuración de la BD
        """
        self.db = get_db_connection(config_file)
    
    # =================================================================
    # QUERIES ESPECÍFICAS PARA {project_name.upper()}
    # =================================================================
    
    def get_dashboard_summary(self):
        """
        Obtiene resumen para dashboard principal.
        
        Returns:
            Dict con métricas del dashboard
        """
        # TODO: Implementar query específico para dashboard
        query = """
        SELECT 
            COUNT(*) as total_records,
            COUNT(CASE WHEN status = 'active' THEN 1 END) as active_records,
            COUNT(CASE WHEN status = 'pending' THEN 1 END) as pending_records,
            MAX(updated_at) as last_update
        FROM main_table
        """
        
        result = self.db.execute_query(query)
        return result[0] if result else {{}}
    
    def get_monthly_statistics(self, year: int, month: int):
        """
        Obtiene estadísticas mensuales.
        
        Args:
            year: Año
            month: Mes
            
        Returns:
            Lista con estadísticas del mes
        """
        # TODO: Implementar query específico para estadísticas
        query = """
        SELECT 
            DATE(created_at) as date,
            COUNT(*) as daily_count,
            AVG(amount) as average_amount
        FROM main_table
        WHERE YEAR(created_at) = %s 
        AND MONTH(created_at) = %s
        GROUP BY DATE(created_at)
        ORDER BY date
        """
        
        return self.db.execute_query(query, (year, month))
    
    def get_complex_report_data(self, start_date: str, end_date: str):
        """
        Obtiene datos para reporte complejo.
        
        Args:
            start_date: Fecha de inicio
            end_date: Fecha de fin
            
        Returns:
            Lista con datos del reporte
        """
        # TODO: Implementar query complejo según necesidades
        query = """
        SELECT 
            main_table.id,
            main_table.name,
            main_table.status,
            related_table.description,
            COUNT(details.id) as detail_count,
            SUM(details.amount) as total_amount
        FROM main_table
        LEFT JOIN related_table ON main_table.related_id = related_table.id
        LEFT JOIN details ON main_table.id = details.main_id
        WHERE DATE(main_table.created_at) BETWEEN %s AND %s
        GROUP BY main_table.id, main_table.name, main_table.status, related_table.description
        ORDER BY total_amount DESC
        """
        
        return self.db.execute_query(query, (start_date, end_date))
    
    # =================================================================
    # QUERIES DE VALIDACIÓN Y CONTROL
    # =================================================================
    
    def validate_data_integrity(self):
        """
        Valida la integridad de los datos.
        
        Returns:
            Lista con problemas encontrados
        """
        # TODO: Implementar validaciones específicas
        queries = [
            ("duplicate_records", "SELECT id, name, COUNT(*) as count FROM main_table GROUP BY name HAVING count > 1"),
            ("orphaned_records", "SELECT id FROM details WHERE main_id NOT IN (SELECT id FROM main_table)"),
            ("invalid_statuses", "SELECT id FROM main_table WHERE status NOT IN ('active', 'inactive', 'pending')")
        ]
        
        issues = []
        for issue_type, query in queries:
            results = self.db.execute_query(query)
            if results:
                issues.append({{"type": issue_type, "count": len(results), "records": results}})
        
        return issues
    
    def cleanup_old_records(self, days_old: int = 90):
        """
        Limpia registros antiguos (solo SELECT para revisar).
        
        Args:
            days_old: Días de antigüedad
            
        Returns:
            Lista de registros que serían eliminados
        """
        query = """
        SELECT id, name, created_at
        FROM main_table 
        WHERE created_at < DATE_SUB(NOW(), INTERVAL %s DAY)
        AND status = 'inactive'
        """
        
        return self.db.execute_query(query, (days_old,))
    
    # =================================================================
    # PLANTILLAS PARA DIFERENTES TIPOS DE NEGOCIO
    # =================================================================
    
    # EJEMPLO PARA E-COMMERCE
    def get_low_stock_products(self, threshold: int = 10):
        """Obtiene productos con stock bajo."""
        query = """
        SELECT p.id, p.name, p.stock_current, p.stock_minimum
        FROM products p
        WHERE p.stock_current <= %s
        AND p.active = 1
        ORDER BY p.stock_current ASC
        """
        return self.db.execute_query(query, (threshold,))
    
    # EJEMPLO PARA FACTURACIÓN
    def get_invoice_summary_by_month(self, year: int, month: int):
        """Obtiene resumen de facturas por mes."""
        query = """
        SELECT 
            COUNT(*) as total_invoices,
            SUM(total_amount) as total_sales,
            AVG(total_amount) as average_invoice,
            COUNT(CASE WHEN status = 'paid' THEN 1 END) as paid_invoices,
            COUNT(CASE WHEN status = 'pending' THEN 1 END) as pending_invoices
        FROM invoices
        WHERE YEAR(invoice_date) = %s AND MONTH(invoice_date) = %s
        """
        result = self.db.execute_query(query, (year, month))
        return result[0] if result else {{}}
    
    # EJEMPLO PARA CRM
    def get_customer_activity_summary(self, customer_id: int, days: int = 30):
        """Obtiene resumen de actividad de cliente."""
        query = """
        SELECT 
            COUNT(DISTINCT o.id) as total_orders,
            SUM(o.total_amount) as total_spent,
            COUNT(DISTINCT c.id) as contacts_made,
            MAX(o.order_date) as last_order_date,
            MAX(c.contact_date) as last_contact_date
        FROM customers cust
        LEFT JOIN orders o ON cust.id = o.customer_id 
        LEFT JOIN contacts c ON cust.id = c.customer_id
        WHERE cust.id = %s
        AND (o.order_date >= DATE_SUB(NOW(), INTERVAL %s DAY) OR o.order_date IS NULL)
        AND (c.contact_date >= DATE_SUB(NOW(), INTERVAL %s DAY) OR c.contact_date IS NULL)
        """
        result = self.db.execute_query(query, (customer_id, days, days))
        return result[0] if result else {{}}


# Instancia global para reutilizar
_custom_queries = None

def get_custom_queries(config_file: str = "config/config.ini"):
    """
    Obtiene instancia singleton de CustomQueries.
    
    Args:
        config_file: Archivo de configuración
        
    Returns:
        Instancia de {project_name.title()}CustomQueries
    """
    global _custom_queries
    
    if _custom_queries is None:
        _custom_queries = {project_name.title()}CustomQueries(config_file)
        
    return _custom_queries
'''

        (queries_dir / "custom_queries.py").write_text(custom_content)
        logger.debug("Archivo custom_queries.py creado")
