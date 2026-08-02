"""Rotas do recurso Profissional (Residente e Preceptor)."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from api.dependencies import get_session
from sgh.queries import basicas, lookups

router = APIRouter(prefix="/profissionais", tags=["profissionais"])


@router.get("/residentes")
def listar_residentes(
    session: Session = Depends(get_session),
) -> list[dict[str, Any]]:
    return basicas.media_atendimentos_por_residente(session=session)


@router.get("/preceptores")
def listar_preceptores(
    session: Session = Depends(get_session),
) -> list[dict[str, Any]]:
    return lookups.listar_preceptores(session=session)
