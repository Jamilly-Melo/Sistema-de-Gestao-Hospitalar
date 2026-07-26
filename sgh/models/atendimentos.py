"""O núcleo transacional: atendimentos, procedimentos executados e internações."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import CheckConstraint, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from sgh.models.base import Base


class Atendimento(Base):
    __tablename__ = "atendimento"

    id_atendimento: Mapped[int] = mapped_column(primary_key=True)
    data_hora: Mapped[datetime]
    duracao_minutos: Mapped[int]
    id_paciente: Mapped[int] = mapped_column(
        ForeignKey("paciente.id_pessoa", onupdate="CASCADE", ondelete="RESTRICT")
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
    # Etapa 2: NOT NULL depois de alteracoes.sql.
    id_unidade: Mapped[int] = mapped_column(
        ForeignKey("unidade.id_unidade", onupdate="CASCADE", ondelete="RESTRICT")
    )

    paciente: Mapped["Paciente"] = relationship(back_populates="atendimentos")
    procedimentos: Mapped[list["ProcedimentoRealizado"]] = relationship(
        back_populates="atendimento", passive_deletes=True
    )
    internacao: Mapped["Internacao | None"] = relationship(
        back_populates="atendimento"
    )

    __table_args__ = (
        CheckConstraint("duracao_minutos > 0", name="ck_atendimento_duracao"),
    )


class ProcedimentoRealizado(Base):
    __tablename__ = "procedimento_realizado"

    id_atendimento: Mapped[int] = mapped_column(
        ForeignKey("atendimento.id_atendimento", onupdate="CASCADE", ondelete="CASCADE"),
        primary_key=True,
    )
    id_procedimento: Mapped[int] = mapped_column(
        ForeignKey(
            "procedimento.id_procedimento", onupdate="CASCADE", ondelete="RESTRICT"
        ),
        primary_key=True,
    )
    quantidade: Mapped[int]
    tempo_real_minutos: Mapped[int]
    observacao: Mapped[str | None] = mapped_column(Text)
    faturado: Mapped[bool] = mapped_column(default=False)
    # Etapa 2.
    data_hora_inicio: Mapped[datetime]

    atendimento: Mapped["Atendimento"] = relationship(back_populates="procedimentos")

    __table_args__ = (
        CheckConstraint("quantidade > 0", name="ck_procedimento_realizado_quantidade"),
        CheckConstraint(
            "tempo_real_minutos > 0", name="ck_procedimento_realizado_tempo"
        ),
    )


class Internacao(Base):
    """Etapa 2. Internação ativa enquanto data_hora_saida for NULL."""

    __tablename__ = "internacao"

    id_internacao: Mapped[int] = mapped_column(primary_key=True)
    id_atendimento: Mapped[int] = mapped_column(
        ForeignKey("atendimento.id_atendimento", onupdate="CASCADE", ondelete="RESTRICT"),
        unique=True,
    )
    data_hora_entrada: Mapped[datetime]
    data_hora_saida: Mapped[datetime | None]

    atendimento: Mapped["Atendimento"] = relationship(back_populates="internacao")

    __table_args__ = (
        CheckConstraint(
            "data_hora_saida IS NULL OR data_hora_saida >= data_hora_entrada",
            name="ck_internacao_datas",
        ),
    )
