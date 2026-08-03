"""Rotas do recurso Paciente."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from api.dependencies import get_session
from api.schemas.pacientes import AtualizarPacienteRequest
from sgh.queries import crud, lookups

router = APIRouter(prefix="/pacientes", tags=["pacientes"])


@router.get("/listagem")
def listagem(session: Session = Depends(get_session)) -> list[dict[str, Any]]:
    """Um paciente por linha, com o último atendimento: data, equipe e
    procedimentos.

    Não há `GET /pacientes` servindo `basicas.atendimentos_do_paciente`: aquela
    consulta devolve uma linha por atendimento, e a tela precisa de uma por
    paciente. Ela continua no CATALOGO e coberta pelos testes de paridade — só
    não tem rota HTTP, porque ninguém a consumia por HTTP.
    """
    return lookups.listar_pacientes_com_ultimo_atendimento(session=session)


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
