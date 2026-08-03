"""Testes de API para /pacientes, usando a mesma sessão revertível dos testes
de sgh/ via dependency_overrides."""

from __future__ import annotations


def test_listagem_de_pacientes(cliente_api):
    """Uma linha por paciente, com o último atendimento."""
    resposta = cliente_api.get("/pacientes/listagem")
    assert resposta.status_code == 200

    linhas = resposta.json()
    assert isinstance(linhas, list) and linhas
    for linha in linhas:
        assert set(linha) == {
            "id_pessoa",
            "nome",
            "data_hora",
            "residente",
            "preceptor",
            "procedimentos",
        }


def test_rota_antiga_de_pacientes_nao_existe_mais(cliente_api):
    """`GET /pacientes` servia uma linha por atendimento e ficou sem consumidor
    quando a tela passou a mostrar uma linha por paciente."""
    assert cliente_api.get("/pacientes").status_code == 404


def test_atualizar_endereco_do_paciente(cliente_api):
    resposta = cliente_api.patch(
        "/pacientes/1", json={"campo": "endereco", "valor": "Rua Nova, 100"}
    )
    assert resposta.status_code == 200
    assert resposta.json() == {"id_pessoa": 1}


def test_atualizar_paciente_inexistente_devolve_404(cliente_api):
    resposta = cliente_api.patch(
        "/pacientes/999", json={"campo": "endereco", "valor": "Rua Nova, 100"}
    )
    assert resposta.status_code == 404


def test_atualizar_campo_invalido_devolve_422(cliente_api):
    resposta = cliente_api.patch(
        "/pacientes/1", json={"campo": "grupo_sanguineo", "valor": "AB-"}
    )
    assert resposta.status_code == 422
