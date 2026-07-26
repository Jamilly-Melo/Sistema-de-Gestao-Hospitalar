"""Catálogo de consultas expostas pela aplicação.

Vive na camada de dados, não na interface: um endpoint /queries de um FastAPI
futuro serve estes mesmos metadados (sem o campo `fn`) para um frontend montar
formulários dinamicamente, sem reescrever nada em TypeScript.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from sgh.queries import analiticas, basicas, crud

CATALOGO: dict[str, dict[str, dict[str, Any]]] = {
    "Consultas básicas": {
        "Atendimentos do paciente": {
            "description": "Lista todos os atendimentos (ordenados por data).",
            "params": [],
            "mutates": False,
            "fn": basicas.atendimentos_do_paciente,
        },
        "Média de duração por residente": {
            "description": "Tempo médio de duração dos atendimentos por residente.",
            "params": [],
            "mutates": False,
            "fn": basicas.media_atendimentos_por_residente,
        },
        "Procedimentos em atendimento": {
            "description": "Procedimentos realizados em cada atendimento.",
            "params": [],
            "mutates": False,
            "fn": basicas.procedimentos_em_atendimento,
        },
    },
    "Consultas analíticas": {
        "Pacientes sem procedimento de risco ALTO": {
            "description": "Pacientes que nunca realizaram procedimento de risco ALTO.",
            "params": [],
            "mutates": False,
            "fn": analiticas.pacientes_sem_procedimento_risco_alto,
        },
        "Plantões por residente nas unidades": {
            "description": "Plantões escalados por residente no mês corrente, por unidade.",
            "params": [],
            "mutates": False,
            "fn": analiticas.plantoes_por_residente_nas_unidades,
        },
        "Preceptores que supervisionaram": {
            "description": "Preceptores com mais de 5 atendimentos em um intervalo.",
            "params": [
                {
                    "name": "inicio",
                    "label": "Início do período",
                    "type": "datetime",
                    "default": datetime(2026, 7, 1),
                },
                {
                    "name": "fim",
                    "label": "Fim do período",
                    "type": "datetime",
                    "default": datetime(2026, 8, 1),
                },
            ],
            "mutates": False,
            "fn": analiticas.preceptores_que_supervisionaram,
        },
        "Ranking de residentes": {
            "description": "Ranking dos residentes por número de atendimentos.",
            "params": [],
            "mutates": False,
            "fn": analiticas.ranking_residentes,
        },
    },
    "CRUD": {
        "Atualizar dados do paciente": {
            "description": "Atualiza endereço ou número de convênio de um paciente.",
            "params": [
                {
                    "name": "campo",
                    "label": "Coluna",
                    "type": "select",
                    "options": ["endereco", "num_convenio"],
                },
                {"name": "valor", "label": "Novo valor", "type": "text"},
                {"name": "id_paciente", "label": "ID do paciente", "type": "int"},
            ],
            "mutates": True,
            "fn": crud.atualizar_dados_paciente,
        },
        "Inserir atendimento": {
            "description": (
                "Insere atendimento se paciente, residente, preceptor e unidade "
                "existirem. IDs do seed: pacientes 1–5, residentes 6–10, "
                "preceptores 11–15, unidades 1–3."
            ),
            "params": [
                {
                    "name": "data_hora",
                    "label": "Data/hora",
                    "type": "datetime",
                    "default": datetime(2026, 8, 1, 8, 0),
                },
                {
                    "name": "duracao_minutos",
                    "label": "Duração (minutos)",
                    "type": "int",
                    "default": 30,
                },
                {"name": "id_paciente", "label": "ID do paciente", "type": "int", "default": 1},
                {"name": "id_residente", "label": "ID do residente", "type": "int", "default": 6},
                {"name": "id_preceptor", "label": "ID do preceptor", "type": "int", "default": 11},
                {"name": "id_unidade", "label": "ID da unidade", "type": "int", "default": 1},
            ],
            "mutates": True,
            "fn": crud.inserir_atendimento,
        },
        "Remover procedimento realizado": {
            "description": "Remove procedimento realizado somente se faturado = FALSE.",
            "params": [
                {"name": "id_atendimento", "label": "ID do atendimento", "type": "int"},
                {"name": "id_procedimento", "label": "ID do procedimento", "type": "int"},
            ],
            "mutates": True,
            "fn": crud.remover_procedimento_realizado,
        },
    },
}
