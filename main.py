"""Interface Streamlit do SGH.

Este arquivo é o único que conhece Streamlit e pandas. Toda a lógica de acesso a
dados vive em sgh/, que não importa nenhum dos dois — é o que permite servir a
mesma camada por HTTP mais adiante.
"""

from __future__ import annotations

from datetime import datetime, time

import pandas as pd
import streamlit as st

from sgh.catalog import CATALOGO
from sgh.config import DB_HOST, DB_NAME, DB_PORT, DB_USER


def collect_params(param_defs: list[dict], key_prefix: str = "") -> list:
    values: list = []
    for param in param_defs:
        key = f"{key_prefix}{param['name']}"
        label = param["label"]
        param_type = param["type"]

        if param_type == "text":
            values.append(
                st.text_input(
                    label, value=param.get("default", ""), key=f"param_{key}"
                )
            )
        elif param_type == "int":
            # Streamlit number_input devolve float; as funções esperam int.
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
            options = param["options"]
            default = param.get("default")
            index = options.index(default) if default in options else 0
            values.append(
                st.selectbox(
                    label, options=options, index=index, key=f"param_{key}"
                )
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


def main() -> None:
    st.set_page_config(page_title="SGH — Consultas", layout="wide")
    st.title("Sistema de Gestão Hospitalar")
    st.caption("Execute consultas e operações CRUD no PostgreSQL via SQLAlchemy.")

    with st.sidebar:
        st.header("Navegação")
        category = st.selectbox("Categoria", list(CATALOGO.keys()))
        query_name = st.selectbox("Query", list(CATALOGO[category].keys()))
        st.divider()
        st.caption(f"DB: {DB_USER}@{DB_HOST}:{DB_PORT}/{DB_NAME}")

    query = CATALOGO[category][query_name]
    st.subheader(query_name)
    st.write(query["description"])

    params: list = []
    if query["params"]:
        st.markdown("#### Parâmetros")
        params = collect_params(
            query["params"], key_prefix=f"{category}_{query_name}_"
        )
    else:
        st.info("Esta query não possui parâmetros.")

    if st.button("Executar", type="primary"):
        try:
            linhas = query["fn"](*params)

            if query["mutates"]:
                if linhas:
                    st.success(f"Operação concluída. Linhas afetadas: {len(linhas)}.")
                else:
                    st.warning(
                        "Nenhuma linha afetada. Confira se os IDs existem "
                        "(paciente / residente / preceptor / unidade) e se as "
                        "condições da operação foram atendidas."
                    )

            if linhas:
                st.dataframe(pd.DataFrame(linhas), use_container_width=True)
                st.caption(f"{len(linhas)} linha(s)")
            elif not query["mutates"]:
                st.warning("A query não retornou linhas.")
        except Exception as exc:
            st.error(f"Erro ao executar a query: {exc}")


if __name__ == "__main__":
    main()
