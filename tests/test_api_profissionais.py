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


def test_listar_residentes(session_revertida):
    cliente = next(_cliente(session_revertida))
    resposta = cliente.get("/profissionais/residentes")
    assert resposta.status_code == 200
    assert len(resposta.json()) == 5


def test_listar_preceptores(session_revertida):
    cliente = next(_cliente(session_revertida))
    resposta = cliente.get("/profissionais/preceptores")
    assert resposta.status_code == 200
    assert len(resposta.json()) == 5
