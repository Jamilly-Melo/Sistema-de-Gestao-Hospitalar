"""Schemas de request para o recurso Atendimento."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class ProcedimentoRealizadoInput(BaseModel):
    id_procedimento: int
    quantidade: int
    tempo_real_minutos: int
    data_hora_inicio: datetime
    observacao: str | None = None
    faturado: bool = False


class CriarAtendimentoRequest(BaseModel):
    data_hora: datetime
    duracao_minutos: int
    id_paciente: int
    id_residente: int
    id_preceptor: int
    id_unidade: int
    procedimentos: list[ProcedimentoRealizadoInput]
