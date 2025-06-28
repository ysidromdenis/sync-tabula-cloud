#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Script para compilar Tabula Cloud Sync Service en ejecutable."""

import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path


class ServiceCompiler:
    """Compilador del servicio a ejecutable."""

    def __init__(self):
        self.project_root = Path(__file__).parent
        self.build_dir = self.project_root / "build"
        self.dist_dir = self.project_root / "dist"
        self.system = platform.system().lower()
        self.version = self._get_version()

    def _get_version(self):
        """Obtiene la versión del proyecto desde setup.py."""
        try:
            setup_py = self.project_root / "setup.py"
            if setup_py.exists():
                with open(setup_py, "r", encoding="utf-8") as f:
                    content = f.read()
                    # Buscar línea version="x.x.x"
                    import re

                    match = re.search(r'version="([^"]+)"', content)
                    if match:
                        return match.group(1)
            return "2.0.0"  # fallback
        except Exception:
            return "2.0.0"  # fallback

    def setup_environment(self):
        """Configura el entorno para compilación."""
        print("=== Configurando entorno de compilación ===")

        # Verificar PyInstaller
        try:
            import PyInstaller

            print(f"PyInstaller {PyInstaller.__version__} disponible")
        except ImportError:
            print("Instalando PyInstaller...")
            subprocess.check_call(
                [sys.executable, "-m", "pip", "install", "pyinstaller>=5.0.0"]
            )

        # Limpiar directorios previos
        if self.build_dir.exists():
            shutil.rmtree(self.build_dir)
        if self.dist_dir.exists():
            shutil.rmtree(self.dist_dir)

        print("Entorno configurado correctamente")

    def create_spec_file(self):
        """Crea el archivo .spec para PyInstaller."""
        print("Creando archivo de especificación...")

        # Detectar archivos a incluir
        data_files = []

        # Agregar archivos con rutas absolutas
        config_template = self.project_root / "config.ini.template"
        if config_template.exists():
            data_files.append((str(config_template), "."))

        icons_dir = self.project_root / "icons"
        if icons_dir.exists():
            data_files.append((str(icons_dir), "icons"))

        # Agregar archivo de instalación para usuarios finales
        install_guide = self.project_root / "INSTALL.md"
        if install_guide.exists():
            data_files.append((str(install_guide), "."))

        # Solo incluir documentación técnica específica si existe
        # (Para usuarios finales solo se incluye INSTALL.md arriba)

        # Agregar archivos de ejemplo si existen
        examples_dir = self.project_root / "examples"
        if examples_dir.exists():
            data_files.append((str(examples_dir), "examples"))

        # Detectar módulos hidden imports necesarios
        hidden_imports = [
            "configparser",
            "requests",
            "logging.handlers",
            "datetime",
            "threading",
            "signal",
            "abc",
            "json",
            "time",
            "pathlib",
            "shutil",
            "subprocess",
            "urllib.request",
            "urllib.parse",
            "urllib.error",
            "ssl",
            "socket",
        ]

        # Agregar imports específicos de Windows si es necesario
        if self.system == "windows":
            hidden_imports.extend(
                [
                    "win32serviceutil",
                    "win32service",
                    "win32event",
                    "servicemanager",
                    "socket",
                ]
            )

        spec_content = f"""# -*- mode: python ; coding: utf-8 -*-

import sys
import os
from pathlib import Path

# Configuración del proyecto
project_root = Path(r'{self.project_root}')
sys.path.insert(0, str(project_root))

# Datos a incluir
data_files = {data_files}

# Imports ocultos
hidden_imports = {hidden_imports}

# Configuración para diferentes plataformas
if sys.platform.startswith('win'):
    # Windows
    icon_path = project_root / 'icons' / 'tabula.ico'
    icon_file = str(icon_path) if icon_path.exists() else None
    console = False
    name = 'tabula-cloud-sync.exe'
elif sys.platform.startswith('linux') or sys.platform.startswith('darwin'):
    # Linux/macOS
    icon_file = None
    console = True
    name = 'tabula-cloud-sync'
else:
    icon_file = None
    console = True
    name = 'tabula-cloud-sync'

a = Analysis(
    [str(project_root / '__main__.py')],
    pathex=[str(project_root)],
    binaries=[],
    datas=data_files,
    hiddenimports=hidden_imports,
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=[
        'tkinter',
        'matplotlib',
        'numpy',
        'scipy',
        'pandas',
        'PIL',
        'PyQt5',
        'PyQt6',
        'PySide2',
        'PySide6',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=None)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name=name,
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=console,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=icon_file,
)
"""

        spec_file = self.project_root / "tabula-service.spec"
        with open(spec_file, "w", encoding="utf-8") as f:
            f.write(spec_content)

        print(f"Archivo de especificación creado: {spec_file}")
        return spec_file

    def create_launcher_script(self):
        """Crea un script launcher específico para el ejecutable."""
        launcher_content = '''#!/usr/bin/env python3
"""Launcher para el ejecutable compilado de Tabula Cloud Sync."""

import sys
import os
from pathlib import Path

# Detectar si estamos ejecutándose desde un ejecutable PyInstaller
if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
    # Ejecutándose desde PyInstaller
    application_path = Path(sys._MEIPASS)
    executable_dir = Path(sys.executable).parent
else:
    # Ejecutándose desde código fuente
    application_path = Path(__file__).parent
    executable_dir = application_path

# Agregar rutas al sys.path
sys.path.insert(0, str(application_path))

# Importar y ejecutar el módulo principal
if __name__ == "__main__":
    try:
        from __main__ import main
        main()
    except ImportError as e:
        print(f"Error importando módulo principal: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error ejecutando aplicación: {e}")
        sys.exit(1)
'''

        launcher_file = self.project_root / "launcher.py"
        with open(launcher_file, "w", encoding="utf-8") as f:
            f.write(launcher_content)

        return launcher_file

    def compile_executable(self):
        """Compila el ejecutable usando PyInstaller."""
        print("=== Compilando ejecutable ===")

        spec_file = self.create_spec_file()

        # Comando PyInstaller
        cmd = [
            sys.executable,
            "-m",
            "PyInstaller",
            "--clean",
            "--noconfirm",
            str(spec_file),
        ]

        print(f"Ejecutando: {' '.join(cmd)}")

        try:
            result = subprocess.run(
                cmd, check=True, capture_output=True, text=True
            )
            print("Compilación exitosa!")
            if result.stdout:
                print("STDOUT:", result.stdout)

        except subprocess.CalledProcessError as e:
            print(f"Error en compilación: {e}")
            if e.stdout:
                print("STDOUT:", e.stdout)
            if e.stderr:
                print("STDERR:", e.stderr)
            return False

        return True

    def create_installer(self):
        """Crea instaladores específicos para cada plataforma."""
        print("=== Creando instaladores ===")

        if self.system == "windows":
            self._create_windows_installer()
        elif self.system == "linux":
            self._create_linux_package()
        elif self.system == "darwin":
            self._create_macos_package()

    def _create_windows_installer(self):
        """Crea instalador para Windows usando NSIS."""
        print("Creando instalador para Windows...")

        # Crear script NSIS
        nsis_script = self.project_root / "installer.nsi"
        nsis_content = f"""
; Instalador NSIS para Tabula Cloud Sync Service

!define APP_NAME "Tabula Cloud Sync Service"
!define APP_VERSION "{self.version}"
!define APP_PUBLISHER "Tu Empresa"
!define APP_EXE "tabula-cloud-sync.exe"

OutFile "TabulaCloudSync-Setup.exe"
InstallDir "$PROGRAMFILES\\TabulaCloudSync"
RequestExecutionLevel admin

Page license
Page directory
Page instfiles

Section "Principal"
    SetOutPath $INSTDIR
    File "dist\\tabula-cloud-sync.exe"
    File "config.ini.template"
    
    ; Crear directorio de configuración
    CreateDirectory "$APPDATA\\TabulaCloudSync"
    CopyFiles "$INSTDIR\\config.ini.template" "$APPDATA\\TabulaCloudSync\\config.ini"
    
    ; Crear entradas en el registro
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\TabulaCloudSync" "DisplayName" "${APP_NAME}"
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\TabulaCloudSync" "UninstallString" "$INSTDIR\\uninstall.exe"
    
    ; Crear desinstalador
    WriteUninstaller "$INSTDIR\\uninstall.exe"
    
    ; Crear accesos directos
    CreateDirectory "$SMPROGRAMS\\${APP_NAME}"
    CreateShortCut "$SMPROGRAMS\\${APP_NAME}\\${APP_NAME}.lnk" "$INSTDIR\\${APP_EXE}"
    CreateShortCut "$SMPROGRAMS\\${APP_NAME}\\Uninstall.lnk" "$INSTDIR\\uninstall.exe"
SectionEnd

Section "Uninstall"
    Delete "$INSTDIR\\*.*"
    RMDir "$INSTDIR"
    Delete "$SMPROGRAMS\\${APP_NAME}\\*.*"
    RMDir "$SMPROGRAMS\\${APP_NAME}"
    DeleteRegKey HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\TabulaCloudSync"
SectionEnd
"""

        with open(nsis_script, "w", encoding="utf-8") as f:
            f.write(nsis_content)

        print(f"Script NSIS creado: {nsis_script}")
        print("Para crear el instalador, ejecute: makensis installer.nsi")

    def _create_linux_package(self):
        """Crea paquete DEB para Linux."""
        print("Creando paquete DEB para Linux...")

        # Crear estructura de paquete DEB
        package_dir = self.project_root / "package" / "tabula-cloud-sync"
        debian_dir = package_dir / "DEBIAN"
        usr_dir = package_dir / "usr"
        bin_dir = usr_dir / "bin"
        etc_dir = package_dir / "etc" / "tabula-cloud-sync"

        # Crear directorios
        for directory in [debian_dir, bin_dir, etc_dir]:
            directory.mkdir(parents=True, exist_ok=True)

        # Copiar ejecutable
        executable_src = self.dist_dir / "tabula-cloud-sync"
        if executable_src.exists():
            shutil.copy2(executable_src, bin_dir)
            os.chmod(bin_dir / "tabula-cloud-sync", 0o755)

        # Copiar configuración
        config_src = self.project_root / "config.ini.template"
        if config_src.exists():
            shutil.copy2(config_src, etc_dir / "config.ini")

        # Crear archivo control
        control_content = f"""Package: tabula-cloud-sync
Version: {self.version}
Section: utils
Priority: optional
Architecture: amd64
Depends:
Maintainer: Tu Empresa <contacto@tuempresa.com>
Description: Tabula Cloud Sync Service
 Servicio para sincronización automática con Tabula Cloud.
 Permite mantener sistemas locales sincronizados con la plataforma Tabula Cloud.
"""

        with open(debian_dir / "control", "w") as f:
            f.write(control_content)

        # Script post-instalación
        postinst_content = """#!/bin/bash
# Configurar permisos
chmod +x /usr/bin/tabula-cloud-sync

# Crear usuario de servicio si no existe
if ! id "tabula" &>/dev/null; then
    useradd -r -s /bin/false tabula
fi

# Configurar systemd si está disponible
if command -v systemctl &> /dev/null; then
    # El usuario debe configurar manualmente el servicio
    echo "Para instalar el servicio systemd, ejecute:"
    echo "sudo /usr/bin/tabula-cloud-sync install --config /etc/tabula-cloud-sync/config.ini"
fi
"""

        with open(debian_dir / "postinst", "w") as f:
            f.write(postinst_content)
        os.chmod(debian_dir / "postinst", 0o755)

        print(f"Paquete DEB creado en: {package_dir}")
        print(
            "Para construir el paquete, ejecute: dpkg-deb --build package/tabula-cloud-sync"
        )

    def _create_macos_package(self):
        """Crea paquete para macOS."""
        print("Creando bundle para macOS...")

        app_dir = self.dist_dir / "TabulaCloudSync.app"
        contents_dir = app_dir / "Contents"
        macos_dir = contents_dir / "MacOS"
        resources_dir = contents_dir / "Resources"

        # Crear estructura de app
        for directory in [macos_dir, resources_dir]:
            directory.mkdir(parents=True, exist_ok=True)

        # Copiar ejecutable
        executable_src = self.dist_dir / "tabula-cloud-sync"
        if executable_src.exists():
            shutil.copy2(executable_src, macos_dir / "TabulaCloudSync")
            os.chmod(macos_dir / "TabulaCloudSync", 0o755)

        # Crear Info.plist
        plist_content = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleExecutable</key>
    <string>TabulaCloudSync</string>
    <key>CFBundleIdentifier</key>
    <string>com.tuempresa.tabulacloudsync</string>
    <key>CFBundleName</key>
    <string>Tabula Cloud Sync</string>
    <key>CFBundleVersion</key>
    <string>{self.version}</string>
    <key>CFBundleShortVersionString</key>
    <string>{self.version}</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
