"""
Script de prueba para validar la instalación y funcionalidad de Tabula Cloud Sync.
"""

import sys
import traceback
from pathlib import Path


def test_imports():
    """Prueba las importaciones básicas."""
    print("🔍 Probando importaciones...")

    try:
        import tabula_cloud_sync

        print(
            f"✅ tabula_cloud_sync importado correctamente (v{tabula_cloud_sync.__version__})"
        )
    except ImportError as e:
        print(f"❌ Error importando tabula_cloud_sync: {e}")
        return False

    try:
        from tabula_cloud_sync import TabulaCloudService

        print("✅ TabulaCloudService importado correctamente")
    except ImportError as e:
        print(f"❌ Error importando TabulaCloudService: {e}")
        return False

    try:
        from tabula_cloud_sync.models import BaseModel

        print("✅ BaseModel importado correctamente")
    except ImportError as e:
        print(f"❌ Error importando BaseModel: {e}")
        return False

    try:
        from tabula_cloud_sync.core import Session

        print("✅ Session importado correctamente")
    except ImportError as e:
        print(f"❌ Error importando Session: {e}")
        return False

    return True


def test_service_creation():
    """Prueba la creación de un servicio básico."""
    print("\n🏗️  Probando creación de servicio...")

    try:
        from tabula_cloud_sync import TabulaCloudService

        class TestService(TabulaCloudService):
            def perform_sync(self):
                return {"status": "test", "message": "Prueba exitosa"}

        # Crear servicio sin configuración (debería auto-configurarse)
        service = TestService("nonexistent_config.ini")
        print("✅ Servicio de prueba creado correctamente")

        # Probar métodos básicos
        status = service.get_status()
        print(f"✅ Estado del servicio obtenido: running={status['running']}")

        return True

    except Exception as e:
        print(f"❌ Error creando servicio: {e}")
        traceback.print_exc()
        return False


def test_cli_commands():
    """Prueba la disponibilidad de comandos CLI."""
    print("\n🖥️  Probando comandos CLI...")

    import os
    import subprocess

    # Construir rutas a los comandos en el entorno virtual
    base_dir = os.path.dirname(os.path.abspath(__file__))
    venv_bin = os.path.join(base_dir, ".venv", "bin")

    tabula_cli = os.path.join(venv_bin, "tabula-cli")
    tabula_service = os.path.join(venv_bin, "tabula-service")

    # Probar tabula-cli
    try:
        result = subprocess.run(
            [tabula_cli, "--help"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode == 0:
            print("✅ Comando tabula-cli disponible")
        else:
            print(f"⚠️  tabula-cli retornó código {result.returncode}")
    except subprocess.TimeoutExpired:
        print("⚠️  Timeout ejecutando tabula-cli")
    except FileNotFoundError:
        print("❌ Comando tabula-cli no encontrado en PATH")
    except Exception as e:
        print(f"❌ Error ejecutando tabula-cli: {e}")

    # Probar tabula-service
    try:
        result = subprocess.run(
            ["tabula-service", "--help"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode == 0:
            print("✅ Comando tabula-service disponible")
        else:
            print(f"⚠️  tabula-service retornó código {result.returncode}")
    except subprocess.TimeoutExpired:
        print("⚠️  Timeout ejecutando tabula-service")
    except FileNotFoundError:
        print("❌ Comando tabula-service no encontrado en PATH")
    except Exception as e:
        print(f"❌ Error ejecutando tabula-service: {e}")


def test_build_tools():
    """Prueba las herramientas de build."""
    print("\n🔧 Probando build tools...")

    try:
        from tabula_cloud_sync.build_tools.project_detector import (
            ProjectDetector,
        )

        detector = ProjectDetector()

        project_root = detector.get_project_root()
        project_type = detector.get_project_type()

        print(f"✅ Project detector funcionando:")
        print(f"   Directorio raíz: {project_root}")
        print(f"   Tipo de proyecto: {project_type}")

        return True

    except Exception as e:
        print(f"❌ Error en build tools: {e}")
        return False


def test_utils():
    """Prueba las utilidades comunes."""
    print("\n🛠️  Probando utilidades...")

    try:
        from tabula_cloud_sync.utils.commons import (
            ensure_directory,
            get_system_info,
        )

        # Probar creación de directorio
        test_dir = Path("/tmp/tabula_test_dir")
        ensure_directory(str(test_dir))

        if test_dir.exists():
            print("✅ ensure_directory funcionando")
            test_dir.rmdir()  # Limpiar
        else:
            print("❌ ensure_directory no creó el directorio")
            return False

        # Probar información del sistema
        sys_info = get_system_info()
        print(
            f"✅ get_system_info funcionando: {sys_info['system']} {sys_info['release']}"
        )

        return True

    except Exception as e:
        print(f"❌ Error en utilidades: {e}")
        return False


def test_models():
    """Prueba los modelos de datos."""
    print("\n📊 Probando modelos...")

    try:
        from dataclasses import dataclass

        from tabula_cloud_sync.models.base_model import TabulaEntity

        @dataclass
        class TestEntity(TabulaEntity):
            codigo: str = ""

            def validate(self):
                errors = super().validate()
                if not self.codigo:
                    errors.append("Código es requerido")
                return errors

        # Crear entidad de prueba
        entity = TestEntity(name="Test", codigo="TEST001")

        if entity.is_valid():
            print("✅ Modelo TabulaEntity funcionando")

            # Probar serialización
            data = entity.to_dict()
            json_str = entity.to_json()

            print("✅ Serialización JSON funcionando")
            return True
        else:
            print(f"❌ Modelo no válido: {entity.get_validation_errors()}")
            return False

    except Exception as e:
        print(f"❌ Error en modelos: {e}")
        return False


def main():
    """Función principal de pruebas."""
    print("🧪 Iniciando pruebas de Tabula Cloud Sync...")
    print("=" * 60)

    tests = [
        ("Importaciones", test_imports),
        ("Creación de servicio", test_service_creation),
        ("Comandos CLI", test_cli_commands),
        ("Build tools", test_build_tools),
        ("Utilidades", test_utils),
        ("Modelos", test_models),
    ]

    passed = 0
    total = len(tests)

    for test_name, test_func in tests:
        try:
            print(f"\n📋 Ejecutando: {test_name}")
            if test_func():
                passed += 1
                print(f"✅ {test_name}: PASÓ")
            else:
                print(f"❌ {test_name}: FALLÓ")
        except Exception as e:
            print(f"❌ {test_name}: ERROR - {e}")

    print("\n" + "=" * 60)
    print(f"📊 Resultados: {passed}/{total} pruebas pasaron")

    if passed == total:
        print(
            "🎉 ¡Todas las pruebas pasaron! La librería está funcionando correctamente."
        )
        return 0
    else:
        print(
            "⚠️  Algunas pruebas fallaron. Revisa los mensajes de error arriba."
        )
        return 1


if __name__ == "__main__":
    sys.exit(main())
