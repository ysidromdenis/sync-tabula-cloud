"""
Modelo de datos personalizado para cli.

Este archivo fue generado automáticamente por Tabula Cloud Sync.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict, Any


@dataclass
class testtabulaprojectModel:
    """Modelo de datos para cli."""

    id: Optional[int] = None
    name: str = ""
    description: str = ""
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    is_active: bool = True
    metadata: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convierte el modelo a diccionario."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "is_active": self.is_active,
            "metadata": self.metadata or {},
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "testtabulaprojectModel":
        """Crea una instancia desde un diccionario."""
        return cls(
            id=data.get("id"),
            name=data.get("name", ""),
            description=data.get("description", ""),
            created_at=(
                datetime.fromisoformat(data["created_at"])
                if data.get("created_at")
                else None
            ),
            updated_at=(
                datetime.fromisoformat(data["updated_at"])
                if data.get("updated_at")
                else None
            ),
            is_active=data.get("is_active", True),
            metadata=data.get("metadata"),
        )

    def validate(self) -> bool:
        """Valida los datos del modelo."""
        if not self.name or not self.name.strip():
            return False
        return True
