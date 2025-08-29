from __future__ import annotations

import logging
import uuid
from datetime import date, datetime, time
from decimal import Decimal
from enum import Enum
from typing import List, Optional

from pydantic import (
    UUID4,
    BaseModel,
    ConfigDict,
    Field,
    PositiveInt,
    field_validator,
    model_validator,
)
from tabula_enums.documents import (
    CondicionOperacionEnum,
    IndicadorPresenciaEnum,
    MedioDocumentoAsociadoEnum,
    MotivoEmisionNCNDEnum,
    SituacionDocumentoEnum,
    SituacionFEEnum,
    TipoCambioEnum,
    TipoComunicacionBajaEnum,
    TipoConstanciaAsociadoEnum,
    TipoDocumentoAsociadoEnum,
    TipoTransaccionEnum,
)
from tabula_enums.impuestos import (
    AfectacionIVAEnum,
    CostoTipoEnum,
    TipoImpuestoAfectadoEnum,
    TipoRentaEnum,
)

from .base import MotivoComunicacionBaja, Operacion
from .company import Sucursal
from .contacto import Contact
from .item import CentroCosto, Item
from .remisiones import (
    CargaGeneral,
    DocumentoDetalleRemision,
    Remision,
    TransporteMercaderia,
)
from .settings import Comprobante, CurrencyConfig, MedidaConfig, Timbrado


# Calculos auxiliares
def round_ext(num, decimales=0):
    """Redondeo que retorna un valor Decimal"""
    # Asegurarnos que num sea Decimal
    if not isinstance(num, Decimal):
        num = Decimal(
            str(num)
        )  # Convertir a Decimal usando string para evitar pérdida de precisión

    # Asegurarnos que decimales sea un entero
    decimales = int(decimales)

    # Realizar el redondeo con precisión decimal
    factor = Decimal(10) ** decimales
    entero = int(num * factor)
    decimal = num * factor - entero

    if decimal >= Decimal("0.5"):
        redondeado = Decimal(entero + 1) / factor
    else:
        redondeado = Decimal(entero) / factor

    return redondeado


def cal_base_gravada_iva(monto_neto, tasa_iva, proporcion_iva, afectacion_iva):
    """Calculo base gravada del IVA"""
    if tasa_iva == 0 or proporcion_iva == 0:
        return Decimal(0.0)
    if (
        afectacion_iva == AfectacionIVAEnum.GRAVADO_PARCIAL
        or afectacion_iva == AfectacionIVAEnum.GRAVADO_IVA
    ):
        return (
            100
            * monto_neto
            * Decimal(proporcion_iva)
            / (10000 + tasa_iva * proporcion_iva)
        )
    return Decimal(0.0)


class DocumentoBuscador(BaseModel):
    """Modelo simplificado para buscador"""

    id: int = 0
    numero: int = 0
    operacion_descripcion: str = ""
    fecha_documento: date | None = None
    numero_comprobante: str | None = None
    contacto_nombre_full: str = ""
    contacto_documento: str = ""
    moneda_id: str = ""
    monto_total: Decimal = 0
    es_vigente: bool = True


class TipoMotivo(Enum):
    INCLUSION = "INCLUSION"
    EXCLUSION = "EXCLUSION"


class MotivoRectificativa(BaseModel):
    """Motivo de Rectificativa"""

    tipo: TipoMotivo = Field(...)
    motivo: str = Field(...)
    descripcion: str

    @field_validator("motivo", mode="after")
    def validar_motivo(cls, value, info):
        tipo = info.data.get("tipo")
        if tipo == TipoMotivo.INCLUSION:
            motivos_validos = [
                "AJUSTE DE INFORMACIÓN COMPLEMENTARIA",
                "AJUSTE DE MONTO DE GASTO NO DEDUCIBLE",
                "ERROR EN DECLARACIÓN DE CASILLA",
                "ERROR EN EL MONTO ACUMULADO",
                "OPERACIÓN NO DECLARADA",
                "SITUACIONES NO CONTEMPLADAS",
            ]
        elif tipo == TipoMotivo.EXCLUSION:
            motivos_validos = [
                "AJUSTE DE INFORMACIÓN COMPLEMENTARIA",
                "AJUSTE DE MONTO DE GASTO NO DEDUCIBLE",
                "ANULACIÓN DE OPERACIONES",
                "CORRESPONDE A OTRO PERIODO FISCAL",
                "DOCUMENTOS QUE NO REUNEN LOS REQUISITOS FORMALES",
                "ERROR EN DECLARACIÓN DE CASILLA",
                "ERROR EN EL MONTO ACUMULADO",
                "EROGACIONES NO RELACIONADAS A LA ACTIVIDAD",
                "OPERACIONES SIN RESPALDO DOCUMENTAL",
                "SITUACIONES NO CONTEMPLADAS",
            ]
        else:
            raise ValueError("Tipo de motivo inválido")

        if value not in motivos_validos:
            raise ValueError(f"Motivo inválido para el tipo {tipo.value}")
        return value

    @field_validator("descripcion", mode="after")
    def validar_descripcion(cls, value, info):
        """Valida que la descripción no esté vacía si el motivo
        es "SITUACIONES NO CONTEMPLADAS"
        y que la longitud esté entre 5 y 150 caracteres.
        """
        if value is None:
            raise ValueError("La descripción es requerida")
        if value and not (5 <= len(value) <= 150):
            raise ValueError(
                "La descripción debe tener entre 5 y 150 caracteres"
            )

        return value

    # Configuración para usar los valores de Enum al exportar


