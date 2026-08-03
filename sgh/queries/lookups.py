"""Consultas de apoio para telas do front.

Não entram no CATALOGO: o critério não é a complexidade da consulta — algumas
aqui têm JOIN e até agregação (`listar_pacientes_com_ultimo_atendimento` faz
outerjoin + GROUP BY + func.max()) —, e sim o que a consulta serve. Nenhuma
função deste módulo é uma "operação de negócio" do sistema; cada uma existe
porque uma tela específica precisa de colunas ou de um formato que as
consultas avaliadas (basicas/analiticas/etapa2) não devolvem, e alterá-las
mexeria num artefato da entrega avaliada. Por isso a necessidade de tela mora
aqui, fora do que é avaliado.
"""

from __future__ import annotations

from typing import Any

from sqlalchemy import func, select
from sqlalchemy.orm import Session, aliased

from sgh.database import fetch_all
from sgh.models import (
    Atendimento,
    Escala,
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
    """Pacientes com id, nome e o ultimo atendimento de cada um: data, equipe
    e procedimentos realizados.

    A tela de pacientes precisa do id para abrir a edicao; a consulta basica
    `atendimentos_do_paciente` devolve so nome + data_hora, e uma linha por
    atendimento em vez de uma por paciente.

    `DISTINCT ON` devolve a **linha inteira** do atendimento mais recente de
    cada paciente. `max(data_hora)` daria so a data, sem caminho para chegar ao
    residente e ao preceptor daquele atendimento especifico.

    Os `outerjoin` mantem na saida o paciente que nunca foi atendido (o seed tem
    um): para ele data_hora, residente e preceptor vem NULL. `array_remove`
    limpa o NULL que `array_agg` produz quando nao ha procedimento, para a lista
    vir vazia em vez de `[None]`.

    A consulta avaliada `avancadas.ultimo_atendimento_por_paciente` responde a
    mesma pergunta navegando pelos relationship() com eager loading. As duas
    coexistem de proposito: aquela demonstra o ORM para a Etapa 2, esta serve a
    tela e devolve o id que a tela precisa. `tests/test_lookups.py` afirma que
    concordam.
    """
    pessoa_residente = aliased(Pessoa)
    pessoa_preceptor = aliased(Pessoa)

    # Residente e Preceptor tem o mesmo id que Profissional, que tem o mesmo id
    # que Pessoa (a chave e propagada pelas FKs), entao da para ir direto de
    # id_residente/id_preceptor a Pessoa sem passar pelas tabelas do meio.
    ultimo = (
        select(
            Atendimento.id_atendimento,
            Atendimento.id_paciente,
            Atendimento.data_hora,
            Atendimento.id_residente,
            Atendimento.id_preceptor,
        )
        .distinct(Atendimento.id_paciente)
        .order_by(Atendimento.id_paciente, Atendimento.data_hora.desc())
        .subquery()
    )

    stmt = (
        select(
            Pessoa.id_pessoa,
            Pessoa.nome,
            ultimo.c.data_hora,
            pessoa_residente.nome.label("residente"),
            pessoa_preceptor.nome.label("preceptor"),
            func.array_remove(func.array_agg(Procedimento.nome), None).label(
                "procedimentos"
            ),
        )
        .select_from(Paciente)
        .join(Pessoa, Pessoa.id_pessoa == Paciente.id_pessoa)
        .outerjoin(ultimo, ultimo.c.id_paciente == Paciente.id_pessoa)
        .outerjoin(
            pessoa_residente, pessoa_residente.id_pessoa == ultimo.c.id_residente
        )
        .outerjoin(
            pessoa_preceptor, pessoa_preceptor.id_pessoa == ultimo.c.id_preceptor
        )
        .outerjoin(
            ProcedimentoRealizado,
            ProcedimentoRealizado.id_atendimento == ultimo.c.id_atendimento,
        )
        .outerjoin(
            Procedimento,
            Procedimento.id_procedimento == ProcedimentoRealizado.id_procedimento,
        )
        .group_by(
            Pessoa.id_pessoa,
            Pessoa.nome,
            ultimo.c.data_hora,
            pessoa_residente.nome,
            pessoa_preceptor.nome,
        )
        .order_by(Pessoa.nome.asc())
    )
    return fetch_all(stmt, session=session)


def plantoes_do_residente(
    id_residente: int, *, session: Session | None = None
) -> list[dict[str, Any]]:
    """Plantões escalados de um residente, para popular o campo de origem do
    reajuste de escala.

    Existe para a tela poder oferecer os plantões que o residente de fato tem,
    em vez de pedir data e turno digitados — que falham silenciosamente quando
    não existe plantão naquela combinação.
    """
    stmt = (
        select(
            Escala.id_escala,
            Escala.data_plantao,
            Escala.turno,
            Unidade.nome.label("unidade"),
        )
        .select_from(Escala)
        .join(Unidade, Unidade.id_unidade == Escala.id_unidade)
        .where(Escala.id_residente == id_residente)
        .order_by(Escala.data_plantao.asc(), Escala.turno.asc())
    )
    return fetch_all(stmt, session=session)
