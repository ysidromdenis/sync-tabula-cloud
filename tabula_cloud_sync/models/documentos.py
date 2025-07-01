from __future__ import annotations

import logging
import uuid
from datetime import date, datetime, time
from decimal import Decimal
from enum import Enum
from typing import TYPE_CHECKING, List, Optional

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

from .remisiones import Remision

if TYPE_CHECKING:
    # Solo para verificación de tipos, no se ejecuta en tiempo de ejecución
    from .remisiones import CargaGeneral, Remision, TransporteMercaderia


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
    sucursal: int = 1
    formulario: int | None = None
    operacion: int | None = None
    numero: int | None = None
    comprobante: int | None = None
    dcomprobante: str | None = None
    fecha_operacion: date | None = None
    fecha_documento: date | None = None
    hora_documento: time | None = None
    fecha_traslado: date | None = None
    contacto: int | None = None
    jcontacto: dict = Field(default_factory=dict)
    es_operacion_exonerada_iva: bool = False
    moneda: str | None = None
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
    agente_interno: int | None = None
    timbrado: int | None = None
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
    centro_costo: int | None = None
    item: int | None = None
    item_id: int | None = None
    item_secuencia: int | None = None
    item_codigo: str | None = None
    item_gtin: str | None = None
    item_nombre: str | None = None
    item_descripcion: str | None = None
    item_medida: int | None = None
    moneda: str = Field(exclude=True, default=None)
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

    # Liquidación de IVA para el caso de documentos
    # recibidos y documento recibido con IVA diferenciado
    imputa_iva: bool = True
    proporcion_imputa_iva: int = 100  # Proporción Imputa IVA
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


# Importación circular para resolver referencias
from .remisiones import (  # noqa: F401
    CargaGeneral,
    DocumentoDetalleRemision,
    Remision,
    TransporteMercaderia,
)

# Rebuilding models
Documento.model_rebuild()
DocumentoDetalle.model_rebuild()
