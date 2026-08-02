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


def test_listar_atendimentos(session_revertida):
    cliente = next(_cliente(session_revertida))
    resposta = cliente.get("/atendimentos")
    assert resposta.status_code == 200


def test_criar_atendimento(session_revertida):
    cliente = next(_cliente(session_revertida))
    resposta = cliente.post(
        "/atendimentos",
        json={
            "data_hora": "2026-08-01T09:00:00",
            "duracao_minutos": 30,
            "id_paciente": 3,
            "id_residente": 7,
            "id_preceptor": 12,
            "id_unidade": 2,
            "procedimentos": [
                {
                    "id_procedimento": 2,
                    "quantidade": 1,
                    "tempo_real_minutos": 10,
                    "data_hora_inicio": "2026-08-01T09:05:00",
                }
            ],
        },
    )
    assert resposta.status_code == 200
    assert isinstance(resposta.json()["id_atendimento"], int)


def test_criar_atendimento_paciente_inexistente_devolve_409(session_revertida):
    cliente = next(_cliente(session_revertida))
    resposta = cliente.post(
        "/atendimentos",
        json={
            "data_hora": "2026-08-01T09:00:00",
            "duracao_minutos": 30,
            "id_paciente": 999,
            "id_residente": 7,
            "id_preceptor": 12,
            "id_unidade": 2,
            "procedimentos": [
                {
                    "id_procedimento": 2,
                    "quantidade": 1,
                    "tempo_real_minutos": 10,
                    "data_hora_inicio": "2026-08-01T09:05:00",
                }
            ],
        },
    )
    assert resposta.status_code == 409


def test_remover_procedimento_nao_faturado(session_revertida):
    cliente = next(_cliente(session_revertida))
    resposta = cliente.delete("/atendimentos/2/procedimentos/2")
    assert resposta.status_code == 200


def test_remover_procedimento_faturado_devolve_422(session_revertida):
    cliente = next(_cliente(session_revertida))
    resposta = cliente.delete("/atendimentos/1/procedimentos/1")
    assert resposta.status_code == 422
