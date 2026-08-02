# tests/test_api_lookups.py
from __future__ import annotations


def test_lookup_pacientes(cliente_api):
    resposta = cliente_api.get("/lookups/pacientes")
    assert resposta.status_code == 200
    assert len(resposta.json()) == 5


def test_lookup_unidades(cliente_api):
    resposta = cliente_api.get("/lookups/unidades")
    assert resposta.status_code == 200
    assert len(resposta.json()) == 3


def test_lookup_procedimentos(cliente_api):
    resposta = cliente_api.get("/lookups/procedimentos")
    assert resposta.status_code == 200
    assert len(resposta.json()) > 0
