from datetime import date
from typing import Annotated, List

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    PositiveInt,
    field_serializer,
    field_validator,
)
from tabula_enums.documents import TipoComunicacionBajaEnum
from tabula_enums.form import SituacionEnum
from tabula_enums.impuestos import VencimientoEnum

from ..core.exceptions import ValidationException


class Currency(BaseModel):
    id: Annotated[
        str, Field(max_length=3)
    ]  # Restricción de longitud máxima como en tu modelo
    orden: PositiveInt = 0  # Esto asegura que el número sea positivo
    nombre: Annotated[
        str, Field(max_length=20)
    ]  # Restricción de longitud máxima
    simbolo: Annotated[str, Field(max_length=5)] | None = (
        None  # Puede ser nulo y tiene restricción de longitud máxima
    )
    decimal: int | None = (
        None  # Asegurar que el número es positivo, pero necesitamos validar los límites
    )
    activo: bool = True  # Valor predeterminado es True

    @field_validator("decimal")
    @classmethod
    def validate_decimal(cls, v):
        if v < 0 or v > 8:  # Asegurando que el valor esté entre 0 y 8
            raise ValidationException(
                "El número decimal debe estar entre 0 y 8", field="decimal"
            )
        return v

    # En Pydantic, el método __str__ no es tan común,
    # pero puedes sobrescribirlo si lo deseas.
    def __str__(self):
        return self.nombre

    # La meta información y ordenación se manejan generalmente en
    # el código que utiliza este modelo,
    # como en consultas de base de datos, o lógica de negocio,
    # y no directamente en el modelo Pydantic.


class MedidaCategoria(BaseModel):
    """Categoría de medida"""

    id: PositiveInt | None = None
    nombre: str
    activo: SituacionEnum = SituacionEnum.ACTIVO


class Medida(BaseModel):
    """Unidad de medidas de los productos"""

    id: PositiveInt | None = None
    nombre: str
    categoria: MedidaCategoria | int | None = None
    simbolo: str
    activo: SituacionEnum = SituacionEnum.ACTIVO


class TipoRegistroSET(BaseModel):
    """Tipo de registro SET"""

    id: int
    nombre: str


class ComprobanteClase(BaseModel):
    """Clase de comprobante"""

    id: int
    nombre: str


class Operacion(BaseModel):
    """Operaciones de comprobante"""

    id: int
    nombre: str
    descripcion: str | None = None
    flujo_caja: bool | None = None
    flujo_inventario: bool | None = None
    tipo_registro_set: TipoRegistroSET | int | None = None
    es_emitida: bool | None = None
    activo: SituacionEnum = SituacionEnum.ACTIVO


class ComprobanteMedioGeneracion(BaseModel):
    """Medio de generacion de documento"""

    id: int = Field(..., gt=0, description="Código")
    nombre: str = Field(
        ..., max_length=30, description="Nombre de Tipo Operacion"
    )


class Comprobante(BaseModel):
    """Comprobante predefinidos del sistema"""

    id: int
    nombre: str
    especificar: bool | None = None
    operaciones: List[Operacion] = []
    es_comprobante_set: bool | None = None
    es_informativo: bool | None = None
    codigo_informativo: int | None = None
    es_libro_iva: bool | None = None
    clase: int | ComprobanteClase | None = None
    usa_timbrado: bool | None = None
    # indicar que es electrónico y default false
    es_electronico: bool | None = None
    codigo_ws: int | None = None
    medio_generacion: List[ComprobanteMedioGeneracion] = []
    weight: int | None = None
    activo: SituacionEnum = SituacionEnum.ACTIVO
    usa_punto_expedicion: bool | None = None
    controlar_inventario: bool | None = None


class Country(BaseModel):
    id: str
    nombre: str
    codealfa2: str | None = None
    numero: int | None = None
    tld: str | None = None

    @classmethod
    def get_header(cls):
        """Generar headers"""
        field_header = {
            "numero": "Orden",
            "tld": "TLD",
        }
        return [
            field_header.get(field_name, field_name)
            for field_name in cls.model_fields.keys()
        ]


class Departamento(BaseModel):
    id: int
    nombre: str

    @classmethod
    def get_header(cls):
        """Generar headers"""
        field_header = {"id": "Código", "nombre": "Departamentos"}
        return [
            field_header.get(field_name, field_name)
            for field_name in cls.model_fields.keys()
        ]


class Distrito(BaseModel):
    id: int
    nombre: str
    departamento: Departamento | int | None = None

    @classmethod
    def get_header(cls):
        """Generar headers"""
        field_header = {
            "id": "Código",
            "nombre": "Distrito",
            "departamento": "Departamento",
        }
        return [
            field_header.get(field_name, field_name)
            for field_name in cls.model_fields.keys()
        ]


class Localidad(BaseModel):
    id: int
    nombre: str
    distrito: Distrito | int | None = None

    @classmethod
    def get_header(cls):
        """Generar headers"""
        field_header = {
            "id": "Código",
            "nombre": "Localidad",
            "distrito": "Distrito",
        }
        return [
            field_header.get(field_name, field_name)
            for field_name in cls.model_fields.keys()
        ]


