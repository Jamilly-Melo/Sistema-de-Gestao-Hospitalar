from __future__ import annotations


def test_listar_residentes(cliente_api):
    resposta = cliente_api.get("/profissionais/residentes")
    assert resposta.status_code == 200
    # Seed: 5 residentes com atendimento + 1 sem nenhum (id_profissional 16).
    assert len(resposta.json()) == 6


def test_listar_preceptores(cliente_api):
    resposta = cliente_api.get("/profissionais/preceptores")
    assert resposta.status_code == 200
    assert len(resposta.json()) == 5
