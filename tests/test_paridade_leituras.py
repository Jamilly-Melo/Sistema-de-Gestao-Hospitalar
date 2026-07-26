"""Cada consulta ORM tem que devolver o mesmo que o .sql que ela substitui.

Regra de comparação: **por padrão, compare as listas na ordem retornada.** Seis
das sete consultas de leitura têm ORDER BY no .sql, e a ordenação é parte do que
precisa ser verificado — passar essas por `ordenado` faria o teste aceitar
silenciosamente uma direção trocada ou um ORDER BY removido.

`ordenado` existe para o único caso sem ORDER BY,
`media_atendimentos_por_residente`, onde a ordem das linhas é indefinida e
comparar listas cruas daria falha intermitente sem bug nenhum.
"""

from tests.conftest import ordenado

from sgh.queries import basicas


def test_atendimentos_do_paciente(executar_sql):
    """O .sql tem ORDER BY atendimento.data_hora DESC — comparar na ordem."""
    esperado = executar_sql("sql/consultas-basicas/atendimentos_do_paciente.sql")
    assert basicas.atendimentos_do_paciente() == esperado


def test_media_atendimentos_por_residente(executar_sql):
    """Única consulta sem ORDER BY — o único uso legítimo de `ordenado`."""
    esperado = executar_sql(
        "sql/consultas-basicas/media_atendimentos_por_residente.sql"
    )
    assert ordenado(basicas.media_atendimentos_por_residente()) == ordenado(esperado)


def test_procedimentos_em_atendimento(executar_sql):
    """O .sql tem ORDER BY a.id_atendimento — comparar na ordem."""
    esperado = executar_sql("sql/consultas-basicas/procedimentos_em_atendimento.sql")
    assert basicas.procedimentos_em_atendimento() == esperado


def test_colunas_da_media_batem_com_o_sql(executar_sql):
    """Postgres rebaixa aliases sem aspas: `pr.crm AS CRM` vira a chave `crm`."""
    esperado = executar_sql(
        "sql/consultas-basicas/media_atendimentos_por_residente.sql"
    )
    assert set(basicas.media_atendimentos_por_residente()[0]) == set(esperado[0])
