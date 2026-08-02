"""Executor genérico das leituras do CATALOGO, restrito às categorias de
relatório (Consultas analíticas + Etapa 2) — Paciente, Atendimento e
Profissional/Residente já têm rota de recurso dedicada e não aparecem aqui."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from api.dependencies import get_session
from sgh.catalog import CATALOGO, CATEGORIAS_RELATORIO

router = APIRouter(prefix="/relatorios", tags=["relatorios"])


def _entradas_de_relatorio() -> dict[str, dict[str, Any]]:
    entradas: dict[str, dict[str, Any]] = {}
    for categoria in CATEGORIAS_RELATORIO:
        entradas.update(CATALOGO[categoria])
    return entradas


@router.get("")
def listar() -> list[dict[str, Any]]:
    return [
        {"nome": nome, "description": entrada["description"], "params": entrada["params"]}
        for nome, entrada in _entradas_de_relatorio().items()
    ]


@router.post("/{nome}")
def executar(
    nome: str,
    parametros: dict[str, Any],
    session: Session = Depends(get_session),
) -> list[dict[str, Any]]:
    entradas = _entradas_de_relatorio()
    if nome not in entradas:
        raise HTTPException(status_code=404, detail=f"Relatório '{nome}' não existe.")

    entrada = entradas[nome]
    args = [
        parametros.get(param["name"], param.get("default"))
        for param in entrada["params"]
    ]
    return entrada["fn"](*args, session=session)
