"use client";

import { useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { apiFetch, ApiError } from "@/lib/api";

export default function EditarPacientePage() {
  const params = useParams<{ id: string }>();
  const router = useRouter();
  const [campo, setCampo] = useState<"endereco" | "num_convenio">("endereco");
  const [valor, setValor] = useState("");
  const [erro, setErro] = useState<string | null>(null);

  async function enviar(evento: React.FormEvent) {
    evento.preventDefault();
    setErro(null);
    try {
      await apiFetch(`/pacientes/${params.id}`, {
        method: "PATCH",
        body: JSON.stringify({ campo, valor }),
      });
      router.push("/pacientes");
    } catch (excecao) {
      setErro(excecao instanceof ApiError ? excecao.message : "Erro inesperado.");
    }
  }

  return (
    <main>
      <h1>Editar paciente #{params.id}</h1>
      <form onSubmit={enviar}>
        <label>
          Campo:
          <select value={campo} onChange={(e) => setCampo(e.target.value as typeof campo)}>
            <option value="endereco">Endereço</option>
            <option value="num_convenio">Número do convênio</option>
          </select>
        </label>
        <label>
          Novo valor:
          <input value={valor} onChange={(e) => setValor(e.target.value)} />
        </label>
        <button type="submit">Salvar</button>
      </form>
      {erro && <p role="alert">{erro}</p>}
    </main>
  );
}
