"""Consultas de apoio para autocomplete: sem agregação, id + nome apenas."""

from __future__ import annotations

from sgh.queries import lookups


def test_listar_pacientes(session_revertida):
    resultado = lookups.listar_pacientes(session=session_revertida)
    # Seed: 5 pacientes com atendimento + 1 sem nenhum (id_pessoa 17).
    assert len(resultado) == 6
    assert {"id_pessoa", "nome"} <= set(resultado[0])
    ids = {linha["id_pessoa"] for linha in resultado}
    assert ids == {1, 2, 3, 4, 5, 17}


def test_listar_unidades(session_revertida):
    resultado = lookups.listar_unidades(session=session_revertida)
    # Seed: 3 unidades originais + 1 sem plantão (Pronto-Socorro).
    assert len(resultado) == 4
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


def test_plantoes_do_residente_traz_data_turno_e_unidade():
    from sgh.queries import basicas

    residentes = basicas.media_atendimentos_por_residente()
    assert residentes, "o seed deveria ter residentes"

    com_plantao = []
    for residente in residentes:
        linhas = lookups.plantoes_do_residente(residente["id"])
        for linha in linhas:
            assert set(linha) == {"id_escala", "data_plantao", "turno", "unidade"}
            assert linha["turno"] in {"MANHA", "TARDE", "NOITE"}
        if linhas:
            com_plantao.append(residente["id"])

    assert com_plantao, "algum residente do seed deveria ter plantão"


def test_plantoes_do_residente_sem_plantao_devolve_lista_vazia():
    """O seed tem um residente sem nenhum plantão — a tela precisa lidar com
    isso sem quebrar."""
    from sgh.queries import basicas

    vazios = [
        r["id"]
        for r in basicas.media_atendimentos_por_residente()
        if not lookups.plantoes_do_residente(r["id"])
    ]
    assert vazios, "o seed deveria ter residente sem plantão"


def test_plantoes_do_residente_inexistente_devolve_lista_vazia():
    assert lookups.plantoes_do_residente(999999) == []


def test_plantoes_do_residente_filtra_pelo_residente_pedido():
    """Somando os plantões de todos os residentes chega-se ao total de escalas."""
    from sgh.database import SessionLocal
    from sgh.models import Escala
    from sqlalchemy import func, select

    from sgh.queries import basicas

    with SessionLocal() as sessao:
        total = sessao.execute(select(func.count(Escala.id_escala))).scalar_one()

    soma = sum(
        len(lookups.plantoes_do_residente(r["id"]))
        for r in basicas.media_atendimentos_por_residente()
    )
    assert soma == total
