"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { Autocomplete } from "@/components/Autocomplete";
import { apiFetch, ApiError } from "@/lib/api";
import { PageContainer } from "@/components/PageContainer";
import { PageHeader } from "@/components/PageHeader";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Label } from "@/components/ui/label";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Alert, AlertDescription } from "@/components/ui/alert";

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
    apiFetch<{ id_unidade: number; nome: string }[]>("/lookups/unidades").then((dados) =>
      setUnidades(dados.map((d) => ({ id: d.id_unidade, nome: d.nome })))
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
    <PageContainer>
      <PageHeader titulo="Novo atendimento" descricao="Registre um atendimento com paciente, equipe e procedimento." />
      <Card className="max-w-md">
        <CardHeader>
          <CardTitle>Registrar atendimento</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={enviar} className="flex flex-col gap-4">
            <div className="flex flex-col gap-2">
              <Label>Paciente</Label>
              <Autocomplete options={pacientes} value={idPaciente} onChange={setIdPaciente} />
            </div>
            <div className="flex flex-col gap-2">
              <Label>Residente</Label>
              <Autocomplete options={residentes} value={idResidente} onChange={setIdResidente} />
            </div>
            <div className="flex flex-col gap-2">
              <Label>Preceptor</Label>
              <Autocomplete options={preceptores} value={idPreceptor} onChange={setIdPreceptor} />
            </div>
            <div className="flex flex-col gap-2">
              <Label>Unidade</Label>
              <Autocomplete options={unidades} value={idUnidade} onChange={setIdUnidade} />
            </div>
            <div className="flex flex-col gap-2">
              <Label>Procedimento</Label>
              <Autocomplete
                options={procedimentos}
                value={idProcedimento}
                onChange={setIdProcedimento}
              />
            </div>
            <div className="flex flex-col gap-2">
              <Label htmlFor="data-hora">Data/hora</Label>
              <Input
                id="data-hora"
                type="datetime-local"
                value={dataHora}
                onChange={(e) => setDataHora(e.target.value)}
              />
            </div>
            <div className="flex flex-col gap-2">
              <Label htmlFor="duracao">Duração (min)</Label>
              <Input
                id="duracao"
                type="number"
                value={duracaoMinutos}
                onChange={(e) => setDuracaoMinutos(Number(e.target.value))}
              />
            </div>
            <Button type="submit" className="w-fit">
              Registrar
            </Button>
          </form>
          {erro && (
            <Alert variant="destructive" className="mt-4">
              <AlertDescription>{erro}</AlertDescription>
            </Alert>
          )}
        </CardContent>
      </Card>
    </PageContainer>
  );
}
