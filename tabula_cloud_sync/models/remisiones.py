from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING, List, Optional, Union

from pydantic import (
    BaseModel,
    Field,
    PositiveInt,
    field_validator,
    model_validator,
)
from tabula_enums.documents import (
    CaracteristicaCargaMercaderiaEnum,
    CondicionFacturacionEnum,
    IdentificacionVehiculoEnum,
    ItemTipoListNombreEnum,
    ModalidadTransporteEnum,
    MotivoNREnum,
    ResponsableFleteEnum,
    ResponsableNREnum,
)

from .base import Country, Departamento, Distrito, Localidad, Medida
from .contacto import Contact
from .item import Item
from .settings import MedidaConfig

if TYPE_CHECKING:
    # Solo para verificación de tipos, no se ejecuta en tiempo de ejecución
    from .documentos import Documento


class Remision(BaseModel):
    """Remisión emitida"""

    id: Optional[int] = None
    documento: Optional[Union[int, "Documento"]] = None
    motivo: int = Field(
        default=MotivoNREnum.VENTA, description="Motivo de la remisión"
    )
    otro_motivo: Optional[str] = Field(
        None,
        max_length=60,
        description="Otro motivo cuando el motivo no está en la lista",
    )
    condicion_facturacion: Optional[int] = Field(
        None,
        description=(
            (
                "Cuando el motivo es Venta, se debe informar la condición de "
                "facturación"
            )
        ),
    )
    fecha_emi_factura: Optional[date] = Field(
        None,
        description=(
            "Informar cuando no se ha emitido aún la factura - "
            "Condicion Facturacion=FACTURA_A_EMITIR"
        ),
    )
    responsable: int = Field(
        default=ResponsableNREnum.EMISOR_FACTURA,
        description=(
            "Responsable de la emisión de la Nota Remisión Electrónica"
        ),
    )
    kilometro_estimado: PositiveInt
    costo_flete: Optional[Decimal] = Field(
        None,
        description=(
            "Costo cuando el traslado sea efectuado por empresas de transporte"
        ),
    )

    @field_validator("condicion_facturacion")
    def validar_condicion_facturacion(cls, v, info):
        motivo = info.data.get("motivo")
        if motivo == MotivoNREnum.VENTA and v is None:
            raise ValueError(
                "Cuando el motivo es Venta, se debe informar "
                "la condición de facturación"
            )
        return v

    @field_validator("fecha_emi_factura")
    def validar_fecha_factura(cls, v, info):
        condicion = info.data.get("condicion_facturacion")
        if (
            condicion == CondicionFacturacionEnum.FACTURA_A_EMITIR
            and v is None
        ):
            raise ValueError(
                "Cuando la condición es Factura a Emitir, se debe informar "
                "la fecha de emisión"
            )
        return v

    model_config = {
        "title": "Remisión",
    }


class TransporteMercaderia(BaseModel):
    """Transporte de la mercadería"""

    id: Optional[int] = None
    documento: Optional[Union[int, "Documento"]] = None
    tipo_transporte: Optional[int] = Field(
        None,
        description="Tipo de Transporte o Trasladado por: (Propio o Tercero)",
    )
    modalidad_transporte: int = Field(
        default=ModalidadTransporteEnum.TERRESTRE,
        description="Modalidad de transporte",
    )
    responsable_flete: int = Field(
        default=ResponsableFleteEnum.EMISOR_FACTURA,
        description="Responsable del costo del flete",
    )
    condicion_negociacion: Optional[str] = Field(
        None,
        max_length=3,
        description="Condición de negociación internacional (Incoterms)",
    )
    numero_manifiesto: Optional[str] = Field(
        None,
        max_length=20,
        description="Número de manifiesto o conocimiento de "
        "carga/declaración de tránsito aduanero/Carta de porte internacional",
    )
    numero_despacho: Optional[str] = Field(
        None,
        max_length=16,
        description=(
            "Número de despacho aduanero (obligatorio si es Importación)"
        ),
    )
    fecha_inicio: Optional[date] = Field(
        None,
        description="Fecha de inicio del traslado (obligatorio si es Nota de remisión)",
    )
    fecha_fin: Optional[date] = Field(
        None,
        description="Fecha estimada de fin del traslado (obligatorio si se"
        "informó fecha de inicio)",
    )
    pais: Optional[str | Country] = Field(None, description="País de destino")
    transportista: Optional[int | Contact] = Field(
        None, description="Transportista"
    )
    chofer: Optional[int | Contact] = Field(None, description="Chofer")
    agente: Optional[int | Contact] = Field(
        None, description="Agente de carga"
    )
    direccion_salida: Optional[Union[int, "TransporteDireccionSalida"]]
    direccion_llegada: List["TransporteDireccionLlegada"] = Field(
        default_factory=list
    )
    vehiculo_traslado: List["VehiculoTraslado"] = Field(default_factory=list)

    @field_validator("fecha_fin")
    def validar_fechas(cls, v, info):
        fecha_inicio = info.data.get("fecha_inicio")
        if fecha_inicio and not v:
            raise ValueError(
                "Si se informó fecha de inicio, debe informar fecha de fin estimada"
            )
        if fecha_inicio and v and v < fecha_inicio:
            raise ValueError(
                "La fecha de fin no puede ser anterior a la fecha de inicio"
            )
        return v

    @field_validator("numero_despacho")
    def validar_despacho(cls, v, info):
        documento = info.data.get("documento")

        # Si documento es None o no es un diccionario, omitir validación
        if documento is None:
            return v

        # Intentar obtener el motivo de forma segura
        motivo = None

        if isinstance(documento, dict):
            # Si es un diccionario, buscar motivo en documento.remision
            remision = documento.get("remision")
            if isinstance(remision, dict):
                motivo = remision.get("motivo")
        elif hasattr(documento, "remision"):
            # Si es un objeto, intentar acceder al atributo remision
            remision = getattr(documento, "remision", None)
            if remision and hasattr(remision, "motivo"):
                motivo = remision.motivo

        # Validación con el motivo encontrado (si se encontró)
        if motivo == MotivoNREnum.IMPORTACION and not v:
            raise ValueError(
                "Si el motivo es Importación, debe informar el número de despacho "
                "aduanero"
            )
        return v

    model_config = {
        "title": "Transporte de Mercadería",
    }


