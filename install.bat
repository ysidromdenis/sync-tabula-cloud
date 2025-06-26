@echo off
REM Script de instalación para Tabula Cloud Sync Service en Windows

echo === Instalador de Tabula Cloud Sync Service ===
echo.

REM Verificar si se está ejecutando como administrador
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo Error: Este script debe ejecutarse como administrador
    echo Haga clic derecho en el archivo y seleccione "Ejecutar como administrador"
    pause
    exit /b 1
)

REM Verificar Python
python --version >nul 2>&1
if %errorLevel% neq 0 (
    echo Error: Python no está instalado o no está en el PATH
    echo Por favor instale Python desde https://python.org
    pause
    exit /b 1
)

echo Python detectado:
python --version

REM Verificar pip
pip --version >nul 2>&1
if %errorLevel% neq 0 (
    echo Error: pip no está disponible
    pause
    exit /b 1
)

echo.
echo Instalando paquete Python...
pip install -e .

if %errorLevel% neq 0 (
    echo Error: Fallo la instalación del paquete
    pause
    exit /b 1
)

REM Instalar dependencias de Windows
echo.
echo Instalando dependencias de Windows...
pip install pywin32

if %errorLevel% neq 0 (
    echo Advertencia: No se pudieron instalar las dependencias de Windows
    echo El servicio de Windows puede no funcionar correctamente
)

REM Crear directorio de configuración
set CONFIG_DIR=%PROGRAMDATA%\TabulaCloudSync
if not exist "%CONFIG_DIR%" (
    echo Creando directorio de configuración...
    mkdir "%CONFIG_DIR%"
)

REM Copiar template de configuración
if not exist "%CONFIG_DIR%\config.ini" (
    echo Copiando template de configuración...
    copy config.ini.template "%CONFIG_DIR%\config.ini"
    echo IMPORTANTE: Edite %CONFIG_DIR%\config.ini con su configuración
)

REM Crear directorio de logs
set LOG_DIR=%PROGRAMDATA%\TabulaCloudSync\logs
if not exist "%LOG_DIR%" (
    echo Creando directorio de logs...
    mkdir "%LOG_DIR%"
)

echo.
set /p response=¿Desea instalar el servicio de Windows? (y/n): 
if /i "%response%"=="y" (
    echo Instalando servicio de Windows...
    python -m service.manager install --config "%CONFIG_DIR%\config.ini"
    
    if %errorLevel% equ 0 (
        echo Servicio instalado correctamente
        echo Para iniciarlo: net start TabulaCloudSync
        echo O use el Administrador de Servicios (services.msc)
    ) else (
        echo Error: No se pudo instalar el servicio
    )
)

echo.
echo === Instalación completada ===
echo.
echo Próximos pasos:
echo 1. Configurar el archivo %CONFIG_DIR%\config.ini con sus credenciales
echo 2. Iniciar el servicio desde el Administrador de Servicios o con:
echo    net start TabulaCloudSync
echo.
echo Para más información, consulte la documentación en docs\
echo.
pause
