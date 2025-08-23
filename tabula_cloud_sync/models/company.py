import uuid
from datetime import date, datetime
from typing import ForwardRef, Optional

from pydantic import UUID4, BaseModel, EmailStr, Field
from tabula_enums.contact import (
    CategoriaPerfilEnum,
    CategoriaSETEnum,
    MesCierreSETEnum,
    SituacionSETEnum,
    TipoContactoEnum,
    TipoDocumentoEnum,
)
from tabula_enums.form import SituacionEnum
from tabula_enums.impuestos import TipoRentaEnum

from .base import ActividadEconomica, Departamento, Distrito, Localidad


def generate_uuid():
    return str(uuid.uuid4())


ProfileCompany = ForwardRef("ProfileCompany")
Company = ForwardRef("Company")


class Sucursal(BaseModel):
    """Sucursal de la empresa"""

    id: int | None = None
    descripcion: str
    direccion: str | None = None
    direccion1: str | None = None
    direccion2: str | None = None
    nrocasa: int = 0
    departamento: Departamento | int
    departamento_nombre: str = Field(exclude=True, default=None)
    distrito: Distrito | int
    distrito_nombre: str = Field(exclude=True, default=None)
    localidad: Localidad | int | None = None
    localidad_nombre: str = Field(exclude=True, default=None)
    email: EmailStr | None = None
    telefono: str | None = None
    activo: SituacionEnum = SituacionEnum.ACTIVO
    company: Company | UUID4 | None = None


class Domain(BaseModel):
    """Dominio de la empresa"""

    id: int
    domain: str
    tenant_id: UUID4
    tenant_name: str
    is_primary: bool = True


class TenantGroup(BaseModel):
    """Grupo de permisos de la empresa"""

    id: int
    name: str
    secuencia: int
    group_name: str
    description: str
    es_activo: bool
    es_administrador: bool
    tenant: str | UUID4 | None = None
    permissions: list[str]


class MarangatuSetting(BaseModel):
    profile: UUID4 | None = None
    es_tercero: bool = False
    documento: str | None = None
    contrasena: str


class Company(BaseModel):
    """Empresa"""

    uuid: UUID4 = Field(default_factory=generate_uuid)
    sucursales: list[Sucursal] = []
    profiles: ProfileCompany | None = None
    schema_name: str | None = None
    created: datetime | None = None
    modified: datetime | None = None
    documento: str | None = None
    name: str | None = None
    slug: str | None = None
    description: str | None = None
    activo: bool = True
    owner: UUID4 | None = None
    parent: "Company" | UUID4 | None = None
    # tenant_groups: list[TenantGroup]
    tenant_groups: list[TenantGroup] | None = None
    domains: list[Domain] | None = None


class CompanyBuscador(BaseModel):
    uuid: UUID4 = Field(
        ...,
    )
    codigo: int = Field(
        ...,
    )
    numedocu_docudv: str = Field(
        ...,
    )
    nombre_nombfict: str = Field(
        ...,
    )
    activo: bool = Field(
        ...,
    )

    @classmethod
    def get_header(cls):
        """Generar headers"""
        field_header = {
            "uuid": "ID",
            "codigo": "Código",
            "numedocu_docudv": "Documento",
            "nombre_nombfict": "Nombre",
            "activo": "Activo",
        }
        return [
            field_header.get(field_name, field_name)
            for field_name in cls.__fields__.keys()
        ]


class ProfileObligacion(BaseModel):
    """Obligaciones tributarias de la empresa"""

    id: int | None = None
    fecha_inicio: date
    fecha_fin: date | None = None
    profile_company: UUID4 | None = None
    obligacion: int | None = None
    impuesto: str | None = None
    obligacion_nombre: str = Field(..., exclude=True)


class ProfileActividad(BaseModel):
    """Actividades económicas tributarias de la empresa"""

    id: int | None = None
    actividad_economica: ActividadEconomica | str
    actividad_economica_nombre: str = Field(..., exclude=True)
    fecha_inicio: date
    fecha_fin: date | None = None
    imputa_iva: bool
    renta: TipoRentaEnum = TipoRentaEnum.IRE
    profile_company: UUID4


class ProfileCompany(BaseModel):
    """Perfil de la empresa"""

    uuid: UUID4 = Field(default_factory=generate_uuid)
    codigo: int | None = None
    categoria: CategoriaPerfilEnum = CategoriaPerfilEnum.CONTRIBUYENTE
    numedocu: str | None = None
    docudv: int | None = None
    ctipodocu: TipoDocumentoEnum = TipoDocumentoEnum.CEDULA_PARAGUAYA
    tipodocu: str | None = None
    nombre: str | None = None
    nombfict: str | None = None
    ctipocont: TipoContactoEnum | None = None
    situacion_set: Optional[SituacionSETEnum] = None
    categoria_set: Optional[CategoriaSETEnum] = None
    mes_cierre_set: MesCierreSETEnum = MesCierreSETEnum.DICIEMBRE
    email_set: EmailStr | None = None
    telefono: str | None = None
    email_fe: str | None = None
    id_csc: str | None = None
    csc: str | None = None
    fecha_nacimiento: date | None = None
    fecha_inicio: date | None = None
    es_importador: bool = False
    es_exportador: bool = False
    es_ley_285: bool = False
    es_emisor_fe: bool = False
    company: Company | UUID4 | None = None
    obligaciones: list[ProfileObligacion] = []
    actividades_economicas: list[ProfileActividad] = []
    marangatu_setting: MarangatuSetting | UUID4 | None = None


class User(BaseModel):
    uuid: UUID4
    password: str
    last_login: datetime
    is_active: bool
    is_verified: bool
    date_joined: datetime
    username: str
    first_name: str
    last_name: str
    email: str
    tenants: list[str]
    groups: list[int]
