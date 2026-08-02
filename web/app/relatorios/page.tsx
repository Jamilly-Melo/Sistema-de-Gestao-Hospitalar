"use client";

import { useEffect, useState } from "react";
import { apiFetch, ApiError } from "@/lib/api";

type Relatorio = { nome: string; description: string; params: { name: string; label: string; type: string }[] };

export default function RelatoriosPage() {
  const [relatorios, setRelatorios] = useState<Relatorio[]>([]);
  const [selecionado, setSelecionado] = useState<string | null>(null);
  const [parametros, setParametros] = useState<Record<string, string>>({});
  const [resultado, setResultado] = useState<Record<string, unknown>[] | null>(null);
  const [erro, setErro] = useState<string | null>(null);

  useEffect(() => {
    apiFetch<Relatorio[]>("/relatorios").then(setRelatorios);
  }, []);

  const atual = relatorios.find((r) => r.nome === selecionado);

  async function executar() {
    if (!selecionado) return;
    setErro(null);
    setResultado(null);
    try {
      const dados = await apiFetch<Record<string, unknown>[]>(
        `/relatorios/${encodeURIComponent(selecionado)}`,
        { method: "POST", body: JSON.stringify(parametros) }
      );
      setResultado(dados);
    } catch (excecao) {
      setErro(excecao instanceof ApiError ? excecao.message : "Erro inesperado.");
    }
  }

  return (
    <main>
      <h1>Relatórios</h1>
      <select value={selecionado ?? ""} onChange={(e) => { setSelecionado(e.target.value || null); setParametros({}); setResultado(null); }}>
        <option value="">Selecione um relatório</option>
        {relatorios.map((r) => <option key={r.nome} value={r.nome}>{r.nome}</option>)}
      </select>

      {atual && (
        <>
          <p>{atual.description}</p>
          {atual.params.map((param) => (
            <label key={param.name}>
              {param.label}
              <input
                value={parametros[param.name] ?? ""}
                onChange={(e) => setParametros({ ...parametros, [param.name]: e.target.value })}
              />
            </label>
          ))}
          <button onClick={executar}>Executar</button>
        </>
      )}

      {erro && <p role="alert">{erro}</p>}

      {resultado && (
        <pre>{JSON.stringify(resultado, null, 2)}</pre>
      )}
    </main>
  );
}
