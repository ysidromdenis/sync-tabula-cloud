# Configuración para tabula-cloud-sync

## Proyectos dependientes conocidos

Agrega aquí los proyectos que usan esta biblioteca como base:

### Proyectos locales

- [ ] /ruta/al/proyecto1
- [ ] /ruta/al/proyecto2

### Proyectos remotos (GitHub)

- [ ] https://github.com/usuario/proyecto1
- [ ] https://github.com/usuario/proyecto2

## Configuración de GitHub Actions

Para habilitar notificaciones automáticas a proyectos dependientes:

1. **En este repositorio**:

   - Agrega los repositorios dependientes en GitHub Secrets como `DEPENDENT_REPOS`
   - Formato: `usuario/repo1,usuario/repo2,usuario/repo3`

2. **En repositorios dependientes**:
   - Copia `docs/example-dependent-workflow.yml` a `.github/workflows/update-tabula-base.yml`
   - Personaliza según las necesidades del proyecto

## Scripts de actualización

### Automático

- `scripts/update-dependents.py` - Script Python multiplataforma
- `scripts/update-dependents.sh` - Script Bash para Linux/macOS

### Manual

```bash
# Actualizar un proyecto específico
cd /ruta/al/proyecto-dependiente

# Si usa git submodules
git submodule update --remote

# Si usa pip install
pip install --upgrade git+https://github.com/ysidromdenis/template-sync-tabula-cloud.git
```

## Estructura de versionado

- **MAJOR** (x.0.0): Cambios incompatibles en la API
- **MINOR** (0.x.0): Nueva funcionalidad compatible
- **PATCH** (0.0.x): Correcciones de errores

## Checklist para releases

- [ ] Actualizar versión en `setup.py`
- [ ] Actualizar `CHANGELOG.md`
- [ ] Crear tag `git tag vX.Y.Z`
- [ ] Push tag `git push origin vX.Y.Z`
- [ ] El workflow de GitHub Actions notificará a proyectos dependientes
- [ ] Verificar que las actualizaciones se propaguen correctamente