class TransporteDireccionSalida(BaseModel):
    """Dirección de salida de la mercadería"""

    id: Optional[int] = None
    transporte: int | TransporteMercaderia | None = None
    direccion: str = Field(..., max_length=255)
    numero_casa: int = Field(default=0)
    direccion_complementaria1: Optional[str] = Field(None, max_length=255)
    direccion_complementaria2: Optional[str] = Field(None, max_length=255)
    departamento: int | Departamento
    distrito: int | Distrito | None = None
    localidad: int | Localidad | None = None
    telefono: Optional[str] = Field(None, max_length=15)

    model_config = {
        "title": "Dirección de Salida",
    }


class TransporteDireccionLlegada(BaseModel):
    """Dirección de llegada de la mercadería"""

    id: Optional[int] = None
    transporte: int | TransporteMercaderia | None = None
    direccion: str = Field(..., max_length=255)
    numero_casa: int = Field(default=0)
    direccion_complementaria1: Optional[str] = Field(None, max_length=255)
    direccion_complementaria2: Optional[str] = Field(None, max_length=255)
    departamento: int | Departamento
    distrito: Optional[int | Distrito] = None
    localidad: int | Localidad
    telefono: Optional[str] = Field(None, max_length=15)

    model_config = {
        "title": "Dirección de Llegada",
    }


class VehiculoTraslado(BaseModel):
    """Vehículo de traslado de la mercadería"""

    id: Optional[int] = None
    transporte: int | TransporteMercaderia | None = None
    tipo: str = Field(..., max_length=10)
    marca: str = Field(..., max_length=10)
    identicacion_vehiculo: int = Field(
        default=IdentificacionVehiculoEnum.NUMERO_MATRICULA,
        description="Tipo de identificación del vehículo",
    )
    numero_identificacion: str = Field(..., max_length=20)
    datos_adicional: Optional[str] = Field(None, max_length=20)
    numero_vuelo: Optional[str] = Field(
        None,
        max_length=6,
        description="Obligatorio si modalidad transporte es aéreo",
    )

    @field_validator("numero_vuelo")
    def validar_numero_vuelo(cls, v, info):
        transporte_id = info.data.get("transporte")
        # Aquí asumimos que hay una forma de obtener la modalidad
        # del transporte
        # En un caso real, probablemente necesitarías una consulta
        # a la base de datos
        # Esta validación podría necesitar ser manejada en el
        # controlador en lugar del modelo
        # modalidad = get_modalidad_by_transporte_id(transporte_id)
        # if modalidad == ModalidadTransporteEnum.AEREO and not v:
        #     raise ValueError("Si la modalidad de transporte
        # es aérea, debe informar el número de vuelo")
        return v

    model_config = {
        "title": "Vehículo de Traslado",
    }


