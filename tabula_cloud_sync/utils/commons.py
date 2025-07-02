import hashlib
import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, Optional, Union


def ensure_directory(path: Union[str, Path]) -> Path:
    """
    Asegura que un directorio existe, creándolo si es necesario.

    Args:
        path: Ruta del directorio

    Returns:
        Path object del directorio
    """
    dir_path = Path(path)
    dir_path.mkdir(parents=True, exist_ok=True)
    return dir_path


def safe_read_file(
    file_path: Union[str, Path], encoding: str = "utf-8"
) -> Optional[str]:
    """
    Lee un archivo de forma segura.

    Args:
        file_path: Ruta del archivo
        encoding: Codificación del archivo

    Returns:
        Contenido del archivo o None si hay error
    """
    try:
        with open(file_path, "r", encoding=encoding) as f:
            return f.read()
    except (FileNotFoundError, PermissionError, UnicodeDecodeError):
        return None


def safe_write_file(
    file_path: Union[str, Path], content: str, encoding: str = "utf-8"
) -> bool:
    """
    Escribe un archivo de forma segura.

    Args:
        file_path: Ruta del archivo
        content: Contenido a escribir
        encoding: Codificación del archivo

    Returns:
        True si se escribió correctamente, False en caso contrario
    """
    try:
        path = Path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)

        with open(path, "w", encoding=encoding) as f:
            f.write(content)
        return True
    except (PermissionError, OSError):
        return False


def load_json_file(file_path: Union[str, Path]) -> Optional[Dict[str, Any]]:
    """
    Carga un archivo JSON de forma segura.

    Args:
        file_path: Ruta del archivo JSON

    Returns:
        Diccionario con el contenido o None si hay error
    """
    content = safe_read_file(file_path)
    if content:
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            pass
    return None


def get_file_hash(
    file_path: Union[str, Path], algorithm: str = "md5"
) -> Optional[str]:
    """
    Calcula el hash de un archivo.

    Args:
        file_path: Ruta del archivo
        algorithm: Algoritmo de hash (md5, sha1, sha256)

    Returns:
        Hash del archivo o None si hay error
    """
    try:
        hash_obj = hashlib.new(algorithm)
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_obj.update(chunk)
        return hash_obj.hexdigest()
    except (FileNotFoundError, ValueError):
        return None


def is_valid_python_identifier(name: str) -> bool:
    """
    Verifica si un string es un identificador Python válido.

    Args:
        name: Nombre a verificar

    Returns:
        True si es válido
    """
    return name.isidentifier() and not name.startswith("__")


def sanitize_filename(filename: str) -> str:
    """
    Sanitiza un nombre de archivo removiendo caracteres no válidos.

    Args:
        filename: Nombre original del archivo

    Returns:
        Nombre sanitizado
    """
    # Caracteres no permitidos en nombres de archivo
    invalid_chars = '<>:"/\\|?*'

    # Reemplazar caracteres inválidos
    sanitized = filename
    for char in invalid_chars:
        sanitized = sanitized.replace(char, "_")

    # Remover espacios múltiples y al inicio/final
    sanitized = " ".join(sanitized.split())

    # Limitar longitud
    if len(sanitized) > 255:
        sanitized = sanitized[:255]

    return sanitized


def merge_dict_deep(
    dict1: Dict[str, Any], dict2: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Hace un merge profundo de dos diccionarios.

    Args:
        dict1: Diccionario base
        dict2: Diccionario a fusionar

    Returns:
        Diccionario fusionado
    """
    result = dict1.copy()

    for key, value in dict2.items():
        if (
            key in result
            and isinstance(result[key], dict)
            and isinstance(value, dict)
        ):
            result[key] = merge_dict_deep(result[key], value)
        else:
            result[key] = value

    return result


def find_python_executable() -> Optional[str]:
    """
    Encuentra el ejecutable de Python actual.

    Returns:
        Ruta del ejecutable de Python
    """
    return sys.executable


def get_package_version(package_name: str) -> Optional[str]:
    """
    Obtiene la versión de un paquete instalado.

    Args:
        package_name: Nombre del paquete

    Returns:
        Versión del paquete o None si no está instalado
    """
    try:
        import pkg_resources

        return pkg_resources.get_distribution(package_name).version
    except (pkg_resources.DistributionNotFound, ImportError):
        return None


def is_windows() -> bool:
    """Verifica si está ejecutándose en Windows."""
    return os.name == "nt"


def is_linux() -> bool:
    """Verifica si está ejecutándose en Linux."""
    return os.name == "posix" and sys.platform.startswith("linux")


def is_macos() -> bool:
    """Verifica si está ejecutándose en macOS."""
    return os.name == "posix" and sys.platform == "darwin"


def get_system_info() -> Dict[str, str]:
    """
    Obtiene información del sistema.

    Returns:
        Diccionario con información del sistema
    """
    import platform

    return {
        "os": os.name,
        "platform": sys.platform,
        "architecture": platform.machine(),
        "python_version": sys.version,
        "python_executable": sys.executable,
        "system": platform.system(),
        "release": platform.release(),
        "version": platform.version(),
    }


# Funcionalidades comunes del sistema
def get_dv(numero: str):
    """
    Obtener Digito Verificador del documento
    """
    basemax = 11
    v_numero_al = ""
    k = 2
    v_total = 0
    for x in range(
        len(numero)
    ):  # Cambia la ultima letra por ascii en caso que la cedula termine en letra
        v_caracter = str(numero[x]).upper()
        if not (ord(v_caracter) >= 48 and ord(v_caracter) <= 57):
            v_numero_al = v_numero_al + str(ord(v_caracter))
        else:
            v_numero_al = v_numero_al + v_caracter
    for x in reversed(v_numero_al):
        if k > basemax:
            k = 2
        v_numero_aux = int(x)
        v_total += v_numero_aux * k
        k += 1
    v_resto = v_total % 11
    if v_resto > 1:
        v_digit = 11 - v_resto
    else:
        v_digit = 0
    return v_digit


def validar_gtin(gtin) -> bool:
    """Valida códigos GTIN-8, GTIN-12, GTIN-13 y GTIN-14."""
    # Verificar si el GTIN contiene solo dígitos y tiene una longitud válida
    if not gtin.isdigit() or len(gtin) not in [8, 12, 13, 14]:
        return False

    # Convertir el GTIN en una lista de enteros para facilitar el manejo
    digitos = [int(d) for d in gtin]

    # Inicializar la suma total
    suma_total = 0

    # La lógica de ponderación varía según la longitud del GTIN
    # Para GTIN-8, la ponderación comienza con 3 en la posición más a la izquierda
    # Para GTIN-12, GTIN-13, y GTIN-14, comienza con 1
    ponderacion = 3 if len(gtin) == 8 else 1

    # Recorrer todos los dígitos excepto el último (dígito de control)
    for i in range(len(digitos) - 1):
        suma_total += digitos[i] * ponderacion
        # Alternar la ponderación
        ponderacion = 4 - ponderacion  # Esto alternará entre 3 y 1

    # Calcular el dígito de control
    digito_control_calculado = (10 - suma_total % 10) % 10

    # Verificar si el dígito de control calculado coincide con el último dígito del GTIN
    return digito_control_calculado == digitos[-1]


# Funcion de redondeo
def round_ext(num, decimales=0):
    factor = 10**decimales
    entero = int(num * factor)
    decimal = num * factor - entero
    if decimal >= 0.5:
        redondeado = (entero + 1) / factor
    else:
        redondeado = entero / factor
    return redondeado
