"""Consultas de apoio para autocomplete.

Não entram no CATALOGO: não são "operações de negócio" que o usuário executa,
são listas triviais (id + nome) que alimentam campos de formulário no front.
Sem JOIN complexo, sem agregação — só o suficiente para popular um autocomplete.
"""

from __future__ import annotations

from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from sgh.database import fetch_all
from sgh.models import Paciente, Pessoa, Preceptor, Procedimento, Profissional, Unidade


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
