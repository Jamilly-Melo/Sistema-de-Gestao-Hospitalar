"""Schemas de request para o recurso Paciente."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel


class AtualizarPacienteRequest(BaseModel):
    campo: Literal["endereco", "num_convenio"]
    valor: str
