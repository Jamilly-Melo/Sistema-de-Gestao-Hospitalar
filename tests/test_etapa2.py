"""Consultas que expõem as views e procedures da etapa 2 via sgh/."""

from __future__ import annotations

from datetime import date, datetime

import pytest
from sqlalchemy.exc import DBAPIError

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


def test_tempo_medio_espera(session_revertida):
    resultado = etapa2.tempo_medio_espera(session=session_revertida)
    assert isinstance(resultado, list)
    if resultado:
        assert {"id_unidade", "unidade", "tempo_medio_espera"} <= set(resultado[0])


def test_registrar_atendimento_completo(session_revertida):
    resultado = etapa2.registrar_atendimento_completo(
        datetime(2026, 8, 1, 9, 0),
        30,
        3,
        7,
        12,
        2,
        [
            {
                "id_procedimento": 2,
                "quantidade": 1,
                "tempo_real_minutos": 10,
                "data_hora_inicio": datetime(2026, 8, 1, 9, 5),
            }
        ],
        session=session_revertida,
    )
    assert len(resultado) == 1
    assert isinstance(resultado[0]["id_atendimento"], int)


def test_registrar_atendimento_completo_recusa_procedimento_antes_da_chegada(
    session_revertida,
):
    with pytest.raises(DBAPIError):
        etapa2.registrar_atendimento_completo(
            datetime(2026, 8, 1, 9, 0),
            30,
            3,
            7,
            12,
            2,
            [
                {
                    "id_procedimento": 2,
                    "quantidade": 1,
                    "tempo_real_minutos": 10,
                    "data_hora_inicio": datetime(2026, 8, 1, 8, 0),
                }
            ],
            session=session_revertida,
        )


# Seed real (sql/insercao_dados.sql, INSERT INTO escala): o residente 6 está
# escalado em 2026-07-01/MANHA e em 2026-07-05/NOITE. Os literais abaixo usam
# essas duas linhas — a segunda serve como destino já ocupado para o teste de
# conflito — em vez dos placeholders de exemplo do brief, que não existem no
# seed.
def test_reajustar_escala(session_revertida):
    resultado = etapa2.reajustar_escala(
        6, date(2026, 7, 1), "MANHA", date(2026, 7, 20), "TARDE",
        session=session_revertida,
    )
    assert resultado == [
        {"id_residente": 6, "data_plantao": date(2026, 7, 20), "turno": "TARDE"}
    ]


def test_reajustar_escala_recusa_conflito_no_destino(session_revertida):
    with pytest.raises(DBAPIError):
        etapa2.reajustar_escala(
            6, date(2026, 7, 1), "MANHA", date(2026, 7, 5), "NOITE",
            session=session_revertida,
        )
