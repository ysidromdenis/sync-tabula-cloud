# Compilación a Ejecutable Standalone

Esta guía explica cómo compilar Tabula Cloud Sync Service en un ejecutable independiente que no requiere Python instalado.

## 🎯 Beneficios del Ejecutable

- ✅ **No requiere Python**: Funciona en sistemas sin Python instalado
- ✅ **Distribución simple**: Un solo archivo ejecutable
- ✅ **Instalación rápida**: Sin dependencias externas
- ✅ **Multiplataforma**: Windows, Linux, macOS
- ✅ **Portabilidad**: Copiar y ejecutar

## 🛠️ Métodos de Compilación

### Método 1: Script Automático (Recomendado)

```bash
# Instalar dependencias y compilar
python build_executable.py

# Solo compilar (si ya tienes dependencias)
python build_executable.py --no-installer

# Verificar ejecutable existente
python build_executable.py --verify-only
```

### Método 2: Makefile

```bash
# Compilación completa con paquete
make compile

# Compilación rápida sin instaladores
make compile-fast

# Información del sistema
make info

# Limpiar y recompilar
make clean compile
```

### Método 3: Manual con PyInstaller

```bash
# Instalar PyInstaller
pip install pyinstaller>=5.0.0

# Compilar (básico)
pyinstaller --onefile __main__.py --name tabula-cloud-sync

# Compilar (avanzado)
pyinstaller --onefile --console --clean \
    --add-data "config.ini.template:." \
    --add-data "docs:docs" \
    --add-data "examples:examples" \
    --hidden-import configparser \
    --hidden-import requests \
    __main__.py \
    --name tabula-cloud-sync
```

## 📋 Requisitos

### Dependencias de Compilación

```bash
# Básicas
pip install pyinstaller>=5.0.0

# Windows (adicionales)
pip install pywin32

# Desarrollo (opcional)
pip install auto-py-to-exe  # GUI para PyInstaller
```

### Requisitos del Sistema

- **RAM**: Mínimo 2GB durante compilación
- **Espacio**: ~500MB para archivos temporales
- **Python**: 3.7+ para compilar (no necesario para ejecutar)

## 🏗️ Proceso de Compilación Detallado

### 1. Preparación

```bash
# Clonar repositorio
git clone https://github.com/ysidromdenis/template-sync-tabula-cloud.git
cd template-sync-tabula-cloud

# Instalar dependencias
pip install -r requirements.txt
pip install pyinstaller>=5.0.0
```

### 2. Compilación

```bash
# Método automático (recomendado)
python build_executable.py

# El script:
# - Instala dependencias automáticamente
# - Crea archivo .spec optimizado
# - Compila el ejecutable
# - Verifica que funcione
# - Crea paquete de distribución
```

### 3. Verificación

```bash
# Verificar que el ejecutable funciona
./dist/tabula-cloud-sync --help
./dist/tabula-cloud-sync --foreground
```

## 📦 Archivos Generados

```
build/                          # Archivos temporales de compilación
dist/
├── tabula-cloud-sync           # Ejecutable principal (Linux/macOS)
└── tabula-cloud-sync.exe       # Ejecutable principal (Windows)

release/                        # Paquete de distribución
├── tabula-cloud-sync           # Ejecutable
├── config.ini.template         # Configuración template
├── README-STANDALONE.md        # Instrucciones
├── install-standalone.sh       # Instalador (Linux)
├── install-standalone.bat      # Instalador (Windows)
└── docs/                       # Documentación

tabula-cloud-sync-linux-standalone.zip     # Paquete final
```

## 🎛️ Configuración Avanzada

### Archivo .spec Personalizado

