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
