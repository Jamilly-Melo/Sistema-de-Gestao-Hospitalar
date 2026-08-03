"""Smoke test do app FastAPI — sem rotas de negócio ainda."""

from __future__ import annotations

from fastapi.testclient import TestClient

from api.main import app


def test_app_sobe_e_responde_openapi():
    cliente = TestClient(app)
    resposta = cliente.get("/openapi.json")
    assert resposta.status_code == 200
