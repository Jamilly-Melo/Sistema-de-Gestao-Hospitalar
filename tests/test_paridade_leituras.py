"""Cada consulta ORM tem que devolver o mesmo que o .sql que ela substitui.

As comparações passam por `ordenado` porque várias consultas não têm ORDER BY —
a ordem das linhas é indefinida e comparar listas cruas daria falso negativo.
"""

from tests.conftest import ordenado

from sgh.queries import basicas


def test_atendimentos_do_paciente(executar_sql):
    esperado = executar_sql("sql/consultas-basicas/atendimentos_do_paciente.sql")
    assert ordenado(basicas.atendimentos_do_paciente()) == ordenado(esperado)


def test_media_atendimentos_por_residente(executar_sql):
    esperado = executar_sql(
        "sql/consultas-basicas/media_atendimentos_por_residente.sql"
    )
    assert ordenado(basicas.media_atendimentos_por_residente()) == ordenado(esperado)


def test_procedimentos_em_atendimento(executar_sql):
    esperado = executar_sql("sql/consultas-basicas/procedimentos_em_atendimento.sql")
    assert ordenado(basicas.procedimentos_em_atendimento()) == ordenado(esperado)


def test_colunas_da_media_batem_com_o_sql(executar_sql):
    """Postgres rebaixa aliases sem aspas: `pr.crm AS CRM` vira a chave `crm`."""
    esperado = executar_sql(
        "sql/consultas-basicas/media_atendimentos_por_residente.sql"
    )
    assert set(basicas.media_atendimentos_por_residente()[0]) == set(esperado[0])
