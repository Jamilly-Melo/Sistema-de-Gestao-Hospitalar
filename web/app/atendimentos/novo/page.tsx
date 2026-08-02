"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { Autocomplete } from "@/components/Autocomplete";
import { apiFetch, ApiError } from "@/lib/api";

type Opcao = { id: number; nome: string };

export default function NovoAtendimentoPage() {
  const router = useRouter();
  const [pacientes, setPacientes] = useState<Opcao[]>([]);
  const [residentes, setResidentes] = useState<Opcao[]>([]);
  const [preceptores, setPreceptores] = useState<Opcao[]>([]);
  const [unidades, setUnidades] = useState<Opcao[]>([]);
  const [procedimentos, setProcedimentos] = useState<Opcao[]>([]);

  const [idPaciente, setIdPaciente] = useState<number | null>(null);
  const [idResidente, setIdResidente] = useState<number | null>(null);
  const [idPreceptor, setIdPreceptor] = useState<number | null>(null);
  const [idUnidade, setIdUnidade] = useState<number | null>(null);
  const [idProcedimento, setIdProcedimento] = useState<number | null>(null);
  const [dataHora, setDataHora] = useState("");
  const [duracaoMinutos, setDuracaoMinutos] = useState(30);
  const [erro, setErro] = useState<string | null>(null);

  useEffect(() => {
    apiFetch<{ id_pessoa: number; nome: string }[]>("/lookups/pacientes").then((dados) =>
      setPacientes(dados.map((d) => ({ id: d.id_pessoa, nome: d.nome })))
    );
    apiFetch<{ id: number; nome: string }[]>("/profissionais/residentes").then(setResidentes);
    apiFetch<{ id_profissional: number; nome: string }[]>("/profissionais/preceptores").then(
      (dados) => setPreceptores(dados.map((d) => ({ id: d.id_profissional, nome: d.nome })))
    );
    apiFetch<{ id_unidade: number; nome: string }[]>("/lookups/unidades").then(
      (dados) => setUnidades(dados.map((d) => ({ id: d.id_unidade, nome: d.nome })))
    );
    apiFetch<{ id_procedimento: number; nome: string }[]>("/lookups/procedimentos").then(
      (dados) => setProcedimentos(dados.map((d) => ({ id: d.id_procedimento, nome: d.nome })))
    );
  }, []);

  async function enviar(evento: React.FormEvent) {
    evento.preventDefault();
    setErro(null);
    try {
      await apiFetch("/atendimentos", {
        method: "POST",
        body: JSON.stringify({
          data_hora: dataHora,
          duracao_minutos: duracaoMinutos,
          id_paciente: idPaciente,
          id_residente: idResidente,
          id_preceptor: idPreceptor,
          id_unidade: idUnidade,
          procedimentos: [
            {
              id_procedimento: idProcedimento,
              quantidade: 1,
              tempo_real_minutos: duracaoMinutos,
              data_hora_inicio: dataHora,
            },
          ],
        }),
      });
      router.push("/atendimentos");
    } catch (excecao) {
      setErro(excecao instanceof ApiError ? excecao.message : "Erro inesperado.");
    }
  }

  return (
    <main>
      <h1>Novo atendimento</h1>
      <form onSubmit={enviar}>
        <label>Paciente <Autocomplete options={pacientes} value={idPaciente} onChange={setIdPaciente} /></label>
        <label>Residente <Autocomplete options={residentes} value={idResidente} onChange={setIdResidente} /></label>
        <label>Preceptor <Autocomplete options={preceptores} value={idPreceptor} onChange={setIdPreceptor} /></label>
        <label>Unidade <Autocomplete options={unidades} value={idUnidade} onChange={setIdUnidade} /></label>
        <label>Procedimento <Autocomplete options={procedimentos} value={idProcedimento} onChange={setIdProcedimento} /></label>
        <label>Data/hora <input type="datetime-local" value={dataHora} onChange={(e) => setDataHora(e.target.value)} /></label>
        <label>Duração (min) <input type="number" value={duracaoMinutos} onChange={(e) => setDuracaoMinutos(Number(e.target.value))} /></label>
        <button type="submit">Registrar</button>
      </form>
      {erro && <p role="alert">{erro}</p>}
    </main>
  );
}
