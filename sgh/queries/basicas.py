"""Consultas básicas.

Tradução literal de sql/consultas-basicas/. As colunas de saída e seus nomes são
os mesmos dos arquivos .sql — os testes de paridade dependem disso.
"""

from __future__ import annotations

from typing import Any

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from sgh.database import fetch_all
from sgh.models import (
    Atendimento,
    Paciente,
    Pessoa,
    Procedimento,
    ProcedimentoRealizado,
    Profissional,
    Residente,
)


def atendimentos_do_paciente(
    *, session: Session | None = None
) -> list[dict[str, Any]]:
    """Atendimentos por paciente, do mais recente para o mais antigo.

    O LEFT JOIN mantém na saída os pacientes que nunca foram atendidos.
    """
    stmt = (
        select(Pessoa.nome, Atendimento.data_hora)
        .select_from(Paciente)
        .join(Pessoa, Pessoa.id_pessoa == Paciente.id_pessoa)
        .outerjoin(Atendimento, Atendimento.id_paciente == Paciente.id_pessoa)
        .order_by(Atendimento.data_hora.desc())
    )
    return fetch_all(stmt, session=session)


def media_atendimentos_por_residente(
    *, session: Session | None = None
) -> list[dict[str, Any]]:
    """Tempo médio de duração dos atendimentos, por residente."""
    stmt = (
        select(
            Residente.id_profissional.label("id"),
            Pessoa.nome.label("nome"),
            Residente.ano_residencia.label("ano_residencia"),
            Profissional.crm.label("crm"),
            func.avg(Atendimento.duracao_minutos).label(
                "tempo_medio_de_atendimentos"
            ),
        )
        .select_from(Residente)
        .join(Profissional, Profissional.id_pessoa == Residente.id_profissional)
        .join(Pessoa, Pessoa.id_pessoa == Profissional.id_pessoa)
        .outerjoin(Atendimento, Atendimento.id_residente == Pessoa.id_pessoa)
        .group_by(
            Residente.id_profissional,
            Pessoa.nome,
            Profissional.crm,
            Residente.ano_residencia,
        )
    )
    return fetch_all(stmt, session=session)


def procedimentos_em_atendimento(
    *, session: Session | None = None
) -> list[dict[str, Any]]:
    """Procedimentos executados em cada atendimento."""
    stmt = (
        select(
            Atendimento.id_atendimento.label("id_atendimento"),
            Atendimento.data_hora.label("data_hora"),
            Procedimento.nome.label("nome"),
            ProcedimentoRealizado.quantidade.label("quantidade"),
            Procedimento.tempo_medio_minutos,
            ProcedimentoRealizado.tempo_real_minutos,
        )
        .select_from(Atendimento)
        .join(
            ProcedimentoRealizado,
            ProcedimentoRealizado.id_atendimento == Atendimento.id_atendimento,
        )
        .join(
            Procedimento,
            Procedimento.id_procedimento == ProcedimentoRealizado.id_procedimento,
        )
        .order_by(Atendimento.id_atendimento)
    )
    return fetch_all(stmt, session=session)
