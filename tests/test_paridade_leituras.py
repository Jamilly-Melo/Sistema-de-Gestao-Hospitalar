"""Cada consulta ORM tem que devolver o mesmo que o .sql que ela substitui.

Regra de comparação: **por padrão, compare as listas na ordem retornada.** Seis
das sete consultas de leitura têm ORDER BY no .sql, e a ordenação é parte do que
precisa ser verificado — passar essas por `ordenado` faria o teste aceitar
silenciosamente uma direção trocada ou um ORDER BY removido.

`ordenado` existe para o único caso sem ORDER BY,
`media_atendimentos_por_residente`, onde a ordem das linhas é indefinida e
comparar listas cruas daria falha intermitente sem bug nenhum.
"""

from datetime import datetime

from tests.conftest import ordenado

from sgh.queries import analiticas, basicas


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


def test_pacientes_sem_procedimento_risco_alto(executar_sql):
    """O .sql tem ORDER BY pe.nome ASC — comparar na ordem."""
    esperado = executar_sql(
        "sql/consultas-analiticas/pacientes_sem_procedimento_risco_alto.sql"
    )
    assert analiticas.pacientes_sem_procedimento_risco_alto() == esperado


def test_plantoes_por_residente_nas_unidades(executar_sql):
    """O .sql ordena por unidade NULLS LAST, total DESC, nome ASC — comparar na
    ordem é o que verifica o nulls_last(), a parte mais fácil de errar."""
    esperado = executar_sql(
        "sql/consultas-analiticas/plantoes_por_residente_nas_unidades.sql"
    )
    assert analiticas.plantoes_por_residente_nas_unidades() == esperado


def test_preceptores_que_supervisionaram(executar_sql):
    """O seed põe 6 atendimentos do preceptor 11 em julho de 2026, acima do
    corte de 5 do HAVING — a janela abaixo garante linhas na saída.

    O .sql tem ORDER BY total_atendimentos DESC, pe.nome ASC — comparar na ordem.
    """
    inicio = datetime(2026, 7, 1)
    fim = datetime(2026, 8, 1)
    esperado = executar_sql(
        "sql/consultas-analiticas/preceptores_que_supervisionaram.sql",
        (inicio, fim),
    )
    assert esperado, "seed mudou: a janela de julho/2026 deveria retornar linhas"
    assert analiticas.preceptores_que_supervisionaram(inicio, fim) == esperado


def test_ranking_residentes(executar_sql):
    """O .sql tem ORDER BY total_atendimentos DESC, pe.nome ASC — comparar na ordem."""
    esperado = executar_sql("sql/consultas-analiticas/ranking_residentes.sql")
    assert analiticas.ranking_residentes() == esperado
