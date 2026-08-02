"use client";

import { useState } from "react";
import { useParams, useRouter } from "next/navigation";
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

const CAMPOS = [
  { value: "endereco", label: "Endereço" },
  { value: "num_convenio", label: "Número do convênio" },
] as const;

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
    <PageContainer>
      <PageHeader
        titulo={<>Editar paciente #{params.id}</>}
        descricao="Atualize o endereço ou o número do convênio do paciente."
      />
      <Card className="max-w-md">
        <CardHeader>
          <CardTitle>Atualizar cadastro</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={enviar} className="flex flex-col gap-4">
            <div className="flex flex-col gap-2">
              <Label htmlFor="campo">Campo</Label>
              <Select
                items={CAMPOS}
                value={campo}
                onValueChange={(v) => setCampo(v as typeof campo)}
              >
                <SelectTrigger id="campo" className="w-full">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {CAMPOS.map((c) => (
                    <SelectItem key={c.value} value={c.value}>
                      {c.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div className="flex flex-col gap-2">
              <Label htmlFor="valor">Novo valor</Label>
              <Input id="valor" value={valor} onChange={(e) => setValor(e.target.value)} />
            </div>
            <Button type="submit" className="w-fit">
              Salvar
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
