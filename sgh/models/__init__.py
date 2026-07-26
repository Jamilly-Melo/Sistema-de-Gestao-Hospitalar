"""Models do SGH.

Todos os módulos são importados aqui para que o registry do SQLAlchemy fique
completo. Um model nunca importado deixa suas referências em string sem resolver,
e o erro só aparece na primeira query — não no import.
"""

from sgh.models.atendimentos import Atendimento, Internacao, ProcedimentoRealizado
from sgh.models.auditoria import AuditoriaAtendimento
from sgh.models.base import Base
from sgh.models.catalogos import Alergia, Procedimento, Unidade
from sgh.models.escalas import Escala
from sgh.models.pessoas import (
    Paciente,
    PacienteAlergia,
    Preceptor,
    Pessoa,
    Profissional,
    Residente,
)

__all__ = [
    "Alergia",
    "Atendimento",
    "AuditoriaAtendimento",
    "Base",
    "Escala",
    "Internacao",
    "Paciente",
    "PacienteAlergia",
    "Preceptor",
    "Pessoa",
    "Procedimento",
    "ProcedimentoRealizado",
    "Profissional",
    "Residente",
    "Unidade",
]