class Documento(BaseModel):
    """
    Este módulo define la clase Documento.
    """

    model_config: ConfigDict = {
        "json_encoders": {
            uuid.UUID: str,
            Decimal: float,
            date: lambda v: v.isoformat(),
            datetime: lambda v: v.isoformat(),
            Enum: lambda v: v.value,
        },
        "arbitrary_types_allowed": True,
    }

    id: PositiveInt | None = None
    referencia: UUID4 = Field(default_factory=uuid.uuid4)
    periodo: int | None = None
    sucursal: Sucursal | int = 1
    formulario: int | None = None
    operacion: Operacion | int | None = None
    numero: int | None = None
    comprobante: Comprobante | int | None = None
    dcomprobante: str | None = None
    fecha_operacion: date | None = None
    fecha_documento: date | None = None
    hora_documento: time | None = None
    fecha_traslado: date | None = None
    contacto: Contact | int | None = None
    jcontacto: dict = Field(default_factory=dict)
    es_operacion_exonerada_iva: bool = False
    moneda: CurrencyConfig | str | None = None
    moneda_decimal: int = Field(exclude=True, default=1)
    condicion_cambio: TipoCambioEnum = TipoCambioEnum.GLOBAL
    tasa_cambio: Decimal = 1
    condicion_operacion: CondicionOperacionEnum = (
        CondicionOperacionEnum.CONTADO
    )
    es_vigente: SituacionDocumentoEnum = SituacionDocumentoEnum.VIGENTE
    motivo_anulacion: str | None = None
    motivo_nominacion: str | None = None
    info_interno: str | None = None
    info_adicional: Optional[dict] = Field(default_factory=dict)
    agente_interno: Contact | int | None = None
    timbrado: Timbrado | int | None = None
    es_timbrado_electronico: bool = False
    serie: str | None = None
    establecimiento: str | None = None
    punto_expedicion: str | None = None
    numero_documento: int | None = None
    numero_comprobante: str | None = None
    monto_exonerado: Decimal = 0
    monto_exenta: Decimal = 0
    # Subtotaes de IVA
    subtotal_exo_exe: Decimal = Field(exclude=True, default=Decimal(0))
    subtotal_iva_5: Decimal = Field(exclude=True, default=Decimal(0))
    subtotal_iva_10: Decimal = Field(exclude=True, default=Decimal(0))
    st_base_gravada_imputa_iva: Decimal = Field(
        exclude=True, default=Decimal(0)
    )
    st_base_no_imputa_iva: Decimal = Field(exclude=True, default=Decimal(0))
    st_liquidacion_iva_imputa: Decimal = Field(
        exclude=True, default=Decimal(0)
    )

    subtotal_imputa_iva: Decimal = Field(exclude=True, default=Decimal(0))

    descuento_item: Decimal = Field(exclude=True, default=Decimal(0))
    descuento_global: Decimal = Field(exclude=True, default=Decimal(0))

    base_gravada_5: Decimal = 0
    base_gravada_10: Decimal = 0
    iva_5: Decimal = 0
    iva_10: Decimal = 0
    redondeo: Decimal = 0
    monto_total: Decimal = 0
    monto_exonerado_mb: Decimal = 0
    monto_exenta_mb: Decimal = 0
    base_gravada_5_mb: Decimal = 0
    base_gravada_10_mb: Decimal = 0
    iva_5_mb: Decimal = 0
    iva_10_mb: Decimal = 0
    redondeo_mb: Decimal = 0
    monto_total_mb: Decimal = 0
    jtotal: dict = Field(default_factory=dict)
    tipo_impuesto_afectado: TipoImpuestoAfectadoEnum = (
        TipoImpuestoAfectadoEnum.IVA_RENTA
    )
    tipo_transaccion: TipoTransaccionEnum | None = None
    jauto_factura: Optional[dict] = Field(default_factory=dict)
    indicador_presencia: int | IndicadorPresenciaEnum | None = None
    dindicador_presencia: str | None = None
    motivo_emision_ncnd: int | MotivoEmisionNCNDEnum | None = None
    cdc: str | None = None
    cds: int | None = None
    info_emisor: str | None = None
    info_fisco: str | None = None
    jdocumento: dict = Field(default_factory=dict)
    situacion_fe: str | SituacionFEEnum | None = None
    respuesta_sifen_fe: str | None = None
    jimpuesto_afectado: dict = Field(default_factory=dict)
    detalles: List["DocumentoDetalle"] = []
    remision: Optional["Remision"] = None
    detalles_remision: List["DocumentoDetalleRemision"] = []
    transporte_mercaderia: Optional["TransporteMercaderia"] = None
    carga_general: Optional["CargaGeneral"] = None
    documentos_asociados: List["DocumentoAsociado"] = []
    es_rectificativa: bool = False
    jestado: dict = Field(default_factory=dict)

    def set_calcular_totales(self):
        """Calcula los totales del documento"""
        self.monto_exonerado = 0
        self.monto_exenta = 0
        self.base_gravada_5 = 0
        self.base_gravada_10 = 0
        self.iva_5 = 0
        self.iva_10 = 0
        self.monto_total = 0

        self.monto_exonerado_mb = 0
        self.monto_exenta_mb = 0
        self.base_gravada_5_mb = 0
        self.base_gravada_10_mb = 0
        self.iva_5_mb = 0
        self.iva_10_mb = 0
        self.monto_total_mb = 0

        self.subtotal_iva_5 = 0
        self.subtotal_iva_10 = 0
        self.subtotal_imputa_iva = 0
        self.st_base_gravada_imputa_iva = 0
        self.st_liquidacion_iva_imputa = 0
        self.st_base_no_imputa_iva = 0

        for detalle in self.detalles:
            logging.debug(
                "Este es detalle: %s %s",
                detalle.item_nombre,
                detalle.monto_neto,
            )
            if self.tipo_impuesto_afectado in (
                TipoImpuestoAfectadoEnum.IVA,
                TipoImpuestoAfectadoEnum.IVA_RENTA,
            ):
                detalle.tasa_cambio = self.tasa_cambio
                E731 = detalle.afectacion_iva
                E734 = detalle.tasa_iva
                EA008 = detalle.monto_neto
                E735 = detalle.base_gravada_iva
                E736 = detalle.liquidacion_iva
                E737 = detalle.base_exenta_iva
                self.monto_exenta += (EA008 if E731 == 3 else 0) + (
                    E737 if E731 == 4 else 0
                )
                self.monto_exonerado += EA008 if E731 == 2 else 0

                self.subtotal_iva_5 += (
                    EA008 if (E731 == 1 and E734 == 5) else 0
                ) + (E735 + E736 if (E731 == 4 and E734 == 5) else 0)
                self.subtotal_iva_10 += (
                    EA008 if (E731 == 1 and E734 == 10) else 0
                ) + (E735 + E736 if (E731 == 4 and E734 == 10) else 0)
                self.iva_5 += E736 if E734 == 5 else 0
                self.iva_10 += E736 if E734 == 10 else 0
                self.base_gravada_5 += E735 if E734 == 5 else 0
                self.base_gravada_10 += E735 if E734 == 10 else 0

                if detalle.imputa_iva:
                    self.subtotal_imputa_iva += detalle.monto_neto
                    self.st_base_gravada_imputa_iva += (
                        detalle.base_gravada_imputa_iva
                    )
                    self.st_liquidacion_iva_imputa += (
                        detalle.liquidacion_iva_imputa
                    )

                    self.st_base_no_imputa_iva += Decimal(
                        detalle.base_no_imputa_iva
                    )
                else:
                    self.st_base_no_imputa_iva += detalle.monto_neto

            self.descuento_item += Decimal(
                round_ext(detalle.descuento * detalle.cantidad, 8)
            )
            self.descuento_global += Decimal(
                round_ext(detalle.descuento_global * detalle.cantidad, 8)
            )
            self.monto_total += detalle.monto_neto
            self.monto_total_mb += detalle.monto_neto_mb

        self.subtotal_exo_exe = round_ext(
            self.monto_exonerado + self.monto_exenta, self.moneda_decimal
        )
        self.monto_exonerado_mb = round_ext(
            Decimal(self.monto_exonerado) * Decimal(self.tasa_cambio), 0
        )
        self.monto_exenta_mb = round_ext(
            Decimal(self.monto_exenta) * Decimal(self.tasa_cambio), 0
        )
        self.base_gravada_10 = round_ext(
            self.base_gravada_10, self.moneda_decimal
        )
        self.base_gravada_10_mb = round_ext(
            Decimal(self.base_gravada_10) * Decimal(self.tasa_cambio), 0
        )
        self.base_gravada_5 = round_ext(
            self.base_gravada_5, self.moneda_decimal
        )
        self.base_gravada_5_mb = round_ext(
            Decimal(self.base_gravada_5) * Decimal(self.tasa_cambio), 0
        )
        self.iva_10 = round_ext(self.iva_10, self.moneda_decimal)
        self.iva_10_mb = round_ext(
            Decimal(self.iva_10) * Decimal(self.tasa_cambio), 0
        )
        self.iva_5 = round_ext(self.iva_5, self.moneda_decimal)
        self.iva_5_mb = round_ext(
            Decimal(self.iva_5) * Decimal(self.tasa_cambio), 0
        )
        self.monto_total = round_ext(self.monto_total, self.moneda_decimal)


