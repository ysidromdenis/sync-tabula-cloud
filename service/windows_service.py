"""Servicio para Windows de Tabula Cloud Sync."""

import os
import sys

try:
    import socket

    import servicemanager
    import win32event
    import win32service
    import win32serviceutil

    WINDOWS_AVAILABLE = True
except ImportError:
    WINDOWS_AVAILABLE = False

from .base_service import TabulaCloudService

if WINDOWS_AVAILABLE:

    class TabulaCloudWindowsService(win32serviceutil.ServiceFramework):
        """Servicio de Windows para Tabula Cloud Sync."""

        _svc_name_ = "TabulaCloudSync"
        _svc_display_name_ = "Tabula Cloud Sync Service"
        _svc_description_ = "Servicio de sincronización con Tabula Cloud"

        def __init__(self, args):
            """Inicializa el servicio de Windows."""
            win32serviceutil.ServiceFramework.__init__(self, args)
            self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
            socket.setdefaulttimeout(60)
            self.tabula_service = None

        def SvcStop(self):
            """Detiene el servicio."""
            self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
            win32event.SetEvent(self.hWaitStop)

            if self.tabula_service:
                self.tabula_service.stop_service()

        def SvcDoRun(self):
            """Ejecuta el servicio."""
            servicemanager.LogMsg(
                servicemanager.EVENTLOG_INFORMATION_TYPE,
                servicemanager.PYS_SERVICE_STARTED,
                (self._svc_name_, ""),
            )

            try:
                # Crear instancia del servicio
                config_file = os.path.join(
                    os.path.dirname(__file__), "..", "config.ini"
                )
                self.tabula_service = WindowsTabulaService(config_file)
                self.tabula_service.start_service()

                # Esperar hasta que se solicite la detención
                win32event.WaitForSingleObject(self.hWaitStop, win32event.INFINITE)

            except Exception as e:
                servicemanager.LogErrorMsg(f"Error en el servicio: {str(e)}")

        @staticmethod
        def install_service():
            """Instala el servicio en Windows."""
            try:
                win32serviceutil.InstallService(
                    TabulaCloudWindowsService._svc_name_,
                    TabulaCloudWindowsService._svc_display_name_,
                    startType=win32service.SERVICE_AUTO_START,
                    description=TabulaCloudWindowsService._svc_description_,
                )
                print("Servicio instalado correctamente")
            except Exception as e:
                print(f"Error al instalar el servicio: {e}")

        @staticmethod
        def remove_service():
            """Desinstala el servicio de Windows."""
            try:
                win32serviceutil.RemoveService(TabulaCloudWindowsService._svc_name_)
                print("Servicio desinstalado correctamente")
            except Exception as e:
                print(f"Error al desinstalar el servicio: {e}")

    class WindowsTabulaService(TabulaCloudService):
        """Implementación específica para Windows."""

        def perform_sync(self):
            """
            Implementación de sincronización para Windows.
            Las clases derivadas pueden sobrescribir este método.
            """
            if self.session:
                try:
                    # Aquí irían las operaciones de sincronización específicas
                    self.logger.info("Realizando sincronización en Windows...")

                    # Marcar tiempo de última sincronización
                    import datetime

                    self._last_sync = datetime.datetime.now().isoformat()

                except Exception as e:
                    self.logger.error(f"Error en sincronización: {e}")
            else:
                self.logger.warning("Sesión no inicializada, omitiendo sincronización")

else:

    class TabulaCloudWindowsService:
        """Stub para cuando las librerías de Windows no están disponibles."""

        def __init__(self, *args, **kwargs):
            raise ImportError(
                "Las librerías de Windows no están disponibles. "
                "Instale pywin32 para usar el servicio de Windows."
            )

        @staticmethod
        def install_service():
            raise ImportError("pywin32 no disponible")

        @staticmethod
        def remove_service():
            raise ImportError("pywin32 no disponible")


def main():
    """Función principal para manejar argumentos de línea de comandos."""
    if not WINDOWS_AVAILABLE:
        print("Este módulo requiere pywin32 para funcionar en Windows")
        sys.exit(1)

    if len(sys.argv) == 1:
        servicemanager.Initialize()
        servicemanager.PrepareToHostSingle(TabulaCloudWindowsService)
        servicemanager.StartServiceCtrlDispatcher()
    else:
        win32serviceutil.HandleCommandLine(TabulaCloudWindowsService)


if __name__ == "__main__":
    main()
