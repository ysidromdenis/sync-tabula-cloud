import uuid
from datetime import date, time
from decimal import Decimal
from typing import ForwardRef, List

from pydantic import UUID4, BaseModel, Field, PositiveInt, validator


# Calculos auxiliares
def round_ext(num, decimales=0):
    factor = 10**decimales
    entero = int(num * factor)
    decimal = num * factor - entero
    if decimal >= 0.5:
        redondeado = (entero + 1) / factor
    else:
        redondeado = entero / factor
    return redondeado


def cal_base_gravada_iva(monto_neto, tasa_iva, proporcion_iva, afectacion_iva):
    """Calculo base gravada del IVA"""
    if tasa_iva == 0 or proporcion_iva == 0:
        return 0
    if True:
        return (
            100
            * monto_neto
            * Decimal(proporcion_iva)
            / (10000 + tasa_iva * proporcion_iva)
        )
    return 0


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


class Documento(BaseModel):
    """
    Este módulo define la clase Documento.
    """

    id: PositiveInt | None = None
    referencia: UUID4 = Field(default_factory=uuid.uuid4)
    periodo: int | None = None
    sucursal: int = 1
    formulario: int | None = None
    operacion: int = 1
    numero: int | None = None
    comprobante: int = 16
    dcomprobante: str | None = None
    fecha_operacion: date | None = None
    fecha_documento: date | None = None
    hora_documento: time | None = None
    fecha_traslado: date | None = None
    contacto: int | None = None
    jcontacto: dict = Field(default_factory=dict)
    es_operacion_exonerada_iva: bool = False
    moneda: str = "PYG"
    moneda_decimal: int = 0
    condicion_cambio: int = 1
    tasa_cambio: Decimal = 1
    condicion_operacion: bool = True
    es_vigente: bool = True
    motivo_anulacion: str | None = None
    info_interno: str | None = None
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
    tipo_impuesto_afectado: int = 5
    tipo_transaccion: int = 1
    tipo_operacion_receptor: int = 2

    indicador_presencia: int = 1
    cdc: str
    cds: int
    info_emisor: str | None = None
    info_fisco: str | None = None
    info_adicional: dict = Field(default_factory=dict)
    jdocumento: dict = Field(default_factory=dict)
    situacion_fe: str | None = None
    jimpuesto_afecto: dict = Field(default_factory=dict)
    detalles: List[ForwardRef("DocumentoDetalle")] = []
    documentos_asociados: List[ForwardRef("DocumentoAsociado")] = []

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
            if True:
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
    documento_int: int | None = None
    orden: int | None = None
    item_tipo: str | None = None
    centro_costo: int = 1
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
    afectacion_iva: int = 1
    proporcion_iva: int = 100
    tasa_iva: int = 10
    base_gravada_iva: Decimal = 0
    liquidacion_iva: Decimal = 0
    base_exenta_iva: Decimal = 0
    base_gravada_iva_mb: Decimal = 0
    liquidacion_iva_mb: Decimal = 0
    base_exenta_iva_mb: Decimal = 0

    # Liquidación de IVA para el caso de documentos recibidos
    # y documento recibido con IVA diferenciado (mas para IRP)
    imputa_iva: bool = True
    proporcion_imputa_iva: int = 100
    base_gravada_imputa_iva: Decimal = 0
    base_gravada_imputa_iva_mb: Decimal = 0
    liquidacion_iva_imputa: Decimal = 0
    liquidacion_iva_imputa_mb: Decimal = 0
    base_no_imputa_iva: Decimal = 0
    base_no_imputa_iva_mb: Decimal = 0

    # Campos costeo de gastos y/o productos neto sin IVA
    tipo_costo: str = "D"
    costo: Decimal = 0
    costo_mb: Decimal = 0
    monto_neto_sin_iva: Decimal = 0
    monto_neto_sin_iva_mb: Decimal = 0

    # Campo de especificación de Renta y Contabilidad
    es_grava_dedu_renta: bool = False

    @validator("monto_bruto", pre=True, always=True)
    def set_monto_bruto(cls, v, values):
        """Calcula el monto bruto del detalle"""
        if "precio" in values and "cantidad" in values and values["precio"]:
            return round_ext(
                values["precio"] * values["cantidad"], values["moneda_decimal"]
            )
        else:
            return 0

    @validator("monto_neto", pre=True, always=True)
    def set_monto_neto(cls, v, values):
        """Calcula el monto neto del detalle"""
        return round_ext(
            values["monto_bruto"]
            - (values["descuento"] * values["cantidad"])
            - (values["descuento_global"] * values["cantidad"]),
            values["moneda_decimal"],
        )

    @validator("monto_neto_mb", pre=False, always=True)
    def set_monto_neto_mb(cls, v, values):
        """Calcula el monto neto del detalle moneda base"""
        return round_ext(values["monto_neto"] * values["tasa_cambio"], 0)

    @validator("base_gravada_iva", pre=True, always=True)
    def set_base_gravada_iva(cls, v, values):
        """Calcula la base gravada del IVA"""
        if "monto_neto" in values and "tasa_iva" in values:
            if values["tasa_iva"] == 0:
                return 0

            return round_ext(
                cal_base_gravada_iva(
                    values["monto_neto"],
                    values["tasa_iva"],
                    values["proporcion_iva"],
                    values["afectacion_iva"],
                ),
                values["moneda_decimal"],
            )

        return 0

    @validator("base_gravada_iva_mb", pre=False, always=True)
    def set_base_gravada_iva_mb(cls, v, values):
        """Calcula la base gravada del IVA en Moneda Base"""
        if "base_gravada_iva" in values and "tasa_cambio" in values:
            return round_ext(
                values["base_gravada_iva"] * Decimal(values["tasa_cambio"]),
                values["moneda_decimal"],
            )

        return 0

    @validator("liquidacion_iva", pre=True, always=True)
    def set_liquidacion_iva(cls, v, values):
        """Calcula la liquidación del IVA"""
        if "base_gravada_iva" in values and "tasa_iva" in values:
            if values["tasa_iva"] == 0:
                return 0
            return round_ext(
                cal_base_gravada_iva(
                    values["monto_neto"],
                    values["tasa_iva"],
                    values["proporcion_iva"],
                    values["afectacion_iva"],
                )
                * Decimal(values["tasa_iva"] / 100),
                values["moneda_decimal"],
            )
        return 0

    @validator("liquidacion_iva_mb", pre=False, always=True)
    def set_liquidacion_iva_mb(cls, v, values):
        """Calcula la base gravada del IVA Moneda Base"""
        if "liquidacion_iva" in values and "tasa_cambio" in values:
            return round_ext(
                values["liquidacion_iva"] * Decimal(values["tasa_cambio"]), 0
            )

        return 0

    @validator("base_exenta_iva", pre=True, always=True)
    def set_base_exenta_iva(cls, v, values):
        """Calcula la base exenta del IVA"""
        if "monto_neto" in values:
            if True:
                return round_ext(
                    (
                        100
                        * values["monto_neto"]
                        * (100 - values["proporcion_iva"])
                    )
                    / (
                        10000 + (values["tasa_iva"] * values["proporcion_iva"])
                    ),
                    values["moneda_decimal"],
                )

        return 0

    @validator("base_exenta_iva_mb", pre=False, always=True)
    def set_base_exenta_iva_mb(cls, v, values):
        """Calcula la base exenta del IVA Moneda Base"""
        if "base_exenta_iva" in values and "tasa_cambio" in values:
            return round_ext(
                values["base_exenta_iva"] * Decimal(values["tasa_cambio"]), 0
            )

        return 0

    @validator("monto_neto_sin_iva", pre=False, always=True)
    def set_monto_neto_sin_iva(cls, v, values):
        """Calcula el monto neto sin IVA"""
        if "monto_neto" in values and "liquidacion_iva" in values:
            return round_ext(
                values["monto_neto"] - values["liquidacion_iva_imputa"]
            )

        return 0

    @validator("monto_neto_sin_iva_mb", pre=False, always=True)
    def set_monto_neto_sin_iva_mb(cls, v, values):
        """Calcula el monto neto sin IVA Moneda base"""
        if "monto_neto_sin_iva" in values and "tasa_cambio" in values:
            return round_ext(
                Decimal(values["monto_neto_sin_iva"])
                * Decimal(values["tasa_cambio"])
            )

        return 0

    @validator("base_gravada_imputa_iva", pre=True, always=True)
    def set_base_gravada_imputa_iva(cls, v, values):
        """Calcula la base gravada del IVA"""
        if "base_gravada_iva" in values and "proporcion_imputa_iva" in values:
            if values["imputa_iva"]:
                return round_ext(
                    cal_base_gravada_iva(
                        values["monto_neto"],
                        values["tasa_iva"],
                        values["proporcion_iva"],
                        values["afectacion_iva"],
                    )
                    * Decimal(values["proporcion_imputa_iva"] / 100),
                    values["moneda_decimal"],
                )

        return 0

    @validator("base_gravada_imputa_iva_mb", pre=False, always=True)
    def set_base_gravada_imputa_iva_mb(cls, v, values):
        """Calcula base gravada imputa IVA Moneda Base"""
        if "base_gravada_imputa_iva" in values:
            return round_ext(
                values["base_gravada_imputa_iva"]
                * Decimal(values["tasa_cambio"]),
                0,
            )

        return 0

    @validator("liquidacion_iva_imputa", pre=True, always=True)
    def set_liquidacion_iva_imputa(cls, v, values):
        """Calcula la base exenta del IVA"""
        if values["imputa_iva"]:
            return round_ext(
                values["liquidacion_iva"]
                * Decimal(values["proporcion_imputa_iva"] / 100),
                values["moneda_decimal"],
            )

        return 0

    @validator("liquidacion_iva_imputa_mb", pre=False, always=True)
    def set_liquidacion_iva_imputa_mb(cls, v, values):
        """Calcula la base exenta del IVA Moneda base"""
        if "liquidacion_iva_imputa" in values:
            return round_ext(
                values["liquidacion_iva_imputa"]
                * Decimal(values["tasa_cambio"]),
                0,
            )

        return 0

    @validator("base_no_imputa_iva", pre=False, always=True)
    def set_base_no_imputa_iva(cls, v, values):
        """Calcula la base exenta del IVA"""
        if (
            "base_gravada_iva" in values
            and "base_gravada_imputa_iva" in values
        ):
            return round_ext(
                values["monto_neto"]
                - values["base_gravada_imputa_iva"]
                - values["liquidacion_iva_imputa"],
                values["moneda_decimal"],
            )
        return 0

    @validator("base_no_imputa_iva_mb", pre=False, always=True)
    def set_base_no_imputa_iva_mb(cls, v, values):
        """Calcula la base exenta del IVA moneda base"""
        if "base_no_imputa_iva" in values and "tasa_cambio" in values:
            return round_ext(
                Decimal(values["base_no_imputa_iva"])
                * Decimal(values["tasa_cambio"]),
                0,
            )
        return 0


class DocumentoAsociado(BaseModel):
    id: PositiveInt | None = None
    documento: Documento | int | None = None
    complementario: Documento | int | None = None
    tipo_documento: int | None = None
    cdc: str | None = None
    timbrado: int | None = None
    numero_comprobante: str | None = None
    tipo_documento_asociado: int | None = None
    fecha_documento: date | None = None
    numero_resolucion_cf: str | None = None
    tipo_constancia: int | None = None
    numero_constancia: int | None = None
    numero_control_constancia: int | None = None