class DocumentoDetalle(BaseModel):
    """Detalle de Documento"""

    id: PositiveInt | None = None
    documento: int | None = None
    orden: int | None = None
    item_tipo: str | None = None
    centro_costo: CentroCosto | int | None = None
    item: Item | int | None = None
    item_id: int | None = None
    item_secuencia: int | None = None
    item_codigo: str | None = None
    item_gtin: str | None = None
    item_nombre: str | None = None
    item_descripcion: str | None = None
    item_medida: MedidaConfig | int | None = None
    moneda: CurrencyConfig | str | None = Field(exclude=True, default=None)
    moneda_decimal: int = Field(exclude=True, default=1)
    cantidad: Decimal = 1
    item_info: str | None = None
    precio: Decimal = 0
    tasa_cambio: Decimal = 1
    monto_bruto: Decimal = 0
    descuento: Decimal = 0
    porcentaje_descuento: Decimal = 0
    descuento_global: Decimal = 0
    monto_neto: Decimal = 0
    monto_neto_mb: Decimal = 0

    # Liquidación de IVA de Documento y para el caso de documentos emitidos
    afectacion_iva: AfectacionIVAEnum | int | None = None
    proporcion_iva: int = 100  # Proporción Gravada del IVA
    tasa_iva: int = 0
    base_gravada_iva: Decimal = 0
    liquidacion_iva: Decimal = 0
    base_exenta_iva: Decimal = 0
    base_gravada_iva_mb: Decimal = 0
    liquidacion_iva_mb: Decimal = 0
    base_exenta_iva_mb: Decimal = 0

    # Liquidación del IVA Soportado: Facturas Recibidas y Aplicación de la Prorrata.
    imputa_iva: bool = True
    proporcion_imputa_iva: int = 100  # Prorrateo Imputa IVA
    base_gravada_imputa_iva: Decimal = 0
    base_gravada_imputa_iva_mb: Decimal = 0
    liquidacion_iva_imputa: Decimal = 0
    liquidacion_iva_imputa_mb: Decimal = 0
    base_no_imputa_iva: Decimal = 0
    base_no_imputa_iva_mb: Decimal = 0

    # Campos costeo de gastos y/o productos neto sin IVA
    tipo_costo: CostoTipoEnum = CostoTipoEnum.DIRECTO
    costo: Decimal = 0
    costo_mb: Decimal = 0
    monto_neto_sin_iva: Decimal = 0
    monto_neto_sin_iva_mb: Decimal = 0

    # Campo de especificación de Renta y Contabilidad
    es_grava_dedu_renta: bool = False
    renta: TipoRentaEnum | str | None = None
    actividad_economica: str | None = None
    obligacion: int | None = None
    marangatu_id: int | None = None

    @model_validator(mode="after")
    def calcular_valores(self) -> "DocumentoDetalle":
        """Calcula todos los campos derivados después de la inicialización."""
        # 1. Inicializar variables y logging
        logging.debug(
            f"Calculando montos para {getattr(self, 'item_nombre', 'N/A')}"
        )

        # 2. Calcular monto_bruto
        if (
            hasattr(self, "precio")
            and hasattr(self, "cantidad")
            and self.precio
        ):
            self.monto_bruto = round_ext(
                self.precio * self.cantidad, self.moneda_decimal
            )

        # 3. Calcular monto_neto
        if hasattr(self, "monto_bruto"):
            self.monto_neto = round_ext(
                self.monto_bruto
                - (self.descuento * self.cantidad)
                - (self.descuento_global * self.cantidad),
                self.moneda_decimal,
            )

        # 4. Calcular monto_neto_mb
        if hasattr(self, "monto_neto") and hasattr(self, "tasa_cambio"):
            self.monto_neto_mb = round_ext(
                self.monto_neto * self.tasa_cambio, 0
            )

        # 5. Calcular base_gravada_iva
        if (
            hasattr(self, "monto_neto")
            and hasattr(self, "tasa_iva")
            and hasattr(self, "proporcion_iva")
            and hasattr(self, "afectacion_iva")
        ):
            if self.tasa_iva != 0:
                self.base_gravada_iva = round_ext(
                    cal_base_gravada_iva(
                        self.monto_neto,
                        self.tasa_iva,
                        self.proporcion_iva,
                        self.afectacion_iva,
                    ),
                    self.moneda_decimal,
                )

        # 6. Calcular base_gravada_iva_mb
        if hasattr(self, "base_gravada_iva") and hasattr(self, "tasa_cambio"):
            self.base_gravada_iva_mb = round_ext(
                self.base_gravada_iva * self.tasa_cambio, self.moneda_decimal
            )

        # 7. Calcular liquidacion_iva
        if (
            hasattr(self, "monto_neto")
            and hasattr(self, "tasa_iva")
            and hasattr(self, "proporcion_iva")
            and hasattr(self, "afectacion_iva")
        ):
            if self.tasa_iva != 0:
                self.liquidacion_iva = round_ext(
                    cal_base_gravada_iva(
                        self.monto_neto,
                        self.tasa_iva,
                        self.proporcion_iva,
                        self.afectacion_iva,
                    )
                    * Decimal(self.tasa_iva / 100),
                    self.moneda_decimal,
                )

        # 8. Calcular liquidacion_iva_mb
        if hasattr(self, "liquidacion_iva") and hasattr(self, "tasa_cambio"):
            self.liquidacion_iva_mb = round_ext(
                self.liquidacion_iva * self.tasa_cambio, 0
            )

        # 9. Calcular base_exenta_iva
        if hasattr(self, "monto_neto") and hasattr(self, "afectacion_iva"):
            afectacion = self.afectacion_iva
            if (
                afectacion == AfectacionIVAEnum.GRAVADO_PARCIAL
                or afectacion == AfectacionIVAEnum.GRAVADO_IVA
            ):
                monto = self.monto_neto
                prop = self.proporcion_iva
                tasa = self.tasa_iva
                self.base_exenta_iva = round_ext(
                    (100 * monto * (100 - prop)) / (10000 + (tasa * prop)),
                    self.moneda_decimal,
                )
            else:
                self.base_exenta_iva = self.monto_neto

        # 10. Calcular base_exenta_iva_mb
        if hasattr(self, "base_exenta_iva") and hasattr(self, "tasa_cambio"):
            self.base_exenta_iva_mb = round_ext(
                self.base_exenta_iva * self.tasa_cambio, 0
            )

        # 11. Calcular monto_neto_sin_iva
        if hasattr(self, "monto_neto") and hasattr(
            self, "liquidacion_iva_imputa"
        ):
            self.monto_neto_sin_iva = round_ext(
                self.monto_neto - self.liquidacion_iva_imputa
            )

        # 12. Calcular monto_neto_sin_iva_mb
        if hasattr(self, "monto_neto_sin_iva") and hasattr(
            self, "tasa_cambio"
        ):
            self.monto_neto_sin_iva_mb = round_ext(
                self.monto_neto_sin_iva * self.tasa_cambio
            )

        # 13. Calcular base_gravada_imputa_iva
        if (
            hasattr(self, "imputa_iva")
            and self.imputa_iva
            and hasattr(self, "monto_neto")
            and hasattr(self, "proporcion_imputa_iva")
        ):
            self.base_gravada_imputa_iva = round_ext(
                cal_base_gravada_iva(
                    self.monto_neto,
                    self.tasa_iva,
                    self.proporcion_iva,
                    self.afectacion_iva,
                )
                * Decimal(self.proporcion_imputa_iva / 100),
                self.moneda_decimal,
            )

        # 14. Calcular base_gravada_imputa_iva_mb
        if hasattr(self, "base_gravada_imputa_iva") and hasattr(
            self, "tasa_cambio"
        ):
            self.base_gravada_imputa_iva_mb = round_ext(
                self.base_gravada_imputa_iva * self.tasa_cambio, 0
            )

        # 15. Calcular liquidacion_iva_imputa
        if (
            hasattr(self, "imputa_iva")
            and self.imputa_iva
            and hasattr(self, "liquidacion_iva")
        ):
            self.liquidacion_iva_imputa = round_ext(
                self.liquidacion_iva
                * Decimal(self.proporcion_imputa_iva / 100),
                self.moneda_decimal,
            )

        # 16. Calcular liquidacion_iva_imputa_mb
        if hasattr(self, "liquidacion_iva_imputa") and hasattr(
            self, "tasa_cambio"
        ):
            self.liquidacion_iva_imputa_mb = round_ext(
                self.liquidacion_iva_imputa * self.tasa_cambio, 0
            )

        # 17. Calcular base_no_imputa_iva
        if (
            hasattr(self, "monto_neto")
            and hasattr(self, "base_gravada_imputa_iva")
            and hasattr(self, "liquidacion_iva_imputa")
        ):
            self.base_no_imputa_iva = round_ext(
                self.monto_neto
                - self.base_gravada_imputa_iva
                - self.liquidacion_iva_imputa,
                self.moneda_decimal,
            )

        # 18. Calcular base_no_imputa_iva_mb
        if hasattr(self, "base_no_imputa_iva") and hasattr(
            self, "tasa_cambio"
        ):
            self.base_no_imputa_iva_mb = round_ext(
                self.base_no_imputa_iva * self.tasa_cambio, 0
            )

        return self


