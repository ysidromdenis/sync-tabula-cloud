#!/usr/bin/env python3
"""
Ejemplo de uso de platformdirs en Tabula Cloud Sync.

Este script demuestra cómo utilizar las nuevas utilidades de directorio
para crear una aplicación que maneja configuración, logs, datos y cache
de manera apropiada para cada sistema operativo.
"""

import logging
import sqlite3
from pathlib import Path

from tabula_cloud_sync.utils.directories import (
    get_appropriate_config_path,
    get_default_log_path,
    tabula_dirs,
)


def setup_logging():
    """Configura logging usando platformdirs."""
    log_file = tabula_dirs.get_log_file_path("ejemplo_app.log")

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.FileHandler(str(log_file)), logging.StreamHandler()],
    )

    logger = logging.getLogger(__name__)
    logger.info(f"Logging configurado. Archivo: {log_file}")
    return logger


def create_database():
    """Crea una base de datos SQLite en la ubicación apropiada."""
    db_path = tabula_dirs.get_data_file_path("ejemplo.db")

    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()

    # Crear tabla de ejemplo
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY,
            nombre TEXT NOT NULL,
            email TEXT UNIQUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """
    )

    # Insertar datos de ejemplo
    cursor.execute(
        "INSERT OR IGNORE INTO usuarios (nombre, email) VALUES (?, ?)",
        ("Usuario Demo", "demo@example.com"),
    )

    conn.commit()
    conn.close()

    return db_path


def load_config():
    """Carga configuración desde ubicación apropiada."""
    config_path = get_appropriate_config_path("ejemplo_config.ini")

    if not config_path.exists():
        # Crear configuración por defecto
        default_config = """[APP]
name = Ejemplo App
version = 1.0.0
debug = false

[DATABASE]
type = sqlite
auto_backup = true

[LOGGING]
level = INFO
rotate = true
"""
        config_path.parent.mkdir(parents=True, exist_ok=True)
        config_path.write_text(default_config)

    return config_path


def manage_cache():
    """Demuestra manejo de cache."""
    import json
    import time

    cache_file = tabula_dirs.get_cache_file_path("datos_cache.json")

    # Datos de ejemplo para cachear
    datos = {
        "timestamp": time.time(),
        "datos": ["item1", "item2", "item3"],
        "configuracion": {"tema": "oscuro", "idioma": "es"},
    }

    # Guardar en cache
    with open(cache_file, "w") as f:
        json.dump(datos, f, indent=2)

    # Leer desde cache
    with open(cache_file, "r") as f:
        datos_leidos = json.load(f)

    return cache_file, datos_leidos


def show_directory_info():
    """Muestra información sobre los directorios utilizados."""
    print("\n" + "=" * 50)
    print("INFORMACIÓN DE DIRECTORIOS")
    print("=" * 50)

    info = tabula_dirs.get_directory_info()

    print(f"📱 Aplicación: {info['app_name']}")
    print(f"👤 Autor: {info['app_author']}")
    print()

    print("📂 Directorios del usuario:")
    print(f"  ⚙️  Configuración: {info['user_config_dir']}")
    print(f"  📊 Datos:         {info['user_data_dir']}")
    print(f"  📝 Logs:          {info['user_log_dir']}")
    print(f"  🗃️  Cache:         {info['user_cache_dir']}")
    print(f"  💾 Backups:       {info['backup_dir']}")
    print(f"  📄 Templates:     {info['templates_dir']}")
    print()

    # Verificar existencia
    print("✅ Estado de directorios:")
    directories_to_check = [
        ("user_config_dir", "Configuración"),
        ("user_data_dir", "Datos"),
        ("user_log_dir", "Logs"),
        ("user_cache_dir", "Cache"),
    ]

    for dir_key, description in directories_to_check:
        path = Path(info[dir_key])
        status = "✅ Existe" if path.exists() else "❌ No existe"
        print(f"  {description}: {status}")


def backup_data():
    """Demuestra cómo crear backups en ubicación apropiada."""
    import datetime
    import shutil

    # Directorio de backup
    backup_dir = tabula_dirs.get_backup_dir()

    # Crear nombre de backup con timestamp
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = f"backup_{timestamp}"
    backup_path = backup_dir / backup_name
    backup_path.mkdir(exist_ok=True)

    # Copiar archivos importantes
    data_dir = tabula_dirs.user_data_dir
    if data_dir.exists():
        for file in data_dir.glob("*.db"):
            shutil.copy2(file, backup_path / file.name)

    config_dir = tabula_dirs.user_config_dir
    if config_dir.exists():
        for file in config_dir.glob("*.ini"):
            shutil.copy2(file, backup_path / file.name)

    return backup_path


def clean_old_files():
    """Limpia archivos antiguos del cache."""
    import time

    cache_dir = tabula_dirs.user_cache_dir
    current_time = time.time()

    # Limpiar archivos de cache más antiguos de 7 días
    for file in cache_dir.glob("*"):
        if file.is_file():
            file_age = current_time - file.stat().st_mtime
            if file_age > (7 * 24 * 3600):  # 7 días en segundos
                file.unlink()
                print(f"🗑️  Eliminado archivo antiguo: {file.name}")


def main():
    """Función principal del ejemplo."""
    print("🚀 Demostración de platformdirs en Tabula Cloud Sync")
    print("=" * 60)

    # 1. Configurar logging
    logger = setup_logging()
    logger.info("Iniciando aplicación de ejemplo")

    # 2. Mostrar información de directorios
    show_directory_info()

    # 3. Cargar/crear configuración
    print("\n📋 CONFIGURACIÓN")
    print("-" * 20)
    config_path = load_config()
    print(f"✅ Configuración cargada desde: {config_path}")
    logger.info(f"Configuración cargada desde {config_path}")

    # 4. Crear base de datos
    print("\n🗄️  BASE DE DATOS")
    print("-" * 20)
    db_path = create_database()
    print(f"✅ Base de datos creada en: {db_path}")
    logger.info(f"Base de datos creada en {db_path}")

    # 5. Manejar cache
    print("\n🗃️  CACHE")
    print("-" * 20)
    cache_file, cache_data = manage_cache()
    print(f"✅ Cache guardado en: {cache_file}")
    print(f"📊 Datos en cache: {len(cache_data)} elementos")
    logger.info(f"Cache actualizado en {cache_file}")

    # 6. Crear backup
    print("\n💾 BACKUP")
    print("-" * 20)
    backup_path = backup_data()
    print(f"✅ Backup creado en: {backup_path}")
    logger.info(f"Backup creado en {backup_path}")

    # 7. Limpiar archivos antiguos
    print("\n🧹 LIMPIEZA")
    print("-" * 20)
    clean_old_files()
    print("✅ Limpieza completada")
    logger.info("Limpieza de archivos antiguos completada")

    # 8. Demostrar proyectos específicos
    print("\n📁 PROYECTOS ESPECÍFICOS")
    print("-" * 30)
    project_name = "proyecto_ejemplo"

    project_dirs = {
        "config": tabula_dirs.get_project_specific_dir(project_name, "config"),
        "data": tabula_dirs.get_project_specific_dir(project_name, "data"),
        "logs": tabula_dirs.get_project_specific_dir(project_name, "logs"),
        "cache": tabula_dirs.get_project_specific_dir(project_name, "cache"),
    }

    for dir_type, path in project_dirs.items():
        print(f"  {dir_type.title()}: {path}")

    logger.info("Demostración completada exitosamente")
    print(f"\n✅ Ejemplo completado. Ver logs en: {get_default_log_path()}")


if __name__ == "__main__":
    main()
