"""Rotas do recurso Atendimento."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from api.dependencies import get_session
from api.schemas.atendimentos import CriarAtendimentoRequest
from sgh.queries import basicas, crud, etapa2, lookups

router = APIRouter(prefix="/atendimentos", tags=["atendimentos"])


@router.get("")
def listar(session: Session = Depends(get_session)) -> list[dict[str, Any]]:
    return basicas.procedimentos_em_atendimento(session=session)


@router.post("")
def criar(
    corpo: CriarAtendimentoRequest, session: Session = Depends(get_session)
) -> dict[str, Any]:
    resultado = etapa2.registrar_atendimento_completo(
        corpo.data_hora,
        corpo.duracao_minutos,
        corpo.id_paciente,
        corpo.id_residente,
        corpo.id_preceptor,
        corpo.id_unidade,
        [item.model_dump() for item in corpo.procedimentos],
        session=session,
    )
    return resultado[0]


@router.get("/{id_atendimento}/procedimentos")
def listar_procedimentos(
    id_atendimento: int, session: Session = Depends(get_session)
) -> list[dict[str, Any]]:
    return lookups.procedimentos_do_atendimento(id_atendimento, session=session)


@router.delete("/{id_atendimento}/procedimentos/{id_procedimento}")
def remover_procedimento(
    id_atendimento: int,
    id_procedimento: int,
    session: Session = Depends(get_session),
) -> dict[str, Any]:
    resultado = crud.remover_procedimento_realizado(
        id_atendimento, id_procedimento, session=session
    )
    if not resultado:
        raise HTTPException(
            status_code=404, detail="Procedimento realizado não encontrado."
        )
    return resultado[0]
