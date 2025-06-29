# Tabula Cloud Sync

**Librería reutilizable para sincronización con Tabula Cloud API**

[![Python Version](https://img.shields.io/badge/python-3.7+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)](CHANGELOG.md)

> **🚀 Nueva versión librería**: Ahora `tabula-cloud-sync` es una librería reutilizable con auto-configuración, CLI integrado y templates personalizables.

## 🌟 Características

- **Auto-configuración**: Se configura automáticamente al instalar/importar
- **Templates personalizables**: Genera código base para servicios personalizados
- **Soporte multi-BD**: Compatible con PostgreSQL, MySQL, SQL Server, SQLite
- **CLI integrado**: Herramientas de línea de comandos para gestión de proyectos
- **Build tools automáticos**: Construcción y configuración automática
- **Logging avanzado**: Sistema de logging configurable y robusto
- **Compatibilidad multiplataforma**: Windows, Linux, macOS
- **Daemon support**: Ejecución como servicio/daemon del sistema

## 📦 Instalación

### Instalación básica

```bash
pip install tabula-cloud-sync
```

### Instalación con soporte para bases de datos

```bash
pip install tabula-cloud-sync[database]
```

### Instalación para desarrollo

```bash
pip install tabula-cloud-sync[dev]
```

## 🔧 Uso Rápido

### 1. Auto-configuración

```python
# Solo importar - se auto-configura automáticamente
from tabula_cloud_sync import TabulaCloudService
```

### 2. Crear servicio personalizado

```python
from tabula_cloud_sync import TabulaCloudService

class MiServicio(TabulaCloudService):
    def perform_sync(self):
        # Tu lógica de sincronización aquí
        return {'status': 'success', 'records': 100}

# Ejecutar
servicio = MiServicio()
servicio.start()
```

### 3. CLI - Inicializar proyecto

```bash
tabula-cli init --project-name "MiEmpresa"
```

---

## 📋 Documentación anterior

> La siguiente documentación corresponde a la versión anterior como template/servicio standalone.
> cp config.ini.template config.ini
> nano config.ini # Editar configuración

# 4. Instalar como servicio

sudo ./tabula-cloud-sync install --config config.ini # Linux/macOS

# o

tabula-cloud-sync.exe install --config config.ini # Windows (como Admin)

````

### Opción 2: Desde Código Fuente (Desarrolladores)

```bash
# Clonar repositorio
git clone https://github.com/ysidromdenis/template-sync-tabula-cloud.git
cd template-sync-tabula-cloud

# Instalar en modo desarrollo
pip install -e .

# Para Windows (soporte completo de servicios)
pip install -e .[windows]
````

### Opción 3: Como Dependencia

```bash
pip install git+https://github.com/ysidromdenis/template-sync-tabula-cloud.git
```

## ✨ Características Principales

- **Ejecutable Standalone**: No requiere Python instalado
- **Core Robusto**: Funcionalidades básicas de sesión, URLs y constantes
- **Modelos de Datos**: Estructuras para documentos de Tabula Cloud
- **Utilidades Avanzadas**: Logging, configuración y helpers
- **Servicio Multiplataforma**: Windows Service / systemd / launchd
- **Sincronización Automática**: Daemon configurable con intervalos
- **Autenticación Segura**: Tokens y credenciales encriptadas
- **CLI Completa**: Interfaz de línea de comandos para gestión
- **Logging Avanzado**: Rotación automática y niveles configurables
- **Recuperación de Errores**: Reintentos automáticos y alertas

## 🎯 Gestión del Servicio

### Comandos Básicos

```bash
# Instalar como servicio del sistema
sudo tabula-cloud-sync install --config /path/to/config.ini

# Gestionar servicio
sudo tabula-cloud-sync start      # Iniciar
sudo tabula-cloud-sync stop       # Detener
sudo tabula-cloud-sync restart    # Reiniciar
sudo tabula-cloud-sync status     # Ver estado
sudo tabula-cloud-sync remove     # Desinstalar

# Ejecutar en primer plano (debug)
tabula-cloud-sync --foreground --config config.ini
```

### Ubicaciones de Configuración

```bash
# Linux
/etc/tabula-cloud-sync/config.ini
# o archivo local: ./config.ini

# Windows
%PROGRAMDATA%\TabulaCloudSync\config.ini
# o archivo local: .\config.ini

# macOS
/usr/local/etc/tabula-cloud-sync/config.ini
# o archivo local: ./config.ini
```

### Logs

```bash
# Linux (systemd)
sudo journalctl -u tabula-cloud-sync -f

# Linux (archivos)
tail -f /var/log/tabula-cloud-sync/service.log

# Windows
# Ver en: %PROGRAMDATA%\TabulaCloudSync\logs\

# macOS
tail -f /usr/local/var/log/tabula-cloud-sync/service.log
```

## 🔧 Configuración

### Archivo de Configuración (config.ini)

```ini
[mysql]
host = tu_host
user = tu_usuario
password = tu_password
database = tu_database
port = 3306

[sincronizador]
token = tu_token_de_api
interval = 30  # segundos entre sincronizaciones
url = tu_dominio.tabula.com.py

[servicio]
log_level = INFO
log_file = tabula_service.log
max_retries = 3
timeout = 30
```

### Plantilla Base

El proyecto incluye `config.ini.template` con todos los parámetros disponibles. Simplemente cópialo y personalízalo:

```bash
cp config.ini.template config.ini
```

## 💻 Uso Programático

### Como Biblioteca en tu Proyecto

```python
from tabula_cloud_sync.core import session, urls, consts
from tabula_cloud_sync.models import documentos
from tabula_cloud_sync.utils import commons, logger
from tabula_cloud_sync.service import TabulaCloudService

# Implementar tu servicio personalizado
class MiProyectoService(TabulaCloudService):
    def perform_sync(self):
        """Tu lógica de sincronización personalizada"""
        self.logger.info("Ejecutando sincronización...")

        # Usar self.session para API calls
        response = self.session.get("api/documents/v1/documentos/")

        if response.status_code == 200:
            documents = response.json()
            # Procesar documentos...
            self.logger.info(f"Procesados {len(documents)} documentos")

# Inicializar y usar
service = MiProyectoService("config.ini")
service.start_service()
```

### Como Script Standalone

```python
#!/usr/bin/env python3
import time
from tabula_cloud_sync import TabulaCloudService

def main():
    # Crear instancia del servicio
    service = TabulaCloudService("config.ini")

    try:
        while True:
            # Ejecutar sincronización
            service.perform_sync()

            # Esperar intervalo configurado
            time.sleep(service.config.getint('sincronizador', 'interval'))

    except KeyboardInterrupt:
        print("Servicio detenido por el usuario")
        service.stop_service()

if __name__ == "__main__":
    main()
```

## 🏗️ Desarrollo

### Configuración del Entorno de Desarrollo

```bash
# Clonar el repositorio
git clone https://github.com/ysidromdenis/template-sync-tabula-cloud.git
cd template-sync-tabula-cloud

# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # Linux/macOS
# o
venv\Scripts\activate     # Windows

# Instalar en modo desarrollo
pip install -e .
pip install -e .[dev]  # Incluye dependencias de desarrollo

# Ejecutar tests
pytest tests/ -v

# Formatear código
black .
isort .

# Verificar linting
flake8 .
```

### Tests y Calidad de Código

```bash
# Ejecutar todos los tests
pytest tests/ -v --cov=.

# Tests específicos
pytest tests/test_service.py -v

# Verificar cobertura
pytest --cov=. --cov-report=html
```

## 📦 Compilación a Ejecutable

### Compilación Local

```bash
# Método 1: Script automático (recomendado)
python build_executable.py

# Método 2: Makefile
make compile

# Método 3: Con verificación previa
python test_compilation.py  # Verificar dependencias
python build_executable.py  # Compilar
```

### Distribución

Los ejecutables compilados **no requieren Python** instalado:

```bash
# Windows
tabula-cloud-sync.exe install --config config.ini
tabula-cloud-sync.exe --foreground

# Linux/macOS
./tabula-cloud-sync install --config config.ini
./tabula-cloud-sync --foreground
```

## 🚀 CI/CD y Releases

### Workflows Automatizados

Este proyecto usa **GitHub Actions** con separación de responsabilidades:

#### 1. **Tests Continuos** (`.github/workflows/test.yml`)

- **Trigger**: Push/PR a `main` y `develop`
- **Matriz**: Ubuntu, Windows, macOS × Python 3.9, 3.10, 3.11
- **Duración**: ~5-8 minutos
- **Propósito**: Validación rápida durante desarrollo

#### 2. **Build y Release** (`.github/workflows/build.yml`)

- **Trigger**: Solo tags `v*` (ej: `v1.0.0`)
- **Salida**: Ejecutables para las 3 plataformas + GitHub Release
- **Duración**: ~15-20 minutos
- **Propósito**: Release de producción con ejecutables

### Estrategia de Releases Automatizada

| Tipo           | Patrón       | Descripción       | Ejemplo          |
| -------------- | ------------ | ----------------- | ---------------- |
| 🟢 **Estable** | `v*`         | Producción        | `v1.0.0`         |
| 🟡 **Beta**    | `v*-beta.*`  | Pre-release       | `v1.1.0-beta.1`  |
| 🟠 **Alpha**   | `v*-alpha.*` | Experimental      | `v2.0.0-alpha.1` |
| 🔵 **RC**      | `v*-rc.*`    | Release candidate | `v1.0.0-rc.1`    |

### Crear una Release

#### Método 1: Script Helper (Recomendado)

```bash
# Release estable
./scripts/create-release.sh stable 1.0.0

# Pre-release
./scripts/create-release.sh beta 1.1.0-beta.1

# Release de desarrollo
./scripts/create-release.sh alpha 1.2.0-alpha.1
```

#### Método 2: Manual

```bash
# Crear y pushear tag
git tag v1.0.0
git push origin v1.0.0
```

#### Método 3: GitHub Web

1. Ve a tu repositorio → "Releases"
2. Click "Create a new release"
3. Escribir tag: `v1.0.0`
4. GitHub Actions compilará automáticamente

### Qué Incluye una Release

Cada release automáticamente genera:

- **Ejecutables compilados** para Windows, Linux, macOS
- **Packages completos** con documentación esencial (`INSTALL.md`)
- **Checksums SHA256** para verificación de integridad
- **Release notes** automáticas con cambios
- **Detección automática** de pre-releases (alpha/beta/rc)

### Verificación de Integridad

```bash
# Descargar checksums
wget https://github.com/ysidromdenis/template-sync-tabula-cloud/releases/download/v1.0.0/checksums.txt

# Verificar archivos descargados
sha256sum -c checksums.txt
```

## 🐳 Docker

### Docker Compose (Recomendado)

```bash
# Crear directorios
mkdir -p config logs data

# Copiar template de configuración
cp config.ini.template config/config.ini
nano config/config.ini  # Editar configuración

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

### Docker con GitHub Container Registry (Opcional)

Si necesitas publicar imágenes Docker, puedes habilitar el workflow opcional:

```bash
# Renombrar el workflow de Docker
mv .github/workflows/docker-optional.yml .github/workflows/docker.yml

# Personalizar configuración si es necesario
nano .github/workflows/docker.yml
```

## 📁 Estructura del Proyecto

```
tabula-cloud-sync/
├── __init__.py                 # Punto de entrada principal
├── __main__.py                # CLI y ejecución directa
├── build_executable.py        # Script de compilación
├── setup.py                   # Configuración de distribución
├── requirements.txt           # Dependencias base
├── pyproject.toml            # Configuración moderna de Python
├── config.ini.template       # Plantilla de configuración
├── INSTALL.md                 # Guía de instalación para usuarios finales
├── Makefile                  # Comandos de automatización
├── docker-compose.yml        # Configuración de Docker
│
├── core/                     # Funcionalidades básicas
│   ├── __init__.py
│   ├── consts.py            # Constantes globales
│   ├── session.py           # Gestión de sesiones HTTP
│   └── urls.py              # URLs y endpoints
│
├── models/                   # Modelos de datos
│   ├── __init__.py
│   └── documentos.py        # Modelos para documentos
│
├── utils/                    # Utilidades comunes
│   ├── __init__.py
│   ├── commons.py           # Funciones auxiliares
│   └── logger.py            # Sistema de logging
│
├── service/                  # Servicio multiplataforma
│   ├── __init__.py
│   ├── base_service.py      # Clase base del servicio
│   ├── daemon.py            # Daemon para Linux/Unix
│   ├── windows_service.py   # Servicio para Windows
│   └── manager.py           # Administrador del servicio
│
├── .github/workflows/        # CI/CD con GitHub Actions
│   ├── test.yml             # Tests continuos
│   ├── build.yml            # Build y release
│   └── docker-optional.yml  # Docker (opcional)
│
├── docs/                     # Documentación técnica
│   ├── GITHUB_RELEASES.md   # Guía de releases
│   ├── GITHUB_ACTIONS.md    # Documentación de CI/CD
│   ├── COMPILATION.md       # Guía de compilación
│   ├── CONFIGURATION.md     # Configuración detallada
│   └── SERVICE_CONFIGURATION.md  # Configuración del servicio
│
├── examples/                 # Ejemplos de uso
│   ├── example_service.py   # Servicio de ejemplo
│   └── mi_proyecto_ejemplo/  # Proyecto completo de ejemplo
│
├── scripts/                  # Scripts de utilidad
│   └── create-release.sh    # Script para crear releases
│
├── tests/                    # Tests unitarios
│   ├── __init__.py
│   └── test_service.py
│
├── docker/                   # Configuración de Docker
│   ├── Dockerfile
│   └── entrypoint.sh
│
└── icons/                    # Recursos gráficos
    └── tabula.ico
```

## 📚 Documentación Adicional

- **[📖 Guía de Instalación](INSTALL.md)** - Instalación simple para usuarios finales
- **[🏷️ GitHub Releases](docs/GITHUB_RELEASES.md)** - Versionado y distribución
- **[🏗️ GitHub Actions](docs/GITHUB_ACTIONS.md)** - Workflows y automatización
- **[⚙️ Configuración del Servicio](docs/SERVICE_CONFIGURATION.md)** - Guía completa del servicio
- **[🔧 Configuración General](docs/CONFIGURATION.md)** - Configuración básica
- **[📦 Compilación](docs/COMPILATION.md)** - Compilación a ejecutables
- **[📋 Ejemplos](examples/)** - Ejemplos prácticos de implementación

## 🤝 Contribuir

### Flujo de Desarrollo

1. Fork el proyecto
2. Crear una rama feature (`git checkout -b feature/nueva-caracteristica`)
3. Commit cambios (`git commit -am 'Agregar nueva característica'`)
4. Push a la rama (`git push origin feature/nueva-caracteristica`)
5. Crear Pull Request

### Guidelines

- Seguir [PEP 8](https://pep8.org/) para estilo de código
- Incluir tests para nuevas funcionalidades
- Documentar cambios en el CHANGELOG.md
- Usar commits descriptivos en español

### Desarrollo Local

```bash
# Configurar hooks de pre-commit
pip install pre-commit
pre-commit install

# Ejecutar verificaciones
pre-commit run --all-files
```

## 📄 Licencia

Este proyecto está bajo la licencia [MIT](LICENSE). Ver el archivo LICENSE para más detalles.

## 🆘 Soporte

- **Issues**: [GitHub Issues](https://github.com/ysidromdenis/template-sync-tabula-cloud/issues)
- **Releases**: [GitHub Releases](https://github.com/ysidromdenis/template-sync-tabula-cloud/releases)
- **Documentación**: [docs/](docs/)

---

**Desarrollado con ❤️ para la comunidad Tabula Cloud**
