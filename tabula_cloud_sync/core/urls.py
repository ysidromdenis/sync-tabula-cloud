import configparser
from pathlib import Path

from ..utils.directories import get_appropriate_config_path

# Buscar archivo de configuración en ubicaciones apropiadas
config_path = get_appropriate_config_path()
config = configparser.ConfigParser()

# Intentar leer configuración desde varias ubicaciones
if config_path.exists():
    config.read(str(config_path))
else:
    # También intentar tabula_config.ini en directorio actual para compatibilidad
    current_config = Path.cwd() / "tabula_config.ini"
    if current_config.exists():
        config.read(str(current_config))
    else:
        # También intentar en el directorio config/
        config_dir_config = Path.cwd() / "config" / "tabula_config.ini"
        if config_dir_config.exists():
            config.read(str(config_dir_config))
        else:
            # También intentar en el directorio examples/ (fallback legacy)
            examples_config = Path.cwd() / "examples" / "tabula_config.ini"
            if examples_config.exists():
                config.read(str(examples_config))

# Obtener la configuración de la API
try:
    # Leer desde la sección [API] (estructura actual)
    base_url = config.get("API", "base_url", fallback="")

    if base_url:
        # Extraer protocolo y URL base de base_url
        if base_url.startswith("https://"):
            PROTOCOLO = "https"
            URL_BASE = base_url.replace("https://", "")
        elif base_url.startswith("http://"):
            PROTOCOLO = "http"
            URL_BASE = base_url.replace("http://", "")
        else:
            # Si no tiene protocolo, asumir https y usar toda la URL
            PROTOCOLO = "https"
            URL_BASE = base_url
    else:
        # Fallback: intentar obtener desde sección [sincronizador] (legacy)
        PROTOCOLO = config.get("sincronizador", "protocolo", fallback="https")
        URL_BASE = config.get("sincronizador", "url", fallback="")

        # También soportar la configuración alternativa (por si usa 'ssl')
        ssl_enabled = config.getboolean("sincronizador", "ssl", fallback=True)
        if ssl_enabled and PROTOCOLO == "http":
            PROTOCOLO = "https"

except (configparser.NoSectionError, configparser.NoOptionError):
    # Valores por defecto si no existe la configuración
    PROTOCOLO = "https"
    URL_BASE = ""

ITEM_SECUENCIA = "api/items/v1/items/secuencia/{secuencia}/"
ITEM_ID = "api/items/v1/items/{id}/"
ITEM = "api/items/v1/items/"

CONTACTO = "api/contacts/v1/contacts/"
CONTACTO_ID = "api/contacts/v1/contacts/{id}/"
CONTACTO_BUSCAR = "api/contacts/v1/buscar/{documento}/"
CONTACTO_BUSCAR_SET = "api/contacts/v1/buscarset/{documento}/"

DOCUMENTO = "api/documents/v1/documentos/"
DOCUMENTO_VERIFICAR_ESTADO = (
    "api/documents/v1/documentos/{referencia}/verificar-estado-de/"
)
DOCUMENTO_REGENERAR_XML = (
    "api/documents/v1/documentos/{referencia}/regenerar-xml/"
)
GENERAR_LOTES_DE = "api/sifen/generar-lote/"

# Configurar puerto basado en el protocolo o configuración específica
try:
    # Intentar obtener puerto desde configuración [API] o [sincronizador]
    PORT = config.get("API", "port", fallback=None)
    if PORT is None:
        PORT = config.get("sincronizador", "puerto", fallback=None)

    if PORT is None:
        # Si no se especifica puerto, usar el estándar según protocolo
        PORT = "443" if PROTOCOLO == "https" else "80"
    else:
        PORT = str(PORT)  # Asegurar que sea string

except (configparser.NoSectionError, configparser.NoOptionError):
    PORT = "443" if PROTOCOLO == "https" else "80"

LOGIN = "api/accounts/v1/login/"
LOGOUT = "api/accounts/v1/logout/"

USER_COMPANIES = "api/companies/v1/user_companies/"
MENU_COMPANIES = "api/settings/v1/menu_companies/"
MENU_FORMULARIOS = "api/base/v1/menu_items/formularios/"

# Configuraciones de Timbrados
TIMBRADO = "api/settings/v1/timbrados/"
TIMBRADO_ID = "api/settings/v1/timbrados/{id}/"

TIMBRADO_PE = "api/settings/v1/timbrado-establecimientos/"
TIMBRADO_PE_ID = "api/settings/v1/timbrado-establecimientos/{id}/"

# Configuracion de unidades de medidas
MEDIDA = "api/base/v1/medidas/"
MEDIDA_ID = "api/base/v1/medidas/{id}/"

MEDIDA_CONFIG = "api/settings/v1/medida-config/"
MEDIDA_CONFIG_ID = "api/settings/v1/medida-config/{id}/"

# Configuracion de monedas
CURRENCY_CONF = "api/settings/v1/currency-config/"
CURRENCY_CONF_ID = "api/settings/v1/currency-config/{id}/"

CURRENCY = "api/base/v1/currencies/"
CURRENCY_ID = "api/base/v1/currencies/{id}/"
