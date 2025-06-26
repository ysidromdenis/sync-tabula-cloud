# Guía de GitHub Releases

## 🎯 Estrategia de Releases

Este proyecto usa **GitHub Releases** como estrategia principal para distribuir ejecutables compilados.

## 📋 Tipos de Release

### 1. **Releases Estables (v1.0.0, v2.1.0)**
- Versiones de producción
- Releases públicas
- Ejecutables completamente probados

### 2. **Pre-releases (v1.0.0-beta.1, v2.0.0-rc.1)**
- Versiones de prueba
- Marcadas automáticamente como "pre-release"
- Para testing antes del release estable

### 3. **Releases de Desarrollo (v1.0.0-alpha.1)**
- Versiones experimentales
- Solo para desarrolladores
- Pueden contener features incompletas

## 🚀 Cómo Crear una Release

### Método 1: Desde línea de comandos
```bash
# Release estable
git tag v1.0.0
git push origin v1.0.0

# Pre-release
git tag v1.1.0-beta.1
git push origin v1.1.0-beta.1

# Release de desarrollo
git tag v1.2.0-alpha.1
git push origin v1.2.0-alpha.1
```

### Método 2: Desde GitHub Web
1. Ve a tu repositorio en GitHub
2. Click en "Releases" → "Create a new release"
3. Escribe el tag (ej: `v1.0.0`)
4. El workflow se ejecutará automáticamente

## 📦 Qué se Incluye en Cada Release

### Archivos automáticamente generados:
- `tabula-cloud-sync-windows-*.zip` - Ejecutable y paquete para Windows
- `tabula-cloud-sync-linux-*.zip` - Ejecutable y paquete para Linux
- `tabula-cloud-sync-macos-*.zip` - Ejecutable y paquete para macOS
- `checksums.txt` - Hashes SHA256 para verificación

### Contenido de cada ZIP:
- Ejecutable compilado (`tabula-cloud-sync` o `tabula-cloud-sync.exe`)
- `config.ini.template` - Plantilla de configuración
- `README.md` - Documentación principal
- `docs/` - Documentación completa
- Scripts de instalación específicos por plataforma

## 🔍 Verificación de Integridad

Cada release incluye un archivo `checksums.txt`:

```bash
# Descargar archivos
wget https://github.com/tu-usuario/tu-repo/releases/download/v1.0.0/tabula-cloud-sync-linux-standalone.zip
wget https://github.com/tu-usuario/tu-repo/releases/download/v1.0.0/checksums.txt

# Verificar integridad
sha256sum -c checksums.txt
```

## 📊 Versionado Semántico

Seguimos [Semantic Versioning](https://semver.org/):

- `MAJOR.MINOR.PATCH` (ej: `v2.1.3`)
- `MAJOR` - Cambios incompatibles
- `MINOR` - Nuevas funcionalidades compatibles
- `PATCH` - Correcciones de bugs

### Ejemplos:
- `v1.0.0` - Primera release estable
- `v1.1.0` - Nuevas características
- `v1.1.1` - Corrección de bugs
- `v2.0.0` - Cambios importantes (breaking changes)

## 🎯 Mejores Prácticas

### 1. **Antes de crear una release:**
```bash
# Verificar que todo funciona
python build_executable.py --no-installer
python build_executable.py --verify-only

# Ejecutar tests
python -m pytest tests/ -v

# Revisar cambios
git log --oneline $(git describe --tags --abbrev=0)..HEAD
```

### 2. **Nomenclatura de tags:**
- ✅ `v1.0.0` - Correcto
- ✅ `v1.0.0-beta.1` - Correcto
- ❌ `1.0.0` - Sin prefijo 'v'
- ❌ `release-1.0.0` - Formato incorrecto

### 3. **Documentación de release:**
- Siempre incluir notas de la versión
- Mencionar cambios importantes
- Incluir instrucciones de migración si aplica

## 🔄 Automatización

### Triggers automáticos:
- **Push de tag v***: Crea release automáticamente
- **Manual**: Desde GitHub Actions → "Run workflow"
- **PR merge**: Solo compila, no crea release

### Workflow incluye:
1. ✅ Compilación para 3 plataformas
2. ✅ Testing automático
3. ✅ Verificación de ejecutables
4. ✅ Creación de checksums
5. ✅ Subida automática a GitHub Releases

## 📱 Notificaciones

GitHub automáticamente:
- Notifica a watchers del repositorio
- Crea entry en el feed de releases
- Permite suscripción a nuevas releases

## 🎯 URLs de Descarga

Los ejecutables están disponibles en:
```
https://github.com/[usuario]/[repo]/releases/download/[tag]/[archivo]
```

Ejemplo:
```
https://github.com/tu-usuario/tabula-cloud-sync/releases/download/v1.0.0/tabula-cloud-sync-windows-standalone.zip
```

## 🔧 Troubleshooting

### Release no se crea:
1. Verificar que el tag empiece con 'v'
2. Revisar los logs en GitHub Actions
3. Verificar permisos de `GITHUB_TOKEN`

### Archivos faltantes:
1. Verificar que la compilación fue exitosa
2. Revisar los artifacts en Actions
3. Verificar que los archivos ZIP se generaron

### Checksums incorrectos:
1. Re-descargar los archivos
2. Verificar integridad de la descarga
3. Comparar con los logs de Actions
