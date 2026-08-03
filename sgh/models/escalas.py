"""Plantões de residentes supervisionados por preceptores."""

from __future__ import annotations

from datetime import date

from sqlalchemy import CheckConstraint, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from sgh.models.base import Base


class Escala(Base):
    __tablename__ = "escala"

    id_escala: Mapped[int] = mapped_column(primary_key=True)
    data_plantao: Mapped[date]
    turno: Mapped[str] = mapped_column(String(10))
    id_unidade: Mapped[int] = mapped_column(
        ForeignKey("unidade.id_unidade", onupdate="CASCADE", ondelete="RESTRICT")
    )
    id_residente: Mapped[int] = mapped_column(
        ForeignKey(
            "residente.id_profissional", onupdate="CASCADE", ondelete="RESTRICT"
        )
    )
    id_preceptor: Mapped[int] = mapped_column(
        ForeignKey(
            "preceptor.id_profissional", onupdate="CASCADE", ondelete="RESTRICT"
        )
    )

    __table_args__ = (
        CheckConstraint(
            "turno IN ('MANHA', 'TARDE', 'NOITE')", name="ck_escala_turno"
        ),
        UniqueConstraint(
            "id_unidade",
            "data_plantao",
            "turno",
            "id_residente",
            name="uq_escala_residente",
        ),
    )
