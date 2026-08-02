"""Testes da API do recurso Escala."""

from __future__ import annotations


def test_listar_escalas(cliente_api):
    resposta = cliente_api.get("/escalas")
    assert resposta.status_code == 200


# Seed real (sql/insercao_dados.sql, INSERT INTO escala): o residente 6 está
# escalado em 2026-07-01/MANHA e em 2026-07-05/NOITE — os mesmos valores já
# comprovados em tests/test_etapa2.py para sp_reajustar_escala.
def test_reajustar_escala(cliente_api):
    resposta = cliente_api.post(
        "/escalas/reajustar",
        json={
            "id_residente": 6,
            "data_origem": "2026-07-01",
            "turno_origem": "MANHA",
            "data_destino": "2026-07-20",
            "turno_destino": "TARDE",
        },
    )
    assert resposta.status_code == 200
    assert resposta.json() == {
        "id_residente": 6,
        "data_plantao": "2026-07-20",
        "turno": "TARDE",
    }


def test_reajustar_escala_conflito_devolve_422(cliente_api):
    resposta = cliente_api.post(
        "/escalas/reajustar",
        json={
            "id_residente": 6,
            "data_origem": "2026-07-01",
            "turno_origem": "MANHA",
            "data_destino": "2026-07-05",
            "turno_destino": "NOITE",
        },
    )
    assert resposta.status_code == 422
