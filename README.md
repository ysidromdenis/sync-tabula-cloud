# Tabula Cloud Sync - Biblioteca Base y Servicio

Esta es una biblioteca base para proyectos que necesitan sincronizar con Tabula Cloud. Proporciona componentes comunes que pueden ser reutilizados en múltiples proyectos, y ahora incluye capacidades de servicio para Windows y Linux.

## Características

- 🔧 **Core**: Funcionalidades básicas de sesión, URLs y constantes
- 📊 **Models**: Modelos de datos para documentos
- 🛠️ **Utils**: Utilidades comunes y logging
- 🎨 **Icons**: Iconos del proyecto
- ⚙️ **Service**: Servicio multiplataforma (Windows/Linux) para sincronización automática
- 🔄 **Daemon**: Capacidad de ejecutar como daemon en Linux/Unix
- 🪟 **Windows Service**: Servicio nativo de Windows

## Instalación

### Como dependencia (Recomendado)

```bash
pip install git+https://github.com/tu-usuario/template-sync-tabula-cloud.git
```

### Para Windows (con soporte de servicio)

```bash
pip install git+https://github.com/tu-usuario/template-sync-tabula-cloud.git[windows]
```

### Para desarrollo

```bash
git clone https://github.com/tu-usuario/template-sync-tabula-cloud.git
cd template-sync-tabula-cloud
pip install -e .
```

## Uso como Servicio

### Instalación del Servicio

```bash
# Linux/Unix - Instalar como servicio systemd
sudo tabula-service install --config /ruta/a/config.ini

# Windows - Instalar como servicio de Windows (ejecutar como administrador)
tabula-service install --config C:\ruta\a\config.ini
```

### Gestión del Servicio

```bash
# Iniciar servicio
tabula-service start

# Detener servicio
tabula-service stop

# Reiniciar servicio
tabula-service restart

# Ver estado
tabula-service status

# Desinstalar servicio
tabula-service remove
```

### Uso Programático del Servicio

```python
from service import TabulaCloudService

class MiProyectoService(TabulaCloudService):
    def perform_sync(self):
        """Tu lógica de sincronización personalizada"""
        self.logger.info("Ejecutando sincronización...")

        # Usar self.session para API calls
        response = self.session.get("api/documents/v1/documentos/")

        if response.status_code == 200:
            documents = response.json()
            # Procesar documentos...

# Inicializar y usar
service = MiProyectoService("config.ini")
service.start_service()

# El servicio se ejecuta en segundo plano
# Para detener: service.stop_service()
```

## Uso como Biblioteca

### Importar módulos en tu proyecto

```python
from tabula_cloud_sync.core import session, urls, consts
from tabula_cloud_sync.models import documentos
from tabula_cloud_sync.utils import commons, logger
from tabula_cloud_sync.service import TabulaCloudService
```

### Configuración

1. Copia el archivo `config.ini.template` a tu proyecto como `config.ini`
2. Configura tus credenciales:

```ini
[mysql]
host = tu_host
user = tu_usuario
password = tu_password
database = tu_database
port = 3306

[sincronizador]
token = tu_token
interval = 30  # segundos
url = tu_dominio.tabula.com.py

[servicio]
log_level = INFO
log_file = tabula_service.log
max_retries = 3
timeout = 30
```

## Documentación Adicional

- [Configuración del Servicio](docs/SERVICE_CONFIGURATION.md) - Guía completa de configuración y uso del servicio
- [Configuración General](docs/CONFIGURATION.md) - Configuración básica de la biblioteca
- [Ejemplos](examples/) - Ejemplos de implementación

## Estructura del proyecto

```
tabula-cloud-sync/
├── core/           # Funcionalidades básicas
├── models/         # Modelos de datos
├── utils/          # Utilidades comunes
├── service/        # Servicio multiplataforma
│   ├── base_service.py      # Clase base del servicio
│   ├── daemon.py           # Daemon para Linux/Unix
│   ├── windows_service.py  # Servicio para Windows
│   └── manager.py          # Administrador del servicio
├── examples/       # Ejemplos de uso
├── docs/          # Documentación
├── icons/         # Recursos gráficos
└── config.ini.template  # Plantilla de configuración
```

## 📦 Compilación a Ejecutable Standalone

### Compilación Rápida

```bash
# Método 1: Script automático (recomendado)
python build_executable.py

# Método 2: Makefile
make compile

# Método 3: Con testing previo
python test_compilation.py  # Verificar que todo esté listo
python build_executable.py  # Compilar
```

### Distribución de Ejecutables

Los ejecutables compilados **no requieren Python** instalado:

```bash
# Windows
tabula-cloud-sync.exe install    # Instalar como servicio
tabula-cloud-sync.exe --foreground  # Ejecutar en primer plano

# Linux
./tabula-cloud-sync install      # Instalar como servicio
./tabula-cloud-sync --foreground # Ejecutar en primer plano
```

### Opciones de Distribución

- **📁 Archivo ZIP**: Descarga y ejecuta directamente
- **🔧 Instalador Windows**: Archivo .exe con instalación automática
- **📦 Paquete DEB**: Para distribuciones basadas en Debian
- **🐳 Docker**: Contenedor con todo incluido
- **☁️ Releases GitHub**: Compilación automática multiplataforma

Ver [docs/COMPILATION.md](docs/COMPILATION.md) para guía detallada.

## 🐳 Uso con Docker

### Docker Compose (Recomendado)

```bash
# Crear directorios de configuración
mkdir -p config logs data

# Copiar template de configuración
cp config.ini.template config/config.ini

# Editar configuración
nano config/config.ini

# Iniciar servicio
docker-compose up -d

# Ver logs
docker-compose logs -f tabula-sync

# Detener
docker-compose down
```

### Docker Manual

```bash
# Construir imagen
docker build -t tabula-cloud-sync .

# Ejecutar contenedor
docker run -d \
  --name tabula-sync \
  -v $(pwd)/config:/etc/tabula \
  -v $(pwd)/logs:/var/log/tabula \
  tabula-cloud-sync
```

Ver [docker-compose.yml](docker-compose.yml) para configuración completa con MySQL, Redis y monitoreo.
