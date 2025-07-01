import logging.config
import os
from logging.handlers import RotatingFileHandler

# Verificar si la carpeta 'logs' existe, y crearla si no es así
log_directory = "logs"
if not os.path.exists(log_directory):
    os.makedirs(log_directory)


LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "file": {
            "level": "INFO",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": os.path.join(log_directory, "servicio.log"),
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
