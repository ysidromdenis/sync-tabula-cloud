# Makefile para Tabula Cloud Sync Service

# Variables
PYTHON = python3
PIP = pip3
PROJECT_NAME = tabula-cloud-sync
VERSION = 2.0.0

# Detectar sistema operativo
UNAME_S := $(shell uname -s)
ifeq ($(UNAME_S),Linux)
    OS = linux
    EXE_EXT = 
endif
ifeq ($(UNAME_S),Darwin)
    OS = macos
    EXE_EXT = 
endif
ifeq ($(OS),Windows_NT)
    OS = windows
    EXE_EXT = .exe
    PYTHON = python
    PIP = pip
endif

# Directorios
BUILD_DIR = build
DIST_DIR = dist
RELEASE_DIR = release

# Targets principales
.PHONY: all clean install install-dev test compile package help

# Target por defecto
all: compile

help:
	@echo "Makefile para Tabula Cloud Sync Service"
	@echo ""
	@echo "Targets disponibles:"
	@echo "  help          - Mostrar esta ayuda"
	@echo "  install       - Instalar dependencias básicas"
	@echo "  install-dev   - Instalar dependencias de desarrollo"
	@echo "  install-build - Instalar dependencias de compilación"
	@echo "  test          - Ejecutar tests"
	@echo "  clean         - Limpiar archivos de compilación"
	@echo "  compile       - Compilar ejecutable"
	@echo "  package       - Crear paquete de distribución"
	@echo "  verify        - Verificar ejecutable compilado"
	@echo "  all           - Compilar ejecutable (target por defecto)"
	@echo ""
	@echo "Sistema detectado: $(OS)"

# Instalación de dependencias
install:
	$(PIP) install -r requirements.txt

install-dev:
	$(PIP) install -r requirements.txt
	$(PIP) install -e .[dev]

install-build:
	$(PIP) install -r requirements.txt
	$(PIP) install -e .[build]
	@echo "Dependencias de compilación instaladas"

# Tests
test:
	$(PYTHON) -m pytest tests/ -v

# Limpieza
clean:
	@echo "Limpiando archivos de compilación..."
	rm -rf $(BUILD_DIR)
	rm -rf $(DIST_DIR)
	rm -rf $(RELEASE_DIR)
	rm -f *.spec
	rm -f *.zip
	rm -f *.tar.gz
	find . -name "*.pyc" -delete
	find . -name "__pycache__" -type d -exec rm -rf {} +
	@echo "Limpieza completada"

# Compilación
compile: install-build
	@echo "Compilando ejecutable para $(OS)..."
	$(PYTHON) build_executable.py
	@echo "Compilación completada"

# Compilación rápida (sin instaladores)
compile-fast: install-build
	@echo "Compilación rápida para $(OS)..."
	$(PYTHON) build_executable.py --no-installer

# Verificación
verify:
	@echo "Verificando ejecutable..."
	$(PYTHON) build_executable.py --verify-only

# Empaquetado
package: compile
	@echo "Creando paquete de distribución..."
	$(PYTHON) build_executable.py
	@echo "Paquete creado"

# Desarrollo - ejecutar en modo foreground
run-dev:
	$(PYTHON) __main__.py --foreground

# Instalación local del servicio (desarrollo)
install-service:
	$(PYTHON) -m service.manager install --config config.ini.template

# Targets específicos por plataforma
ifeq ($(OS),windows)
compile-windows: compile
	@echo "Ejecutable para Windows compilado"
	@echo "Ubicación: $(DIST_DIR)/$(PROJECT_NAME).exe"

package-windows: package
	@echo "Paquete Windows creado"

install-windows-service:
	$(DIST_DIR)/$(PROJECT_NAME).exe install
endif

ifeq ($(OS),linux)
compile-linux: compile
	@echo "Ejecutable para Linux compilado"
	@echo "Ubicación: $(DIST_DIR)/$(PROJECT_NAME)"

package-linux: package
	@echo "Paquete Linux creado"
	@echo "Para crear DEB: dpkg-deb --build package/tabula-cloud-sync"

install-linux-service:
	sudo $(DIST_DIR)/$(PROJECT_NAME) install
endif

ifeq ($(OS),macos)
compile-macos: compile
	@echo "Ejecutable para macOS compilado"
	@echo "Ubicación: $(DIST_DIR)/$(PROJECT_NAME)"

package-macos: package
	@echo "Bundle macOS creado"
endif

# Desarrollo y debug
debug-compile:
	@echo "Compilación en modo debug..."
	$(PYTHON) -c "
import PyInstaller.__main__
PyInstaller.__main__.run([
    '__main__.py',
    '--onefile',
    '--console',
    '--debug=all',
    '--name=$(PROJECT_NAME)',
    '--clean'
])
"

# Release completo
release: clean test compile package
	@echo "Release $(VERSION) completado para $(OS)"
	@echo "Archivos generados:"
	@ls -la *.zip 2>/dev/null || echo "No hay archivos ZIP"
	@ls -la $(DIST_DIR)/ 2>/dev/null || echo "No hay archivos en dist/"

# Información del sistema
info:
	@echo "Información del sistema:"
	@echo "  OS: $(OS)"
	@echo "  Python: $(shell $(PYTHON) --version)"
	@echo "  Pip: $(shell $(PIP) --version)"
	@echo "  PyInstaller: $(shell $(PYTHON) -c 'import PyInstaller; print(PyInstaller.__version__)' 2>/dev/null || echo 'No instalado')"
	@echo "  Directorio actual: $(shell pwd)"
	@echo "  Archivos principales:"
	@ls -la __main__.py setup.py requirements.txt 2>/dev/null || echo "Archivos no encontrados"

# Docker (opcional para compilación cruzada)
docker-build-linux:
	@echo "Compilando en Docker para Linux..."
	docker run --rm -v $(shell pwd):/app -w /app python:3.9-slim bash -c "
		apt-get update && apt-get install -y build-essential &&
		pip install -r requirements.txt &&
		pip install pyinstaller &&
		python build_executable.py --no-installer
	"

# Targets de utilidad
check-deps:
	@echo "Verificando dependencias..."
	$(PYTHON) -c "
import sys
required = ['requests', 'configparser']
try:
    import PyInstaller
    print('✅ PyInstaller disponible:', PyInstaller.__version__)
except ImportError:
    print('❌ PyInstaller no disponible')

for pkg in required:
    try:
        __import__(pkg)
        print(f'✅ {pkg} disponible')
    except ImportError:
        print(f'❌ {pkg} no disponible')
"

# Benchmark de tamaño
size-report:
	@if [ -f "$(DIST_DIR)/$(PROJECT_NAME)$(EXE_EXT)" ]; then \
		echo "Reporte de tamaño del ejecutable:"; \
		ls -lh "$(DIST_DIR)/$(PROJECT_NAME)$(EXE_EXT)"; \
		echo ""; \
		echo "Comparación:"; \
		echo "  Código fuente: $$(du -sh . --exclude=$(BUILD_DIR) --exclude=$(DIST_DIR) | cut -f1)"; \
		echo "  Ejecutable: $$(ls -lh $(DIST_DIR)/$(PROJECT_NAME)$(EXE_EXT) | awk '{print $$5}')"; \
	else \
		echo "Ejecutable no encontrado. Ejecute 'make compile' primero."; \
	fi

# Target para CI/CD
ci: clean install-build test compile verify
	@echo "Pipeline CI completado exitosamente"
