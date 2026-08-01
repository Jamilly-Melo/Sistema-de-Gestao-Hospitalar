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

from tests.conftest import ROOT, ordenado

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


def test_plantoes_mantem_residente_sem_plantao_no_mes(session_revertida):
    """O caso que o teste de paridade sozinho não alcança.

    `plantoes_por_residente_nas_unidades` põe as condições de data no ON do LEFT
    JOIN justamente para manter os residentes sem plantão no mês, com unidade
    nula e total zero. Mas o seed tem as 10 escalas todas no mesmo mês e cobrindo
    os 5 residentes — então, enquanto a data corrente cair nesse mês, nenhuma
    linha sai com unidade nula, e mover as condições para o WHERE não faria
    nenhum teste falhar.

    Aqui o cenário é construído removendo as escalas de um residente e desfeito
    no rollback da fixture. Os dois lados rodam na MESMA sessão, porque a
    remoção não está commitada — a fixture `executar_sql` abre sessão própria e
    não a enxergaria.
    """
    from sqlalchemy import delete

    from sgh.models import Escala

    session_revertida.execute(delete(Escala).where(Escala.id_residente == 6))
    session_revertida.flush()

    atual = analiticas.plantoes_por_residente_nas_unidades(session=session_revertida)

    assert any(
        linha["unidade"] is None and linha["total_plantoes"] == 0 for linha in atual
    ), "nenhum residente sem plantão no resultado — o ramo do LEFT JOIN não foi exercitado"

    sql = (
        ROOT / "sql/consultas-analiticas/plantoes_por_residente_nas_unidades.sql"
    ).read_text(encoding="utf-8")
    esperado = [
        dict(linha)
        for linha in session_revertida.connection().exec_driver_sql(sql).mappings()
    ]
    assert atual == esperado


def test_ranking_residentes_com_residente_sem_atendimento(session_revertida):
    """O seed empata todos os residentes em 2 atendimentos, então nem o LEFT
    JOIN nem o DESC de ranking_residentes têm poder de detecção sozinhos:
    trocar outerjoin por join, ou desc por asc, não muda nada. Apagar os
    atendimentos do residente 6 zera o total dele mantendo os demais em 2,
    o que cobre as duas coisas de uma vez: a linha do LEFT JOIN aparece e os
    agregados deixam de ser todos iguais.
    """
    from sqlalchemy import delete

    from sgh.models import Atendimento

    session_revertida.execute(
        delete(Atendimento).where(Atendimento.id_residente == 6)
    )
    session_revertida.flush()

    atual = analiticas.ranking_residentes(session=session_revertida)

    assert any(
        linha["total_atendimentos"] == 0 for linha in atual
    ), "nenhum residente com total 0 — o ramo do LEFT JOIN não foi exercitado"

    sql = (ROOT / "sql/consultas-analiticas/ranking_residentes.sql").read_text(
        encoding="utf-8"
    )
    esperado = [
        dict(linha)
        for linha in session_revertida.connection().exec_driver_sql(sql).mappings()
    ]
    assert atual == esperado


def test_media_atendimentos_por_residente_com_residente_sem_atendimento(
    session_revertida,
):
    """Mesmo raciocínio de ranking_residentes, aplicado a
    media_atendimentos_por_residente: sem um residente zerado, outerjoin vira
    join sem quebrar nenhum teste. Sem ORDER BY no .sql, compara via
    `ordenado`."""
    from sqlalchemy import delete

    from sgh.models import Atendimento

    session_revertida.execute(
        delete(Atendimento).where(Atendimento.id_residente == 6)
    )
    session_revertida.flush()

    atual = basicas.media_atendimentos_por_residente(session=session_revertida)

    assert any(
        linha["tempo_medio_de_atendimentos"] is None for linha in atual
    ), "nenhum residente sem atendimento no resultado — o ramo do LEFT JOIN não foi exercitado"

    sql = (
        ROOT / "sql/consultas-basicas/media_atendimentos_por_residente.sql"
    ).read_text(encoding="utf-8")
    esperado = [
        dict(linha)
        for linha in session_revertida.connection().exec_driver_sql(sql).mappings()
    ]
    assert ordenado(atual) == ordenado(esperado)


