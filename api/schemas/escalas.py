"""Schemas de request para o recurso Escala."""

from __future__ import annotations

from datetime import date
from typing import Literal

from pydantic import BaseModel

Turno = Literal["MANHA", "TARDE", "NOITE"]


class ReajustarEscalaRequest(BaseModel):
    id_residente: int
    data_origem: date
    turno_origem: Turno
    data_destino: date
    turno_destino: Turno
