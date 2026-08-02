# tests/test_api_lookups.py
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


def test_lookup_pacientes(session_revertida):
    cliente = next(_cliente(session_revertida))
    resposta = cliente.get("/lookups/pacientes")
    assert resposta.status_code == 200
    assert len(resposta.json()) == 5


def test_lookup_unidades(session_revertida):
    cliente = next(_cliente(session_revertida))
    resposta = cliente.get("/lookups/unidades")
    assert resposta.status_code == 200
    assert len(resposta.json()) == 3


def test_lookup_procedimentos(session_revertida):
    cliente = next(_cliente(session_revertida))
    resposta = cliente.get("/lookups/procedimentos")
    assert resposta.status_code == 200
    assert len(resposta.json()) > 0
