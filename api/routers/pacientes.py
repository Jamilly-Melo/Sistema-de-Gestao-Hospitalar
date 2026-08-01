"""Rotas do recurso Paciente."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from api.dependencies import get_session
from api.schemas.pacientes import AtualizarPacienteRequest
from sgh.queries import basicas, crud

router = APIRouter(prefix="/pacientes", tags=["pacientes"])


@router.get("")
def listar(session: Session = Depends(get_session)) -> list[dict[str, Any]]:
    """Listagem de pacientes com o atendimento mais recente (nome + data)."""
    return basicas.atendimentos_do_paciente(session=session)


@router.patch("/{id_paciente}")
def atualizar(
    id_paciente: int,
    corpo: AtualizarPacienteRequest,
    session: Session = Depends(get_session),
) -> dict[str, Any]:
    resultado = crud.atualizar_dados_paciente(
        corpo.campo, corpo.valor, id_paciente, session=session
    )
    if not resultado:
        raise HTTPException(status_code=404, detail="Paciente não encontrado.")
    return resultado[0]
