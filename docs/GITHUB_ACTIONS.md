# GitHub Actions Workflows

Este proyecto utiliza GitHub Actions para automatización de CI/CD. Tenemos dos workflows principales:

## 🔄 Workflows Configurados

### 1. **Tests** (`.github/workflows/test.yml`)

- **Trigger**: Push/PR a `main` y `develop`
- **Propósito**: Validación continua durante desarrollo
- **Jobs**:
  - **test**: Ejecuta tests en matriz de SO y versiones Python
  - **lint**: Verificación de formato y estilo de código

#### Matriz de Testing:

- **Sistemas**: Ubuntu, Windows, macOS
- **Python**: 3.9, 3.10, 3.11
- **Total**: 9 combinaciones de testing

### 2. **Build and Release** (`.github/workflows/build.yml`)

- **Trigger**: Solo tags que empiecen con `v*`
- **Propósito**: Compilación y release de ejecutables
- **Jobs**:
  - **build**: Compila ejecutables para las 3 plataformas
  - **release**: Crea GitHub Release con archivos

## 📋 Separación de Responsabilidades

| Acción              | Workflow           | Duración   | Propósito         |
| ------------------- | ------------------ | ---------- | ----------------- |
| Push a `main`       | ✅ Tests           | ~5-8 min   | Validación rápida |
| Push a `develop`    | ✅ Tests           | ~5-8 min   | Validación rápida |
| Pull Request        | ✅ Tests           | ~5-8 min   | Validación de PR  |
| Tag `v1.0.0`        | ✅ Build & Release | ~15-20 min | Release completo  |
| Push otros branches | ❌ Ninguno         | -          | Sin validación    |

## 🚀 Crear una Release

### Método 1: Script Helper (Recomendado)

```bash
# Release estable
./scripts/create-release.sh stable 1.0.0

# Pre-release
./scripts/create-release.sh beta 1.1.0-beta.1
```

### Método 2: Manual

```bash
# Crear y pushear tag
git tag v1.0.0
git push origin v1.0.0
```

### Método 3: GitHub Web

1. Ve a tu repositorio → "Releases"
2. Click "Create a new release"
3. Escribir tag: `v1.0.0`
4. GitHub Actions compilará automáticamente

## 📦 Qué Incluye una Release

Cada release automáticamente genera:

- **Ejecutables compilados** para Windows, Linux, macOS
- **Packages completos** con documentación
- **Checksums SHA256** para verificación
- **Release notes** automáticas
- **Pre-release detection** para alpha/beta/rc

## 🔧 Configuración Local

Para contribuir al proyecto:

```bash
# Instalar dependencias de desarrollo
pip install -r requirements.txt
pip install pytest pytest-cov black isort flake8

# Ejecutar tests
pytest tests/ -v

# Verificar formato
black --check .
isort --check-only .
flake8 .

# Formatear código
black .
isort .
```

## 🎯 Beneficios de esta Configuración

### ⚡ **Para Desarrollo**

- Tests rápidos (5-8 min vs 15-20 min anterior)
- Feedback inmediato en PRs
- Linting automático para calidad de código

### 📦 **Para Releases**

- Solo compila cuando realmente se necesita
- Releases profesionales con documentación
- Verificación de integridad incluida
- Soporte para pre-releases

### 💰 **Para Recursos**

- Menor uso de minutos de GitHub Actions
- Compilaciones solo en releases reales
- Testing continuo sin sobrecarga

## 🐛 Troubleshooting

### Tests fallan en PR

```bash
# Ejecutar tests localmente
pytest tests/ -v --cov=.

# Verificar linting
black --check .
isort --check-only .
flake8 .
```

### Release no se crea

- Verificar que el tag empiece con `v`
- Revisar logs en GitHub Actions
- Verificar permisos de `GITHUB_TOKEN`

### Ejecutables no se generan

- Verificar que la compilación fue exitosa
- Revisar artifacts en Actions
- Verificar que `build_executable.py` funciona localmente

## 📊 Monitoreo

- **Tests**: Ve a "Actions" → "Tests" para ver el estado de validación
- **Releases**: Ve a "Actions" → "Build and Release" para ver compilaciones
- **Cobertura**: Integrado con Codecov (próximamente)

## 🔄 Evolución

Esta configuración permite:

- ✅ Desarrollo ágil con validación rápida
- ✅ Releases controladas y documentadas
- ✅ Escalabilidad para más plataformas
- ✅ Integración con herramientas de calidad
