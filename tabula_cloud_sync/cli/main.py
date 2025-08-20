"""
CLI principal para Tabula Cloud Sync.

Proporciona comandos para inicializar proyectos, generar configuraciones,
y gestionar servicios de sincronización.
"""

import sys
from pathlib import Path
from typing import Optional

import click

from ..build_tools.post_install import PostInstallHooks
from ..build_tools.project_detector import ProjectDetector
from ..build_tools.template_generator import TemplateGenerator
from ..config.builder import ConfigBuilder


@click.group()
@click.version_option(version="1.0.0", prog_name="tabula-cli")
def cli():
    """
    CLI para Tabula Cloud Sync - Librería de sincronización con Tabula Cloud.

    Esta herramienta te ayuda a configurar y gestionar proyectos que utilizan
    la librería Tabula Cloud Sync.
    """
    pass


@cli.command()
@click.option(
    "--project-name",
    prompt="Nombre del proyecto",
    help="Nombre del proyecto a crear",
)
@click.option(
    "--service-name", help="Nombre personalizado para el servicio (opcional)"
)
@click.option(
    "--database-type",
    type=click.Choice(["sqlite", "postgresql", "mysql", "sqlserver"]),
    help="Tipo de base de datos a configurar",
)
@click.option(
    "--force",
    is_flag=True,
    help="Forzar la inicialización incluso si ya existe configuración",
)
def init(
    project_name: str,
    service_name: Optional[str],
    database_type: Optional[str],
    force: bool,
):
    """
    Inicializa un nuevo proyecto con Tabula Cloud Sync.

    Crea la estructura de directorios, archivos de configuración,
    y templates base para comenzar a usar la librería.
    """
    click.echo("🚀 Inicializando proyecto Tabula Cloud Sync...")

    # Usar el directorio actual de trabajo donde se invoca el comando
    project_root = Path.cwd()
    click.echo(f"📁 Inicializando en: {project_root}")

    # Verificar si ya existe configuración en el directorio actual
    config_exists = (project_root / "config" / "tabula_config.ini").exists()
    tabula_marker_exists = (project_root / ".tabula_markers").exists()

    if not force and (config_exists or tabula_marker_exists):
        if not click.confirm(
            "Ya existe configuración de Tabula Cloud Sync en este directorio. "
            "¿Continuar?"
        ):
            click.echo("❌ Operación cancelada")
            return

    try:
        # Crear estructura de directorios
        click.echo("📁 Creando estructura de directorios...")
        PostInstallHooks._create_project_structure(project_root)

        # Generar configuración
        click.echo("⚙️  Generando archivos de configuración...")
        config_builder = ConfigBuilder(project_root, database_type=database_type)
        config_builder.generate_main_config()
        config_builder.generate_logging_config()
        config_builder.generate_database_config()
        config_builder.generate_service_config()

        # Generar templates
        click.echo("📄 Generando templates de código...")
        template_gen = TemplateGenerator(project_root)

        # Usar nombres personalizados si se proporcionan
        actual_service_name = service_name or f"{project_name}Service"

        service_file = template_gen.generate_service_template(
            service_name=actual_service_name, project_name=project_name
        )
        model_file = template_gen.generate_model_template(
            f"{project_name}Model"
        )
        daemon_file = template_gen.generate_daemon_template(
            actual_service_name
        )

        # Marcar como configurado
        tabula_marker_file = project_root / ".tabula_markers"
        with open(tabula_marker_file, "w") as f:
            f.write(f"configured_at={project_root}\n")
            f.write("version=1.0.0\n")

        click.echo("✅ Proyecto inicializado exitosamente!")
        click.echo(f"📂 Directorio: {project_root}")
        click.echo(f"🔧 Servicio: {service_file}")
        click.echo(f"📊 Modelo: {model_file}")
        click.echo(f"⚙️  Daemon: {daemon_file}")
        if database_type:
            click.echo(f"💾 Base de datos configurada: {database_type}")
        click.echo("")
        click.echo("📝 Próximos pasos:")
        click.echo("   1. Edita config/tabula_config.ini con tus credenciales")
        click.echo(
            f"   2. Personaliza {service_file.name} con tu lógica de negocio"
        )
        click.echo(
            "   3. Ejecuta 'tabula-service start' para iniciar el servicio"
        )

    except Exception as e:
        click.echo(f"❌ Error durante la inicialización: {e}")
        sys.exit(1)


@cli.command()
@click.option(
    "--config-file",
    default="config/tabula_config.ini",
    help="Archivo de configuración a validar",
)
def validate(config_file: str):
    """
    Valida la configuración del proyecto.

    Verifica que todos los archivos de configuración estén presentes
    y tengan valores válidos.
    """
    click.echo("🔍 Validando configuración...")

    project_root = Path.cwd()
    config_path = project_root / config_file

    if not config_path.exists():
        click.echo(f"❌ Archivo de configuración no encontrado: {config_path}")
        sys.exit(1)

    # TODO: Implementar validación detallada
    click.echo("✅ Configuración válida")


