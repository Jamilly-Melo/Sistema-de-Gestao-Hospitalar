"""Testes da API do recurso Escala."""

from __future__ import annotations

from fastapi.testclient import TestClient

from api.dependencies import get_session
from api.main import app


def _cliente(session_revertida) -> TestClient:
    def _get_session():
        yield session_revertida

    app.dependency_overrides[get_session] = _get_session
    cliente = TestClient(app, raise_server_exceptions=False)
    yield cliente
    app.dependency_overrides.clear()


def test_listar_escalas(session_revertida):
    cliente = next(_cliente(session_revertida))
    resposta = cliente.get("/escalas")
    assert resposta.status_code == 200


# Seed real (sql/insercao_dados.sql, INSERT INTO escala): o residente 6 está
# escalado em 2026-07-01/MANHA e em 2026-07-05/NOITE — os mesmos valores já
# comprovados em tests/test_etapa2.py para sp_reajustar_escala.
def test_reajustar_escala(session_revertida):
    cliente = next(_cliente(session_revertida))
    resposta = cliente.post(
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


def test_reajustar_escala_conflito_devolve_422(session_revertida):
    cliente = next(_cliente(session_revertida))
    resposta = cliente.post(
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
