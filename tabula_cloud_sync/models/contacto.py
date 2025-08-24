import uuid
from datetime import date

from pydantic import UUID4, BaseModel, EmailStr, Field
from tabula_enums.contact import (
    CategoriaContactoEnum,
    NaturalezaReceptorEnum,
    TipoContactoEnum,
    TipoCorreoEnum,
    TipoDocumentoEnum,
    TipoTelefonoEnum,
)

from .base import (
    Comprobante,
    ComprobanteMedioGeneracion,
    Country,
    Departamento,
    Distrito,
    Localidad,
)


def generate_uuid():
    return str(uuid.uuid4())


class Direccion(BaseModel):
    contacto: UUID4
    ipais: str
    direccion: str
    numecasa: int
    iciud: int = None
    codigo_postal: str = None


class Telefono(BaseModel):
    contacto: UUID4
    numero: str
    tipo: TipoTelefonoEnum = None
    tiene_whatsapp: bool = False
    tiene_telegram: bool = False
    es_principal: bool = False


class CorreoElectronico(BaseModel):
    direccion: EmailStr
    tipo: TipoCorreoEnum = None
    es_principal: bool = False


class Contact(BaseModel):
    id: int = 0
    uuid: UUID4 = Field(default_factory=generate_uuid)
    numedocu: str
    docudv: int | None = None
    ctipodocu: TipoDocumentoEnum = TipoDocumentoEnum.CEDULA_PARAGUAYA
    tipodocu: str | None = None
    cnaturece: NaturalezaReceptorEnum = NaturalezaReceptorEnum.NO_CONTRIBUYENTE
    nombre: str
    nombfict: str | None = None
    ctipooper: CategoriaContactoEnum = CategoriaContactoEnum.CONSUMIDOR_FINAL
    ctipocont: TipoContactoEnum | None = None
    inacionalidad: Country | str | None = (
        "PRY"  # Campo opcional con valor por defecto
    )
    direccion: str | None = None
    nrocasa: int = 0
    pais: Country | str | None = None
    departamento: Departamento | int | None = None
    distrito: Distrito | int | None = None
    localidad: Localidad | int | None = None
    email: str | None = None
    telefono: str | None = None
    celular: str | None = None
    retencion_iva: int = 0
    retencion_renta: int = 0
    website: str | None = None
    situacion: bool = True


class ContactBuscador(BaseModel):
    uuid: UUID4 = Field(
        ...,
    )
    id: int = Field(
        ...,
    )
    numedocu_docudv: str = Field(
        ...,
    )
    nombre_nombfict: str = Field(
        ...,
    )
    situacion: bool = Field(
        ...,
    )

    @classmethod
    def get_header(cls):
        """Generar headers"""
        field_header = {
            "id": "ID",
            "numedocu_docudv": "Documento",
            "nombre_nombfict": "Nombre",
            "situacion": "Situación",
        }
        return [
            field_header.get(field_name, field_name)
            for field_name in cls.__fields__.keys()
        ]


class ResultContactoData(BaseModel):
    count: int = None
    next: str = None
    previous: str = None
    results: list[ContactBuscador]


class TimbradoContacto(BaseModel):
    id: int = 0
    contacto: Contact | int
    timbrado: int
    comprobante: Comprobante | int
    establecimiento: str
    punto_expedicion: str
    fecha_inicio: date | None = None
    fecha_vencimiento: date | None = None
    medio_generacion: ComprobanteMedioGeneracion | int | None = None
    es_valido: bool | None = None