class DocumentoAsociado(BaseModel):
    id: PositiveInt | None = None
    documento: Documento | int | None = None
    complementario: Documento | int | None = None
    tipo_documento: MedioDocumentoAsociadoEnum | int | None = None
    cdc: str | None = None
    timbrado: int | None = None
    numero_comprobante: str | None = None
    tipo_documento_asociado: TipoDocumentoAsociadoEnum | int | None = None
    fecha_documento: date | None = None
    numero_resolucion_cf: str | None = None
    tipo_constancia: TipoConstanciaAsociadoEnum | int | None = None
    numero_constancia: int | None = None
    numero_control_constancia: int | None = None


class DocumentoMarangatu(BaseModel):
    id: int | None = None
    operacion: int | None = None
    documento: int | None = None
    tipo_registro: int
    clase: int = Field(ge=0)
    cod_dnit: str | None = None
    comprobante: int = Field(ge=0)
    dcomprobante: str | None = None
    comprobante_nombre: str | None = None
    timbrado: int | None = None
    serie: str | None = None
    numero_comprobante: str
    medio_generacion: str | None = Field(max_length=1)
    tipo_documento: str | None = None  # Tipo documento razon social
    ruc: str
    razon_social: str
    fecha_documento: date
    condicion_operacion: bool = False
    importe_iva10: float = 0
    iva10: float = 0
    importe_iva5: float = 0
    iva5: float = 0
    importe_exenta: float = 0
    total: float = 0
    imputa_iva: bool = False
    imputa_ire: bool = False
    imputa_irp: bool = False
    no_imputa: bool = False
    asoc_documento: str | None = None
    asoc_timbrado: int | None = None
    cdc: str | None = None

    monto_gravado: float = 0
    monto_no_gravado: float = 0

    descripcion_bien: str | None = None
    identificacion_empleador_ips: str | None = None
    numero_cuenta: str | None = None
    entidad_financiera: str | None = None
    fecha_registro: date | None = None

    json_documento: str | None = None
    origen: int = 1
    imputado: bool = False
    cargado: bool = False
    conciliado: bool = False
    formulario: int | None = None