</dict>
</plist>
"""

        with open(contents_dir / "Info.plist", "w") as f:
            f.write(plist_content)

        print(f"Bundle de macOS creado: {app_dir}")

    def verify_executable(self):
        """Verifica que el ejecutable funcione correctamente."""
        print("=== Verificando ejecutable ===")

        if self.system == "windows":
            executable = self.dist_dir / "tabula-cloud-sync.exe"
        else:
            executable = self.dist_dir / "tabula-cloud-sync"

        if not executable.exists():
            print(f"Error: Ejecutable no encontrado en {executable}")
            return False

        # Probar ejecución básica
        try:
            result = subprocess.run(
                [str(executable), "--help"],
                capture_output=True,
                text=True,
                timeout=10,
            )

            if result.returncode == 0:
                print("[OK] Ejecutable funciona correctamente")
                return True
            else:
                print(f"[ERROR] Error en ejecutable: {result.stderr}")
                return False

        except subprocess.TimeoutExpired:
            print("[ERROR] Timeout ejecutando el ejecutable")
            return False
        except Exception as e:
            print(f"[ERROR] Error verificando ejecutable: {e}")
            return False

    def create_distribution_package(self):
        """Crea paquete final de distribución."""
        print("=== Creando paquete de distribución ===")

        # Crear directorio de distribución
        release_dir = self.project_root / "release"
        if release_dir.exists():
            shutil.rmtree(release_dir)
        release_dir.mkdir()

        # Copiar ejecutable
        if self.system == "windows":
            executable_name = "tabula-cloud-sync.exe"
        else:
            executable_name = "tabula-cloud-sync"

        src_executable = self.dist_dir / executable_name
        if src_executable.exists():
            shutil.copy2(src_executable, release_dir)

        # Copiar archivos necesarios
        files_to_copy = [
            "config.ini.template",
            "README.md",
            "LICENSE",
            "CHANGELOG.md",
        ]

        for filename in files_to_copy:
            src_file = self.project_root / filename
            if src_file.exists():
                shutil.copy2(src_file, release_dir)

        # Copiar solo INSTALL.md para usuarios finales
        install_guide = self.project_root / "INSTALL.md"
        if install_guide.exists():
            shutil.copy2(install_guide, release_dir)

        # Crear archivo de instalación simple
        if self.system == "windows":
            install_script = "install-standalone.bat"
            install_content = """@echo off
