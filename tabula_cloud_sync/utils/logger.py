import logging.config

from .directories import get_appropriate_log_dir

# Obtener directorio de logs apropiado usando platformdirs
log_directory = get_appropriate_log_dir()

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "file": {
            "level": "INFO",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": str(log_directory / "servicio.log"),
            "maxBytes": 10 * 1024 * 1024,
            "backupCount": 10,
            "encoding": "utf-8",
            "formatter": "standard",
        },
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "standard",
            "stream": "ext://sys.stdout",  # Usar la salida estándar (consola)
        },
    },
    "formatters": {
        "standard": {
            "format": "%(asctime)s:%(levelname)s:%(message)s",
        },
    },
    "loggers": {
        "": {  # root logger
            "handlers": ["file", "console"],
            "level": "DEBUG",
            "propagate": True,
        },
    },
}

logging.config.dictConfig(LOGGING_CONFIG)
