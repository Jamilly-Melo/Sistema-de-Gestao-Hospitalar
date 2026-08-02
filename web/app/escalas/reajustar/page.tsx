"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { Autocomplete } from "@/components/Autocomplete";
import { apiFetch, ApiError } from "@/lib/api";

type Opcao = { id: number; nome: string };
type Turno = "MANHA" | "TARDE" | "NOITE";

export default function ReajustarEscalaPage() {
  const router = useRouter();
  const [residentes, setResidentes] = useState<Opcao[]>([]);
  const [idResidente, setIdResidente] = useState<number | null>(null);
  const [dataOrigem, setDataOrigem] = useState("");
  const [turnoOrigem, setTurnoOrigem] = useState<Turno>("MANHA");
  const [dataDestino, setDataDestino] = useState("");
  const [turnoDestino, setTurnoDestino] = useState<Turno>("MANHA");
  const [erro, setErro] = useState<string | null>(null);

  useEffect(() => {
    apiFetch<Opcao[]>("/profissionais/residentes").then(setResidentes);
  }, []);

  async function enviar(evento: React.FormEvent) {
    evento.preventDefault();
    setErro(null);
    try {
      await apiFetch("/escalas/reajustar", {
        method: "POST",
        body: JSON.stringify({
          id_residente: idResidente,
          data_origem: dataOrigem,
          turno_origem: turnoOrigem,
          data_destino: dataDestino,
          turno_destino: turnoDestino,
        }),
      });
      router.push("/escalas");
    } catch (excecao) {
      setErro(excecao instanceof ApiError ? excecao.message : "Erro inesperado.");
    }
  }

  const turnos: Turno[] = ["MANHA", "TARDE", "NOITE"];

  return (
    <main>
      <h1>Reajustar escala</h1>
      <form onSubmit={enviar}>
        <label>Residente <Autocomplete options={residentes} value={idResidente} onChange={setIdResidente} /></label>
        <label>Data de origem <input type="date" value={dataOrigem} onChange={(e) => setDataOrigem(e.target.value)} /></label>
        <label>
          Turno de origem
          <select value={turnoOrigem} onChange={(e) => setTurnoOrigem(e.target.value as Turno)}>
            {turnos.map((t) => <option key={t} value={t}>{t}</option>)}
          </select>
        </label>
        <label>Data de destino <input type="date" value={dataDestino} onChange={(e) => setDataDestino(e.target.value)} /></label>
        <label>
          Turno de destino
          <select value={turnoDestino} onChange={(e) => setTurnoDestino(e.target.value as Turno)}>
            {turnos.map((t) => <option key={t} value={t}>{t}</option>)}
          </select>
        </label>
        <button type="submit">Reajustar</button>
      </form>
      {erro && <p role="alert">{erro}</p>}
    </main>
  );
}
