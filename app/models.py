from datetime import datetime
from enum import Enum

from sqlalchemy import DateTime, Enum as SqlEnum, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class ApplicationStatus(str, Enum):
    enviado = "enviado"
    entrevista = "entrevista"
    oferta = "oferta"
    recusado = "recusado"


class Application(Base):
    __tablename__ = "candidaturas"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    empresa: Mapped[str] = mapped_column(String(150), index=True)
    cargo: Mapped[str] = mapped_column(String(150), index=True)
    link: Mapped[str | None] = mapped_column(String(2048), nullable=True)
    salario: Mapped[str | None] = mapped_column(String(120), nullable=True)
    requisitos: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[ApplicationStatus] = mapped_column(
        SqlEnum(ApplicationStatus, native_enum=False, length=20),
        default=ApplicationStatus.enviado,
        index=True,
    )
    anotacoes: Mapped[str | None] = mapped_column(Text, nullable=True)
    data_candidatura: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    criado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    atualizado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )
