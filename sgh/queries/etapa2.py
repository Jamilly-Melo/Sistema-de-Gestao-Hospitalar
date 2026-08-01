"""Wrappers para as views e procedures da etapa 2.

As views (vw_*) e a procedure de leitura (sp_calcular_tempo_medio_espera) viram
consultas de relatório, expostas via /relatorios. As procedures de escrita
(sp_registrar_atendimento_completo, sp_reajustar_escala) viram mutações de
recurso na API — chamadas via CALL, e não recriadas em SQLAlchemy.
"""

from __future__ import annotations

import json
from datetime import date, datetime
from typing import Any

from sqlalchemy import text
from sqlalchemy.orm import Session

from sgh.database import sessao


def pacientes_internados(*, session: Session | None = None) -> list[dict[str, Any]]:
    """Wrapper de vw_pacientes_internados."""
    with sessao(session=session) as s:
        resultado = s.execute(text("SELECT * FROM vw_pacientes_internados"))
        return [dict(linha) for linha in resultado.mappings()]


def residentes_sem_supervisor(*, session: Session | None = None) -> list[dict[str, Any]]:
    """Wrapper de vw_residentes_sem_supervisor."""
    with sessao(session=session) as s:
        resultado = s.execute(text("SELECT * FROM vw_residentes_sem_supervisor"))
        return [dict(linha) for linha in resultado.mappings()]


def estatisticas_atendimentos_mensal(
    *, session: Session | None = None
) -> list[dict[str, Any]]:
    """Wrapper de vw_estatisticas_atendimentos_mensal."""
    with sessao(session=session) as s:
        resultado = s.execute(
            text("SELECT * FROM vw_estatisticas_atendimentos_mensal")
        )
        return [dict(linha) for linha in resultado.mappings()]


def tempo_medio_espera(*, session: Session | None = None) -> list[dict[str, Any]]:
    """Wrapper de sp_calcular_tempo_medio_espera.

    A procedure devolve um REFCURSOR, não um result set direto: é preciso um
    FETCH ALL explícito no mesmo cursor, dentro da mesma transação do CALL.
    """
    with sessao(session=session) as s:
        s.execute(
            text("CALL sp_calcular_tempo_medio_espera('cursor_tempo_espera')")
        )
        resultado = s.execute(text("FETCH ALL FROM cursor_tempo_espera"))
        return [dict(linha) for linha in resultado.mappings()]


def registrar_atendimento_completo(
    data_hora: datetime,
    duracao_minutos: int,
    id_paciente: int,
    id_residente: int,
    id_preceptor: int,
    id_unidade: int,
    procedimentos: list[dict[str, Any]],
    *,
    session: Session | None = None,
) -> list[dict[str, Any]]:
    """Wrapper de sp_registrar_atendimento_completo.

    Substitui inserir_atendimento como caminho de escrita de atendimento na
    API: a procedure grava o atendimento e os procedimentos na mesma
    transação. Erros de validação (RAISE EXCEPTION dentro da procedure) e
    violação de FK sobem como DBAPIError — a API mapeia para 422/409.
    """
    with sessao(session=session) as s:
        resultado = s.execute(
            text(
                "CALL sp_registrar_atendimento_completo("
                ":data_hora, :duracao_minutos, :id_paciente, :id_residente, "
                ":id_preceptor, :id_unidade, CAST(:procedimentos AS JSONB), NULL)"
            ),
            {
                "data_hora": data_hora,
                "duracao_minutos": duracao_minutos,
                "id_paciente": id_paciente,
                "id_residente": id_residente,
                "id_preceptor": id_preceptor,
                "id_unidade": id_unidade,
                "procedimentos": json.dumps(procedimentos, default=str),
            },
        )
        linha = resultado.mappings().one()
        s.commit()
        return [{"id_atendimento": linha["p_id_atendimento"]}]


def reajustar_escala(
    id_residente: int,
    data_origem: date,
    turno_origem: str,
    data_destino: date,
    turno_destino: str,
    *,
    session: Session | None = None,
) -> list[dict[str, Any]]:
    """Wrapper de sp_reajustar_escala.

    Validações (turno inválido, conflito no destino, escala não encontrada)
    são RAISE EXCEPTION dentro da procedure e sobem como DBAPIError.
    """
    with sessao(session=session) as s:
        s.execute(
            text(
                "CALL sp_reajustar_escala("
                ":id_residente, :data_origem, :turno_origem, "
                ":data_destino, :turno_destino)"
            ),
            {
                "id_residente": id_residente,
                "data_origem": data_origem,
                "turno_origem": turno_origem,
                "data_destino": data_destino,
                "turno_destino": turno_destino,
            },
        )
        s.commit()
        return [
            {
                "id_residente": id_residente,
                "data_plantao": data_destino,
                "turno": turno_destino,
            }
        ]