class CargaGeneral(BaseModel):
    """Datos generales de la carga"""

    id: Optional[int] = None
    documento: Optional[Union[int, "Documento"]] = None
    medida_volumen: Optional[int | Medida] = Field(
        None, description="Unidad de medida del volumen de la mercadería"
    )
    total_volumen: Decimal = Field(
        default=0, description="Volumen total de la mercadería"
    )
    medida_peso: Optional[int | Medida] = Field(
        None, description="Unidad de medida del peso de la mercadería"
    )
    total_peso: Decimal = Field(
        default=0, description="Peso total de la mercadería"
    )
    caracteristica_carga: Optional[int | CaracteristicaCargaMercaderiaEnum] = (
        Field(None, description="Tipo de característica de la carga")
    )
    caracteristica_carga_descripcion: Optional[str] = Field(
        None, max_length=50
    )

    model_config = {
        "title": "Carga General Documento",
    }


class DocumentoDetalleRemision(BaseModel):
    """Lista de items de la remisión.

    Attributes:
        id (int): Identificador único
        documento (int): ID del documento relacionado
        orden (int): Orden del ítem en la remisión
        item_tipo (int): ID del tipo de ítem
        item (int): ID del ítem
        item_secuencia (int): Secuencia del ítem
        item_codigo (str): Código del ítem
        item_gtin (str): Código GTIN del ítem
        item_gtin_paq (str): Código GTIN del paquete
        item_nombre (str): Nombre del ítem
        item_descripcion (str): Descripción detallada del ítem
        item_medida (int): ID de la unidad de medida
        cantidad (Decimal): Cantidad de unidades
        item_info (str): Información adicional del ítem
        tolerancia (int): Tipo de tolerancia en la remisión
        valor_tolerancia (Decimal): Valor de la tolerancia
        numero_lote (str): Número de lote para trazabilidad
        fecha_vencimiento (date): Fecha de vencimiento del lote
        serie (str): Serie de los ítems
    """

    id: Optional[int] = None
    documento: Optional[Union[int, "Documento"]] = None
    orden: int = Field(..., gt=0, description="Orden del ítem en la remisión")
    item_tipo: Optional[int | ItemTipoListNombreEnum] = Field(
        None, description="Tipo de ítem"
    )
    item: int | Item
    item_id: int | None = None
    item_secuencia: int = Field(
        default=0, ge=0, description="Secuencia del ítem"
    )
    item_codigo: Optional[str] = Field(
        None, max_length=50, description="Código del ítem"
    )
    item_gtin: Optional[str] = Field(
        None, max_length=14, description="Código GTIN del ítem"
    )
    item_gtin_paq: Optional[str] = Field(
        None, max_length=14, description="Código GTIN del paquete"
    )
    item_nombre: str = Field(
        ..., max_length=200, description="Nombre del ítem"
    )
    item_descripcion: Optional[str] = Field(
        None, max_length=1800, description="Descripción detallada del ítem"
    )
    item_medida: int | MedidaConfig = Field(
        default=1, description="Unidad de medida del ítem"
    )
    cantidad: Decimal = Field(
        ..., ge=0, description="Cantidad de unidades del ítem"
    )
    item_info: Optional[str] = Field(
        None,
        max_length=500,
        description="Información de interés del emisor con respecto al ítem",
    )
    tolerancia: Optional[int] = Field(
        None, description="Tolerancia de la mercadería en la remisión"
    )
    valor_tolerancia: Decimal = Field(
        default=Decimal(0), ge=0, description="Valor de la tolerancia"
    )
    numero_lote: Optional[str] = Field(
        None,
        max_length=80,
        description="Número de lote para rastreo de mercaderías",
    )
    fecha_vencimiento: Optional[date] = Field(
        None, description="Fecha de vencimiento del lote"
    )
    serie: Optional[str] = Field(
        None, max_length=80, description="Serie de los ítems"
    )

    @field_validator("cantidad")
    def validar_cantidad(cls, v):
        """Validar que la cantidad sea positiva"""
        if v <= 0:
            raise ValueError("La cantidad debe ser mayor que cero")
        return v

    @field_validator("valor_tolerancia")
    def validar_valor_tolerancia(cls, v: Decimal, info):
        """Validar que el valor de tolerancia sea positivo
        cuando hay tolerancia"""
        if info.data.get("tolerancia") is not None and v <= 0:
            raise ValueError(
                "El valor de tolerancia debe ser mayor a 0 cuando"
                " se especifica tolerancia"
            )
        return v

    @model_validator(mode="after")
    def validar_item_nombre(self):
        """Validar que el nombre del ítem no esté vacío"""
        if not self.item_nombre or self.item_nombre.strip() == "":
            raise ValueError("El nombre del ítem no puede estar vacío")
        return self

    model_config = {
        "title": "Documento Detalle Remisión",
        "populate_by_name": True,
        "json_schema_extra": {
            "examples": [
                {
                    "documento": 1,
                    "orden": 1,
                    "item": 101,
                    "item_codigo": "ABC123",
                    "item_nombre": "Producto de ejemplo",
                    "item_medida": 1,
                    "cantidad": 10.5,
                }
            ]
        },
    }
