from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models import ApplicationStatus


class ApplicationCreate(BaseModel):
    empresa: str = Field(min_length=1, max_length=150)
    cargo: str = Field(min_length=1, max_length=150)
    link: str | None = Field(default=None, max_length=2048)
    salario: str | None = Field(default=None, max_length=120)
    requisitos: str | None = Field(default=None, max_length=5000)
    status: ApplicationStatus = ApplicationStatus.enviado
    anotacoes: str | None = None
    data_candidatura: datetime | None = None

    @field_validator("empresa", "cargo")
    @classmethod
    def trim_required_text(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("O campo não pode ficar vazio.")
        return value

    @field_validator("salario", "requisitos")
    @classmethod
    def trim_optional_text(cls, value: str | None) -> str | None:
        value = value.strip() if value is not None else None
        return value or None


class ApplicationUpdate(BaseModel):
    empresa: str | None = Field(default=None, min_length=1, max_length=150)
    cargo: str | None = Field(default=None, min_length=1, max_length=150)
    link: str | None = Field(default=None, max_length=2048)
    salario: str | None = Field(default=None, max_length=120)
    requisitos: str | None = Field(default=None, max_length=5000)
    status: ApplicationStatus | None = None
    anotacoes: str | None = None
    data_candidatura: datetime | None = None

    @field_validator("empresa", "cargo")
    @classmethod
    def validate_required_text(cls, value: str | None) -> str | None:
        if value is None:
            raise ValueError("O campo não pode ser nulo.")
        value = value.strip()
        if not value:
            raise ValueError("O campo não pode ficar vazio.")
        return value

    @field_validator("status")
    @classmethod
    def validate_status(cls, value: ApplicationStatus | None) -> ApplicationStatus:
        if value is None:
            raise ValueError("O status não pode ser nulo.")
        return value

    @field_validator("data_candidatura")
    @classmethod
    def validate_application_date(cls, value: datetime | None) -> datetime:
        if value is None:
            raise ValueError("A data da candidatura não pode ser nula.")
        return value

    @field_validator("salario", "requisitos")
    @classmethod
    def trim_optional_text(cls, value: str | None) -> str | None:
        value = value.strip() if value is not None else None
        return value or None


class ApplicationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    empresa: str
    cargo: str
    link: str | None
    salario: str | None
    requisitos: str | None
    status: ApplicationStatus
    anotacoes: str | None
    data_candidatura: datetime
    criado_em: datetime
    atualizado_em: datetime


class FunnelSummary(BaseModel):
    total: int
    por_status: dict[ApplicationStatus, int]
