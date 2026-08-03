"""Tabelas de referência: alergias, unidades e o catálogo de procedimentos."""

from __future__ import annotations

from decimal import Decimal

from sqlalchemy import CheckConstraint, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from sgh.models.base import Base


class Alergia(Base):
    __tablename__ = "alergia"

    id_alergia: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str] = mapped_column(String(100), unique=True)

    pacientes: Mapped[list["PacienteAlergia"]] = relationship(
        back_populates="alergia"
    )

    __table_args__ = (
        CheckConstraint("TRIM(nome) <> ''", name="ck_alergia_nome"),
    )


class Unidade(Base):
    __tablename__ = "unidade"

    id_unidade: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str] = mapped_column(String(100), unique=True)
    tipo: Mapped[str] = mapped_column(String(30))
    capacidade_leitos: Mapped[int]

    __table_args__ = (
        CheckConstraint(
            "tipo IN ('ENFERMARIA', 'UTI', 'PRONTO_SOCORRO', 'AMBULATORIO')",
            name="ck_unidade_tipo",
        ),
        CheckConstraint("capacidade_leitos >= 0", name="ck_unidade_capacidade"),
    )


class Procedimento(Base):
    __tablename__ = "procedimento"

    id_procedimento: Mapped[int] = mapped_column(primary_key=True)
    codigo: Mapped[str] = mapped_column(String(20), unique=True)
    nome: Mapped[str] = mapped_column(String(100))
    tempo_medio_minutos: Mapped[int]
    nivel_risco: Mapped[str] = mapped_column(String(10))

    # Etapa 2: mantida pela trigger trg_atualiza_media_procedimentos.
    media_tempo_procedimento: Mapped[Decimal | None] = mapped_column(Numeric(10, 2))

    __table_args__ = (
        CheckConstraint("TRIM(nome) <> ''", name="ck_procedimento_nome"),
        CheckConstraint("tempo_medio_minutos > 0", name="ck_procedimento_tempo"),
        CheckConstraint(
            "nivel_risco IN ('BAIXO', 'MEDIO', 'ALTO')",
            name="ck_procedimento_nivel_risco",
        ),
    )
