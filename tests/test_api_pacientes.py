"""Testes de API para /pacientes, usando a mesma sessão revertível dos testes
de sgh/ via dependency_overrides."""

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


def test_listar_pacientes(session_revertida):
    cliente = next(_cliente(session_revertida))
    resposta = cliente.get("/pacientes")
    assert resposta.status_code == 200
    assert isinstance(resposta.json(), list)


def test_atualizar_endereco_do_paciente(session_revertida):
    cliente = next(_cliente(session_revertida))
    resposta = cliente.patch(
        "/pacientes/1", json={"campo": "endereco", "valor": "Rua Nova, 100"}
    )
    assert resposta.status_code == 200
    assert resposta.json() == {"id_pessoa": 1}


def test_atualizar_paciente_inexistente_devolve_404(session_revertida):
    cliente = next(_cliente(session_revertida))
    resposta = cliente.patch(
        "/pacientes/999", json={"campo": "endereco", "valor": "Rua Nova, 100"}
    )
    assert resposta.status_code == 404


def test_atualizar_campo_invalido_devolve_422(session_revertida):
    cliente = next(_cliente(session_revertida))
    resposta = cliente.patch(
        "/pacientes/1", json={"campo": "grupo_sanguineo", "valor": "AB-"}
    )
    assert resposta.status_code == 422
