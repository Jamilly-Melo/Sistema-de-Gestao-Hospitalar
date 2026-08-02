"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { apiFetch, ApiError } from "@/lib/api";

type Linha = {
  id_atendimento: number;
  data_hora: string;
  nome: string;
  quantidade: number;
  tempo_medio_minutos: number;
  tempo_real_minutos: number;
};

export default function AtendimentosPage() {
  const [linhas, setLinhas] = useState<Linha[]>([]);
  const [erro, setErro] = useState<string | null>(null);
  const [idsProcedimento, setIdsProcedimento] = useState<Record<number, string>>({});

  async function carregar() {
    setLinhas(await apiFetch<Linha[]>("/atendimentos"));
  }

  useEffect(() => {
    carregar();
  }, []);

  async function remover(indice: number, idAtendimento: number) {
    setErro(null);
    const valor = idsProcedimento[indice];
    const idProcedimento = Number(valor);
    if (!valor || Number.isNaN(idProcedimento)) {
      setErro("Informe o id do procedimento a remover.");
      return;
    }
    try {
      await apiFetch(`/atendimentos/${idAtendimento}/procedimentos/${idProcedimento}`, {
        method: "DELETE",
      });
      await carregar();
    } catch (excecao) {
      setErro(excecao instanceof ApiError ? excecao.message : "Erro inesperado.");
    }
  }

  return (
    <main>
      <h1>Atendimentos</h1>
      <p><Link href="/atendimentos/novo">Novo atendimento</Link></p>
      {erro && <p role="alert">{erro}</p>}
      <p>
        A listagem abaixo não traz o id do procedimento (a consulta de origem só devolve o
        nome do procedimento) — para remover, digite o id do procedimento ao lado do botão.
      </p>
      <table>
        <thead>
          <tr>
            <th>Atendimento</th>
            <th>Data</th>
            <th>Procedimento</th>
            <th>Qtd</th>
            <th>Id do procedimento</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          {linhas.map((linha, indice) => (
            <tr key={indice}>
              <td>{linha.id_atendimento}</td>
              <td>{linha.data_hora}</td>
              <td>{linha.nome}</td>
              <td>{linha.quantidade}</td>
              <td>
                <input
                  type="number"
                  style={{ width: "5rem" }}
                  value={idsProcedimento[indice] ?? ""}
                  onChange={(evento) =>
                    setIdsProcedimento((atual) => ({ ...atual, [indice]: evento.target.value }))
                  }
                />
              </td>
              <td>
                <button onClick={() => remover(indice, linha.id_atendimento)}>
                  Remover
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </main>
  );
}
