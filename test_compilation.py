#!/usr/bin/env python3
"""Script para probar la compilación del ejecutable."""

import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


def test_compilation():
    """Prueba la compilación del ejecutable."""
    print("=== Test de Compilación ===")

    # Verificar que estamos en el directorio correcto
    if not Path("setup.py").exists():
        print("❌ Error: Ejecute desde el directorio raíz del proyecto")
        return False

    # Crear directorio temporal para pruebas
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        print(f"📁 Directorio temporal: {temp_path}")

        # Copiar archivos necesarios
        files_to_copy = [
            "__main__.py",
            "setup.py",
            "requirements.txt",
            "config.ini.template",
            "core",
            "service",
            "models",
            "utils",
            "build_executable.py",
        ]

        for item in files_to_copy:
            src = Path(item)
            if src.exists():
                if src.is_dir():
                    shutil.copytree(src, temp_path / item)
                else:
                    shutil.copy2(src, temp_path)

        # Cambiar al directorio temporal
        original_dir = os.getcwd()
        os.chdir(temp_path)

        try:
            # Instalar dependencias
            print("📦 Instalando dependencias...")
            subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "pip",
                    "install",
                    "-r",
                    "requirements.txt",
                ],
                check=True,
                capture_output=True,
            )

            # Instalar PyInstaller
            print("🔧 Instalando PyInstaller...")
            subprocess.run(
                [sys.executable, "-m", "pip", "install", "pyinstaller>=5.0.0"],
                check=True,
                capture_output=True,
            )

            # Compilar ejecutable
            print("⚙️ Compilando ejecutable...")
            result = subprocess.run(
                [sys.executable, "build_executable.py", "--no-installer"],
                capture_output=True,
                text=True,
            )

            if result.returncode != 0:
                print("❌ Error en compilación:")
                print(result.stderr)
                return False

            # Verificar que el ejecutable se creó
            if sys.platform.startswith("win"):
                executable = temp_path / "dist" / "tabula-cloud-sync.exe"
            else:
                executable = temp_path / "dist" / "tabula-cloud-sync"

            if not executable.exists():
                print(f"❌ Ejecutable no encontrado: {executable}")
                return False

            print(f"✅ Ejecutable creado: {executable}")

            # Probar el ejecutable
            print("🧪 Probando ejecutable...")
            test_result = subprocess.run(
                [str(executable), "--help"],
                capture_output=True,
                text=True,
                timeout=30,
            )

            if test_result.returncode == 0:
                print("✅ Ejecutable funciona correctamente")

                # Mostrar información del ejecutable
                size = executable.stat().st_size
                size_mb = size / (1024 * 1024)
                print(f"📊 Tamaño del ejecutable: {size_mb:.1f} MB")

                return True
            else:
                print("❌ Error ejecutando el ejecutable:")
                print(test_result.stderr)
                return False

        except subprocess.TimeoutExpired:
            print("❌ Timeout probando el ejecutable")
            return False
        except Exception as e:
            print(f"❌ Error en prueba: {e}")
            return False
        finally:
            os.chdir(original_dir)


def test_dependencies():
    """Prueba que todas las dependencias estén disponibles."""
    print("=== Test de Dependencias ===")

    required_modules = [
        "configparser",
        "requests",
        "logging",
        "threading",
        "signal",
        "abc",
        "datetime",
        "os",
        "sys",
        "platform",
    ]

    missing = []
    for module in required_modules:
        try:
            __import__(module)
            print(f"✅ {module}")
        except ImportError:
            print(f"❌ {module}")
            missing.append(module)

    if missing:
        print(f"❌ Módulos faltantes: {missing}")
        return False

    # Probar PyInstaller
    try:
        import PyInstaller

        print(f"✅ PyInstaller {PyInstaller.__version__}")
    except ImportError:
        print("⚠️  PyInstaller no disponible (se instalará automáticamente)")

    return True


def test_project_structure():
    """Verifica la estructura del proyecto."""
    print("=== Test de Estructura del Proyecto ===")

    required_files = [
        "__main__.py",
        "setup.py",
        "requirements.txt",
        "config.ini.template",
        "build_executable.py",
    ]

    required_dirs = ["core", "service", "models", "utils"]

    missing = []

    for file in required_files:
        if not Path(file).exists():
            print(f"❌ Archivo faltante: {file}")
            missing.append(file)
        else:
            print(f"✅ {file}")

    for dir in required_dirs:
        if not Path(dir).exists():
            print(f"❌ Directorio faltante: {dir}")
            missing.append(dir)
        else:
            print(f"✅ {dir}/")

    if missing:
        print(f"❌ Elementos faltantes: {missing}")
        return False

    return True


def main():
    """Función principal."""
    print("🚀 Test de Compilación de Tabula Cloud Sync")
    print("=" * 50)

    tests = [
        ("Estructura del Proyecto", test_project_structure),
        ("Dependencias", test_dependencies),
        ("Compilación", test_compilation),
    ]

    results = []

    for test_name, test_func in tests:
        print(f"\n🔍 Ejecutando: {test_name}")
        print("-" * 30)

        try:
            result = test_func()
            results.append((test_name, result))

            if result:
                print(f"✅ {test_name}: EXITOSO")
            else:
                print(f"❌ {test_name}: FALLIDO")

        except Exception as e:
            print(f"❌ {test_name}: ERROR - {e}")
            results.append((test_name, False))

    # Resumen final
    print("\n" + "=" * 50)
    print("📋 RESUMEN DE PRUEBAS")
    print("=" * 50)

    passed = 0
    total = len(results)

    for test_name, result in results:
        status = "✅ EXITOSO" if result else "❌ FALLIDO"
        print(f"{test_name}: {status}")
        if result:
            passed += 1

    print(f"\n📊 Resultado: {passed}/{total} pruebas exitosas")

    if passed == total:
        print(
            "🎉 ¡Todas las pruebas pasaron! El proyecto está listo para compilar."
        )
        return True
    else:
        print(
            "⚠️  Algunas pruebas fallaron. Revise los errores antes de compilar."
        )
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
