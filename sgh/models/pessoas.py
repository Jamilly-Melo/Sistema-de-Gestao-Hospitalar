"""Pessoa e suas especializações.

Não há herança de tabela unida aqui, embora o DDL desenhe a hierarquia: as
especializações não são disjuntas por constraint (nada impede uma pessoa de ser
paciente e profissional ao mesmo tempo) e não existe coluna discriminadora.
Relacionamentos 1:1 representam o schema fielmente.

Referências a models de outros módulos usam string — o registry do SQLAlchemy as
resolve na configuração dos mappers, não no import, o que evita ciclos.
"""

from __future__ import annotations

from datetime import date

from sqlalchemy import CHAR, CheckConstraint, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from sgh.models.base import Base


class Pessoa(Base):
    __tablename__ = "pessoa"

    id_pessoa: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str] = mapped_column(String(100))
    cpf: Mapped[str] = mapped_column(CHAR(11), unique=True)
    data_nascimento: Mapped[date]
    is_flamengo: Mapped[bool] = mapped_column(default=False)
    telefone: Mapped[str] = mapped_column(String(20))
    endereco: Mapped[str] = mapped_column(String(200))

    paciente: Mapped["Paciente | None"] = relationship(
        back_populates="pessoa", passive_deletes=True
    )
    profissional: Mapped["Profissional | None"] = relationship(
        back_populates="pessoa", passive_deletes=True
    )

    __table_args__ = (
        CheckConstraint("cpf ~ '^[0-9]{11}$'", name="ck_pessoa_cpf"),
        CheckConstraint("TRIM(nome) <> ''", name="ck_pessoa_nome"),
        CheckConstraint(
            "data_nascimento <= CURRENT_DATE", name="ck_pessoa_data_nascimento"
        ),
    )


class Paciente(Base):
    __tablename__ = "paciente"

    id_pessoa: Mapped[int] = mapped_column(
        ForeignKey("pessoa.id_pessoa", onupdate="CASCADE", ondelete="CASCADE"),
        primary_key=True,
    )
    num_convenio: Mapped[str] = mapped_column(String(30), unique=True)
    grupo_sanguineo: Mapped[str] = mapped_column(String(3))

    pessoa: Mapped["Pessoa"] = relationship(back_populates="paciente")
    alergias: Mapped[list["PacienteAlergia"]] = relationship(
        back_populates="paciente", passive_deletes=True
    )
    # `atendimentos` é acrescentado na Task 3, quando Atendimento existir.

    __table_args__ = (
        CheckConstraint(
            "grupo_sanguineo IN ('A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-')",
            name="ck_paciente_grupo_sanguineo",
        ),
    )


class PacienteAlergia(Base):
    __tablename__ = "paciente_alergia"

    id_paciente: Mapped[int] = mapped_column(
        ForeignKey("paciente.id_pessoa", onupdate="CASCADE", ondelete="CASCADE"),
        primary_key=True,
    )
    id_alergia: Mapped[int] = mapped_column(
        ForeignKey("alergia.id_alergia", onupdate="CASCADE", ondelete="RESTRICT"),
        primary_key=True,
    )

    paciente: Mapped["Paciente"] = relationship(back_populates="alergias")
    # `alergia` é acrescentado na Task 3, quando Alergia existir.


class Profissional(Base):
    __tablename__ = "profissional"

    id_pessoa: Mapped[int] = mapped_column(
        ForeignKey("pessoa.id_pessoa", onupdate="CASCADE", ondelete="CASCADE"),
        primary_key=True,
    )
    crm: Mapped[str] = mapped_column(String(20), unique=True)
    data_admissao: Mapped[date]
    especialidade: Mapped[str] = mapped_column(String(100))

    pessoa: Mapped["Pessoa"] = relationship(back_populates="profissional")
    residente: Mapped["Residente | None"] = relationship(
        back_populates="profissional", passive_deletes=True
    )
    preceptor: Mapped["Preceptor | None"] = relationship(
        back_populates="profissional", passive_deletes=True
    )

    __table_args__ = (
        CheckConstraint(
            "data_admissao <= CURRENT_DATE", name="ck_profissional_data_admissao"
        ),
        CheckConstraint(
            "TRIM(especialidade) <> ''", name="ck_profissional_especialidade"
        ),
    )


class Residente(Base):
    __tablename__ = "residente"

    id_profissional: Mapped[int] = mapped_column(
        ForeignKey("profissional.id_pessoa", onupdate="CASCADE", ondelete="CASCADE"),
        primary_key=True,
    )
    ano_residencia: Mapped[str] = mapped_column(String(2))

    profissional: Mapped["Profissional"] = relationship(back_populates="residente")

    __table_args__ = (
        CheckConstraint(
            "ano_residencia IN ('R1', 'R2', 'R3')", name="ck_residente_ano"
        ),
    )


class Preceptor(Base):
    __tablename__ = "preceptor"

    id_profissional: Mapped[int] = mapped_column(
        ForeignKey("profissional.id_pessoa", onupdate="CASCADE", ondelete="CASCADE"),
        primary_key=True,
    )
    titulacao: Mapped[str] = mapped_column(String(30))

    profissional: Mapped["Profissional"] = relationship(back_populates="preceptor")

    __table_args__ = (
        CheckConstraint(
            "titulacao IN ('ESPECIALISTA', 'MESTRE', 'DOUTOR', 'POS_DOUTOR')",
            name="ck_preceptor_titulacao",
        ),
    )