class NominarDocumento(BaseModel):
    """Modelo para nominar el documento"""

    referencia: Optional[UUID4] = Field(
        None, description="Referencia del documento"
    )

    cdc: Optional[str] = Field(
        None,
        min_length=44,
        max_length=44,
        description="Código de Control del documento",
    )
    motivo: str = Field(
        ...,
        min_length=5,
        max_length=500,
        description="Motivo de la nominación",
    )
    contacto_id: int = Field(..., description="ID del contacto")

    @field_validator("motivo")
    @classmethod
    def validate_motivo(cls, v: str) -> str:
        if len(v) < 5:
            raise ValueError("El motivo debe tener al menos 5 caracteres.")
        if len(v) > 500:
            raise ValueError("El motivo no debe exceder los 500 caracteres.")
        return v

    model_config = {
        "json_schema_extra": {
            "error_messages": {
                "cdc": {
                    "min_length": "El CDC debe tener 44 caracteres.",
                    "max_length": "El CDC debe tener 44 caracteres.",
                },
                "motivo": {
                    "min_length": "El motivo debe tener al menos 5 caracteres.",
                    "max_length": "El motivo no debe exceder los 500 caracteres.",
                },
                "contacto": {
                    "type_error": "El contacto ingresado no es válido.",
                    "value_error": "El contacto es requerido.",
                },
            }
        }
    }