def test_atendimentos_do_paciente_com_paciente_sem_atendimento(session_revertida):
    """O seed nunca deixa um paciente sem atendimento, então outerjoin virar
    join não quebra o teste de paridade. Apagar os atendimentos do paciente 1
    cria esse cenário dentro do rollback da fixture."""
    from sqlalchemy import delete

    from sgh.models import Atendimento

    session_revertida.execute(delete(Atendimento).where(Atendimento.id_paciente == 1))
    session_revertida.flush()

    atual = basicas.atendimentos_do_paciente(session=session_revertida)

    assert any(
        linha["data_hora"] is None for linha in atual
    ), "nenhum paciente sem atendimento no resultado — o ramo do LEFT JOIN não foi exercitado"

    sql = (ROOT / "sql/consultas-basicas/atendimentos_do_paciente.sql").read_text(
        encoding="utf-8"
    )
    esperado = [
        dict(linha)
        for linha in session_revertida.connection().exec_driver_sql(sql).mappings()
    ]
    assert atual == esperado


def test_plantoes_por_residente_nas_unidades_desc_com_totais_distintos(
    session_revertida,
):
    """`test_plantoes_mantem_residente_sem_plantao_no_mes` cobre o NULLS LAST e
    o ramo do LEFT JOIN, mas não dá poder de detecção ao `desc(total_plantoes)`
    em si: a linha do residente sem plantão tem unidade nula, que já vai por
    último por causa do NULLS LAST, então o total dela nunca é comparado
    contra o de outra linha da mesma unidade. No seed, todo grupo
    (unidade, residente) empata em 2 plantões. Um plantão extra para o
    residente 6 na unidade 1 rompe esse empate dentro do mesmo grupo de
    unidade, dando ao DESC algo de fato para ordenar."""
    from datetime import date

    from sgh.models import Escala

    session_revertida.add(
        Escala(
            data_plantao=date(2026, 7, 15),
            turno="TARDE",
            id_unidade=1,
            id_residente=6,
            id_preceptor=11,
        )
    )
    session_revertida.flush()

    atual = analiticas.plantoes_por_residente_nas_unidades(session=session_revertida)

    totais = {linha["total_plantoes"] for linha in atual}
    assert len(totais) >= 2, "totais de plantão continuam todos iguais — DESC não tem o que ordenar"

    sql = (
        ROOT / "sql/consultas-analiticas/plantoes_por_residente_nas_unidades.sql"
    ).read_text(encoding="utf-8")
    esperado = [
        dict(linha)
        for linha in session_revertida.connection().exec_driver_sql(sql).mappings()
    ]
    assert atual == esperado


def test_preceptores_que_supervisionaram_desc_com_totais_distintos(session_revertida):
    """O seed só faz o preceptor 11 passar do corte de 5 na janela de
    julho/2026 — nenhuma segunda linha existe para o `desc(total_atendimentos)`
    ordenar contra. Insere atendimentos extras para o preceptor 12 dentro do
    rollback, dando a ele um total diferente do preceptor 11 e também acima
    de 5."""
    from datetime import datetime

    from sgh.models import Atendimento

    novos = [
        Atendimento(
            data_hora=datetime(2026, 7, 20, 8 + i, 0),
            duracao_minutos=30,
            id_paciente=(i % 5) + 1,
            id_residente=7,
            id_preceptor=12,
            id_unidade=2,
        )
        for i in range(7)
    ]
    session_revertida.add_all(novos)
    session_revertida.flush()

    inicio = datetime(2026, 7, 1)
    fim = datetime(2026, 8, 1)
    atual = analiticas.preceptores_que_supervisionaram(
        inicio, fim, session=session_revertida
    )

    totais = {linha["total_atendimentos"] for linha in atual}
    assert len(totais) >= 2, "totais continuam iguais — DESC não tem o que ordenar"

    sql = (
        ROOT / "sql/consultas-analiticas/preceptores_que_supervisionaram.sql"
    ).read_text(encoding="utf-8")
    esperado = [
        dict(linha)
        for linha in session_revertida.connection()
        .exec_driver_sql(sql, (inicio, fim))
        .mappings()
    ]
    assert esperado, "preceptor 12 deveria passar do corte de 5"
    assert atual == esperado


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
