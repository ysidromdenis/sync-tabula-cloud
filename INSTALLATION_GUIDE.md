# 📋 Guía de Instalación - Tabula Cloud Sync Librería

Esta guía te ayudará a instalar y configurar la librería **Tabula Cloud Sync** en tu proyecto.

## 🎯 ¿Qué es Tabula Cloud Sync?

Tabula Cloud Sync es una **librería de Python reutilizable** que facilita la creación de servicios de sincronización personalizados con la API de Tabula Cloud.

### ✨ Características principales:

- ✅ **Auto-configuración**: Se configura automáticamente al instalar
- ✅ **Templates de código**: Genera servicios base personalizados
- ✅ **CLI integrado**: Herramientas de línea de comandos
- ✅ **Multi-base de datos**: PostgreSQL, MySQL, SQLite, SQL Server
- ✅ **Logging avanzado**: Sistema de logs configurable
- ✅ **Daemon/Servicio**: Ejecuta como servicio del sistema

## 🚀 Instalación Rápida

### Método 1: Instalación Automática (Recomendado)

```bash
# Descargar e instalar
curl -sSL https://raw.githubusercontent.com/ysidromdenis/template-sync-tabula-cloud/main/install_library.sh | bash

# O usando wget
wget -qO- https://raw.githubusercontent.com/ysidromdenis/template-sync-tabula-cloud/main/install_library.sh | bash
```

### Método 2: Instalación Manual

1. **Instalar con pip:**

   ```bash
   pip install tabula-cloud-sync
   ```

2. **Inicializar proyecto:**
   ```bash
   tabula-cli init --project-name "MiEmpresa"
   ```

## 📋 Requisitos del Sistema

- **Python**: 3.7 o superior
- **Sistema Operativo**: Windows, Linux, macOS
- **Memoria**: 512 MB RAM mínimo
- **Espacio**: 100 MB libres

### Verificar Python:

```bash
python --version
# o
python3 --version
```

