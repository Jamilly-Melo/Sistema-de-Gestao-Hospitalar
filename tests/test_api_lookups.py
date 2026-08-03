# tests/test_api_lookups.py
from __future__ import annotations


def test_lookup_pacientes(cliente_api):
    resposta = cliente_api.get("/lookups/pacientes")
    assert resposta.status_code == 200
    # Seed: 5 pacientes com atendimento + 1 sem nenhum (id_pessoa 17).
    assert len(resposta.json()) == 6


def test_lookup_unidades(cliente_api):
    resposta = cliente_api.get("/lookups/unidades")
    assert resposta.status_code == 200
    # Seed: 3 unidades originais + 1 sem plantão (Pronto-Socorro).
    assert len(resposta.json()) == 4


def test_lookup_procedimentos(cliente_api):
    resposta = cliente_api.get("/lookups/procedimentos")
    assert resposta.status_code == 200
    assert len(resposta.json()) > 0
