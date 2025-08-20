# Uso de platformdirs en Tabula Cloud Sync

Este documento explica cómo el proyecto ahora utiliza la librería `platformdirs` para un manejo más robusto y multiplataforma de directorios.

## ¿Qué es platformdirs?

`platformdirs` es una librería que proporciona rutas estándar y apropiadas para cada sistema operativo para almacenar datos de aplicaciones, configuraciones, cache, logs, etc.

## Beneficios implementados

### 1. Rutas multiplataforma estándar

En lugar de usar rutas fijas como `logs/` o `config/`, ahora se usan rutas apropiadas para cada OS:

**Linux:**

- Config: `~/.config/TabulaCloudSync/`
- Data: `~/.local/share/TabulaCloudSync/`
- Cache: `~/.cache/TabulaCloudSync/`
- Logs: `~/.local/state/TabulaCloudSync/`

**Windows:**

- Config: `%APPDATA%\Tabula\TabulaCloudSync\`
- Data: `%LOCALAPPDATA%\Tabula\TabulaCloudSync\`
- Cache: `%LOCALAPPDATA%\Tabula\TabulaCloudSync\Cache\`
- Logs: `%LOCALAPPDATA%\Tabula\TabulaCloudSync\Logs\`

**macOS:**

- Config: `~/Library/Application Support/TabulaCloudSync/`
- Data: `~/Library/Application Support/TabulaCloudSync/`
- Cache: `~/Library/Caches/TabulaCloudSync/`
- Logs: `~/Library/Logs/TabulaCloudSync/`

### 2. Manejo inteligente de configuración

La nueva implementación busca archivos de configuración en el siguiente orden:

1. Archivo especificado explícitamente (e.g., `--config mi_config.ini`)
2. `config.ini` en el directorio actual
3. Archivo en el directorio de configuración del usuario
4. Archivo en el directorio de configuración del sistema

### 3. Fallback automático

Si no se puede escribir en una ubicación (permisos), automáticamente usa ubicaciones alternativas apropiadas.

## Nuevas utilidades disponibles

### Módulo `directories`

```python
from tabula_cloud_sync.utils.directories import tabula_dirs

# Obtener directorios estándar
config_dir = tabula_dirs.user_config_dir
data_dir = tabula_dirs.user_data_dir
log_dir = tabula_dirs.user_log_dir
cache_dir = tabula_dirs.user_cache_dir

# Obtener rutas de archivos específicos
config_file = tabula_dirs.get_config_file_path("mi_config.ini")
log_file = tabula_dirs.get_log_file_path("mi_app.log")
data_file = tabula_dirs.get_data_file_path("database.db")

# Directorios específicos de proyecto
project_data = tabula_dirs.get_project_specific_dir("mi_proyecto", "data")
```

### Comandos CLI nuevos

```bash
# Ver información de directorios
tabula-cli directories

# Ver en formato JSON
tabula-cli directories --format json

# Solo mostrar rutas
tabula-cli directories --format paths

# Ver rutas de configuración
tabula-cli paths
```

## Componentes actualizados

### 1. Logger (`utils/logger.py`)

- Ahora usa `get_appropriate_log_dir()` para determinar dónde guardar logs
- Fallback automático si no se puede escribir en directorio local

### 2. ConfigBuilder (`config/builder.py`)

- Usa rutas de platformdirs para SQLite databases
- Logs configurados en ubicaciones apropiadas del sistema

### 3. CLI (`cli/main.py`)

- Nuevos comandos para inspeccionar directorios
- Usa `get_appropriate_config_path()` para encontrar configuración

### 4. Core (`core/urls.py`)

- Busca configuración en múltiples ubicaciones usando platformdirs

### 5. PostInstall (`build_tools/post_install.py`)

- Usa el nuevo sistema de directorios para crear estructura de proyecto

## Migración automática

### Para usuarios existentes

El sistema mantiene compatibilidad con configuraciones existentes:

- Si existe `config.ini` en el directorio actual, se usará
- Si existen directorios `logs/`, `data/`, etc. locales, se priorizarán
- Los nuevos directorios solo se usan cuando no existen locales

### Para nuevas instalaciones

Las nuevas instalaciones usarán automáticamente las ubicaciones estándar del sistema operativo.

## Configuración específica por proyecto

```python
from tabula_cloud_sync.utils.directories import tabula_dirs

