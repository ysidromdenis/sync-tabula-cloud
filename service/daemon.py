"""Daemon para Linux de Tabula Cloud Sync."""

import atexit
import os
import signal
import sys
import time

from .base_service import TabulaCloudService


class TabulaCloudDaemon(TabulaCloudService):
    """Daemon para sistemas Linux/Unix."""

    def __init__(
        self,
        pidfile: str = "/var/run/tabula_cloud.pid",
        config_file: str = "config.ini",
    ):
        """
        Inicializa el daemon.

        Args:
            pidfile: Archivo donde se almacena el PID del proceso
            config_file: Archivo de configuración
        """
        super().__init__(config_file)
        self.pidfile = pidfile

    def daemonize(self) -> None:
        """Convierte el proceso en un daemon."""
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
        sys.stdout.flush()
        sys.stderr.flush()
        si = open(os.devnull, "r")
        so = open(os.devnull, "a+")
        se = open(os.devnull, "a+")

        os.dup2(si.fileno(), sys.stdin.fileno())
        os.dup2(so.fileno(), sys.stdout.fileno())
        os.dup2(se.fileno(), sys.stderr.fileno())

        # Escribir pidfile
        atexit.register(self.delpid)
        pid = str(os.getpid())
        with open(self.pidfile, "w+") as f:
            f.write(pid + "\n")

    def delpid(self) -> None:
        """Elimina el archivo PID."""
        if os.path.exists(self.pidfile):
            os.remove(self.pidfile)

    def start(self) -> None:
        """Inicia el daemon."""
        # Verificar si el daemon ya está ejecutándose
        try:
            with open(self.pidfile, "r") as pf:
                pid = int(pf.read().strip())
        except IOError:
            pid = None

        if pid:
            try:
                os.kill(pid, 0)
                message = f"El daemon ya está ejecutándose con PID {pid}\n"
                sys.stderr.write(message)
                return
            except OSError:
                # El proceso no existe, eliminar el pidfile obsoleto
                self.delpid()

        # Iniciar el daemon
        self.daemonize()
        self.run()

    def stop(self) -> None:
        """Detiene el daemon."""
        # Obtener el PID del pidfile
        try:
            with open(self.pidfile, "r") as pf:
                pid = int(pf.read().strip())
        except IOError:
            pid = None

        if not pid:
            message = "El daemon no está ejecutándose\n"
            sys.stderr.write(message)
            return

        # Intentar terminar el proceso
        try:
            while True:
                os.kill(pid, signal.SIGTERM)
                time.sleep(0.1)
        except OSError as err:
            e = str(err.args)
            if e.find("No such process") > 0:
                self.delpid()
            else:
                print(str(err.args))
                sys.exit(1)

    def restart(self) -> None:
        """Reinicia el daemon."""
        self.stop()
        time.sleep(1)
        self.start()

    def status(self) -> None:
        """Muestra el estado del daemon."""
        try:
            with open(self.pidfile, "r") as pf:
                pid = int(pf.read().strip())

            try:
                os.kill(pid, 0)
                print(f"El daemon está ejecutándose con PID {pid}")

                # Mostrar información adicional del servicio
                status_info = self.get_status()
                for key, value in status_info.items():
                    print(f"  {key}: {value}")

            except OSError:
                print("El daemon no está ejecutándose (archivo PID obsoleto)")
                self.delpid()

        except IOError:
            print("El daemon no está ejecutándose")

    def run(self) -> None:
        """Ejecuta el daemon."""
        # Configurar manejadores de señales
        signal.signal(signal.SIGTERM, self._signal_handler)
        signal.signal(signal.SIGINT, self._signal_handler)

        try:
            self.start_service()

            # Mantener el daemon ejecutándose
            while self.running:
                time.sleep(1)

        except Exception as e:
            self.logger.error(f"Error en el daemon: {e}")
        finally:
            self.stop_service()

    def _signal_handler(self, signum, frame) -> None:
        """Manejador de señales para terminación limpia."""
        self.logger.info(f"Recibida señal {signum}, terminando...")
        self.stop_service()

    def perform_sync(self) -> None:
        """
        Implementación por defecto de sincronización.
        Las clases derivadas pueden sobrescribir este método.
        """
        # Ejemplo básico de sincronización
        if self.session:
            try:
                # Aquí irían las operaciones de sincronización específicas
                self.logger.info("Realizando sincronización...")

                # Marcar tiempo de última sincronización
                import datetime

                self._last_sync = datetime.datetime.now().isoformat()

            except Exception as e:
                self.logger.error(f"Error en sincronización: {e}")
        else:
            self.logger.warning(
                "Sesión no inicializada, omitiendo sincronización"
            )