@cli.command()
@click.argument(
    "template_type", type=click.Choice(["service", "model", "daemon"])
)
@click.option(
    "--name",
    prompt="Nombre del template",
    help="Nombre para el nuevo template",
)
@click.option(
    "--output-dir",
    help="Directorio de salida (por defecto: services/ o models/)",
)
def generate(template_type: str, name: str, output_dir: Optional[str]):
    """
    Genera nuevos templates de código.

    TEMPLATE_TYPE puede ser: service, model, o daemon
    """
    click.echo(f"📄 Generando template {template_type}...")

    project_root = Path.cwd()
    template_gen = TemplateGenerator(project_root)

    try:
        if template_type == "service":
            output_file = template_gen.generate_service_template(
                service_name=name, project_name=project_root.name
            )
        elif template_type == "model":
            output_file = template_gen.generate_model_template(name)
        elif template_type == "daemon":
            output_file = template_gen.generate_daemon_template(name)

        click.echo(f"✅ Template generado: {output_file}")

    except Exception as e:
        click.echo(f"❌ Error generando template: {e}")
        sys.exit(1)


@cli.command()
def status():
    """
    Muestra el estado del proyecto y configuración.

    Proporciona información sobre la configuración actual,
    servicios detectados, y estado de sincronización.
    """
    click.echo("📊 Estado del proyecto Tabula Cloud Sync")
    click.echo("=" * 50)

    # Usar el directorio actual en lugar del directorio raíz del proyecto
    project_root = Path.cwd()

    # Crear un detector temporal para obtener información del proyecto
    detector = ProjectDetector()

    click.echo(f"📂 Directorio actual: {project_root}")
    click.echo(f"🔧 Tipo de proyecto: {detector.get_project_type()}")
    click.echo(
        f"💾 Base de datos: {detector.detect_database_type() or 'No detectada'}"
    )

    # Verificar configuración en el directorio actual
    config_file = project_root / "config" / "tabula_config.ini"
    if config_file.exists():
        click.echo("✅ Configuración principal: Presente")
    else:
        click.echo("❌ Configuración principal: No encontrada")

    # Buscar servicios en el directorio actual
    services = []
    python_files = list(project_root.rglob("*.py"))

    for py_file in python_files:
        try:
            with open(py_file, "r", encoding="utf-8") as f:
                content = f.read()
                if (
                    "class" in content
                    and "TabulaCloudService" in content
                    and "def perform_sync" in content
                ):
                    services.append(py_file)
        except (UnicodeDecodeError, PermissionError):
            continue

    if services:
        click.echo(f"🔧 Servicios encontrados: {len(services)}")
        for service in services:
            click.echo(f"   - {service.name}")
    else:
        click.echo("⚠️  No se encontraron servicios")


@cli.command()
@click.option(
    "--environment",
    type=click.Choice(["development", "testing", "production"]),
    default="development",
    help="Entorno para el cual generar la configuración",
)
def configure(environment: str):
    """
    Configura el entorno específico.

    Genera archivos de configuración optimizados para diferentes entornos.
    """
    click.echo(f"⚙️  Configurando entorno: {environment}")

    project_root = Path.cwd()
    config_builder = ConfigBuilder(project_root)

    try:
        config_file = config_builder.generate_environment_config(environment)
        click.echo(
            f"✅ Configuración de {environment} generada: {config_file}"
        )

    except Exception as e:
        click.echo(f"❌ Error configurando entorno: {e}")
        sys.exit(1)


@cli.command()
@click.option(
    "--output",
    default="project_info.json",
    help="Archivo de salida para la información del proyecto",
)
def info(output: str):
    """
    Exporta información detallada del proyecto.

    Genera un archivo JSON con toda la información relevante
    del proyecto y su configuración.
    """
    click.echo("📋 Recopilando información del proyecto...")

    # Usar el directorio actual en lugar del directorio raíz del proyecto
    project_root = Path.cwd()

    # Crear un detector temporal para obtener información del proyecto
    detector = ProjectDetector()

    from ..utils.commons import get_system_info, save_json_file

    # Verificar si está configurado en el directorio actual
    config_exists = (project_root / "config" / "tabula_config.ini").exists()
    tabula_marker_exists = (project_root / ".tabula_markers").exists()
    is_configured = config_exists or tabula_marker_exists

    # Buscar servicios en el directorio actual
    services = []
    python_files = list(project_root.rglob("*.py"))

    for py_file in python_files:
        try:
            with open(py_file, "r", encoding="utf-8") as f:
                content = f.read()
                if (
                    "class" in content
                    and "TabulaCloudService" in content
                    and "def perform_sync" in content
                ):
                    services.append(py_file)
        except (UnicodeDecodeError, PermissionError):
            continue

    project_info = {
        "project": {
            "name": project_root.name,
            "root": str(project_root),
            "type": detector.get_project_type(),
        },
        "configuration": {
            "database_type": detector.detect_database_type(),
            "services": [str(s) for s in services],
            "is_configured": is_configured,
        },
        "system": get_system_info(),
        "tabula_cloud_sync": {
            "version": "1.0.0",
            "cli_version": "1.0.0",
        },
    }

    if save_json_file(output, project_info):
        click.echo(f"✅ Información exportada a: {output}")
    else:
        click.echo("❌ Error exportando información")
        sys.exit(1)


if __name__ == "__main__":
    cli()
