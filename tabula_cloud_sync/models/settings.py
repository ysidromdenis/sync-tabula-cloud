from datetime import date
from typing import List

from pydantic import BaseModel, Field, PositiveInt, model_validator
from tabula_enums.documents import (
    EstadoAbiertoEnum,
    SituacionPeriodoEnum,
    TipoTimbradoEnum,
)
from tabula_enums.form import SituacionEnum

from .base import Comprobante, Currency, Medida, MedidaCategoria
from .company import Sucursal


class CurrencyConfig(BaseModel):
    """COnfiguracion de mondea para la empresa"""

    id: Currency | str
    nombre: str = Field(exclude=True, default=None)
    esbase: bool = False

    def __str__(self):
        return f"{self.id} ({self.esbase})"


class MedidaConfig(BaseModel):
    """Configuracion de unidad de medida para la empresa"""

    id: PositiveInt | None = None
    nombre: str
    abreviatura: str
    categoria: MedidaCategoria | int | None = None
    medida: Medida | int | None = None
    activo: SituacionEnum = SituacionEnum.ACTIVO

    def __str__(self):
        return f"{self.abreviatura} ({self.nombre})"


class Timbrado(BaseModel):
    """Configuracion de Timbrado para la empresa"""

    id: int
    fecha_autorizacion: date
    fecha_vencimiento: date | None = None
    numero_autorizacion: str | None = None
    medio_generacion: int | TipoTimbradoEnum
    activo: SituacionEnum = SituacionEnum.ACTIVO

    def isoformat_dates(self):
        # Convierte las fechas a cadenas en formato ISO antes de la serialización JSON
        self.fecha_autorizacion = self.fecha_autorizacion.isoformat()
        if self.fecha_vencimiento:
            self.fecha_vencimiento = self.fecha_vencimiento.isoformat()


class TimbradoEstablecimientoSecuencia(BaseModel):
    """Secuencia de numeración para establecimientos de timbrado.

    Attributes:
        id (int): Identificador único
        serie (str | None): Serie del timbrado
        establecimiento (str): Código de establecimiento
        punto_expedicion (str): Punto de expedición
        siguiente_numero (int): Siguiente número disponible
        comprobante (int | Comprobante): Comprobante asociado
        siguiente_timbrado (int | None): ID del siguiente timbrado
    """

    id: int
    serie: str | None = None
    establecimiento: str
    punto_expedicion: str
    siguiente_numero: int
    comprobante: int | Comprobante
    siguiente_timbrado: int | None = None


class SecuenciaResponse(BaseModel):
    """Respuesta con lista de secuencias y total."""

    secuencias: List[TimbradoEstablecimientoSecuencia]
    total: int


class TimbradoEstablecimiento(BaseModel):
    """Establecimiento de Timbrado para la empresa"""

    id: int | None = None
    sucursal: Sucursal | int | None = None
    timbrado: Timbrado | int | None = None
    serie: str | None = None
    establecimiento: str
    punto_expedicion: str
    comprobante: Comprobante | int | None = None
    numero_inicio: int
    numero_final: int
    ultimo_numero: int | None = None
    activo: SituacionEnum = SituacionEnum.ACTIVO
    siguiente_timbrado: int | None = None
    siguiente_numero: int = 0
    siguiente_serie: str | None = None
    cantidad_minima: int = 0
    cantidad_disponibles: int = 0

    @classmethod
    def buscar_en_lista(
        cls,
        lista: list["TimbradoEstablecimiento"],
        numero_documento: int = None,
        fecha_documento: date = None,
        **criterios,
    ) -> list["TimbradoEstablecimiento"]:
        """Busca instancias que coincidan con los criterios especificados.

        Args:
            lista: Lista de instancias TimbradoEstablecimiento
            numero_documento: Número de documento a validar en el rango
            **criterios: Diccionario de campos y valores a buscar
                Ejemplo: establecimiento='001', serie='A'

        Returns:
            Lista de instancias que cumplen con los criterios
        """
        # Filtrar criterios None
        criterios = {k: v for k, v in criterios.items() if v is not None}

        resultados = []
        for item in lista:
            cumple_criterios = True

            # Validar rango si se especifica numero_documento
            if numero_documento is not None:
                if not cls._esta_en_rango(item, int(numero_documento)):
                    continue

            if fecha_documento is not None:
                if not cls._esta_en_rango_fecha(item, fecha_documento):
                    continue

            for campo, valor in criterios.items():
                if not hasattr(item, campo):
                    continue

                valor_item = getattr(item, campo)
                if isinstance(valor_item, (Comprobante, Timbrado)):
                    valor_item = valor_item.id

                if isinstance(valor_item, str) and isinstance(valor, str):
                    if valor.lower() not in valor_item.lower():
                        cumple_criterios = False
                        break

                elif str(valor_item) != str(valor):
                    cumple_criterios = False
                    break

            if cumple_criterios:
                resultados.append(item)

        return resultados

    @staticmethod
    def _esta_en_rango(item: "TimbradoEstablecimiento", numero: int) -> bool:
        """Verifica si un número está dentro del rango válido."""
        if not isinstance(numero, int):
            return False

        if numero < item.numero_inicio:
            return False

        if item.numero_final is not None and numero > item.numero_final:
            return False

        return True

    @staticmethod
    def _esta_en_rango_fecha(
        item: "TimbradoEstablecimiento", fecha: date
    ) -> bool:
        """Verifica si una fecha está dentro del rango válido."""
        if not isinstance(fecha, date):
            return False

        if isinstance(item.timbrado, Timbrado):
            if fecha < item.timbrado.fecha_autorizacion:
                return False

            if (
                item.timbrado.fecha_vencimiento is not None
                and fecha > item.timbrado.fecha_vencimiento
            ):
                return False

        return True


class Ejercicio(BaseModel):
    id: int
    fecha_inicio: date
    fecha_fin: date
    es_abierto: EstadoAbiertoEnum = EstadoAbiertoEnum.ABIERTO
    observacion: str | None = None
    ejercicio_anterior_id: int | None = None

    @model_validator(mode="after")
    def validar_fechas(self):
        """Valida que la fecha de fin no sea anterior a la fecha de inicio"""
        if (
            self.fecha_inicio
            and self.fecha_fin
            and self.fecha_fin < self.fecha_inicio
        ):
            raise ValueError(
                "La fecha de fin no puede ser anterior a la fecha de inicio"
            )
        return self


class Periodo(BaseModel):
    id: int
    fecha_inicio: date
    fecha_fin: date
    es_habilitado: SituacionPeriodoEnum = SituacionPeriodoEnum.HABILITADO
    es_abierto: EstadoAbiertoEnum = EstadoAbiertoEnum.ABIERTO
    observacion: str | None = None
    ejercicio_id: int | None = None
    periodo_anterior_id: int | None = None
