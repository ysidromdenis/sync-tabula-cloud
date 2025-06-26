# Changelog

Todos los cambios notables de este proyecto serán documentados en este archivo.

El formato está basado en [Keep a Changelog](https://keepachangelog.com/es/1.0.0/),
y este proyecto se adhiere a [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.0] - 2025-06-26

### Agregado

- **Servicio multiplataforma**: Soporte completo para Windows y Linux
- **Clase base TabulaCloudService**: Servicio abstracto para personalización
- **TabulaCloudDaemon**: Daemon nativo para sistemas Linux/Unix
- **TabulaCloudWindowsService**: Servicio nativo para Windows
- **Administrador de servicios**: Script unificado para gestión de servicios
- **Configuración extendida**: Nuevas opciones de configuración para servicios
- **Ejemplo completo**: Proyecto de ejemplo mostrando implementación personalizada
- **Scripts de instalación**: Instaladores automáticos para Windows y Linux
- **Documentación de servicios**: Guía completa de configuración y uso
- **Tests básicos**: Suite de pruebas para validar funcionalidad
- **Punto de entrada CLI**: Comando `tabula-service` para administración
- **Logging avanzado**: Sistema de logging configurable y robusto
- **Health checks**: Verificación de estado del servicio
- **Manejo de errores**: Recuperación automática y manejo de fallos

### Modificado

- **Configuración**: Template actualizado con nuevas opciones de servicio
- **Requirements**: Dependencias opcionales para Windows agregadas
- **Setup.py**: Entry points y clasificadores actualizados
- **README**: Documentación completamente reescrita con ejemplos de servicio

### Características del Servicio

- ✅ **Multiplataforma**: Funciona en Windows y Linux sin modificaciones
- ✅ **Auto-instalación**: Scripts de instalación automática incluidos
- ✅ **Configuración flexible**: Cada proyecto puede personalizar completamente
- ✅ **Logging robusto**: Sistema de logs configurable y rotativo
- ✅ **Recuperación de errores**: Manejo automático de fallos y reconexiones
- ✅ **Sincronización personalizable**: Lógica de negocio completamente personalizable
- ✅ **Gestión de recursos**: Limpieza automática de recursos y conexiones
- ✅ **Monitoreo**: Health checks y reportes de estado integrados

### Casos de Uso

- **Sincronización automática**: Mantener sistemas locales sincronizados con Tabula Cloud
- **Procesamiento de lotes**: Procesar documentos, pedidos y facturas automáticamente
- **Integración de sistemas**: Conectar ERPs locales con Tabula Cloud
- **Distribuidores**: Automatizar operaciones de distribución y ventas
- **Monitoreo continuo**: Supervisar cambios y generar reportes automáticos

## [Sin publicar]

### Agregado

- Configuración inicial del proyecto como biblioteca base
- Scripts de automatización para actualización de dependientes
- GitHub Actions para notificaciones automáticas
- Documentación completa de uso e instalación

## [1.0.0] - 2024-06-26

### Agregado

- Módulo `core` con constantes, sesión y URLs
- Módulo `models` con modelo de documentos
- Módulo `utils` con utilidades comunes y logging
- Directorio `icons` con recursos gráficos
- Plantilla de configuración `config.ini.template`
- Estructura de paquete Python distribuible

### Configuración

- Setup.py para instalación como dependencia
- Manifesto para incluir archivos adicionales
- Requirements.txt con dependencias básicas
