"""Testes funcionais das operações de escrita.

Não há teste de paridade aqui: estas operações mutam estado, e a versão .sql do
insert estava quebrada contra o schema completo antes da correção desta task.

Cada teste recebe `session_revertida` e a repassa para a função, de modo que os
commits internos viram savepoints e o rollback do fixture desfaz tudo.
"""

from datetime import datetime

from sgh.models import Atendimento, Paciente, Pessoa, ProcedimentoRealizado
from sgh.queries import crud


def test_inserir_atendimento_com_ids_validos(session_revertida):
    resultado = crud.inserir_atendimento(
        datetime(2026, 8, 1, 8, 0),
        45,
        1,
        6,
        11,
        1,
        session=session_revertida,
    )
    assert len(resultado) == 1
    assert resultado[0]["id_paciente"] == 1
    assert resultado[0]["id_unidade"] == 1
    assert resultado[0]["id_atendimento"] is not None

    gravado = session_revertida.get(Atendimento, resultado[0]["id_atendimento"])
    assert gravado.duracao_minutos == 45


def test_inserir_atendimento_recusa_paciente_inexistente(session_revertida):
    resultado = crud.inserir_atendimento(
        datetime(2026, 8, 1, 8, 0),
        45,
        999,
        6,
        11,
        1,
        session=session_revertida,
    )
    assert resultado == []


def test_inserir_atendimento_recusa_unidade_inexistente(session_revertida):
    resultado = crud.inserir_atendimento(
        datetime(2026, 8, 1, 8, 0),
        45,
        1,
        6,
        11,
        999,
        session=session_revertida,
    )
    assert resultado == []


def test_atualizar_endereco_do_paciente(session_revertida):
    resultado = crud.atualizar_dados_paciente(
        "endereco", "Rua Nova, 100", 1, session=session_revertida
    )
    assert resultado == [{"id_pessoa": 1}]
    assert session_revertida.get(Pessoa, 1).endereco == "Rua Nova, 100"


def test_atualizar_num_convenio_do_paciente(session_revertida):
    resultado = crud.atualizar_dados_paciente(
        "num_convenio", "C999", 1, session=session_revertida
    )
    assert resultado == [{"id_pessoa": 1}]
    assert session_revertida.get(Paciente, 1).num_convenio == "C999"


def test_atualizar_campo_nao_permitido(session_revertida):
    """O SQL original resolvia isto com uma CTE, porque não dá para escolher a
    coluna em tempo de execução. Em Python o despacho é um if, e o guard é o que
    impede um `campo` arbitrário vindo da UI de virar escrita em coluna
    inesperada — precisa de teste."""
    import pytest

    with pytest.raises(ValueError, match="não atualizável"):
        crud.atualizar_dados_paciente(
            "grupo_sanguineo", "AB-", 1, session=session_revertida
        )

    assert session_revertida.get(Paciente, 1).grupo_sanguineo == "A+"


def test_atualizar_paciente_inexistente(session_revertida):
    resultado = crud.atualizar_dados_paciente(
        "endereco", "Rua Nova, 100", 999, session=session_revertida
    )
    assert resultado == []


def test_remover_procedimento_nao_faturado(session_revertida):
    """O seed marca (2, 2) com faturado = FALSE."""
    resultado = crud.remover_procedimento_realizado(2, 2, session=session_revertida)
    assert resultado == [{"id_atendimento": 2, "id_procedimento": 2}]
    assert session_revertida.get(ProcedimentoRealizado, (2, 2)) is None


def test_nao_remove_procedimento_faturado(session_revertida):
    """O seed marca (1, 1) com faturado = TRUE."""
    resultado = crud.remover_procedimento_realizado(1, 1, session=session_revertida)
    assert resultado == []
    assert session_revertida.get(ProcedimentoRealizado, (1, 1)) is not None


def test_remover_procedimento_inexistente(session_revertida):
    resultado = crud.remover_procedimento_realizado(
        999, 999, session=session_revertida
    )
    assert resultado == []
