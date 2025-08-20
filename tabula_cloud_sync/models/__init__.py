"""Modelos base para Tabula Cloud Sync."""

from .documentos import (
    BaseModel,
    Documento,
    DocumentoAsociado,
    DocumentoDetalle,
)
from .remisiones import (
    CargaGeneral,
    DocumentoDetalleRemision,
    Remision,
    TransporteDireccionLlegada,
    TransporteDireccionSalida,
    TransporteMercaderia,
    VehiculoTraslado,
)

__version__ = "1.0.0"
__all__ = [
    "BaseModel",
    "Documento",
    "DocumentoAsociado",
    "DocumentoDetalle",
    "CargaGeneral",
    "DocumentoDetalleRemision",
    "Remision",
    "TransporteDireccionLlegada",
    "TransporteDireccionSalida",
    "TransporteMercaderia",
    "VehiculoTraslado",
]
