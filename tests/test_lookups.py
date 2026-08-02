"""Consultas de apoio para autocomplete: sem agregação, id + nome apenas."""

from __future__ import annotations

from sgh.queries import lookups


def test_listar_pacientes(session_revertida):
    resultado = lookups.listar_pacientes(session=session_revertida)
    assert len(resultado) == 5
    assert {"id_pessoa", "nome"} <= set(resultado[0])
    ids = {linha["id_pessoa"] for linha in resultado}
    assert ids == {1, 2, 3, 4, 5}


def test_listar_unidades(session_revertida):
    resultado = lookups.listar_unidades(session=session_revertida)
    assert len(resultado) == 3
    assert {"id_unidade", "nome"} <= set(resultado[0])


def test_listar_procedimentos(session_revertida):
    resultado = lookups.listar_procedimentos(session=session_revertida)
    assert len(resultado) > 0
    assert {"id_procedimento", "nome"} <= set(resultado[0])


def test_listar_preceptores(session_revertida):
    resultado = lookups.listar_preceptores(session=session_revertida)
    assert len(resultado) == 5
    ids = {linha["id_profissional"] for linha in resultado}
    assert ids == {11, 12, 13, 14, 15}
    assert {"id_profissional", "nome", "titulacao"} <= set(resultado[0])


def test_procedimentos_do_atendimento_traz_id_e_faturado():
    linhas = lookups.procedimentos_do_atendimento(1)
    assert linhas, "atendimento 1 deveria ter ao menos um procedimento no seed"
    for linha in linhas:
        assert set(linha) == {
            "id_procedimento",
            "nome",
            "quantidade",
            "tempo_real_minutos",
            "faturado",
        }
        assert isinstance(linha["id_procedimento"], int)
        assert isinstance(linha["faturado"], bool)


def test_procedimentos_do_atendimento_filtra_pelo_atendimento_pedido():
    from sgh.queries import basicas

    todos = basicas.procedimentos_em_atendimento()
    esperado = sum(1 for l in todos if l["id_atendimento"] == 1)
    assert len(lookups.procedimentos_do_atendimento(1)) == esperado


def test_procedimentos_do_atendimento_inexistente_devolve_lista_vazia():
    assert lookups.procedimentos_do_atendimento(999999) == []


def test_listar_pacientes_com_ultimo_atendimento_traz_id_e_uma_linha_por_paciente():
    linhas = lookups.listar_pacientes_com_ultimo_atendimento()
    ids = [linha["id_pessoa"] for linha in linhas]
    assert ids, "deveria haver pacientes no seed"
    assert len(ids) == len(set(ids)), "um paciente não pode aparecer duas vezes"
    for linha in linhas:
        assert set(linha) == {"id_pessoa", "nome", "data_hora"}


def test_listar_pacientes_com_ultimo_atendimento_cobre_todos_os_pacientes():
    assert len(lookups.listar_pacientes_com_ultimo_atendimento()) == len(
        lookups.listar_pacientes()
    )
