#!/bin/bash
# -*- coding: utf-8 -*-
"""Script helper para crear releases de Tabula Cloud Sync."""

set -e

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Función para mostrar ayuda
show_help() {
    echo -e "${BLUE}Tabula Cloud Sync - Release Helper${NC}"
    echo ""
    echo "Uso: $0 [TIPO] [VERSION]"
    echo ""
    echo "TIPOS:"
    echo "  stable    - Release estable (v1.0.0)"
    echo "  beta      - Pre-release beta (v1.0.0-beta.1)"
    echo "  alpha     - Release alpha (v1.0.0-alpha.1)"
    echo "  rc        - Release candidate (v1.0.0-rc.1)"
    echo ""
    echo "Ejemplos:"
    echo "  $0 stable 1.0.0"
    echo "  $0 beta 1.1.0-beta.1"
    echo "  $0 alpha 2.0.0-alpha.1"
    echo ""
    echo "El script:"
    echo "  1. Verifica el estado del repositorio"
    echo "  2. Ejecuta tests y compilación"
    echo "  3. Crea y pushea el tag"
    echo "  4. GitHub Actions se encarga del resto"
}

# Función para logging
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Verificar argumentos
if [ $# -lt 2 ]; then
    show_help
    exit 1
fi

RELEASE_TYPE=$1
VERSION=$2

# Validar tipo de release
case $RELEASE_TYPE in
    stable|beta|alpha|rc)
        ;;
    *)
        log_error "Tipo de release inválido: $RELEASE_TYPE"
        show_help
        exit 1
        ;;
esac

# Agregar prefijo v si no lo tiene
if [[ ! $VERSION =~ ^v ]]; then
    VERSION="v$VERSION"
fi

log_info "Preparando release $RELEASE_TYPE: $VERSION"

# Verificar que estamos en el directorio correcto
if [ ! -f "build_executable.py" ]; then
    log_error "No se encontró build_executable.py. ¿Estás en el directorio correcto?"
    exit 1
fi

# Verificar estado del repositorio
log_info "Verificando estado del repositorio..."

if [ -n "$(git status --porcelain)" ]; then
    log_warning "Hay cambios sin commit en el repositorio"
    git status --short
    echo ""
    read -p "¿Continuar de todas formas? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        log_info "Operación cancelada"
        exit 1
    fi
fi

# Verificar que estamos en main o develop
CURRENT_BRANCH=$(git branch --show-current)
if [[ "$CURRENT_BRANCH" != "main" && "$CURRENT_BRANCH" != "develop" ]]; then
    log_warning "No estás en branch main o develop (actual: $CURRENT_BRANCH)"
    read -p "¿Continuar de todas formas? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        log_info "Operación cancelada"
        exit 1
    fi
fi

# Verificar que el tag no existe
if git tag -l | grep -q "^$VERSION$"; then
    log_error "El tag $VERSION ya existe"
    exit 1
fi

# Ejecutar tests
log_info "Ejecutando tests..."
if command -v python3 &> /dev/null; then
    PYTHON=python3
else
    PYTHON=python
fi

if [ -f "tests/test_service.py" ]; then
    if ! $PYTHON -m pytest tests/ -v; then
        log_error "Los tests fallaron"
        exit 1
    fi
    log_success "Tests pasaron correctamente"
else
    log_warning "No se encontraron tests"
fi

# Verificar compilación
log_info "Verificando compilación..."
if ! $PYTHON build_executable.py --no-installer; then
    log_error "La compilación falló"
    exit 1
fi

if ! $PYTHON build_executable.py --verify-only; then
    log_error "La verificación del ejecutable falló"
    exit 1
fi

log_success "Compilación verificada correctamente"

# Limpiar archivos de compilación
rm -rf build/ dist/ || true

# Mostrar información del release
echo ""
log_info "=== Información del Release ==="
echo "Tipo: $RELEASE_TYPE"
echo "Versión: $VERSION"
echo "Branch: $CURRENT_BRANCH"
echo "Commit: $(git rev-parse --short HEAD)"
echo "Fecha: $(date)"
echo ""

# Generar notas del release automáticamente
LAST_TAG=$(git describe --tags --abbrev=0 2>/dev/null || echo "")
if [ -n "$LAST_TAG" ]; then
    log_info "Cambios desde $LAST_TAG:"
    git log --oneline $LAST_TAG..HEAD | head -10
    echo ""
fi

# Confirmar creación del release
echo -e "${YELLOW}¿Crear release $VERSION?${NC}"
echo "Esto creará el tag y activará GitHub Actions para:"
echo "  ✅ Compilar ejecutables para Windows, Linux y macOS"
echo "  ✅ Ejecutar todos los tests"
echo "  ✅ Crear release en GitHub con archivos adjuntos"
echo "  ✅ Generar checksums automáticamente"
echo ""
read -p "Confirmar (y/N): " -n 1 -r
echo

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    log_info "Operación cancelada"
    exit 0
fi

# Crear y pushear tag
log_info "Creando tag $VERSION..."
git tag -a "$VERSION" -m "Release $VERSION

Tipo: $RELEASE_TYPE
Branch: $CURRENT_BRANCH
Commit: $(git rev-parse HEAD)
Fecha: $(date -u +%Y-%m-%d\ %H:%M:%S\ UTC)

Auto-generado por release-helper.sh"

log_info "Pusheando tag a origin..."
git push origin "$VERSION"

log_success "¡Tag $VERSION creado y pusheado!"
echo ""
log_info "GitHub Actions iniciará automáticamente la compilación y creación del release."
log_info "Puedes seguir el progreso en: https://github.com/$(git config --get remote.origin.url | sed 's/.*github.com[:/]//' | sed 's/.git$//')/actions"
echo ""
log_success "¡Release $VERSION en proceso!"
