"""Operações de escrita.

Estas são as três operações que viram ORM de verdade: manipulam entidades em vez
de montar SQL. As checagens de existência que o SQL original fazia com
`WHERE EXISTS` viram `session.get()` dentro da mesma transação — mesma garantia,
muito mais legível.

Todas devolvem [] quando a operação não se aplica, o que a UI traduz em "nenhuma
linha afetada".
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy.orm import Session

from sgh.database import sessao
from sgh.models import (
    Atendimento,
    Paciente,
    Preceptor,
    ProcedimentoRealizado,
    Residente,
    Unidade,
)


def inserir_atendimento(
    data_hora: datetime,
    duracao_minutos: int,
    id_paciente: int,
    id_residente: int,
    id_preceptor: int,
    id_unidade: int,
    *,
    session: Session | None = None,
) -> list[dict[str, Any]]:
    """Insere um atendimento se paciente, residente, preceptor e unidade existirem.

    id_unidade é obrigatório desde alteracoes.sql, que tornou a coluna NOT NULL.

    A verificação e o insert são duas operações na mesma transação, e não uma
    sentença única como o `INSERT ... WHERE EXISTS` do .sql original. Se um dos
    cadastros for removido por outra transação nesse intervalo, a FK do schema
    barra a escrita, mas o erro sobe como IntegrityError em vez de virar uma
    recusa graciosa com []. Aceito: uso acadêmico single-user.
    """
    with sessao(session=session) as s:
        existem = (
            s.get(Paciente, id_paciente) is not None
            and s.get(Residente, id_residente) is not None
            and s.get(Preceptor, id_preceptor) is not None
            and s.get(Unidade, id_unidade) is not None
        )
        if not existem:
            return []

        atendimento = Atendimento(
            data_hora=data_hora,
            duracao_minutos=duracao_minutos,
            id_paciente=id_paciente,
            id_residente=id_residente,
            id_preceptor=id_preceptor,
            id_unidade=id_unidade,
        )
        s.add(atendimento)
        s.commit()

        return [
            {
                "id_atendimento": atendimento.id_atendimento,
                "data_hora": atendimento.data_hora,
                "duracao_minutos": atendimento.duracao_minutos,
                "id_paciente": atendimento.id_paciente,
                "id_residente": atendimento.id_residente,
                "id_preceptor": atendimento.id_preceptor,
                "id_unidade": atendimento.id_unidade,
            }
        ]


def atualizar_dados_paciente(
    campo: str,
    valor: str,
    id_paciente: int,
    *,
    session: Session | None = None,
) -> list[dict[str, Any]]:
    """Atualiza `endereco` (em pessoa) ou `num_convenio` (em paciente).

    O SQL original fazia isso com uma CTE e dois UPDATEs condicionais, porque em
    SQL não dá para escolher a tabela em tempo de execução. Em Python o despacho
    é um if.

    A validação de quais campos são editáveis vive só na API (Pydantic, em
    `api/schemas/pacientes.py`) — esta função não repete a checagem. O único
    chamador real é a rota da API, que já restringe `campo` antes de chegar
    aqui; qualquer valor diferente de "endereco" cai no `else` e grava em
    `num_convenio`.
    """
    with sessao(session=session) as s:
        paciente = s.get(Paciente, id_paciente)
        if paciente is None:
            return []

        if campo == "endereco":
            paciente.pessoa.endereco = valor
        else:
            paciente.num_convenio = valor

        s.commit()
        return [{"id_pessoa": paciente.id_pessoa}]


def remover_procedimento_realizado(
    id_atendimento: int,
    id_procedimento: int,
    *,
    session: Session | None = None,
) -> list[dict[str, Any]]:
    """Remove um procedimento realizado, desde que ainda não faturado.

    Devolve [] só quando o par (id_atendimento, id_procedimento) não existe.
    Quando existe mas está faturado, levanta ValueError — o contrato antigo
    (devolver [] nos dois casos) impedia a API de diferenciar "não existe" de
    "recusado por regra de negócio".
    """
    with sessao(session=session) as s:
        procedimento = s.get(
            ProcedimentoRealizado, (id_atendimento, id_procedimento)
        )
        if procedimento is None:
            return []

        if procedimento.faturado:
            raise ValueError("Procedimento já faturado, não pode ser removido.")

        s.delete(procedimento)
        s.commit()
        return [
            {"id_atendimento": id_atendimento, "id_procedimento": id_procedimento}
        ]
