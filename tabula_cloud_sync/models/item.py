from datetime import datetime
from typing import Annotated, Optional, Union
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, PositiveInt
from tabula_enums.documents import ItemTipoListNombreEnum
from tabula_enums.form import SituacionEnum
from tabula_enums.impuestos import TipoRentaEnum

from .base import ActividadEconomica
from .settings import CurrencyConfig, MedidaConfig


class CentroCosto(BaseModel):
    """Modelo Pydantic para los centro de costo"""

    id: Optional[PositiveInt] = None
    nombre: Annotated[str, Field(max_length=50)]
    descripcion: Optional[str] = None
    parent: Union["CentroCosto", int, None] = None
    imputa_iva: bool = False
    tipo_actividad: Union[TipoRentaEnum, str, None] = None
    activo: SituacionEnum = SituacionEnum.ACTIVO


class Rubro(BaseModel):
    """Modelo Pydantic para los rubros o sectores de actividad económica."""

    id: Optional[PositiveInt] = None
    nombre: Annotated[str, Field(max_length=50)]
    descripcion: Optional[str] = None
    actividad_economica: Union[ActividadEconomica, str, None] = None
    centro_costo: Union[CentroCosto, int, None] = None
    activo: SituacionEnum = SituacionEnum.ACTIVO


class CategoriaRefParent(BaseModel):
    """Modelo Pydantic para los centro de costo"""

    id: Optional[PositiveInt] = None
    nombre: Annotated[str, Field(max_length=50)]


class Categoria(BaseModel):
    """Modelo Pydantic para los centro de costo"""

    id: Optional[PositiveInt] = None
    nombre: Annotated[str, Field(max_length=50)]
    itemtipo: Union[ItemTipoListNombreEnum, str, None] = None
    parent: Union[CategoriaRefParent, int, None] = None
    # Hacer que padre sea opcional si puede ser None
    padre: Union["Categoria", None] = None
    activo: SituacionEnum = SituacionEnum.ACTIVO


class Marca(BaseModel):
    """Modelo Pydantic para marca de productos y/o ítems."""

    id: Optional[PositiveInt] = None
    nombre: Annotated[
        str, Field(max_length=50, description="Nombre de la marca")
    ]
    activo: bool = Field(
        default=True, description="Indica si el registro se encuentra activo"
    )

    def __str__(self):
        return self.nombre

    @classmethod
    def get_header(cls):
        """Generar headers para mostrar en tablas"""
        field_header = {
            "id": "ID",
            "nombre": "Nombre",
            "activo": "Activo",
        }
        return [
            field_header.get(field_name, field_name)
            for field_name in cls.model_fields.keys()
        ]


class Item(BaseModel):
    id: int = 0
    uuid: UUID = Field(default_factory=uuid4, exclude=True)
    tipo: ItemTipoListNombreEnum = ItemTipoListNombreEnum.PRODUCTO
    secuencia: int = 0
    codigo: Optional[str] = None
    nombre: str = Field(max_length=200)
    descripcion: Optional[str] = Field(
        default=None, max_length=1800, nullable=True
    )
    slug: Optional[str] = Field(default=None, exclude=True, nullable=True)
    update_nombre_al_vender: bool = False
    add_descripcion_al_vender: bool = False
    rubro: Union[Rubro, int, None] = None
    categoria: Union[Categoria, int, None] = None
    marca: Union[Marca, int, None] = None
    centro_costo: Union[CentroCosto, int, None] = (
        None  # Centro de costo desde detalle de documento
    )
    es_exonera_iva: bool = False
    tasa_iva: int = 0
    proporcion_gravada_iva: int = 100
    medida_base: Union[MedidaConfig, int, None] = None
    moneda_base: Union[CurrencyConfig, str] = "PYG"
    maneja_serie: bool = False
    maneja_lote: bool = False
    maneja_vencimiento: bool = False
    activo: SituacionEnum = SituacionEnum.ACTIVO
    created: datetime = Field(default=None, exclude=True)
    modified: datetime = Field(default=None, exclude=True)

    # Definicion de actividad economica y obligacion
    actividad_economica: Union[ActividadEconomica, str, None] = (
        None  # Actividad economica desde rubro de item
    )
    centro_costo_rubro: Union[CentroCosto, int, None] = (
        None  # Centro de costo desde rubro del item
    )
    imputa_iva: bool = False  # Imputa IVA desde detalle de documento
    imputa_iva_rubro_cc: bool = False  # Imputa IVA desde rubro del item
    impuesto_rubro_cc: Union[TipoRentaEnum, str, None] = (
        None  # Impuesto o Renta afectada desde rubro del item
    )
    impueto_cc: Union[TipoRentaEnum, str, None] = (
        None  # Impuesto o Renta afectada desde detalle de documento
    )
    obligacion: Optional[int] = None
    # codigos_barra = List[ForwardRef('CodigoBarra')] = []


class CodigoBarra(BaseModel):
    """Codigo de Barra de Item"""

    id: int = 0
    item: Union[Item, int]
    codigo: str
    created: datetime = Field(default=None, exclude=True)
    modified: datetime = Field(default=None, exclude=True)
