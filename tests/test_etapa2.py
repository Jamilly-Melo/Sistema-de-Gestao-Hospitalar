"""Consultas que expõem as views e procedures da etapa 2 via sgh/."""

from __future__ import annotations

from sgh.queries import etapa2


def test_pacientes_internados(session_revertida):
    resultado = etapa2.pacientes_internados(session=session_revertida)
    assert isinstance(resultado, list)
    for linha in resultado:
        assert linha["data_hora_saida"] is None
        assert {"id_paciente", "paciente", "unidade", "id_internacao"} <= set(linha)


def test_residentes_sem_supervisor(session_revertida):
    resultado = etapa2.residentes_sem_supervisor(session=session_revertida)
    assert isinstance(resultado, list)
    for linha in resultado:
        assert linha["titulacao"] not in ("DOUTOR", "POS_DOUTOR")


def test_estatisticas_atendimentos_mensal(session_revertida):
    resultado = etapa2.estatisticas_atendimentos_mensal(session=session_revertida)
    assert isinstance(resultado, list)
    if resultado:
        assert {"mes", "unidade", "total_atendimentos", "media_duracao_minutos"} <= set(
            resultado[0]
        )
