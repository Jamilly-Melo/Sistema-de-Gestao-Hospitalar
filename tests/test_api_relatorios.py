# tests/test_api_relatorios.py
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


def test_listar_relatorios_disponiveis(session_revertida):
    cliente = next(_cliente(session_revertida))
    resposta = cliente.get("/relatorios")
    assert resposta.status_code == 200
    nomes = {item["nome"] for item in resposta.json()}
    assert "Ranking de residentes" in nomes
    assert "Pacientes internados" in nomes
    # não deve incluir consultas básicas nem CRUD
    assert "Atendimentos do paciente" not in nomes
    assert "Inserir atendimento" not in nomes


def test_executar_relatorio_sem_parametros(session_revertida):
    cliente = next(_cliente(session_revertida))
    resposta = cliente.post("/relatorios/Ranking de residentes", json={})
    assert resposta.status_code == 200
    assert isinstance(resposta.json(), list)


def test_executar_relatorio_com_parametros(session_revertida):
    cliente = next(_cliente(session_revertida))
    resposta = cliente.post(
        "/relatorios/Preceptores que supervisionaram",
        json={"inicio": "2026-07-01T00:00:00", "fim": "2026-08-01T00:00:00"},
    )
    assert resposta.status_code == 200


def test_executar_relatorio_inexistente_devolve_404(session_revertida):
    cliente = next(_cliente(session_revertida))
    resposta = cliente.post("/relatorios/Não existe", json={})
    assert resposta.status_code == 404