echo === Instalador Standalone Tabula Cloud Sync ===
echo.

REM Verificar permisos de administrador
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo Error: Este script debe ejecutarse como administrador
    pause
    exit /b 1
)

REM Crear directorio de instalación
set INSTALL_DIR=%PROGRAMFILES%\\TabulaCloudSync
if not exist "%INSTALL_DIR%" mkdir "%INSTALL_DIR%"

REM Copiar ejecutable
copy tabula-cloud-sync.exe "%INSTALL_DIR%\\"

REM Crear directorio de configuración
set CONFIG_DIR=%PROGRAMDATA%\\TabulaCloudSync
if not exist "%CONFIG_DIR%" mkdir "%CONFIG_DIR%"

REM Copiar configuración si no existe
if not exist "%CONFIG_DIR%\\config.ini" (
    copy config.ini.template "%CONFIG_DIR%\\config.ini"
)

REM Agregar al PATH
setx PATH "%PATH%;%INSTALL_DIR%" /M

echo.
echo === Instalación completada ===
echo Ejecutable instalado en: %INSTALL_DIR%
echo Configuración en: %CONFIG_DIR%
echo.
echo Para instalar como servicio: tabula-cloud-sync install
echo Para ejecutar: tabula-cloud-sync --foreground
echo.
pause
"""
        else:
            install_script = "install-standalone.sh"
            install_content = """#!/bin/bash
