"""Testes das consultas avançadas do item 5 da Etapa 2."""

from __future__ import annotations

from decimal import Decimal

from sgh.queries import avancadas


def test_flamenguistas_traz_preceptor_e_titulacao_sem_repetir():
    linhas = avancadas.preceptores_de_pacientes_flamenguistas()
    assert linhas, "o seed tem flamenguistas atendidos, deveria retornar linhas"
    for linha in linhas:
        assert set(linha) == {"preceptor", "titulacao"}
        assert isinstance(linha["preceptor"], str)
    nomes = [linha["preceptor"] for linha in linhas]
    assert len(nomes) == len(set(nomes)), "distinct() deveria evitar repetição"


def test_flamenguistas_e_subconjunto_de_todos_os_preceptores():
    """Nem todo preceptor atendeu flamenguista — a consulta precisa filtrar."""
    from sgh.queries import lookups

    todos = {p["nome"] for p in lookups.listar_preceptores()}
    filtrados = {p["preceptor"] for p in avancadas.preceptores_de_pacientes_flamenguistas()}
    assert filtrados <= todos


def test_percentual_cobre_todos_os_residentes():
    """Inclui quem não atendeu ninguém — o seed tem um residente assim."""
    from sgh.queries import basicas

    linhas = avancadas.percentual_procedimentos_risco_alto()
    total_residentes = len(basicas.media_atendimentos_por_residente())
    assert len(linhas) == total_residentes
    for linha in linhas:
        assert set(linha) == {
            "residente",
            "total_procedimentos",
            "procedimentos_risco_alto",
            "percentual_risco_alto",
        }


def test_percentual_e_zero_e_nao_erro_para_residente_sem_atendimento():
    linhas = avancadas.percentual_procedimentos_risco_alto()
    sem_atendimento = [l for l in linhas if l["total_procedimentos"] == 0]
    assert sem_atendimento, "o seed tem um residente sem atendimento"
    for linha in sem_atendimento:
        assert Decimal(str(linha["percentual_risco_alto"])) == Decimal("0")


def test_percentual_bate_com_a_contagem_da_propria_linha():
    for linha in avancadas.percentual_procedimentos_risco_alto():
        total = linha["total_procedimentos"]
        if total == 0:
            continue
        esperado = round(linha["procedimentos_risco_alto"] * 100 / total, 1)
        assert abs(float(linha["percentual_risco_alto"]) - esperado) < 0.05


def test_ultimo_atendimento_tem_uma_linha_por_paciente():
    from sgh.queries import lookups

    linhas = avancadas.ultimo_atendimento_por_paciente()
    assert len(linhas) == len(lookups.listar_pacientes())
    for linha in linhas:
        assert set(linha) == {
            "paciente",
            "data_hora",
            "residente",
            "preceptor",
            "procedimentos",
        }
        assert isinstance(linha["procedimentos"], list)


def test_ultimo_atendimento_e_mesmo_o_mais_recente():
    """Compara com a consulta básica, que lista todos os atendimentos."""
    from sgh.queries import basicas

    todos = basicas.atendimentos_do_paciente()
    mais_recente_por_paciente: dict[str, object] = {}
    for linha in todos:
        if linha["data_hora"] is None:
            continue
        atual = mais_recente_por_paciente.get(linha["nome"])
        if atual is None or linha["data_hora"] > atual:
            mais_recente_por_paciente[linha["nome"]] = linha["data_hora"]

    for linha in avancadas.ultimo_atendimento_por_paciente():
        esperado = mais_recente_por_paciente.get(linha["paciente"])
        assert linha["data_hora"] == esperado


def test_paciente_sem_atendimento_vem_com_campos_nulos():
    linhas = avancadas.ultimo_atendimento_por_paciente()
    sem = [l for l in linhas if l["data_hora"] is None]
    assert sem, "o seed tem um paciente sem atendimento"
    for linha in sem:
        assert linha["residente"] is None
        assert linha["preceptor"] is None
        assert linha["procedimentos"] == []


def test_lista_de_procedimentos_bate_com_a_consulta_de_apoio():
    """Atendimentos 1, 6 e 9 do seed têm múltiplos procedimentos."""
    from sgh.queries import lookups

    for linha in avancadas.ultimo_atendimento_por_paciente():
        if linha["data_hora"] is None:
            continue
        assert all(isinstance(nome, str) for nome in linha["procedimentos"])

    # ao menos um paciente deve ter mais de um procedimento no último atendimento
    assert any(
        len(l["procedimentos"]) > 1
        for l in avancadas.ultimo_atendimento_por_paciente()
    ), "o seed tem atendimentos com múltiplos procedimentos"
