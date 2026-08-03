"""Lazy vs eager loading, medido em número de queries.

O item 4 da Etapa 2 pede a demonstração dos dois modos de carregamento de
relacionamento. Este arquivo não afirma a diferença — ele conta as instruções
SQL que o SQLAlchemy emite em cada modo, usando o evento `before_cursor_execute`
do engine.
"""

from __future__ import annotations

from contextlib import contextmanager
from typing import Iterator

from sqlalchemy import event, select
from sqlalchemy.orm import selectinload

from sgh.database import SessionLocal, engine
from sgh.models import Atendimento, Paciente

# Uma query por nível: pacientes, atendimentos, procedimentos. Se este número
# mudar, reconfira o valor observado em vez de afrouxar para uma desigualdade —
# a igualdade é o que faz uma regressão de N+1 quebrar o build.
QUERIES_EAGER_ESPERADAS = 3


@contextmanager
def contar_queries() -> Iterator[dict[str, int]]:
    """Conta as instruções SQL emitidas dentro do bloco."""
    contador = {"total": 0}

    def ao_executar(conn, cursor, statement, parameters, context, executemany):
        contador["total"] += 1

    event.listen(engine, "before_cursor_execute", ao_executar)
    try:
        yield contador
    finally:
        event.remove(engine, "before_cursor_execute", ao_executar)


def _percorrer_lazy() -> tuple[int, int]:
    """Percorre pacientes -> atendimentos -> procedimentos sem eager loading."""
    with SessionLocal() as s:
        with contar_queries() as contador:
            pacientes = s.execute(select(Paciente)).scalars().all()
            for paciente in pacientes:
                for atendimento in paciente.atendimentos:
                    list(atendimento.procedimentos)
            total_pacientes = len(pacientes)
        return contador["total"], total_pacientes


def _percorrer_eager() -> tuple[int, int]:
    """O mesmo percurso, com selectinload nos dois níveis."""
    stmt = select(Paciente).options(
        selectinload(Paciente.atendimentos).selectinload(Atendimento.procedimentos)
    )
    with SessionLocal() as s:
        with contar_queries() as contador:
            pacientes = s.execute(stmt).scalars().unique().all()
            for paciente in pacientes:
                for atendimento in paciente.atendimentos:
                    list(atendimento.procedimentos)
            total_pacientes = len(pacientes)
        return contador["total"], total_pacientes


def test_lazy_loading_cresce_com_o_numero_de_pacientes():
    """Cada relacionamento acessado vai ao banco na hora — o problema N+1."""
    queries, pacientes = _percorrer_lazy()
    assert pacientes > 1, "o seed precisa de vários pacientes para o teste valer"
    # 1 query dos pacientes + 1 por paciente (seus atendimentos), no mínimo.
    assert queries > pacientes, (
        f"lazy loading emitiu {queries} queries para {pacientes} pacientes; "
        "esperado mais de uma por paciente"
    )


def test_eager_loading_nao_cresce_com_o_numero_de_pacientes():
    """selectinload carrega cada nível numa query só."""
    queries, pacientes = _percorrer_eager()
    assert queries == QUERIES_EAGER_ESPERADAS
    assert queries < pacientes, (
        f"eager loading emitiu {queries} queries para {pacientes} pacientes; "
        "deveria ser constante e menor que o número de pacientes"
    )


def test_eager_emite_menos_queries_que_lazy():
    """A comparação que o item 4 da Etapa 2 pede, em número."""
    lazy, _ = _percorrer_lazy()
    eager, _ = _percorrer_eager()
    assert eager < lazy, f"eager={eager} deveria ser menor que lazy={lazy}"
