"""Consultas avançadas — item 5 da Etapa 2.

Módulo separado de propósito: `basicas.py`, `analiticas.py`, `etapa2.py` e
`crud.py` são artefato da entrega já avaliada e não devem ser alterados.
"""

from __future__ import annotations

from typing import Any

from sqlalchemy import Numeric, case, cast, desc, func, select
from sqlalchemy.orm import Session, aliased, selectinload

from sgh.database import fetch_all, sessao
from sgh.models import (
    Atendimento,
    Paciente,
    Pessoa,
    Preceptor,
    Procedimento,
    ProcedimentoRealizado,
    Profissional,
    Residente,
)


def preceptores_de_pacientes_flamenguistas(
    *, session: Session | None = None
) -> list[dict[str, Any]]:
    """Preceptores que supervisionaram atendimentos de pacientes flamenguistas.

    `Pessoa` entra duas vezes na consulta — uma para o nome do preceptor, outra
    para o `is_flamengo` do paciente —, por isso os dois `aliased()`. Sem eles o
    SQLAlchemy não saberia a qual das duas cada coluna se refere.

    O `distinct()` é necessário porque o JOIN com `atendimento` multiplica o
    preceptor por atendimento qualificante.
    """
    pessoa_preceptor = aliased(Pessoa)
    pessoa_paciente = aliased(Pessoa)

    stmt = (
        select(
            pessoa_preceptor.nome.label("preceptor"),
            Preceptor.titulacao.label("titulacao"),
        )
        .select_from(Preceptor)
        .join(Profissional, Profissional.id_pessoa == Preceptor.id_profissional)
        .join(pessoa_preceptor, pessoa_preceptor.id_pessoa == Profissional.id_pessoa)
        .join(Atendimento, Atendimento.id_preceptor == Preceptor.id_profissional)
        .join(Paciente, Paciente.id_pessoa == Atendimento.id_paciente)
        .join(pessoa_paciente, pessoa_paciente.id_pessoa == Paciente.id_pessoa)
        .where(pessoa_paciente.is_flamengo.is_(True))
        .distinct()
        .order_by(pessoa_preceptor.nome.asc())
    )
    return fetch_all(stmt, session=session)


def percentual_procedimentos_risco_alto(
    *, session: Session | None = None
) -> list[dict[str, Any]]:
    """Percentual de procedimentos de risco ALTO realizados por cada residente.

    Os `outerjoin` encadeados mantêm na saída o residente que nunca atendeu
    (o seed tem um). Para ele o total é 0, e `nullif(total, 0)` transforma a
    divisão em NULL em vez de estourar — o `coalesce` externo devolve 0.

    O `cast` para Numeric é necessário porque `count()` devolve inteiro no
    Postgres, e inteiro dividido por inteiro trunca.
    """
    total = func.count(ProcedimentoRealizado.id_procedimento)
    alto = func.count(case((Procedimento.nivel_risco == "ALTO", 1)))
    percentual = func.coalesce(
        func.round(cast(alto, Numeric) * 100 / func.nullif(total, 0), 1), 0
    )

    stmt = (
        select(
            Pessoa.nome.label("residente"),
            total.label("total_procedimentos"),
            alto.label("procedimentos_risco_alto"),
            percentual.label("percentual_risco_alto"),
        )
        .select_from(Residente)
        .join(Profissional, Profissional.id_pessoa == Residente.id_profissional)
        .join(Pessoa, Pessoa.id_pessoa == Profissional.id_pessoa)
        .outerjoin(Atendimento, Atendimento.id_residente == Residente.id_profissional)
        .outerjoin(
            ProcedimentoRealizado,
            ProcedimentoRealizado.id_atendimento == Atendimento.id_atendimento,
        )
        .outerjoin(
            Procedimento,
            Procedimento.id_procedimento == ProcedimentoRealizado.id_procedimento,
        )
        .group_by(Residente.id_profissional, Pessoa.nome)
        .order_by(desc("percentual_risco_alto"), Pessoa.nome.asc())
    )
    return fetch_all(stmt, session=session)


def ultimo_atendimento_por_paciente(
    *, session: Session | None = None
) -> list[dict[str, Any]]:
    """Último atendimento de cada paciente, com a lista de procedimentos.

    Diferente das outras consultas do projeto, esta navega pelos
    `relationship()` em vez de montar um SELECT plano com JOIN. O motivo é a
    forma do dado: um atendimento tem N procedimentos, então um JOIN devolveria
    uma linha por procedimento e a lista teria de ser remontada em Python de
    qualquer jeito.

    `selectinload` é **eager loading**: o SQLAlchemy carrega cada nível de
    relacionamento numa query só, antes de o código acessar os atributos. Sem
    ele valeria o padrão — **lazy loading** —, em que cada
    `paciente.atendimentos` e cada `atendimento.procedimentos` dispara um SELECT
    próprio no momento do acesso, o que produz o problema N+1.

    `tests/test_carregamento.py` conta as queries emitidas nos dois modos e
    mostra a diferença em número, não em afirmação.
    """
    stmt = select(Paciente).options(
        selectinload(Paciente.pessoa),
        selectinload(Paciente.atendimentos)
        .selectinload(Atendimento.procedimentos)
        .selectinload(ProcedimentoRealizado.procedimento),
        selectinload(Paciente.atendimentos)
        .selectinload(Atendimento.residente)
        .selectinload(Residente.profissional)
        .selectinload(Profissional.pessoa),
        selectinload(Paciente.atendimentos)
        .selectinload(Atendimento.preceptor)
        .selectinload(Preceptor.profissional)
        .selectinload(Profissional.pessoa),
    )

    with sessao(session=session) as s:
        pacientes = s.execute(stmt).scalars().unique().all()

        linhas: list[dict[str, Any]] = []
        for paciente in pacientes:
            if not paciente.atendimentos:
                linhas.append(
                    {
                        "paciente": paciente.pessoa.nome,
                        "data_hora": None,
                        "residente": None,
                        "preceptor": None,
                        "procedimentos": [],
                    }
                )
                continue

            ultimo = max(paciente.atendimentos, key=lambda a: a.data_hora)
            linhas.append(
                {
                    "paciente": paciente.pessoa.nome,
                    "data_hora": ultimo.data_hora,
                    "residente": ultimo.residente.profissional.pessoa.nome,
                    "preceptor": ultimo.preceptor.profissional.pessoa.nome,
                    "procedimentos": [
                        realizado.procedimento.nome
                        for realizado in ultimo.procedimentos
                    ],
                }
            )

        linhas.sort(key=lambda linha: linha["paciente"])
        return linhas
