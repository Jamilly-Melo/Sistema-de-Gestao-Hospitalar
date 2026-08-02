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
  const turnoItems = turnos.map((t) => ({ value: t, label: t }));

  return (
    <PageContainer>
      <PageHeader titulo="Reajustar escala" descricao="Mova um plantão de residente entre datas e turnos." />
      <Card className="max-w-md">
        <CardHeader>
          <CardTitle>Mover plantão</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={enviar} className="flex flex-col gap-4">
            <div className="flex flex-col gap-2">
              <Label>Residente</Label>
              <Autocomplete options={residentes} value={idResidente} onChange={setIdResidente} />
            </div>
            <div className="flex flex-col gap-2">
              <Label htmlFor="data-origem">Data de origem</Label>
              <Input
                id="data-origem"
                type="date"
                value={dataOrigem}
                onChange={(e) => setDataOrigem(e.target.value)}
              />
            </div>
            <div className="flex flex-col gap-2">
              <Label htmlFor="turno-origem">Turno de origem</Label>
              <Select
                items={turnoItems}
                value={turnoOrigem}
                onValueChange={(v) => setTurnoOrigem(v as Turno)}
              >
                <SelectTrigger id="turno-origem" className="w-full">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {turnos.map((t) => (
                    <SelectItem key={t} value={t}>
                      {t}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
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
                items={turnoItems}
                value={turnoDestino}
                onValueChange={(v) => setTurnoDestino(v as Turno)}
              >
                <SelectTrigger id="turno-destino" className="w-full">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {turnos.map((t) => (
                    <SelectItem key={t} value={t}>
                      {t}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <Button type="submit" className="w-fit">
              Reajustar
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
