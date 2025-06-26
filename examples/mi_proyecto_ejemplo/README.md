# Proyecto Ejemplo: Mi Distribuidor Tabula

Este directorio contiene un ejemplo de cómo usar la librería `tabula-cloud-sync` como servicio en tu proyecto.

## Estructura del Proyecto

```
mi_distribuidor_tabula/
├── requirements.txt
├── config.ini
├── mi_servicio.py
├── models/
│   └── mi_modelo.py
└── README.md
```

## Instalación

1. Clonar o crear tu proyecto
2. Instalar dependencias:

```bash
pip install -r requirements.txt
```

3. Configurar `config.ini` con tus credenciales
4. Ejecutar el servicio:

```bash
# Modo desarrollo (foreground)
python mi_servicio.py --foreground

# Como daemon (Linux)
python mi_servicio.py start

# Como servicio (Windows)
python mi_servicio.py install
net start MiDistribuidorTabula
```

## Personalización

El archivo `mi_servicio.py` muestra cómo:

- Extender la clase base `TabulaCloudService`
- Implementar lógica de sincronización personalizada
- Manejar errores específicos del proyecto
- Configurar logging personalizado
- Integrar con bases de datos locales

## Beneficios

- **Separación de responsabilidades**: Tu lógica de negocio separada de la infraestructura de servicio
- **Multiplataforma**: El mismo código funciona en Windows y Linux
- **Mantenimiento fácil**: Actualizaciones automáticas de la librería base
- **Configuración flexible**: Cada proyecto puede tener su propia configuración