echo "=== Instalador Standalone Tabula Cloud Sync ==="
echo

# Verificar permisos
if [ "$EUID" -ne 0 ]; then
    echo "Error: Este script debe ejecutarse como root (use sudo)"
    exit 1
fi

# Directorio de instalación
INSTALL_DIR="/usr/local/bin"
CONFIG_DIR="/etc/tabula-cloud-sync"

# Copiar ejecutable
cp tabula-cloud-sync "$INSTALL_DIR/"
chmod +x "$INSTALL_DIR/tabula-cloud-sync"

# Crear directorio de configuración
mkdir -p "$CONFIG_DIR"

# Copiar configuración si no existe
if [ ! -f "$CONFIG_DIR/config.ini" ]; then
    cp config.ini.template "$CONFIG_DIR/config.ini"
fi

echo
echo "=== Instalación completada ==="
echo "Ejecutable instalado en: $INSTALL_DIR"
echo "Configuración en: $CONFIG_DIR"
echo
echo "Para instalar como servicio: tabula-cloud-sync install"
echo "Para ejecutar: tabula-cloud-sync --foreground"
echo
"""

        with open(release_dir / install_script, "w") as f:
            f.write(install_content)

        if self.system != "windows":
            os.chmod(release_dir / install_script, 0o755)

        # Crear archivo README para la distribución
        readme_content = f"""# Tabula Cloud Sync Service - Distribución Standalone

