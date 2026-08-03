"""O catálogo é o contrato entre a camada de dados e qualquer interface.

Estes testes o percorrem inteiro, sem passar por Streamlit — é o mesmo caminho
que um endpoint /queries de um FastAPI futuro usaria.
"""

import pytest

from sgh.catalog import CATALOGO

ENTRADAS = [
    (categoria, nome, entrada)
    for categoria, consultas in CATALOGO.items()
    for nome, entrada in consultas.items()
]


def test_catalogo_tem_as_dezessete_entradas():
    assert len(ENTRADAS) == 17


@pytest.mark.parametrize("categoria,nome,entrada", ENTRADAS)
def test_entrada_do_catalogo_esta_bem_formada(categoria, nome, entrada):
    assert callable(entrada["fn"]), f"{nome}: fn não é chamável"
    assert isinstance(entrada["description"], str) and entrada["description"]
    assert isinstance(entrada["mutates"], bool)
    for param in entrada["params"]:
        assert {"name", "label", "type"} <= set(param), f"{nome}: parâmetro incompleto"
        assert param["type"] in {"text", "int", "select", "datetime"}
        if param["type"] == "select":
            assert param["options"], f"{nome}: select sem opções"


@pytest.mark.parametrize(
    "categoria,nome,entrada", [e for e in ENTRADAS if not e[2]["mutates"]]
)
def test_consultas_de_leitura_executam(categoria, nome, entrada, session_revertida):
    """As 7 leituras rodam com os defaults do catálogo e devolvem list[dict]."""
    args = [param.get("default") for param in entrada["params"]]
    resultado = entrada["fn"](*args, session=session_revertida)
    assert isinstance(resultado, list)
    assert all(isinstance(linha, dict) for linha in resultado)


def test_operacoes_de_escrita_executam(session_revertida):
    """As 3 operações de escrita, com os defaults do catálogo, dentro do rollback.

    O assert é sobre resultado não vazio, e não sobre o tipo: as três funções
    devolvem [] quando recusam a operação, então `isinstance(resultado, list)`
    passaria mesmo se todas recusassem tudo. Os defaults do catálogo precisam
    apontar para dados que existem no seed e satisfazem as pré-condições.
    """
    escritas = [entrada for _, _, entrada in ENTRADAS if entrada["mutates"]]
    assert len(escritas) == 3

    for entrada in escritas:
        faltando = [p["name"] for p in entrada["params"] if "default" not in p]
        assert not faltando, (
            f"{entrada['fn'].__name__}: parâmetros sem default no catálogo: "
            f"{faltando}. Toda operação de escrita precisa de defaults que a UI "
            f"possa pré-preencher e que este teste possa exercitar."
        )

        args = [param["default"] for param in entrada["params"]]
        resultado = entrada["fn"](*args, session=session_revertida)

        assert resultado, (
            f"{entrada['fn'].__name__} recusou a operação com os defaults do "
            f"catálogo — os defaults não satisfazem as pré-condições."
        )
        assert all(isinstance(linha, dict) for linha in resultado)


def test_categorias_relatorio_existem_no_catalogo():
    from sgh.catalog import CATALOGO, CATEGORIAS_RELATORIO

    assert CATEGORIAS_RELATORIO == (
        "Consultas analíticas",
        "Etapa 2",
        "Consultas avançadas",
    )
    for categoria in CATEGORIAS_RELATORIO:
        assert categoria in CATALOGO


def test_consultas_avancadas_estao_expostas_como_relatorio():
    from sgh.catalog import CATALOGO, CATEGORIAS_RELATORIO

    assert "Consultas avançadas" in CATALOGO
    assert "Consultas avançadas" in CATEGORIAS_RELATORIO

    esperadas = {
        "Preceptores de pacientes flamenguistas",
        "Último atendimento por paciente",
        "Percentual de procedimentos de risco alto",
    }
    assert set(CATALOGO["Consultas avançadas"]) == esperadas

    for entrada in CATALOGO["Consultas avançadas"].values():
        assert entrada["mutates"] is False
        assert entrada["params"] == []
        assert callable(entrada["fn"])


def test_toda_entrada_de_relatorio_declara_a_tecnica():
    """A tela mostra qual item da Etapa 2 cada relatório demonstra."""
    from sgh.catalog import CATALOGO, CATEGORIAS_RELATORIO

    tecnicas_validas = {"ORM", "ORM + eager loading", "View", "Stored procedure"}
    for categoria in CATEGORIAS_RELATORIO:
        for nome, entrada in CATALOGO[categoria].items():
            assert "tecnica" in entrada, f"{nome} não declara tecnica"
            assert entrada["tecnica"] in tecnicas_validas, (
                f"{nome} declara tecnica inesperada: {entrada['tecnica']}"
            )


def test_tecnicas_batem_com_a_implementacao_real():
    """View e procedure são as de etapa2.py; eager loading é a consulta que usa
    selectinload. Se uma consulta mudar de técnica, este teste avisa."""
    from sgh.catalog import CATALOGO

    esperado = {
        "Pacientes internados": "View",
        "Residentes sem supervisor adequado": "View",
        "Estatísticas mensais de atendimentos": "View",
        "Tempo médio de espera": "Stored procedure",
        "Último atendimento por paciente": "ORM + eager loading",
    }
    encontrado = {}
    for categoria in ("Etapa 2", "Consultas avançadas"):
        for nome, entrada in CATALOGO[categoria].items():
            if nome in esperado:
                encontrado[nome] = entrada["tecnica"]

    assert encontrado == esperado
