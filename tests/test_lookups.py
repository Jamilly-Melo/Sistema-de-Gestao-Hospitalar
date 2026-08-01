"""Consultas de apoio para autocomplete: sem agregação, id + nome apenas."""

from __future__ import annotations

from sgh.queries import lookups


def test_listar_pacientes(session_revertida):
    resultado = lookups.listar_pacientes(session=session_revertida)
    assert len(resultado) == 5
    assert {"id_pessoa", "nome"} <= set(resultado[0])
    ids = {linha["id_pessoa"] for linha in resultado}
    assert ids == {1, 2, 3, 4, 5}


def test_listar_unidades(session_revertida):
    resultado = lookups.listar_unidades(session=session_revertida)
    assert len(resultado) == 3
    assert {"id_unidade", "nome"} <= set(resultado[0])


def test_listar_procedimentos(session_revertida):
    resultado = lookups.listar_procedimentos(session=session_revertida)
    assert len(resultado) > 0
    assert {"id_procedimento", "nome"} <= set(resultado[0])


def test_listar_preceptores(session_revertida):
    resultado = lookups.listar_preceptores(session=session_revertida)
    assert len(resultado) == 5
    ids = {linha["id_profissional"] for linha in resultado}
    assert ids == {11, 12, 13, 14, 15}
    assert {"id_profissional", "nome", "titulacao"} <= set(resultado[0])