class DocumentoInutilizado(BaseModel):
    """Documento emitido inutilizado o dado de baja.

    Attributes:
        id (int): Identificador único
        sucursal (int): ID de la sucursal
        comprobante (int): ID del comprobante
        fecha_documento (date): Fecha de inutilización/baja
        timbrado (int | None): ID del timbrado
        serie (str | None): Serie del documento
        establecimiento (str): Código de establecimiento
        punto_expedicion (str): Punto de expedición
        rango_inicio (int): Número inicial del rango
        rango_final (int): Número final del rango
        tipo_inutilizacion (int): Tipo de inutilización
        motivo_comunicacion (int | None): ID del motivo de comunicación
        motivo (str): Descripción del motivo
        es_vigente (bool): Estado de vigencia
        situacion (str): Situación del evento
        respuesta (str | None): Respuesta del Sifen
        documento (int | None): ID del documento relacionado
    """

    id: Optional[int] = None
    sucursal: int | Sucursal = Field(
        ..., description="ID o instancia de la sucursal"
    )
    comprobante: int | Comprobante = Field(
        ..., description="ID o instancia del comprobante"
    )
    fecha_documento: date
    timbrado: int | Timbrado | None = Field(
        None, description="ID o instancia del timbrado del documento"
    )
    serie: Optional[str] = Field(None, max_length=2)
    establecimiento: str = Field(..., max_length=3)
    punto_expedicion: str = Field(..., max_length=3)
    rango_inicio: int
    rango_final: int
    tipo_inutilizacion: TipoComunicacionBajaEnum | None = Field(
        default=TipoComunicacionBajaEnum.BAJA,
        description="Tipo de inutilización o baja",
    )
    motivo_comunicacion: int | MotivoComunicacionBaja | None = Field(
        None, description="ID o instancia del motivo de comunicación"
    )
    motivo: str = Field(..., max_length=255)
    es_vigente: bool = Field(
        default=True, description="Indica si la inutilizacion es vigente"
    )
    situacion: SituacionFEEnum = Field(
        default=SituacionFEEnum.INUTILIZADO, description="Situacion del evento"
    )
    respuesta: Optional[str] = Field(None, max_length=255)
    documento: Optional[int] = None

    @field_validator("rango_final")
    def validar_rangos(cls, v: int, info) -> int:
        rango_inicio = info.data.get("rango_inicio")
        if rango_inicio and v < rango_inicio:
            raise ValueError(
                "El rango final no puede ser menor al rango inicial"
            )
        return v

    @field_validator("tipo_inutilizacion", mode="before")
    @classmethod
    def set_default_tipo_inutilizacion(cls, v):
        if v is None:
            return TipoComunicacionBajaEnum.BAJA
        return v


# Importación circular para resolver referencias

# Rebuilding models
Documento.model_rebuild()
DocumentoDetalle.model_rebuild()

Documento.model_rebuild()
