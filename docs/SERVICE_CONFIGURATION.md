# Configuración del Servicio Tabula Cloud Sync

Esta guía explica cómo configurar y usar el servicio Tabula Cloud Sync en tu proyecto.

## Configuración Inicial

### 1. Archivo de Configuración

Copia el archivo `config.ini.template` a `config.ini` y configura los valores apropiados:

```ini
[mysql]
host = tu_servidor_mysql
user = tu_usuario
password = tu_password
database = tu_base_de_datos
port = 3306

[sincronizador]
# Token de autenticación para Tabula Cloud
token = tu_token_de_tabula_cloud
# Intervalo de sincronización en segundos
interval = 30
# URL de tu instancia de Tabula Cloud
url = tu_dominio.tabula.com.py

[servicio]
# Nivel de logging
log_level = INFO
# Archivo de log (opcional)
log_file = tabula_service.log
# Configuraciones adicionales
max_retries = 3
timeout = 30
```

### 2. Variables de Entorno (Opcional)

También puedes usar variables de entorno para configuraciones sensibles:

```bash
export TABULA_TOKEN="tu_token_aqui"
export TABULA_URL="tu_dominio.tabula.com.py"
export MYSQL_PASSWORD="tu_password_mysql"
```

## Instalación del Servicio

### Linux/Unix

```bash
# Instalar como servicio systemd
sudo python -m service.manager install --config /ruta/a/config.ini

# Iniciar el servicio
sudo systemctl start tabula-cloud-sync

# Habilitar inicio automático
sudo systemctl enable tabula-cloud-sync

# Ver estado
sudo systemctl status tabula-cloud-sync

# Ver logs
sudo journalctl -u tabula-cloud-sync -f
```

### Windows

```cmd
# Ejecutar como administrador
# Instalar el servicio
python -m service.manager install --config C:\ruta\a\config.ini

# Iniciar el servicio
net start TabulaCloudSync

# Detener el servicio
net stop TabulaCloudSync

# Ver estado en el Administrador de Servicios
services.msc
```

## Uso Programático

### Servicio Básico

```python
from service import TabulaCloudService

class MiServicio(TabulaCloudService):
    def perform_sync(self):
        # Tu lógica de sincronización aquí
        self.logger.info("Ejecutando sincronización personalizada")

        # Usar self.session para hacer llamadas a la API
        response = self.session.get("api/documents/v1/documentos/")

        if response.status_code == 200:
            docs = response.json()
            self.logger.info(f"Procesando {len(docs)} documentos")
            # Procesar documentos...

# Usar el servicio
service = MiServicio("config.ini")
service.start_service()

# El servicio se ejecutará en segundo plano
# Para detenerlo: service.stop_service()
```

### Daemon de Linux

```python
from service import TabulaCloudDaemon

class MiDaemon(TabulaCloudDaemon):
    def perform_sync(self):
        # Tu lógica aquí
        pass

# Crear e iniciar el daemon
daemon = MiDaemon(pidfile="/var/run/mi_app.pid")
daemon.start()  # Inicia como daemon
daemon.stop()   # Detiene el daemon
daemon.status() # Muestra el estado
```

### Servicio de Windows

```python
# En Windows, crear un archivo de servicio
from service import TabulaCloudWindowsService

if __name__ == '__main__':
    # Esto manejará la instalación/inicio/parada del servicio
    import sys
    import win32serviceutil

    if len(sys.argv) == 1:
        # Ejecutar el servicio
        servicemanager.Initialize()
        servicemanager.PrepareToHostSingle(TabulaCloudWindowsService)
        servicemanager.StartServiceCtrlDispatcher()
    else:
        # Manejar argumentos de línea de comandos
        win32serviceutil.HandleCommandLine(TabulaCloudWindowsService)
```

## Personalización Avanzada

### Extender la Funcionalidad

```python
from service import TabulaCloudService
import datetime

class MiServicioAvanzado(TabulaCloudService):
    def __init__(self, config_file="config.ini"):
        super().__init__(config_file)
        self.custom_data = {}

    def on_start(self):
        """Ejecutado al iniciar el servicio"""
        self.logger.info("Servicio personalizado iniciado")
        self._load_custom_config()

    def on_stop(self):
        """Ejecutado al detener el servicio"""
        self.logger.info("Limpiando recursos...")
        self._cleanup()

    def perform_sync(self):
        """Lógica de sincronización personalizada"""
        try:
            # Sincronizar documentos
            self._sync_documents()

            # Sincronizar contactos
            self._sync_contacts()

            # Procesar cola de tareas
            self._process_task_queue()

            # Actualizar estadísticas
            self._update_stats()

        except Exception as e:
            self.logger.error(f"Error en sincronización: {e}")
            self._handle_sync_error(e)

    def _sync_documents(self):
        """Sincronizar documentos específicos"""
        # Implementación específica
        pass

    def _handle_sync_error(self, error):
        """Manejar errores de sincronización"""
        # Implementar lógica de recuperación
        pass
```

### Configuración de Logging Personalizada

```python
import logging
from service import TabulaCloudService

class MiServicioConLogging(TabulaCloudService):
    def __init__(self, config_file="config.ini"):
        super().__init__(config_file)
        self._setup_custom_logging()

    def _setup_custom_logging(self):
        """Configurar logging personalizado"""
        # Crear formateador personalizado
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
        )

        # Agregar handler para archivos rotativos
        from logging.handlers import RotatingFileHandler

        file_handler = RotatingFileHandler(
            'mi_servicio.log',
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5
        )
        file_handler.setFormatter(formatter)

        self.logger.addHandler(file_handler)
        self.logger.setLevel(logging.INFO)
```

## Monitoreo y Mantenimiento

### Verificar Estado

```bash
# Linux
python -m service.manager status

# O usando systemctl
sudo systemctl status tabula-cloud-sync
```

### Ver Logs

```bash
# Linux - logs del sistema
sudo journalctl -u tabula-cloud-sync -f

# O logs de la aplicación
tail -f tabula_service.log
```

### Reiniciar Servicio

```bash
# Linux
sudo systemctl restart tabula-cloud-sync

# Windows
net stop TabulaCloudSync && net start TabulaCloudSync
```

### Health Check Programático

```python
from service import TabulaCloudService

service = TabulaCloudService("config.ini")
service.load_config()
service.initialize_session()

# Verificar estado
status = service.get_status()
print(f"Estado del servicio: {status}")

# Health check
is_healthy = service.health_check()
print(f"Servicio saludable: {is_healthy}")
```

## Solución de Problemas

### Problemas Comunes

1. **Error de permisos en Linux**: Ejecutar con `sudo` para operaciones de servicio
2. **Puerto ocupado**: Verificar que no haya otro proceso usando el mismo puerto
3. **Configuración incorrecta**: Validar el archivo `config.ini`
4. **Token expirado**: Renovar el token en la configuración

### Debugging

```python
# Habilitar logging de debug
import logging
logging.basicConfig(level=logging.DEBUG)

# Ejecutar servicio en modo debug
service = MiServicio("config.ini")
service.logger.setLevel(logging.DEBUG)
service.start_service()
```

### Logs Útiles

- **Linux**: `/var/log/syslog` o `journalctl -u tabula-cloud-sync`
- **Windows**: Visor de eventos de Windows
- **Aplicación**: `tabula_service.log` (configurable)
