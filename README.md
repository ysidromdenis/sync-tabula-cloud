# Tabula Cloud Sync - Biblioteca Base

Esta es una biblioteca base para proyectos que necesitan sincronizar con Tabula Cloud. Proporciona componentes comunes que pueden ser reutilizados en múltiples proyectos.

## Características

- 🔧 **Core**: Funcionalidades básicas de sesión, URLs y constantes
- 📊 **Models**: Modelos de datos para documentos
- 🛠️ **Utils**: Utilidades comunes y logging
- 🎨 **Icons**: Iconos del proyecto

## Instalación

### Como dependencia (Recomendado)

```bash
pip install git+https://github.com/tu-usuario/template-sync-tabula-cloud.git
```

### Para desarrollo

```bash
git clone https://github.com/tu-usuario/template-sync-tabula-cloud.git
cd template-sync-tabula-cloud
pip install -e .
```

## Uso

### Importar módulos en tu proyecto

```python
from tabula_cloud_sync.core import session, urls, consts
from tabula_cloud_sync.models import documentos
from tabula_cloud_sync.utils import commons, logger
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
intervalo = 1
url = tu_dominio.tabula.com.py
```

## Estructura del proyecto

```
tabula-cloud-sync/
├── core/           # Funcionalidades básicas
├── models/         # Modelos de datos
├── utils/          # Utilidades comunes
├── icons/          # Recursos gráficos
└── config.ini.template  # Plantilla de configuración
```

## Proyectos dependientes

Este proyecto está diseñado para ser usado como base en otros proyectos. Para mantener sincronización automática:

### Método 1: Git Submodules (Recomendado para desarrollo)

En tu proyecto dependiente:

```bash
# Añadir como submódulo
git submodule add https://github.com/tu-usuario/template-sync-tabula-cloud.git tabula_base

# Actualizar el submódulo
git submodule update --remote

# En tu código Python
import sys
sys.path.append('./tabula_base')
from core import session
```

### Método 2: Instalación directa desde Git

```bash
# Instalar la última versión
pip install --upgrade git+https://github.com/tu-usuario/template-sync-tabula-cloud.git

# O especificar una rama específica
pip install git+https://github.com/tu-usuario/template-sync-tabula-cloud.git@main
```

### Método 3: Requirements.txt con versión específica

En tu `requirements.txt`:

```txt
git+https://github.com/tu-usuario/template-sync-tabula-cloud.git@v1.0.0
```

## Automatización de actualizaciones

### GitHub Actions para proyectos dependientes

Crea `.github/workflows/update-base.yml` en tus proyectos dependientes:

```yaml
name: Update Base Library

on:
  schedule:
    - cron: "0 9 * * *" # Diario a las 9 AM
  workflow_dispatch: # Manual

jobs:
  update:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: "3.9"

      - name: Update tabula-cloud-sync
        run: |
          pip install --upgrade git+https://github.com/tu-usuario/template-sync-tabula-cloud.git

      - name: Run tests
        run: |
          python -m pytest tests/

      - name: Create Pull Request
        if: success()
        uses: peter-evans/create-pull-request@v5
        with:
          title: "Auto-update: tabula-cloud-sync library"
          body: "Actualización automática de la biblioteca base tabula-cloud-sync"
```

## Desarrollo

### Configurar entorno de desarrollo

```bash
# Clonar el repositorio
git clone https://github.com/tu-usuario/template-sync-tabula-cloud.git
cd template-sync-tabula-cloud

# Instalar en modo desarrollo
pip install -e .

# Instalar dependencias de desarrollo
pip install pytest black flake8
```

### Hacer cambios

1. Realiza tus cambios en `core/`, `models/`, `utils/` o `icons/`
2. Incrementa la versión en `setup.py`
3. Crea un commit y tag:

```bash
git add .
git commit -m "feat: nueva funcionalidad"
git tag v1.1.0
git push origin main --tags
```

### Los proyectos dependientes se actualizarán automáticamente

## Versionado

Este proyecto usa [Semantic Versioning](https://semver.org/):

- **MAJOR**: Cambios incompatibles en la API
- **MINOR**: Nueva funcionalidad compatible
- **PATCH**: Correcciones de errores

## Contribuir

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit tus cambios (`git commit -am 'Add nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Crea un Pull Request

## Licencia

Este proyecto está bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para más detalles.
