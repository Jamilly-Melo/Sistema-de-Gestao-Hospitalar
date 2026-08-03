"use client";

import { useEffect, useState } from "react";
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
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";

type Relatorio = {
  nome: string;
  description: string;
  params: { name: string; label: string; type: string }[];
};

// O resultado de um relatório é uma lista de objetos com formato desconhecido em
// tempo de compilação — o catálogo é dinâmico. Esta função é a única que decide
// como cada valor vira texto.
function celula(valor: unknown): string {
  if (valor === null || valor === undefined) return "—";
  // "Último atendimento por paciente" traz `procedimentos` como array.
  if (Array.isArray(valor)) return valor.length > 0 ? valor.join(", ") : "—";
  if (typeof valor === "object") return JSON.stringify(valor);
  return String(valor);
}

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
    <PageContainer>
      <PageHeader titulo="Relatórios" descricao="Consultas analíticas sobre atendimentos, escalas e pacientes." />
      <Card className="max-w-5xl">
        <CardHeader>
          <CardTitle>Executar relatório</CardTitle>
        </CardHeader>
        <CardContent className="flex flex-col gap-4">
          <div className="flex flex-col gap-2">
            <Label>Relatório</Label>
            <Select
              items={relatorios.map((r) => ({ value: r.nome, label: r.nome }))}
              value={selecionado ?? undefined}
              onValueChange={(v) => {
                setSelecionado(v);
                setParametros({});
                setResultado(null);
              }}
            >
              <SelectTrigger className="w-full">
                <SelectValue placeholder="Selecione um relatório" />
              </SelectTrigger>
              <SelectContent>
                {relatorios.map((r) => (
                  <SelectItem key={r.nome} value={r.nome}>
                    {r.nome}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          {atual && (
            <>
              <p className="text-sm text-muted-foreground">{atual.description}</p>
              {atual.params.map((param) => (
                <div key={param.name} className="flex flex-col gap-2">
                  <Label htmlFor={param.name}>{param.label}</Label>
                  <Input
                    id={param.name}
                    value={parametros[param.name] ?? ""}
                    onChange={(e) =>
                      setParametros({ ...parametros, [param.name]: e.target.value })
                    }
                  />
                </div>
              ))}
              <Button onClick={executar} className="w-fit">
                Executar
              </Button>
            </>
          )}

          {erro && (
            <Alert variant="destructive">
              <AlertDescription>{erro}</AlertDescription>
            </Alert>
          )}

          {resultado &&
            (resultado.length === 0 ? (
              <p className="py-8 text-center text-sm text-muted-foreground">
                A consulta não retornou nenhuma linha.
              </p>
            ) : (
              <Table>
                <TableHeader>
                  <TableRow>
                    {Object.keys(resultado[0]).map((coluna) => (
                      <TableHead key={coluna}>{coluna}</TableHead>
                    ))}
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {resultado.map((linha, indice) => (
                    <TableRow key={indice}>
                      {Object.keys(resultado[0]).map((coluna) => (
                        <TableCell key={coluna}>{celula(linha[coluna])}</TableCell>
                      ))}
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            ))}
        </CardContent>
      </Card>
    </PageContainer>
  );
}
