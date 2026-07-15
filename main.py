from __future__ import annotations

from datetime import datetime, time
from pathlib import Path

import pandas as pd
import streamlit as st
from psycopg2 import connect
from psycopg2.extras import RealDictCursor

ROOT = Path(__file__).resolve().parent

DB_CONFIG = {
    "host": "database",
    "port": "5432",
    "database": "sgh_db",
    "user": "postgres",
    "password": "postgres",
}

QUERIES: dict[str, dict[str, dict]] = {
    "Consultas básicas": {
        "Atendimentos do paciente": {
            "path": "sql/consultas-basicas/atendimentos_do_paciente.sql",
            "description": "Lista todos os atendimentos (ordenados por data).",
            "params": [],
            "mutates": False,
        },
        "Média de duração por residente": {
            "path": "sql/consultas-basicas/media_atendimentos_por_residente.sql",
            "description": "Tempo médio de duração dos atendimentos por residente.",
            "params": [],
            "mutates": False,
        },
        "Procedimentos em atendimento": {
            "path": "sql/consultas-basicas/procedimentos_em_atendimento.sql",
            "description": "Procedimentos realizados em cada atendimento.",
            "params": [],
            "mutates": False,
        },
    },
    "Consultas analíticas": {
        "Pacientes sem procedimento de risco ALTO": {
            "path": "sql/consultas-analiticas/pacientes_sem_procedimento_risco_alto.sql",
            "description": "Pacientes que nunca realizaram procedimento de risco ALTO.",
            "params": [],
            "mutates": False,
        },
        "Plantões por residente nas unidades": {
            "path": "sql/consultas-analiticas/plantoes_por_residente_nas_unidades.sql",
            "description": "Plantões escalados por residente no mês corrente, por unidade.",
            "params": [],
            "mutates": False,
        },
        "Preceptores que supervisionaram": {
            "path": "sql/consultas-analiticas/preceptores_que_supervisionaram.sql",
            "description": "Preceptores com mais de 5 atendimentos em um intervalo.",
            "params": [
                {
                    "name": "inicio",
                    "label": "Início do período",
                    "type": "datetime",
                    "default": datetime(2024, 1, 1),
                },
                {
                    "name": "fim",
                    "label": "Fim do período",
                    "type": "datetime",
                    "default": datetime(2024, 2, 1),
                },
            ],
            "mutates": False,
        },
        "Ranking de residentes": {
            "path": "sql/consultas-analiticas/ranking_residentes.sql",
            "description": "Ranking dos residentes por número de atendimentos.",
            "params": [],
            "mutates": False,
        },
    },
    "CRUD": {
        "Atualizar dados do paciente": {
            "path": "sql/crud/atualizar_dados_paciente.sql",
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
        },
        "Inserir atendimento": {
            "path": "sql/crud/inserir_atendimento.sql",
            "description": (
                "Insere atendimento se paciente, residente e preceptor existirem. "
                "IDs do seed: pacientes 1–5, residentes 6–10, preceptores 11–15."
            ),
            "params": [
                {
                    "name": "data_hora",
                    "label": "Data/hora",
                    "type": "datetime",
                    "default": datetime.now(),
                },
                {
                    "name": "duracao_minutos",
                    "label": "Duração (minutos)",
                    "type": "int",
                    "default": 30,
                },
                {
                    "name": "id_paciente",
                    "label": "ID do paciente",
                    "type": "int",
                    "default": 1,
                },
                {
                    "name": "id_residente",
                    "label": "ID do residente",
                    "type": "int",
                    "default": 6,
                },
                {
                    "name": "id_preceptor",
                    "label": "ID do preceptor",
                    "type": "int",
                    "default": 11,
                },
            ],
            "mutates": True,
        },
        "Remover procedimento realizado": {
            "path": "sql/crud/remover_procedimento_realizado.sql",
            "description": "Remove procedimento realizado somente se faturado = FALSE.",
            "params": [
                {"name": "id_atendimento", "label": "ID do atendimento", "type": "int"},
                {
                    "name": "id_procedimento",
                    "label": "ID do procedimento",
                    "type": "int",
                },
            ],
            "mutates": True,
        },
    },
}


