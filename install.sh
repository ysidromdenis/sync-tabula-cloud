#!/bin/bash
# Script de instalación para Tabula Cloud Sync Service

set -e

echo "=== Instalador de Tabula Cloud Sync Service ==="
echo

# Detectar sistema operativo
OS=$(uname -s)
ARCH=$(uname -m)

echo "Sistema detectado: $OS $ARCH"

# Verificar Python
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 no está instalado"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1-2)
echo "Python version: $PYTHON_VERSION"

# Verificar pip
if ! command -v pip3 &> /dev/null; then
    echo "Error: pip3 no está instalado"
    exit 1
fi

# Función para compilar ejecutable
compile_executable() {
    echo "¿Desea compilar un ejecutable standalone? (y/n)"
    read -r response
    if [[ "$response" =~ ^[Yy]$ ]]; then
        echo "Instalando dependencias de compilación..."
        pip3 install pyinstaller>=5.0.0
        
        echo "Compilando ejecutable..."
        python3 build_executable.py
        
        if [ -f "dist/tabula-cloud-sync" ]; then
            echo "✅ Ejecutable compilado exitosamente: dist/tabula-cloud-sync"
            echo "Puede distribuir este archivo sin necesidad de Python"
            
            echo "¿Desea instalar el ejecutable en el sistema? (y/n)"
            read -r install_response
            if [[ "$install_response" =~ ^[Yy]$ ]]; then
                sudo cp dist/tabula-cloud-sync /usr/local/bin/
                sudo chmod +x /usr/local/bin/tabula-cloud-sync
                echo "Ejecutable instalado en /usr/local/bin/tabula-cloud-sync"
            fi
        else
            echo "❌ Error en la compilación del ejecutable"
        fi
    fi
}

# Función para instalar en Linux/Unix
install_linux() {
    echo "Instalando para Linux/Unix..."
    
    # Verificar si se quiere compilar
    echo "Opciones de instalación:"
    echo "1. Instalación normal (requiere Python)"
    echo "2. Compilar ejecutable standalone"
    echo "3. Ambas opciones"
    echo -n "Seleccione una opción (1-3): "
    read -r option
    
    case $option in
        1)
            install_normal_linux
            ;;
        2)
            compile_executable
            ;;
        3)
            install_normal_linux
            compile_executable
            ;;
        *)
            echo "Opción inválida, instalando normalmente..."
            install_normal_linux
            ;;
    esac
}

# Función de instalación normal (separada)
install_normal_linux() {
    # Instalar el paquete
    echo "Instalando paquete Python..."
    pip3 install -e .
    
    # Crear directorio de configuración si no existe
    CONFIG_DIR="/etc/tabula-cloud-sync"
    if [ ! -d "$CONFIG_DIR" ]; then
        echo "Creando directorio de configuración..."
        sudo mkdir -p "$CONFIG_DIR"
    fi
    
    # Copiar template de configuración
    if [ ! -f "$CONFIG_DIR/config.ini" ]; then
        echo "Copiando template de configuración..."
        sudo cp config.ini.template "$CONFIG_DIR/config.ini"
        echo "IMPORTANTE: Edite $CONFIG_DIR/config.ini con su configuración"
    fi
    
    # Crear directorio de logs
    LOG_DIR="/var/log/tabula-cloud-sync"
    if [ ! -d "$LOG_DIR" ]; then
        echo "Creando directorio de logs..."
        sudo mkdir -p "$LOG_DIR"
        sudo chmod 755 "$LOG_DIR"
    fi
    
    # Instalar servicio systemd
    echo "¿Desea instalar el servicio systemd? (y/n)"
    read -r response
    if [[ "$response" =~ ^[Yy]$ ]]; then
        sudo python3 -m service.manager install --config "$CONFIG_DIR/config.ini"
        echo "Servicio instalado. Para iniciarlo: sudo systemctl start tabula-cloud-sync"
    fi
}

# Función para instalar en macOS
install_macos() {
    echo "Instalando para macOS..."
    
    # Instalar el paquete
    echo "Instalando paquete Python..."
    pip3 install -e .
    
    # Crear directorio de configuración
    CONFIG_DIR="$HOME/.config/tabula-cloud-sync"
    if [ ! -d "$CONFIG_DIR" ]; then
        echo "Creando directorio de configuración..."
        mkdir -p "$CONFIG_DIR"
    fi
    
    # Copiar template de configuración
    if [ ! -f "$CONFIG_DIR/config.ini" ]; then
        echo "Copiando template de configuración..."
        cp config.ini.template "$CONFIG_DIR/config.ini"
        echo "IMPORTANTE: Edite $CONFIG_DIR/config.ini con su configuración"
    fi
    
    echo "Para ejecutar el servicio manualmente:"
    echo "python3 -m service.daemon start"
}

# Función principal
main() {
    case "$OS" in
        Linux*)
            install_linux
            ;;
        Darwin*)
            install_macos
            ;;
        *)
            echo "Sistema operativo no soportado: $OS"
            echo "Por favor, instale manualmente usando:"
            echo "pip3 install -e ."
            exit 1
            ;;
    esac
    
    echo
    echo "=== Instalación completada ==="
    echo
    echo "Próximos pasos:"
    echo "1. Configurar el archivo config.ini con sus credenciales"
    echo "2. Iniciar el servicio según su plataforma"
    echo
    echo "Para más información, consulte la documentación en docs/"
}

# Verificar si estamos en el directorio correcto
if [ ! -f "setup.py" ]; then
    echo "Error: Ejecute este script desde el directorio raíz del proyecto"
    exit 1
fi

# Ejecutar instalación
main