class ActividadEconomica(BaseModel):
    """Lista de actividades económicas"""

    id: str
    serie: str
    nombre: str
    padre: str | None = None
    operativo: bool = True

    @classmethod
    def get_header(cls):
        """Generar headers"""
        field_header = {
            "id": "Código",
            "nombre": "Descripción",
            "operativo": "operativo",
        }
        return [
            field_header.get(field_name, field_name)
            for field_name in cls.model_fields.keys()
        ]


class TipoImpuesto(BaseModel):
    id: str
    nombre: str
    activo: bool


class Obligacion(BaseModel):
    id: int
    name: str
    inicio_vigencia: date | None = None
    fin_vigencia: date | None = None
    vencimiento: VencimientoEnum | None = None
    impuesto: str | None = None

    @classmethod
    def get_header(cls):
        """Generar headers"""
        field_header = {
            "id": "Código",
            "nombre": "Descripción",
            "impuesto": "Codigo Impuesto",
        }
        return [
            field_header.get(field_name, field_name)
            for field_name in cls.model_fields.keys()
        ]


class TipoRegistroSET(BaseModel):
    id: int
    nombre: str

    @classmethod
    def get_header(cls):
        """Generar headers"""
        field_header = {
            "id": "Código",
            "nombre": "Descripción",
        }
        return [
            field_header.get(field_name, field_name)
            for field_name in cls.model_fields.keys()
        ]


class ComprobanteClase(BaseModel):
    """Clase de comprobante"""

    id: int
    nombre: str


class Operacion(BaseModel):
    """Operaciones de comprobante"""

    id: int
    nombre: str
    descripcion: str | None = None
    flujo_caja: bool | None = None
    flujo_inventario: bool | None = None
    tipo_registro_set: TipoRegistroSET | int | None = None
    es_emitida: bool | None = None
    usar_tasa_comprador: bool | None = None
    activo: SituacionEnum = SituacionEnum.ACTIVO


class ItemTipo(BaseModel):
    """Modelo Pydantic para los tipos de item"""

    id: str | None = None
    nombre: str
    nombre_plural: str | None = None
    descripcion: str | None = None
    weight: int = 0
    es_vendible: bool = False
    es_comprable: bool = False
    es_solo_comercial: bool = False


class MotivoComunicacionBaja(BaseModel):
    """Motivo de comunicación de baja de comprobante.

    Attributes:
        id (int): Código identificador
        nombre (str): Nombre del motivo
        tipo_inutilizacion (TipoComunicacionBajaEnum): Tipo de inutilización
    """

    id: int = Field(..., gt=0, description="Código identificador")
    nombre: str = Field(
        ..., max_length=100, description="Nombre del motivo de comunicación"
    )
    tipo_inutilizacion: TipoComunicacionBajaEnum = Field(
        ..., description="Tipo de inutilización o baja"
    )

    @classmethod
    def get_header(cls):
        """Generar headers"""
        field_header = {
            "id": "Código",
            "nombre": "Motivo",
            "tipo_inutilizacion": "Tipo",
        }
        return [
            field_header.get(field_name, field_name)
            for field_name in cls.model_fields.keys()
        ]


class MotivoEmisionNR(BaseModel):
    """Motivo de emisión de comprobante no registrado.

    Attributes:
        id (int): Código identificador
        nombre (str): Nombre del motivo
    """

    id: int = Field(..., gt=0, description="Código identificador")
    nombre: str = Field(
        ..., max_length=60, description="Nombre del motivo de emisión"
    )

    @classmethod
    def get_header(cls):
        """Generar headers"""
        field_header = {
            "id": "Código",
            "nombre": "Motivo",
        }
        return [
            field_header.get(field_name, field_name)
            for field_name in cls.model_fields.keys()
        ]


class CaracteristicaCargaMercaderia(BaseModel):
    """Características de la carga de mercadería.

    Attributes:
        id (int): Código único de la característica de carga
        nombre (str): Nombre descriptivo de la característica de carga
        activo (bool): Indica si esta característica está disponible para su uso
    """

    id: PositiveInt = Field(
        ...,
        description="Código único de la característica de carga",
        examples=[1, 5, 10],
    )
    nombre: Annotated[
        str,
        Field(
            max_length=100,
            description="Nombre descriptivo de la característica de carga",
        ),
    ]
    activo: bool = Field(
        default=True,
        description="Indica si esta característica está disponible para su uso",
    )

    # Metadatos equivalentes a la clase Meta de Django
    model_config = {
        "title": "Característica de Carga",
        "json_schema_extra": {
            "description": (
                "Modelo para almacenar las características de la carga de mercadería"
            )
        },
        # Para mantener compatibilidad con las APIs
        "populate_by_name": True,
        # Permite ordenar los campos en la misma secuencia que Django
        "json_schema_serialization_defaults": {"by_alias": True},
    }

    @field_serializer("id")
    def serialize_id(self, id: int, _info):
        """Serializa el id como entero"""
        return int(id)

    @classmethod
    def get_header(cls):
        """Genera los encabezados para tablas o reportes"""
        field_header = {"id": "Código", "nombre": "Nombre", "activo": "Activo"}
        return [
            field_header.get(field_name, field_name)
            for field_name in cls.model_fields.keys()
        ]

    def __str__(self):
        """Representación en string del objeto"""
        return f"{self.id} - {self.nombre}"