Esta es la versión ejecutable standalone de Tabula Cloud Sync Service.

## Instalación Rápida

### Windows
1. Ejecutar como administrador: `{install_script}`
2. Configurar: `%PROGRAMDATA%\\TabulaCloudSync\\config.ini`
3. Instalar servicio: `tabula-cloud-sync install`

### Linux
1. Ejecutar como root: `sudo ./{install_script}`
2. Configurar: `/etc/tabula-cloud-sync/config.ini`
3. Instalar servicio: `sudo tabula-cloud-sync install`

## Uso Manual

```bash
# Ejecutar en primer plano (para pruebas)
./tabula-cloud-sync --foreground

# Instalar como servicio del sistema
./tabula-cloud-sync install

# Administrar servicio
./tabula-cloud-sync start|stop|restart|status
```

## Configuración

Edite el archivo `config.ini` con sus credenciales de Tabula Cloud:

- Token de autenticación
- URL de su instancia
- Configuraciones de base de datos
- Parámetros del servicio

## Documentación

Consulte el archivo `INSTALL.md` para la guía de instalación completa.

Para documentación técnica avanzada, visite:
https://github.com/ysidromdenis/template-sync-tabula-cloud/tree/main/docs

## Soporte

Para soporte técnico, consulte la documentación o contacte al administrador del sistema.
"""

        with open(release_dir / "README-STANDALONE.md", "w") as f:
            f.write(readme_content)

        # Crear archivo ZIP de la distribución
        import zipfile

        zip_name = f"tabula-cloud-sync-{self.system}-standalone.zip"
        zip_path = self.project_root / zip_name

        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
            for file_path in release_dir.rglob("*"):
                if file_path.is_file():
                    arcname = file_path.relative_to(release_dir)
                    zipf.write(file_path, arcname)

        print(f"[OK] Paquete de distribución creado: {zip_path}")
        print(f"[INFO] Contenido en: {release_dir}")

        return zip_path


def main():
    """Función principal del compilador."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Compilador de Tabula Cloud Sync Service"
    )
    parser.add_argument(
        "--no-installer", action="store_true", help="No crear instaladores"
    )
    parser.add_argument(
        "--verify-only",
        action="store_true",
        help="Solo verificar ejecutable existente",
    )
    parser.add_argument(
        "--clean", action="store_true", help="Limpiar build anterior"
    )

    args = parser.parse_args()

    compiler = ServiceCompiler()

    if args.clean:
        print("Limpiando builds anteriores...")
        if compiler.build_dir.exists():
            shutil.rmtree(compiler.build_dir)
        if compiler.dist_dir.exists():
            shutil.rmtree(compiler.dist_dir)
        print("Limpieza completada")
        return

    if args.verify_only:
        success = compiler.verify_executable()
        sys.exit(0 if success else 1)

    try:
        # Configurar entorno
        compiler.setup_environment()

        # Compilar ejecutable
        if not compiler.compile_executable():
            print("[ERROR] Error en compilación")
            sys.exit(1)

        # Verificar ejecutable
        if not compiler.verify_executable():
            print("[ERROR] Error en verificación")
            sys.exit(1)

        # Crear instaladores
        if not args.no_installer:
            compiler.create_installer()

        # Crear paquete de distribución
        package_path = compiler.create_distribution_package()

        print("\n[SUCCESS] ¡Compilación completada exitosamente!")
        print(f"[INFO] Paquete listo: {package_path}")
        print("\n[INFO] Próximos pasos:")
        print("1. Probar el ejecutable en sistemas sin Python")
        print("2. Distribuir el paquete ZIP")
        print("3. Documentar el proceso de instalación")

    except Exception as e:
        print(f"[ERROR] Error durante compilación: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