# Crear directorios específicos para un proyecto
project_name = "mi_proyecto_especial"

project_config = tabula_dirs.get_project_specific_dir(project_name, "config")
project_data = tabula_dirs.get_project_specific_dir(project_name, "data")
project_logs = tabula_dirs.get_project_specific_dir(project_name, "logs")
project_cache = tabula_dirs.get_project_specific_dir(project_name, "cache")
```

## Limpieza y mantenimiento

```python
from tabula_cloud_sync.utils.directories import tabula_dirs

# Limpiar cache
tabula_dirs.clean_cache()

# Asegurar que todos los directorios existen
tabula_dirs.ensure_all_directories()

# Obtener información completa
info = tabula_dirs.get_directory_info()
print(info)
```

## Mejores prácticas

### 1. Usar funciones de utilidad

```python
# ✅ Recomendado
from tabula_cloud_sync.utils.directories import get_default_config_path
config_path = get_default_config_path()

# ❌ Evitar
config_path = "./config.ini"
```

### 2. Verificar rutas antes de usar

```python
from tabula_cloud_sync.utils.directories import get_appropriate_config_path

config_path = get_appropriate_config_path()
if config_path.exists():
    # Procesar configuración
    pass
else:
    # Crear configuración por defecto
    pass
```

### 3. Usar ensure_directory mejorada

```python
from tabula_cloud_sync.utils.directories import ensure_directory

# Tiene fallback automático si hay problemas de permisos
safe_dir = ensure_directory("/path/that/might/fail")
```

## Ejemplos de uso

### Configurar logging personalizado

```python
from tabula_cloud_sync.utils.directories import tabula_dirs
import logging

# Obtener ruta apropiada para logs
log_file = tabula_dirs.get_log_file_path("mi_aplicacion.log")

logging.basicConfig(
    filename=str(log_file),
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
```

### Crear base de datos SQLite

```python
from tabula_cloud_sync.utils.directories import tabula_dirs
import sqlite3

# Base de datos en ubicación apropiada
db_path = tabula_dirs.get_data_file_path("mi_app.db")

conn = sqlite3.connect(str(db_path))
# ... usar conexión
```

### Cache personalizado

```python
from tabula_cloud_sync.utils.directories import tabula_dirs
import pickle

# Guardar en cache
cache_file = tabula_dirs.get_cache_file_path("datos.pkl")
with open(cache_file, 'wb') as f:
    pickle.dump(mis_datos, f)

# Leer desde cache
if cache_file.exists():
    with open(cache_file, 'rb') as f:
        datos = pickle.load(f)
```

## Comandos útiles

```bash
# Ver dónde están los directorios actuales
tabula-cli directories

# Ver información en JSON para scripts
tabula-cli directories --format json

# Solo las rutas (útil para scripts)
tabula-cli directories --format paths

# Ver orden de búsqueda de configuración
tabula-cli paths

# Inicializar proyecto con nueva estructura
tabula-cli init mi_proyecto
```

## Compatibilidad

- ✅ **Python 3.7+**: Totalmente compatible
- ✅ **Windows**: Usa rutas estándar de Windows
- ✅ **Linux**: Sigue XDG Base Directory Specification
- ✅ **macOS**: Usa convenciones de macOS
- ✅ **Retrocompatibilidad**: Mantiene compatibilidad con configuraciones existentes

## Resolución de problemas

### "No se pueden crear directorios"

El sistema incluye fallbacks automáticos. Si hay problemas de permisos, automáticamente usará ubicaciones alternativas como el directorio temporal del usuario.

### "No encuentra mi configuración"

Usa `tabula-cli paths` para ver dónde busca la configuración y verifica que tu archivo esté en una de esas ubicaciones.

### "Quiero usar directorios locales"

Simplemente mantén tus archivos `config.ini`, carpetas `logs/`, `data/`, etc. en el directorio actual. El sistema los priorizará automáticamente.
