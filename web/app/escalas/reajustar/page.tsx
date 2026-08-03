"use client";

import { useCallback, useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { Autocomplete } from "@/components/Autocomplete";
import { apiFetch, ApiError } from "@/lib/api";
import { PageContainer } from "@/components/PageContainer";
import { PageHeader } from "@/components/PageHeader";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Label } from "@/components/ui/label";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Alert, AlertDescription } from "@/components/ui/alert";

type Opcao = { id: number; nome: string };
type Turno = "MANHA" | "TARDE" | "NOITE";
type Plantao = {
  id_escala: number;
  data_plantao: string;
  turno: Turno;
  unidade: string;
};

const TURNOS: Turno[] = ["MANHA", "TARDE", "NOITE"];

// O valor do select de origem carrega data e turno juntos, porque é isso que a
// API precisa — o id_escala não entra no corpo do POST.
function chaveDoPlantao(plantao: Plantao): string {
  return `${plantao.data_plantao}|${plantao.turno}`;
}

function rotuloDoPlantao(plantao: Plantao): string {
  return `${plantao.data_plantao} — ${plantao.turno} — ${plantao.unidade}`;
}

export default function ReajustarEscalaPage() {
  const router = useRouter();
  const [residentes, setResidentes] = useState<Opcao[]>([]);
  const [idResidente, setIdResidente] = useState<number | null>(null);
  const [plantoes, setPlantoes] = useState<Plantao[]>([]);
  const [origem, setOrigem] = useState<string | null>(null);
  const [dataDestino, setDataDestino] = useState("");
  const [turnoDestino, setTurnoDestino] = useState<Turno>("MANHA");
  const [erro, setErro] = useState<string | null>(null);

  useEffect(() => {
    apiFetch<Opcao[]>("/profissionais/residentes").then(setResidentes);
  }, []);

  const carregarPlantoes = useCallback(async () => {
    if (idResidente === null) {
      setPlantoes([]);
      return;
    }
    try {
      setPlantoes(await apiFetch<Plantao[]>(`/escalas/residente/${idResidente}`));
    } catch (excecao) {
      setErro(excecao instanceof ApiError ? excecao.message : "Erro inesperado.");
      setPlantoes([]);
    }
  }, [idResidente]);

  // Trocar de residente invalida o plantão escolhido: ele pertencia ao anterior.
  useEffect(() => {
    setOrigem(null);
    carregarPlantoes();
  }, [carregarPlantoes]);

  async function enviar(evento: React.FormEvent) {
    evento.preventDefault();
    setErro(null);

    if (idResidente === null || origem === null || dataDestino === "") {
      setErro("Escolha o residente, o plantão de origem e a data de destino.");
      return;
    }

    const [dataOrigem, turnoOrigem] = origem.split("|");

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
      router.push(`/escalas?ok=${encodeURIComponent("Escala reajustada com sucesso.")}`);
    } catch (excecao) {
      setErro(excecao instanceof ApiError ? excecao.message : "Erro inesperado.");
    }
  }

  return (
    <PageContainer>
      <PageHeader
        titulo="Reajustar escala"
        descricao="Mova um plantão de residente entre datas e turnos."
      />
      <Card className="max-w-3xl">
        <CardHeader>
          <CardTitle>Mover plantão</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={enviar} className="grid grid-cols-2 gap-5">
            <div className="col-span-2 flex flex-col gap-2">
              <Label>Residente</Label>
              <Autocomplete
                options={residentes}
                value={idResidente}
                onChange={setIdResidente}
              />
            </div>

            <div className="col-span-2 flex flex-col gap-2">
              <Label htmlFor="plantao-origem">Plantão de origem</Label>
              {idResidente === null ? (
                <p className="text-sm text-muted-foreground">
                  Escolha um residente para ver os plantões dele.
                </p>
              ) : plantoes.length === 0 ? (
                <p className="text-sm text-muted-foreground">
                  Este residente não tem nenhum plantão escalado.
                </p>
              ) : (
                <Select
                  items={plantoes.map((p) => ({
                    value: chaveDoPlantao(p),
                    label: rotuloDoPlantao(p),
                  }))}
                  value={origem ?? undefined}
                  onValueChange={(v) => setOrigem(v)}
                >
                  <SelectTrigger id="plantao-origem" className="w-full">
                    <SelectValue placeholder="Selecione o plantão" />
                  </SelectTrigger>
                  <SelectContent>
                    {plantoes.map((p) => (
                      <SelectItem key={p.id_escala} value={chaveDoPlantao(p)}>
                        {rotuloDoPlantao(p)}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              )}
            </div>

            <div className="flex flex-col gap-2">
              <Label htmlFor="data-destino">Data de destino</Label>
              <Input
                id="data-destino"
                type="date"
                value={dataDestino}
                onChange={(e) => setDataDestino(e.target.value)}
              />
            </div>

            <div className="flex flex-col gap-2">
              <Label htmlFor="turno-destino">Turno de destino</Label>
              <Select
                items={TURNOS.map((t) => ({ value: t, label: t }))}
                value={turnoDestino}
                onValueChange={(v) => setTurnoDestino(v as Turno)}
              >
                <SelectTrigger id="turno-destino" className="w-full">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {TURNOS.map((t) => (
                    <SelectItem key={t} value={t}>
                      {t}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div className="col-span-2">
              <Button type="submit">Reajustar</Button>
            </div>
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
