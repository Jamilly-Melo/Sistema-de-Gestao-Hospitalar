"""Rotas do recurso Escala/Unidade."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from api.dependencies import get_session
from api.schemas.escalas import ReajustarEscalaRequest
from sgh.queries import analiticas, etapa2, lookups

router = APIRouter(prefix="/escalas", tags=["escalas"])


@router.get("")
def listar(session: Session = Depends(get_session)) -> list[dict[str, Any]]:
    """Painel mensal de plantões por residente e unidade (mês corrente)."""
    return analiticas.plantoes_por_residente_nas_unidades(session=session)


@router.get("/residente/{id_residente}")
def plantoes_do_residente(
    id_residente: int, session: Session = Depends(get_session)
) -> list[dict[str, Any]]:
    return lookups.plantoes_do_residente(id_residente, session=session)


@router.post("/reajustar")
def reajustar(
    corpo: ReajustarEscalaRequest, session: Session = Depends(get_session)
) -> dict[str, Any]:
    resultado = etapa2.reajustar_escala(
        corpo.id_residente,
        corpo.data_origem,
        corpo.turno_origem,
        corpo.data_destino,
        corpo.turno_destino,
        session=session,
    )
    return resultado[0]
