"""Trilha de auditoria dos atendimentos (etapa 2).

Alimentada exclusivamente pela trigger trg_audita_atendimento. A aplicação lê,
nunca escreve. id_atendimento não tem FK de propósito: o registro precisa
sobreviver à exclusão do atendimento original.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy import BigInteger, CheckConstraint, String, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from sgh.models.base import Base


class AuditoriaAtendimento(Base):
    __tablename__ = "auditoria_atendimento"

    id_auditoria: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    id_atendimento: Mapped[int | None]
    operacao: Mapped[str] = mapped_column(String(10))
    usuario: Mapped[str] = mapped_column(String(100))
    data_hora: Mapped[datetime] = mapped_column(server_default=func.current_timestamp())
    dados_antigos: Mapped[dict[str, Any] | None] = mapped_column(JSONB)
    dados_novos: Mapped[dict[str, Any] | None] = mapped_column(JSONB)

    __table_args__ = (
        CheckConstraint(
            "operacao IN ('INSERT', 'UPDATE', 'DELETE')",
            name="ck_auditoria_atendimento_operacao",
        ),
    )
