"""Consultas analíticas.

Tradução de sql/consultas-analiticas/. São agregações: devolvem colunas, não
entidades — nenhum ORM transforma GROUP BY em objeto.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy import and_, desc, func, literal, nulls_last, select, text
from sqlalchemy.orm import Session

from sgh.database import fetch_all
from sgh.models import (
    Atendimento,
    Escala,
    Paciente,
    Preceptor,
    Pessoa,
    Procedimento,
    ProcedimentoRealizado,
    Profissional,
    Residente,
    Unidade,
)

# Aritmética de intervalo é específica do Postgres e o SQLAlchemy não tem um
# construtor portável para INTERVAL. text() aqui reproduz o SQL original
# literalmente, o que é mais legível do que montar o cast à mão.
_INICIO_MES = text("DATE_TRUNC('month', CURRENT_DATE)")
_FIM_MES = text("DATE_TRUNC('month', CURRENT_DATE) + INTERVAL '1 month'")


def pacientes_sem_procedimento_risco_alto(
    *, session: Session | None = None
) -> list[dict[str, Any]]:
    """Pacientes que nunca passaram por procedimento de risco ALTO."""
    tem_procedimento_alto = (
        select(literal(1))
        .select_from(Atendimento)
        .join(
            ProcedimentoRealizado,
            ProcedimentoRealizado.id_atendimento == Atendimento.id_atendimento,
        )
        .join(
            Procedimento,
            Procedimento.id_procedimento == ProcedimentoRealizado.id_procedimento,
        )
        .where(
            Atendimento.id_paciente == Paciente.id_pessoa,
            Procedimento.nivel_risco == "ALTO",
        )
    )
    stmt = (
        select(Pessoa.id_pessoa, Pessoa.nome.label("paciente"))
        .select_from(Paciente)
        .join(Pessoa, Pessoa.id_pessoa == Paciente.id_pessoa)
        .where(~tem_procedimento_alto.exists())
        .order_by(Pessoa.nome.asc())
    )
    return fetch_all(stmt, session=session)


def plantoes_por_residente_nas_unidades(
    *, session: Session | None = None
) -> list[dict[str, Any]]:
    """Plantões do mês corrente por residente e unidade.

    As condições de data ficam no ON do LEFT JOIN, não no WHERE: no WHERE elas
    eliminariam os residentes sem plantão, que a consulta precisa manter com
    total zero e unidade nula.
    """
    stmt = (
        select(
            Unidade.nome.label("unidade"),
            Pessoa.nome.label("residente"),
            func.count(Escala.id_escala).label("total_plantoes"),
        )
        .select_from(Residente)
        .join(Profissional, Profissional.id_pessoa == Residente.id_profissional)
        .join(Pessoa, Pessoa.id_pessoa == Profissional.id_pessoa)
        .outerjoin(
            Escala,
            and_(
                Escala.id_residente == Residente.id_profissional,
                Escala.data_plantao >= _INICIO_MES,
                Escala.data_plantao < _FIM_MES,
            ),
        )
        .outerjoin(Unidade, Unidade.id_unidade == Escala.id_unidade)
        .group_by(
            Unidade.id_unidade,
            Unidade.nome,
            Residente.id_profissional,
            Pessoa.nome,
        )
        .order_by(
            nulls_last(Unidade.nome.asc()),
            desc("total_plantoes"),
            Pessoa.nome.asc(),
        )
    )
    return fetch_all(stmt, session=session)


def preceptores_que_supervisionaram(
    inicio: datetime, fim: datetime, *, session: Session | None = None
) -> list[dict[str, Any]]:
    """Preceptores com mais de 5 atendimentos supervisionados no intervalo."""
    total = func.count(Atendimento.id_atendimento)
    stmt = (
        select(Pessoa.nome.label("preceptor"), total.label("total_atendimentos"))
        .select_from(Preceptor)
        .join(Profissional, Profissional.id_pessoa == Preceptor.id_profissional)
        .join(Pessoa, Pessoa.id_pessoa == Profissional.id_pessoa)
        .join(Atendimento, Atendimento.id_preceptor == Preceptor.id_profissional)
        .where(Atendimento.data_hora >= inicio, Atendimento.data_hora < fim)
        .group_by(Preceptor.id_profissional, Pessoa.nome)
        .having(total > 5)
        .order_by(desc("total_atendimentos"), Pessoa.nome.asc())
    )
    return fetch_all(stmt, session=session)


def ranking_residentes(*, session: Session | None = None) -> list[dict[str, Any]]:
    """Residentes ordenados por número de atendimentos."""
    stmt = (
        select(
            Pessoa.nome.label("residente"),
            func.count(Atendimento.id_atendimento).label("total_atendimentos"),
        )
        .select_from(Residente)
        .join(Profissional, Profissional.id_pessoa == Residente.id_profissional)
        .join(Pessoa, Pessoa.id_pessoa == Profissional.id_pessoa)
        .outerjoin(
            Atendimento, Atendimento.id_residente == Residente.id_profissional
        )
        .group_by(Residente.id_profissional, Pessoa.nome)
        .order_by(desc("total_atendimentos"), Pessoa.nome.asc())
    )
    return fetch_all(stmt, session=session)
