#!/bin/bash
# Script de entrada para el contenedor Docker

set -e

# Función de log
log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1"
}

# Configurar archivos de configuración por defecto
setup_config() {
    if [ ! -f "$CONFIG_FILE" ]; then
        log "Creando archivo de configuración por defecto..."
        cp /app/config.ini.template "$CONFIG_FILE"
        log "Configuración creada en $CONFIG_FILE"
        log "IMPORTANTE: Configure sus credenciales antes de usar el servicio"
    fi
}

# Validar configuración
validate_config() {
    if [ ! -f "$CONFIG_FILE" ]; then
        log "ERROR: Archivo de configuración no encontrado: $CONFIG_FILE"
        exit 1
    fi
    
    log "Validando configuración..."
    python -c "
import configparser
import sys
try:
    config = configparser.ConfigParser()
    config.read('$CONFIG_FILE')
    
    # Validar secciones básicas
    required_sections = ['sincronizador']
    for section in required_sections:
        if section not in config:
            print(f'ERROR: Sección requerida no encontrada: {section}')
            sys.exit(1)
    
    # Validar campos críticos
    if not config.get('sincronizador', 'token', fallback=''):
        print('ADVERTENCIA: Token no configurado')
    
    if not config.get('sincronizador', 'url', fallback=''):
        print('ADVERTENCIA: URL no configurada')
    
    print('Configuración validada correctamente')
    
except Exception as e:
    print(f'ERROR validando configuración: {e}')
    sys.exit(1)
"
}

# Mostrar información del contenedor
show_info() {
    log "=== Tabula Cloud Sync Service (Docker) ==="
    log "Versión: 2.0.0"
    log "Configuración: $CONFIG_FILE"
    log "Logs: /var/log/tabula/"
    log "Usuario: $(whoami)"
    log "Directorio de trabajo: $(pwd)"
    log "Python: $(python --version)"
    log "============================================="
}

# Función principal
main() {
    show_info
    setup_config
    validate_config
    
    # Cambiar al directorio de la aplicación
    cd /app
    
    # Ejecutar servicio según argumentos
    case "$1" in
        --foreground)
            log "Iniciando servicio en modo foreground..."
            exec python __main__.py --foreground --config "$CONFIG_FILE"
            ;;
        --daemon)
            log "Iniciando servicio en modo daemon..."
            exec python __main__.py start --config "$CONFIG_FILE"
            ;;
        --status)
            python __main__.py status --config "$CONFIG_FILE"
            ;;
        --help)
            python __main__.py --help
            ;;
        *)
            log "Iniciando servicio con argumentos personalizados: $*"
            exec python __main__.py "$@" --config "$CONFIG_FILE"
            ;;
    esac
}

# Manejar señales para terminación limpia
trap 'log "Recibida señal de terminación, cerrando..."; exit 0' SIGTERM SIGINT

# Ejecutar función principal
main "$@"