def load_sql(relative_path: str) -> str:
    return (ROOT / relative_path).read_text(encoding="utf-8")


def collect_params(param_defs: list[dict], key_prefix: str = "") -> list:
    values: list = []
    for param in param_defs:
        key = f"{key_prefix}{param['name']}"
        label = param["label"]
        param_type = param["type"]

        if param_type == "text":
            values.append(st.text_input(label, key=f"param_{key}"))
        elif param_type == "int":
            # Streamlit number_input devolve float; o SQL espera int.
            values.append(
                int(
                    st.number_input(
                        label,
                        min_value=1,
                        step=1,
                        value=int(param.get("default", 1)),
                        key=f"param_{key}",
                    )
                )
            )
        elif param_type == "select":
            values.append(
                st.selectbox(label, options=param["options"], key=f"param_{key}")
            )
        elif param_type == "datetime":
            default = param.get("default", datetime.now())
            chosen_date = st.date_input(
                f"{label} (data)",
                value=default.date() if isinstance(default, datetime) else default,
                key=f"param_{key}_date",
            )
            chosen_time = st.time_input(
                f"{label} (hora)",
                value=default.time() if isinstance(default, datetime) else time(0, 0),
                key=f"param_{key}_time",
            )
            values.append(datetime.combine(chosen_date, chosen_time))
        else:
            raise ValueError(f"Tipo de parâmetro não suportado: {param_type}")

    return values


def run_query(sql: str, params: list, mutates: bool) -> tuple[pd.DataFrame | None, int]:
    with connect(**DB_CONFIG) as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(sql, params or None)
            rowcount = cursor.rowcount

            if cursor.description is not None:
                rows = cursor.fetchall()
                df = pd.DataFrame(rows)
            else:
                df = None

            if mutates:
                conn.commit()

            return df, rowcount


def main() -> None:
    st.set_page_config(page_title="SGH — Consultas", layout="wide")
    st.title("Sistema de Gestão Hospitalar")
    st.caption("Execute consultas e operações CRUD no PostgreSQL.")

    with st.sidebar:
        st.header("Navegação")
        category = st.selectbox("Categoria", list(QUERIES.keys()))
        query_name = st.selectbox("Query", list(QUERIES[category].keys()))
        st.divider()
        st.caption(
            f"DB: {DB_CONFIG['user']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/"
            f"{DB_CONFIG['database']}"
        )

    query = QUERIES[category][query_name]
    st.subheader(query_name)
    st.write(query["description"])

    with st.expander("SQL", expanded=False):
        st.code(load_sql(query["path"]), language="sql")

    params: list = []
    if query["params"]:
        st.markdown("#### Parâmetros")
        params = collect_params(query["params"], key_prefix=f"{category}_{query_name}_")
    else:
        st.info("Esta query não possui parâmetros.")

    if st.button("Executar", type="primary"):
        try:
            sql = load_sql(query["path"])
            df, rowcount = run_query(sql, params, query["mutates"])

            if query["mutates"]:
                if rowcount and rowcount > 0:
                    st.success(f"Operação concluída. Linhas afetadas: {rowcount}.")
                else:
                    st.warning(
                        "Nenhuma linha afetada. Confira se os IDs existem "
                        "(paciente / residente / preceptor) e se as condições da query foram atendidas."
                    )

            if df is not None:
                if df.empty:
                    st.warning("A query não retornou linhas.")
                else:
                    st.dataframe(df, use_container_width=True)
                    st.caption(f"{len(df)} linha(s)")
            elif not query["mutates"]:
                st.info("A query não retornou um result set.")
        except Exception as exc:
            st.error(f"Erro ao executar a query: {exc}")


if __name__ == "__main__":
    main()
