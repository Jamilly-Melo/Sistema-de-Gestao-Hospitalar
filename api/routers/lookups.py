"""Rotas de autocomplete — id + nome para popular formulários."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from api.dependencies import get_session
from sgh.queries import lookups

router = APIRouter(prefix="/lookups", tags=["lookups"])


@router.get("/pacientes")
def pacientes(session: Session = Depends(get_session)) -> list[dict[str, Any]]:
    return lookups.listar_pacientes(session=session)


@router.get("/unidades")
def unidades(session: Session = Depends(get_session)) -> list[dict[str, Any]]:
    return lookups.listar_unidades(session=session)


@router.get("/procedimentos")
def procedimentos(session: Session = Depends(get_session)) -> list[dict[str, Any]]:
    return lookups.listar_procedimentos(session=session)
