"""
Daemon mejorado para Tabula Cloud Sync.

Proporciona funcionalidad de daemon multiplataforma con gestión avanzada
de procesos, señales, y monitoreo de estado.
"""

import atexit
import os
import platform
import signal
import sys
import time
from pathlib import Path
from typing import Any, Dict, Optional, Type

from ..utils.commons import ensure_directory, is_windows
from .base_service import TabulaCloudService


class TabulaCloudDaemon:
    """
    Daemon multiplataforma para servicios de Tabula Cloud.

    Soporta Linux/Unix como daemon tradicional y Windows como servicio.
    """

    def __init__(
        self,
        service_class: Type[TabulaCloudService],
        pidfile: str = None,
        config_file: str = "config/tabula_config.ini",
        name: str = None,
    ):
        """
        Inicializa el daemon.

        Args:
            service_class: Clase del servicio a ejecutar como daemon
            pidfile: Archivo donde se almacena el PID del proceso
            config_file: Archivo de configuración
            name: Nombre del daemon (por defecto usa el nombre de la clase)
        """
        self.service_class = service_class
        self.config_file = config_file
        self.service_instance = None
        self.name = name or service_class.__name__

        # Configurar archivo PID según el sistema operativo
        if pidfile:
            self.pidfile = pidfile
        elif is_windows():
            self.pidfile = f"C:\\temp\\{self.name.lower()}_daemon.pid"
        else:
            self.pidfile = f"/tmp/{self.name.lower()}_daemon.pid"

        # Asegurar que el directorio del pidfile existe
        pidfile_dir = Path(self.pidfile).parent
        ensure_directory(str(pidfile_dir))

    def daemonize(self) -> None:
        """Convierte el proceso en un daemon (solo Linux/Unix)."""
        if is_windows():
            # En Windows, simplemente crear el proceso en background
            self._create_pidfile()
            return

        try:
            # Primera bifurcación
            pid = os.fork()
            if pid > 0:
                # Terminar el proceso padre
                sys.exit(0)
        except OSError as e:
            sys.stderr.write(f"fork #1 falló: {e.errno} ({e.strerror})\n")
            sys.exit(1)

        # Desacoplar del entorno padre
        os.chdir("/")
        os.setsid()
        os.umask(0)

        # Segunda bifurcación
        try:
            pid = os.fork()
            if pid > 0:
                # Terminar el segundo proceso padre
                sys.exit(0)
        except OSError as e:
            sys.stderr.write(f"fork #2 falló: {e.errno} ({e.strerror})\n")
            sys.exit(1)

        # Redirigir flujos estándar
        self._redirect_standard_streams()

        # Escribir pidfile
        self._create_pidfile()

    def _redirect_standard_streams(self) -> None:
        """Redirige los flujos estándar para el daemon."""
        sys.stdout.flush()
        sys.stderr.flush()

        # Redirigir a logs en lugar de /dev/null
        log_dir = Path("logs")
        ensure_directory(str(log_dir))

        stdin_redirect = "/dev/null" if not is_windows() else "nul"
        stdout_log = log_dir / f"{self.name.lower()}_stdout.log"
        stderr_log = log_dir / f"{self.name.lower()}_stderr.log"

        si = open(stdin_redirect, "r")
        so = open(stdout_log, "a+")
        se = open(stderr_log, "a+")

        os.dup2(si.fileno(), sys.stdin.fileno())
        os.dup2(so.fileno(), sys.stdout.fileno())
        os.dup2(se.fileno(), sys.stderr.fileno())

    def _create_pidfile(self) -> None:
        """Crea el archivo PID."""
        atexit.register(self.delpid)
        pid = str(os.getpid())
        with open(self.pidfile, "w+") as f:
            f.write(f"{pid}\n")
            f.write(f"name={self.name}\n")
            f.write(f"class={self.service_class.__name__}\n")
            f.write(f"config={self.config_file}\n")

    def delpid(self) -> None:
        """Elimina el archivo PID."""
        if os.path.exists(self.pidfile):
            try:
                os.remove(self.pidfile)
            except OSError:
                pass

    def _get_pid_info(self) -> Optional[Dict[str, str]]:
        """Lee información del archivo PID."""
        try:
            with open(self.pidfile, "r") as pf:
                lines = pf.read().strip().split("\n")

                info = {"pid": lines[0]}
                for line in lines[1:]:
                    if "=" in line:
                        key, value = line.split("=", 1)
                        info[key] = value

                return info
        except (IOError, IndexError, ValueError):
            return None

    def _is_running(self, pid: int) -> bool:
        """Verifica si un proceso está ejecutándose."""
        try:
            if is_windows():
                import subprocess

                result = subprocess.run(
                    ["tasklist", "/FI", f"PID eq {pid}"],
                    capture_output=True,
                    text=True,
                )
                return str(pid) in result.stdout
            else:
                os.kill(pid, 0)
                return True
        except (OSError, subprocess.SubprocessError):
            return False

    def start(self) -> None:
        """Inicia el daemon."""
        print(f"Iniciando daemon {self.name}...")

        # Verificar si el daemon ya está ejecutándose
        pid_info = self._get_pid_info()

        if pid_info:
            pid = int(pid_info["pid"])
            if self._is_running(pid):
                print(f"El daemon ya está ejecutándose con PID {pid}")
                return
            else:
                # El proceso no existe, eliminar el pidfile obsoleto
                print("Eliminando archivo PID obsoleto...")
                self.delpid()

        # Iniciar el daemon
        self.daemonize()
        self.run()

    def stop(self) -> None:
        """Detiene el daemon."""
        print(f"Deteniendo daemon {self.name}...")

        # Obtener información del PID
        pid_info = self._get_pid_info()

        if not pid_info:
            print("El daemon no está ejecutándose")
            return

        pid = int(pid_info["pid"])

        if not self._is_running(pid):
            print("El daemon no está ejecutándose (archivo PID obsoleto)")
            self.delpid()
            return

        # Intentar terminar el proceso
        try:
            if is_windows():
                import subprocess

                subprocess.run(["taskkill", "/F", "/PID", str(pid)], check=True)
            else:
                # Intentar terminación elegante primero
                os.kill(pid, signal.SIGTERM)

                # Esperar un poco para terminación elegante
                for _ in range(50):  # 5 segundos
                    if not self._is_running(pid):
                        break
                    time.sleep(0.1)

                # Si aún está ejecutándose, forzar terminación
                if self._is_running(pid):
                    print("Forzando terminación...")
                    os.kill(pid, signal.SIGKILL)

            print(f"Daemon {self.name} detenido")
            self.delpid()

        except (OSError, subprocess.SubprocessError) as e:
            print(f"Error deteniendo daemon: {e}")
            sys.exit(1)

    def restart(self) -> None:
        """Reinicia el daemon."""
        print(f"Reiniciando daemon {self.name}...")
        self.stop()
        time.sleep(2)
        self.start()

    def status(self) -> None:
        """Muestra el estado del daemon."""
        pid_info = self._get_pid_info()

        if not pid_info:
            print(f"Daemon {self.name} no está ejecutándose")
            return

        pid = int(pid_info["pid"])

        if self._is_running(pid):
            print(f"Daemon {self.name} está ejecutándose:")
            print(f"  PID: {pid}")
            print(f"  Clase de servicio: {pid_info.get('class', 'Desconocida')}")
            print(
                f"  Archivo de configuración: {pid_info.get('config', 'Desconocido')}"
            )

            # Intentar obtener estado del servicio si es posible
            try:
                if self.service_instance:
                    status_info = self.service_instance.get_status()
                    print(f"  Estado del servicio:")
                    for key, value in status_info.items():
                        print(f"    {key}: {value}")
            except Exception:
                print("  Estado del servicio: No disponible")

        else:
            print(f"Daemon {self.name} no está ejecutándose (archivo PID obsoleto)")
            self.delpid()

    def run(self) -> None:
        """Ejecuta el daemon."""
        # Configurar manejadores de señales (solo en Unix)
        if not is_windows():
            signal.signal(signal.SIGTERM, self._signal_handler)
            signal.signal(signal.SIGINT, self._signal_handler)
            signal.signal(signal.SIGHUP, self._reload_handler)

        try:
            # Crear e inicializar la instancia del servicio
            self.service_instance = self.service_class(self.config_file)
            self.service_instance.start()

            print(f"Daemon {self.name} iniciado exitosamente")

            # Mantener el daemon ejecutándose
            while self.service_instance.running:
                time.sleep(1)

        except Exception as e:
            print(f"Error en el daemon: {e}")
            if self.service_instance:
                self.service_instance.logger.error(f"Error crítico en daemon: {e}")
        finally:
            if self.service_instance:
                self.service_instance.stop()

    def _signal_handler(self, signum, frame) -> None:
        """Manejador de señales para terminación limpia."""
        if self.service_instance:
            self.service_instance.logger.info(f"Recibida señal {signum}, terminando...")
            self.service_instance.stop()

    def _reload_handler(self, signum, frame) -> None:
        """Manejador de señal para recargar configuración."""
        if self.service_instance:
            self.service_instance.logger.info(
                "Recibida señal SIGHUP, recargando configuración..."
            )
            try:
                self.service_instance.reload_config()
            except Exception as e:
                self.service_instance.logger.error(
                    f"Error recargando configuración: {e}"
                )

    def get_service_instance(self) -> Optional[TabulaCloudService]:
        """Retorna la instancia del servicio (solo si está ejecutándose)."""
        return self.service_instance