Si no tienes Python, descárgalo desde [python.org](https://python.org)

## 🔧 Configuración Inicial

### 1. Configurar credenciales

Edita el archivo `config/tabula_config.ini`:

```ini
[API]
base_url = https://api.tabula.com.py
api_key = TU_API_KEY_AQUI
client_id = TU_CLIENT_ID_AQUI

[SYNC]
interval = 300
batch_size = 100
```

### 2. Obtener credenciales de API

1. Inicia sesión en tu cuenta de Tabula Cloud
2. Ve a **Configuración** → **API Keys**
3. Genera una nueva API Key
4. Copia la API Key y Client ID al archivo de configuración

## 📝 Crear tu Primer Servicio

### 1. Generar servicio base:

```bash
tabula-cli generate service --name "MiServicio"
```

### 2. Personalizar el servicio:

Edita `services/miservicio.py`:

```python
from tabula_cloud_sync import TabulaCloudService

class MiServicio(TabulaCloudService):
    def perform_sync(self):
        """Tu lógica de sincronización aquí"""

        # Ejemplo: obtener productos locales
        productos = self._obtener_productos()

        # Enviar a Tabula Cloud
        for producto in productos:
            response = self.session.post('productos', json_data=producto)
            if response.status_code == 201:
                self.logger.info(f"Producto {producto['nombre']} sincronizado")

        return {
            'status': 'success',
            'productos_procesados': len(productos)
        }

    def _obtener_productos(self):
        # Tu lógica para obtener datos locales
        return [
            {'nombre': 'Producto 1', 'precio': 100.0},
            {'nombre': 'Producto 2', 'precio': 200.0}
        ]
```

### 3. Ejecutar el servicio:

```bash
# Modo de prueba (30 segundos)
tabula-service test

# Ejecutar en primer plano
tabula-service start --foreground

# Ejecutar como daemon (background)
tabula-service start
```

## 🗂️ Estructura del Proyecto

Después de la instalación, tendrás esta estructura:

```
tu_proyecto/
├── config/
│   ├── tabula_config.ini        # Configuración principal
│   ├── logging_config.yaml      # Configuración de logs
│   └── database_config.yaml     # Configuración de BD
├── services/
│   ├── miservicio.py           # Tu servicio personalizado
│   └── daemon.py               # Script de daemon
├── models/
│   └── mimodelo.py             # Modelos de datos
├── logs/
│   ├── tabula_service.log      # Log principal
│   └── sync_errors.log         # Log de errores
├── data/                        # Datos locales
├── cache/                       # Cache temporal
└── backups/                     # Respaldos
```

## 🛠️ Comandos Útiles

### CLI de Gestión:

```bash
# Ver estado del proyecto
tabula-cli status

# Validar configuración
tabula-cli validate

# Generar componentes
tabula-cli generate service --name "NuevoServicio"
tabula-cli generate model --name "Cliente"
```

### Gestión de Servicios:

```bash
# Iniciar servicio
tabula-service start

# Ver estado
tabula-service status

# Detener servicio
tabula-service stop

# Reiniciar servicio
tabula-service restart
```

## 🔍 Verificar Instalación

Ejecuta este comando para verificar que todo funciona:

```bash
python -c "
import tabula_cloud_sync
print(f'✅ Tabula Cloud Sync v{tabula_cloud_sync.__version__} instalado correctamente')
"
```

O usa el script de pruebas:

```bash
# Si clonaste el repositorio
python test_library.py
```

## 🗄️ Configuración de Base de Datos

### SQLite (Por defecto):

```ini
[DATABASE]
type = sqlite
path = data/tabula_sync.db
```

### PostgreSQL:

```ini
[DATABASE]
type = postgresql
host = localhost
port = 5432
database = mi_bd
username = postgres
password = mi_password
```

### MySQL:

```ini
[DATABASE]
type = mysql
host = localhost
port = 3306
database = mi_bd
username = root
password = mi_password
```

Para usar bases de datos específicas, instala con:

```bash
pip install tabula-cloud-sync[database]
```

## 🚨 Solución de Problemas

### Error: "Command not found: tabula-cli"

**Solución:**

```bash
# Reinstalar con dependencias
pip install --force-reinstall tabula-cloud-sync

# O agregar al PATH
export PATH=$PATH:~/.local/bin

# Permanente (Linux/Mac)
echo 'export PATH=$PATH:~/.local/bin' >> ~/.bashrc
source ~/.bashrc
```

### Error: "API key no configurada"

**Solución:**

1. Verifica que el archivo `config/tabula_config.ini` existe
2. Asegúrate de que `api_key` no sea `YOUR_API_KEY_HERE`
3. Obtén una API key válida desde Tabula Cloud

### Error: "No se puede conectar a la base de datos"

**Solución:**

```bash
# Verificar configuración
tabula-cli validate

# Ver logs de errores
tail -f logs/sync_errors.log

# Usar SQLite por defecto
tabula-cli configure --database-type sqlite
```

### Problemas de permisos (Linux):

**Solución:**

```bash
# Dar permisos a directorios
chmod -R 755 logs/ data/ cache/

# Ejecutar como usuario específico
sudo chown -R $USER:$USER .
```

## 📞 Soporte y Ayuda

### 🌐 Recursos Online:

- **Documentación**: [GitHub Wiki](https://github.com/ysidromdenis/template-sync-tabula-cloud/wiki)
- **Ejemplos**: [Carpeta examples/](https://github.com/ysidromdenis/template-sync-tabula-cloud/tree/main/examples)
- **Issues**: [GitHub Issues](https://github.com/ysidromdenis/template-sync-tabula-cloud/issues)

### 📧 Contacto Directo:

- **Email**: contacto@tabula.com.py
- **Soporte técnico**: soporte@tabula.com.py

### 💬 Ayuda Comunitaria:

- Crear un **Issue** en GitHub con tu problema
- Incluir logs relevantes y pasos para reproducir
- Especificar tu sistema operativo y versión de Python

## 🎯 Próximos Pasos

Una vez instalado, puedes:

1. **Explorar ejemplos**: `examples/ejemplo_servicio_mejorado.py`
2. **Leer documentación**: Archivos en `docs/`
3. **Personalizar configuración**: Editar archivos en `config/`
4. **Desarrollar tu lógica**: Implementar `perform_sync()` en tu servicio
5. **Desplegar en producción**: Configurar como servicio del sistema

## 🔄 Actualizaciones

Para actualizar a la última versión:

```bash
pip install --upgrade tabula-cloud-sync
```

Para ver el changelog:

```bash
# Ver archivo CHANGELOG.md o
pip show tabula-cloud-sync
```

---

**¡Listo! Ya tienes Tabula Cloud Sync instalado y configurado. 🎉**

**Siguiente paso**: [Crear tu primer servicio personalizado →](examples/ejemplo_servicio_mejorado.py)