# Equivalente a verbose_name_plural en Meta de Django
CaracteristicaCargaMercaderia.__doc__ = (
    "Características de Carga de Mercadería"
)


class SubtipoOperacion(BaseModel):
    """Clasificación fiscal de operaciones para reportes tributarios.
    Define el contexto general del documento.

    Attributes:
        id (int | None): Identificador único del subtipo
        operacion (Operacion | int): Operación asociada (puede ser objeto completo o ID)
        codigo (str): Código interno (VL, VE, VR, CL, CI, etc)
        nombre (str): Nombre del subtipo de operación
        descripcion (str): Descripción detallada del subtipo
        es_exportacion (bool): Indica si es operación de exportación
        es_importacion (bool): Indica si es operación de importación
        es_exonerada_iva (bool): Indica si la operación está exonerada de IVA
        es_exento_iva (bool): Indica si la operación es exenta de IVA
        es_default (bool): Indica si este subtipo es el valor por
        defecto para la operación
        activo (bool): Indica si el subtipo está activo
        orden (int): Orden de visualización

    Constraints (a nivel de base de datos):
        - unique_together: (operacion, codigo)
        - unique_constraint: Solo un subtipo puede ser default por operación
        cuando está activo
    """

    id: PositiveInt | None = None
    operacion: Operacion | int = Field(..., description="Operación asociada")
    codigo: Annotated[
        str,
        Field(
            max_length=10,
            description="Código interno (VL, VE, VR, CL, CI, etc)",
        ),
    ]
    nombre: Annotated[
        str,
        Field(max_length=100, description="Nombre del subtipo de operación"),
    ]
    descripcion: str = Field(
        default="", description="Descripción detallada del subtipo"
    )

    # Características fiscales simples
    es_exportacion: bool = Field(
        default=False, description="Indica si es operación de exportación"
    )
    es_importacion: bool = Field(
        default=False, description="Indica si es operación de importación"
    )
    es_exonerada_iva: bool = Field(
        default=False,
        description="Indica si la operación está exonerada de IVA",
    )
    es_exento_iva: bool = Field(
        default=False, description="Indica si la operación es exenta de IVA"
    )

    es_default: bool = Field(
        default=False,
        description="Indica si este subtipo es el valor por defecto para la "
        "operación. Solo puede haber uno por operación.",
    )

    activo: bool = Field(
        default=True, description="Indica si el subtipo está activo"
    )
    orden: int = Field(default=0, ge=0, description="Orden de visualización")

    model_config = ConfigDict(
        from_attributes=True,
        title="Subtipo de Operación",
        json_schema_extra={
            "description": (
                "Clasificación fiscal de operaciones para reportes tributarios"
            )
        },
    )

    @classmethod
    def get_header(cls):
        """Genera los encabezados para tablas o reportes"""
        field_header = {
            "id": "ID",
            "operacion": "Operación",
            "codigo": "Código",
            "nombre": "Nombre",
            "descripcion": "Descripción",
            "es_exportacion": "Es Exportación",
            "es_importacion": "Es Importación",
            "es_exonerada_iva": "Exonerada IVA",
            "es_exento_iva": "Exento IVA",
            "es_default": "Por Defecto",
            "activo": "Activo",
            "orden": "Orden",
        }
        return [
            field_header.get(field_name, field_name)
            for field_name in cls.model_fields.keys()
        ]

    def __str__(self):
        """Representación en string del objeto"""
        operacion_nombre = (
            self.operacion.nombre
            if isinstance(self.operacion, Operacion)
            else f"Operación {self.operacion}"
        )
        return f"{operacion_nombre} - {self.nombre}"

    @classmethod
    def get_default_for_operacion(
        cls, operacion_id: int
    ) -> "SubtipoOperacion | None":
        """
        Método de utilidad para obtener el subtipo por defecto de una operación.

        Nota: Este método es un helper. La lógica real de consulta debe
        implementarse en el servicio/repositorio que interactúa con la base de datos.

        Args:
            operacion_id: ID de la operación

        Returns:
            SubtipoOperacion | None: El subtipo por defecto si existe

        Example:
            En tu servicio/repositorio:
            ```python
            def get_default_subtipo(self, operacion_id: int) -> SubtipoOperacion | None:
                result = db.query(SubtipoOperacion).filter(
                    SubtipoOperacion.operacion_id == operacion_id,
                    SubtipoOperacion.es_default == True,
                    SubtipoOperacion.activo == True
                ).order_by(SubtipoOperacion.orden).first()

                if result:
                    return SubtipoOperacion.from_orm(result)
                return None
            ```
        """
        # Este es un método placeholder que debe ser implementado
        # en la capa de servicio/repositorio
        raise NotImplementedError(
            "Este método debe ser implementado en el servicio/repositorio "
            "que maneja la persistencia de datos"
        )
