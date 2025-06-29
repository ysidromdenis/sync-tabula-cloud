"""
Modelo base para entidades de Tabula Cloud Sync.

Proporciona funcionalidad común para todos los modelos de datos
incluyendo serialización, validación, y persistencia.
"""

import json
from abc import ABC, abstractmethod
from dataclasses import asdict, dataclass, fields
from datetime import datetime
from typing import Any, Dict, List, Optional, Union


@dataclass
class BaseModel(ABC):
    """
    Modelo base abstracto para todas las entidades.

    Proporciona funcionalidad común como serialización JSON,
    validación de datos, y conversiones de tipo.
    """

    id: Optional[Union[int, str]] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def __post_init__(self):
        """Post-inicialización para configurar timestamps."""
        if self.created_at is None:
            self.created_at = datetime.now()
        self.updated_at = datetime.now()

    def to_dict(self) -> Dict[str, Any]:
        """
        Convierte el modelo a diccionario.

        Returns:
            Diccionario con todos los campos del modelo
        """
        data = asdict(self)

        # Convertir datetime a string ISO
        for key, value in data.items():
            if isinstance(value, datetime):
                data[key] = value.isoformat()

        return data

    def to_json(self, indent: int = None) -> str:
        """
        Convierte el modelo a JSON.

        Args:
            indent: Indentación para el JSON (None para compacto)

        Returns:
            String JSON del modelo
        """
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "BaseModel":
        """
        Crea una instancia del modelo desde un diccionario.

        Args:
            data: Diccionario con los datos del modelo

        Returns:
            Nueva instancia del modelo
        """
        # Obtener los campos del modelo
        model_fields = {f.name: f.type for f in fields(cls)}

        # Preparar datos para la instancia
        instance_data = {}

        for field_name, field_type in model_fields.items():
            if field_name in data:
                value = data[field_name]

                # Convertir strings ISO a datetime
                if field_type == Optional[datetime] or field_type == datetime:
                    if isinstance(value, str):
                        try:
                            value = datetime.fromisoformat(value)
                        except ValueError:
                            value = None

                instance_data[field_name] = value

        return cls(**instance_data)

    @classmethod
    def from_json(cls, json_str: str) -> "BaseModel":
        """
        Crea una instancia del modelo desde JSON.

        Args:
            json_str: String JSON con los datos del modelo

        Returns:
            Nueva instancia del modelo
        """
        data = json.loads(json_str)
        return cls.from_dict(data)

    def update_from_dict(self, data: Dict[str, Any]) -> None:
        """
        Actualiza el modelo con datos de un diccionario.

        Args:
            data: Diccionario con los nuevos datos
        """
        model_fields = {f.name for f in fields(self)}

        for key, value in data.items():
            if key in model_fields:
                setattr(self, key, value)

        self.updated_at = datetime.now()

    @abstractmethod
    def validate(self) -> List[str]:
        """
        Valida los datos del modelo.

        Returns:
            Lista de errores de validación (vacía si es válido)
        """
        pass

    def is_valid(self) -> bool:
        """
        Verifica si el modelo es válido.

        Returns:
            True si el modelo es válido
        """
        return len(self.validate()) == 0

    def get_validation_errors(self) -> List[str]:
        """
        Obtiene los errores de validación del modelo.

        Returns:
            Lista de errores de validación
        """
        return self.validate()

    def __str__(self) -> str:
        """Representación string del modelo."""
        return f"{self.__class__.__name__}(id={self.id})"

    def __repr__(self) -> str:
        """Representación detallada del modelo."""
        return f"{self.__class__.__name__}({self.to_dict()})"


@dataclass
class SyncableModel(BaseModel):
    """
    Modelo base para entidades sincronizables con Tabula Cloud.

    Incluye campos adicionales para control de sincronización.
    """

    sync_status: str = "pending"  # pending, synced, error
    last_sync_at: Optional[datetime] = None
    sync_error: Optional[str] = None
    sync_attempts: int = 0
    external_id: Optional[str] = None  # ID en el sistema externo

    def mark_as_synced(self, external_id: str = None) -> None:
        """
        Marca el modelo como sincronizado exitosamente.

        Args:
            external_id: ID en el sistema externo (opcional)
        """
        self.sync_status = "synced"
        self.last_sync_at = datetime.now()
        self.sync_error = None
        self.sync_attempts += 1

        if external_id:
            self.external_id = external_id

    def mark_as_error(self, error: str) -> None:
        """
        Marca el modelo con error de sincronización.

        Args:
            error: Mensaje de error
        """
        self.sync_status = "error"
        self.sync_error = error
        self.sync_attempts += 1
        self.updated_at = datetime.now()

    def reset_sync_status(self) -> None:
        """Resetea el estado de sincronización."""
        self.sync_status = "pending"
        self.sync_error = None
        self.sync_attempts = 0
        self.updated_at = datetime.now()

    def needs_sync(self) -> bool:
        """
        Determina si el modelo necesita sincronización.

        Returns:
            True si necesita sincronización
        """
        return (
            self.sync_status in ["pending", "error"] and self.sync_attempts < 3
        )  # Máximo 3 intentos

    def validate(self) -> List[str]:
        """
        Validación base para modelos sincronizables.

        Returns:
            Lista de errores de validación
        """
        errors = []

        # Validar sync_status
        valid_statuses = ["pending", "synced", "error"]
        if self.sync_status not in valid_statuses:
            errors.append(f"sync_status debe ser uno de: {valid_statuses}")

        # Validar sync_attempts
        if self.sync_attempts < 0:
            errors.append("sync_attempts no puede ser negativo")

        return errors


@dataclass
class TabulaEntity(SyncableModel):
    """
    Modelo base específico para entidades de Tabula Cloud.

    Incluye campos comunes a todas las entidades de Tabula.
    """

    name: str = ""
    description: str = ""
    is_active: bool = True
    metadata: Optional[Dict[str, Any]] = None

    def __post_init__(self):
        """Post-inicialización específica para entidades de Tabula."""
        super().__post_init__()

        if self.metadata is None:
            self.metadata = {}

    def validate(self) -> List[str]:
        """
        Validación específica para entidades de Tabula.

        Returns:
            Lista de errores de validación
        """
        errors = super().validate()

        # Validar name
        if not self.name or not self.name.strip():
            errors.append("El campo 'name' es requerido")

        if len(self.name) > 255:
            errors.append("El campo 'name' no puede exceder 255 caracteres")

        # Validar description
        if len(self.description) > 1000:
            errors.append(
                "El campo 'description' no puede exceder 1000 caracteres"
            )

        return errors

    def add_metadata(self, key: str, value: Any) -> None:
        """
        Agrega metadatos al modelo.

        Args:
            key: Clave del metadato
            value: Valor del metadato
        """
        if self.metadata is None:
            self.metadata = {}

        self.metadata[key] = value
        self.updated_at = datetime.now()

    def get_metadata(self, key: str, default: Any = None) -> Any:
        """
        Obtiene un metadato del modelo.

        Args:
            key: Clave del metadato
            default: Valor por defecto si no existe

        Returns:
            Valor del metadato
        """
        if self.metadata is None:
            return default

        return self.metadata.get(key, default)
