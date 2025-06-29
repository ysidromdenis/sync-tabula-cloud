#!/bin/bash

# Script de instalación mejorado para Tabula Cloud Sync Librería
# Versión 2.0 - Ahora como librería reutilizable

set -e

echo "🚀 Instalando Tabula Cloud Sync Librería..."

# Detectar Python
if command -v python3 &> /dev/null; then
    PYTHON=python3
elif command -v python &> /dev/null; then
    PYTHON=python
else
    echo "❌ Error: Python no encontrado. Instala Python 3.7+ primero."
    exit 1
fi

# Verificar versión de Python
PYTHON_VERSION=$($PYTHON -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
echo "📍 Python detectado: $PYTHON_VERSION"

if [[ $(echo "$PYTHON_VERSION < 3.7" | bc -l) -eq 1 ]]; then
    echo "❌ Error: Se requiere Python 3.7 o superior. Versión actual: $PYTHON_VERSION"
    exit 1
fi

# Verificar pip
if ! command -v pip &> /dev/null && ! command -v pip3 &> /dev/null; then
    echo "❌ Error: pip no encontrado. Instala pip primero."
    exit 1
fi

PIP=$(command -v pip3 || command -v pip)

# Opciones de instalación
INSTALL_MODE="basic"
INSTALL_DEV=false
INSTALL_DATABASE=false
PROJECT_DIR=""

# Procesar argumentos
while [[ $# -gt 0 ]]; do
    case $1 in
        --dev)
            INSTALL_DEV=true
            shift
            ;;
        --database)
            INSTALL_DATABASE=true
            shift
            ;;
        --project-dir)
            PROJECT_DIR="$2"
            shift 2
            ;;
        --help)
            echo "Uso: $0 [opciones]"
            echo ""
            echo "Opciones:"
            echo "  --dev          Instalar dependencias de desarrollo"
            echo "  --database     Instalar soporte para bases de datos"
            echo "  --project-dir  Directorio donde inicializar el proyecto"
            echo "  --help         Mostrar esta ayuda"
            exit 0
            ;;
        *)
            echo "❌ Opción desconocida: $1"
            echo "Usa --help para ver opciones disponibles"
            exit 1
            ;;
    esac
done

# Determinar comando de instalación
INSTALL_CMD="$PIP install tabula-cloud-sync"

if [[ "$INSTALL_DEV" == true ]]; then
    INSTALL_CMD="$INSTALL_CMD[dev]"
    echo "📦 Modo: Desarrollo (incluye dependencias de dev)"
elif [[ "$INSTALL_DATABASE" == true ]]; then
    INSTALL_CMD="$INSTALL_CMD[database]"
    echo "📦 Modo: Con soporte para bases de datos"
else
    echo "📦 Modo: Instalación básica"
fi

# Instalar librería
echo "⬇️  Instalando librería..."
if [[ -f "setup.py" ]]; then
    # Instalación local (desarrollo)
    echo "📁 Detectado setup.py local - Instalando en modo desarrollo..."
    $PIP install -e .
    
    if [[ "$INSTALL_DEV" == true ]]; then
        $PIP install -e .[dev]
    fi
    
    if [[ "$INSTALL_DATABASE" == true ]]; then
        $PIP install -e .[database]
    fi
else
    # Instalación desde PyPI
    eval "$INSTALL_CMD"
fi

echo "✅ Librería instalada exitosamente"

# Verificar instalación
echo "🔍 Verificando instalación..."
if $PYTHON -c "import tabula_cloud_sync; print(f'Tabula Cloud Sync v{tabula_cloud_sync.__version__} instalado correctamente')" 2>/dev/null; then
    echo "✅ Verificación exitosa"
else
    echo "❌ Error en la verificación de instalación"
    exit 1
fi

# Inicializar proyecto si se especificó directorio
if [[ -n "$PROJECT_DIR" ]]; then
    echo "🏗️  Inicializando proyecto en: $PROJECT_DIR"
    
    if [[ ! -d "$PROJECT_DIR" ]]; then
        mkdir -p "$PROJECT_DIR"
    fi
    
    cd "$PROJECT_DIR"
    
    # Usar CLI para inicializar
    if command -v tabula-cli &> /dev/null; then
        echo "📋 Ejecutando configuración inicial..."
        tabula-cli init --project-name "$(basename "$PROJECT_DIR")"
        echo "✅ Proyecto inicializado en $PROJECT_DIR"
    else
        echo "⚠️  CLI no disponible, creando estructura básica..."
        
        # Crear estructura básica manualmente
        mkdir -p config logs data cache services models
        
        # Crear archivo de configuración básico
        cat > config/tabula_config.ini << 'EOF'
[API]
base_url = https://api.tabula.com.py
version = v1
api_key = YOUR_API_KEY_HERE
timeout = 30

[SYNC]
interval = 300
batch_size = 100
retry_attempts = 3
auto_start = true

[LOGGING]
level = INFO
file = logs/tabula_service.log
max_size = 10MB
backup_count = 5
EOF
        
        echo "📁 Estructura básica creada"
        echo "⚙️  Edita config/tabula_config.ini con tus credenciales"
    fi
fi

# Información final
echo ""
echo "🎉 Instalación completada exitosamente!"
echo ""
echo "📝 Próximos pasos:"
echo "   1. Importa la librería: from tabula_cloud_sync import TabulaCloudService"
echo "   2. Crea tu servicio personalizado heredando de TabulaCloudService"
echo "   3. Implementa el método perform_sync() con tu lógica"
echo ""
echo "🛠️  Comandos disponibles:"
echo "   tabula-cli init          - Inicializar nuevo proyecto"
echo "   tabula-cli status        - Ver estado del proyecto actual"
echo "   tabula-service start     - Iniciar servicio como daemon"
echo ""
echo "📖 Documentación: https://github.com/ysidromdenis/template-sync-tabula-cloud"
echo "💬 Soporte: contacto@tabula.com.py"

# Detectar shell para sugerir actualización de PATH
if [[ -n "$SHELL" ]]; then
    echo ""
    echo "💡 Tip: Si los comandos CLI no funcionan, ejecuta:"
    echo "   source ~/.bashrc  # o ~/.zshrc según tu shell"
fi
