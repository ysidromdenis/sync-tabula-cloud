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
    # También intentar config.ini en directorio actual para compatibilidad
    current_config = Path.cwd() / "tabula_config.ini"
    if current_config.exists():
        config.read(str(current_config))

# Obtener la configuración de MySQL
# configuracion = config.get("sincronizador", "")

PROTOCOLO = "http"
# URL_BASE = configuracion.get("url")
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

PORT = "80"

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
