"""Consultas de apoio para autocomplete.

Não entram no CATALOGO: não são "operações de negócio" que o usuário executa,
são listas triviais (id + nome) que alimentam campos de formulário no front.
Sem JOIN complexo, sem agregação — só o suficiente para popular um autocomplete.
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
    Preceptor,
    Procedimento,
    ProcedimentoRealizado,
    Profissional,
    Unidade,
)


def listar_pacientes(*, session: Session | None = None) -> list[dict[str, Any]]:
    """Pacientes cadastrados, id + nome, para autocomplete."""
    stmt = (
        select(Pessoa.id_pessoa, Pessoa.nome)
        .select_from(Paciente)
        .join(Pessoa, Pessoa.id_pessoa == Paciente.id_pessoa)
        .order_by(Pessoa.nome.asc())
    )
    return fetch_all(stmt, session=session)


def listar_unidades(*, session: Session | None = None) -> list[dict[str, Any]]:
    """Unidades cadastradas, id + nome, para autocomplete."""
    stmt = select(Unidade.id_unidade, Unidade.nome).order_by(Unidade.nome.asc())
    return fetch_all(stmt, session=session)


def listar_procedimentos(*, session: Session | None = None) -> list[dict[str, Any]]:
    """Procedimentos do catálogo, id + nome, para autocomplete."""
    stmt = (
        select(Procedimento.id_procedimento, Procedimento.nome)
        .order_by(Procedimento.nome.asc())
    )
    return fetch_all(stmt, session=session)


def listar_preceptores(*, session: Session | None = None) -> list[dict[str, Any]]:
    """Preceptores cadastrados, id + nome + titulação, para autocomplete."""
    stmt = (
        select(Preceptor.id_profissional, Pessoa.nome, Preceptor.titulacao)
        .select_from(Preceptor)
        .join(Profissional, Profissional.id_pessoa == Preceptor.id_profissional)
        .join(Pessoa, Pessoa.id_pessoa == Profissional.id_pessoa)
        .order_by(Pessoa.nome.asc())
    )
    return fetch_all(stmt, session=session)


def procedimentos_do_atendimento(
    id_atendimento: int, *, session: Session | None = None
) -> list[dict[str, Any]]:
    """Procedimentos de um atendimento, com id e situacao de faturamento.

    Separada de `basicas.procedimentos_em_atendimento` de proposito: a tela de
    detalhe precisa do `id_procedimento` (para saber o que remover) e de
    `faturado` (para desabilitar a remocao antes do usuario tomar erro), e a
    consulta basica nao devolve nenhum dos dois. Acrescentar colunas la mexeria
    num artefato da entrega avaliada, entao a necessidade de tela mora aqui.
    """
    stmt = (
        select(
            ProcedimentoRealizado.id_procedimento,
            Procedimento.nome,
            ProcedimentoRealizado.quantidade,
            ProcedimentoRealizado.tempo_real_minutos,
            ProcedimentoRealizado.faturado,
        )
        .select_from(ProcedimentoRealizado)
        .join(
            Procedimento,
            Procedimento.id_procedimento == ProcedimentoRealizado.id_procedimento,
        )
        .where(ProcedimentoRealizado.id_atendimento == id_atendimento)
        .order_by(Procedimento.nome.asc())
    )
    return fetch_all(stmt, session=session)


def listar_pacientes_com_ultimo_atendimento(
    *, session: Session | None = None
) -> list[dict[str, Any]]:
    """Pacientes com id, nome e data do ultimo atendimento.

    A tela de pacientes precisa do id para abrir a edicao; a consulta basica
    `atendimentos_do_paciente` devolve so nome + data_hora. O LEFT JOIN mantem
    quem nunca foi atendido (data_hora vem NULL), e o GROUP BY garante uma
    linha por paciente — a consulta basica devolve uma linha por atendimento.
    """
    stmt = (
        select(
            Pessoa.id_pessoa,
            Pessoa.nome,
            func.max(Atendimento.data_hora).label("data_hora"),
        )
        .select_from(Paciente)
        .join(Pessoa, Pessoa.id_pessoa == Paciente.id_pessoa)
        .outerjoin(Atendimento, Atendimento.id_paciente == Paciente.id_pessoa)
        .group_by(Pessoa.id_pessoa, Pessoa.nome)
        .order_by(Pessoa.nome.asc())
    )
    return fetch_all(stmt, session=session)
