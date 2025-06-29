"""
CLI para herramientas de build de Tabula Cloud Sync.
"""

import sys
from pathlib import Path

import click

from ..config.builder import ConfigBuilder
from .post_install import PostInstallHooks
from .project_detector import ProjectDetector
from .template_generator import TemplateGenerator


@click.group()
@click.version_option(version="1.0.0", prog_name="tabula-build")
def build_cli():
    """
    Herramientas de build para proyectos Tabula Cloud Sync.

    Comandos para construir, configurar y gestionar proyectos.
    """
    pass


@build_cli.command()
def setup():
    """
    Ejecuta la configuración inicial del proyecto.

    Equivalente a la configuración post-instalación.
    """
    click.echo("🔧 Ejecutando configuración inicial...")
    PostInstallHooks.run_post_install()


@build_cli.command()
@click.option("--force", is_flag=True, help="Forzar reconfiguración")
def rebuild(force: bool):
    """
    Reconstruye la configuración del proyecto.
    """
    if not force:
        detector = ProjectDetector()
        if not detector.is_new_project():
            if not click.confirm("¿Reconstruir configuración existente?"):
                return

    click.echo("🔄 Reconstruyendo configuración...")
    PostInstallHooks.run_post_install()


@build_cli.command()
def detect():
    """
    Detecta y muestra información del proyecto.
    """
    detector = ProjectDetector()

    click.echo("🔍 Información del proyecto:")
    click.echo(f"  Raíz: {detector.get_project_root()}")
    click.echo(f"  Tipo: {detector.get_project_type()}")
    click.echo(f"  Base de datos: {detector.detect_database_type() or 'No detectada'}")
    click.echo(f"  Es nuevo: {detector.is_new_project()}")

    services = detector.get_existing_services()
    if services:
        click.echo(f"  Servicios encontrados: {len(services)}")
        for service in services:
            click.echo(f"    - {service}")


if __name__ == "__main__":
    build_cli()