```python
# tabula-service.spec
# -*- mode: python ; coding: utf-8 -*-

a = Analysis(
    ['__main__.py'],
    pathex=['.'],
    binaries=[],
    datas=[
        ('config.ini.template', '.'),
        ('docs', 'docs'),
        ('examples', 'examples'),
    ],
    hiddenimports=[
        'configparser',
        'requests',
        'logging.handlers',
        'win32serviceutil',  # Solo Windows
        'win32service',      # Solo Windows
    ],
    excludes=[
        'tkinter',
        'matplotlib',
        'numpy',
        'scipy',
    ],
)

exe = EXE(
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='tabula-cloud-sync',
    debug=False,
    strip=False,
    upx=True,
    console=True,
)
```

### Optimizaciones

```bash
# Compilación optimizada para tamaño
pyinstaller --onefile --strip --upx-dir=/usr/bin/upx __main__.py

# Compilación sin consola (Windows)
pyinstaller --onefile --windowed __main__.py

# Compilación con icono
pyinstaller --onefile --icon=icons/tabula.ico __main__.py
```

## 🚀 Distribución

### 1. Paquete Simple

```bash
# Crear paquete ZIP
python build_executable.py
# Genera: tabula-cloud-sync-{platform}-standalone.zip
```

### 2. Instaladores Nativos

#### Windows (NSIS)

```bash
# Instalar NSIS (https://nsis.sourceforge.io/)
# Compilar instalador
makensis installer.nsi
# Genera: TabulaCloudSync-Setup.exe
```

#### Linux (DEB)

```bash
# Crear paquete DEB
python build_executable.py
dpkg-deb --build package/tabula-cloud-sync
# Genera: tabula-cloud-sync.deb
```

#### macOS (App Bundle)

```bash
# Crear bundle .app
python build_executable.py
# Genera: dist/TabulaCloudSync.app
```

## 🔧 Solución de Problemas

### Error: Módulo no encontrado

```bash
# Agregar imports ocultos
pyinstaller --hidden-import=nombre_modulo __main__.py
```

### Ejecutable muy grande

```bash
# Excluir módulos innecesarios
pyinstaller --exclude-module=tkinter --exclude-module=matplotlib __main__.py

# Usar UPX para compresión
pyinstaller --upx-dir=/usr/bin/upx __main__.py
```

### Error en Windows: pywin32

```bash
# Instalar pywin32
pip install pywin32

# Verificar instalación
python -c "import win32serviceutil; print('OK')"
```

### Error: Archivo no encontrado

```bash
# Verificar que todos los archivos estén incluidos
pyinstaller --add-data "config.ini.template:." __main__.py
```

## 📊 Comparación de Tamaños

| Plataforma | Código Fuente | Ejecutable | Comprimido |
| ---------- | ------------- | ---------- | ---------- |
| Linux      | ~500KB        | ~15MB      | ~6MB       |
| Windows    | ~500KB        | ~12MB      | ~5MB       |
| macOS      | ~500KB        | ~18MB      | ~7MB       |

## 🔄 CI/CD con GitHub Actions

El proyecto incluye workflows de GitHub Actions que compilan automáticamente para múltiples plataformas:

```yaml
# .github/workflows/build.yml
- name: Compilar ejecutable
  run: python build_executable.py --no-installer

- name: Subir artefactos
  uses: actions/upload-artifact@v3
  with:
    name: executables
    path: dist/
```

## 📖 Uso del Ejecutable

### Instalación

```bash
# Linux
sudo ./install-standalone.sh

# Windows (como administrador)
install-standalone.bat

# Manual
cp tabula-cloud-sync /usr/local/bin/  # Linux
# o copiar a C:\Program Files\  # Windows
```

### Ejecución

```bash
# Primer plano (pruebas)
./tabula-cloud-sync --foreground

# Como servicio
./tabula-cloud-sync install
./tabula-cloud-sync start

# Verificar estado
./tabula-cloud-sync status
```

## 🚀 Distribución a Usuarios Finales

1. **Descargar** el paquete ZIP desde releases
2. **Extraer** en directorio deseado
3. **Ejecutar** script de instalación
4. **Configurar** archivo config.ini
5. **Instalar** como servicio del sistema

¡El ejecutable standalone facilita enormemente la distribución a sistemas que no tienen Python instalado!
