"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { apiFetch, ApiError } from "@/lib/api";
import { PageContainer } from "@/components/PageContainer";
import { PageHeader } from "@/components/PageHeader";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Input } from "@/components/ui/input";
import { Button, buttonVariants } from "@/components/ui/button";
import { Alert, AlertDescription } from "@/components/ui/alert";

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
    <PageContainer>
      <PageHeader
        titulo="Atendimentos"
        descricao="Procedimentos registrados por atendimento."
        acao={
          <Link href="/atendimentos/novo" className={buttonVariants()}>
            Novo atendimento
          </Link>
        }
      />
      {erro && (
        <Alert variant="destructive" className="mb-4">
          <AlertDescription>{erro}</AlertDescription>
        </Alert>
      )}
      <p className="mb-4 text-sm text-muted-foreground">
        A listagem abaixo não traz o id do procedimento (a consulta de origem só
        devolve o nome do procedimento) — para remover, digite o id do procedimento ao
        lado do botão.
      </p>
      <Card>
        <CardHeader>
          <CardTitle>Lista de atendimentos</CardTitle>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Atendimento</TableHead>
                <TableHead>Data</TableHead>
                <TableHead>Procedimento</TableHead>
                <TableHead>Qtd</TableHead>
                <TableHead>Id do procedimento</TableHead>
                <TableHead></TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {linhas.map((linha, indice) => (
                <TableRow key={indice}>
                  <TableCell>{linha.id_atendimento}</TableCell>
                  <TableCell>{linha.data_hora}</TableCell>
                  <TableCell>{linha.nome}</TableCell>
                  <TableCell>{linha.quantidade}</TableCell>
                  <TableCell>
                    <Input
                      type="number"
                      className="w-20"
                      value={idsProcedimento[indice] ?? ""}
                      onChange={(evento) =>
                        setIdsProcedimento((atual) => ({
                          ...atual,
                          [indice]: evento.target.value,
                        }))
                      }
                    />
                  </TableCell>
                  <TableCell>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => remover(indice, linha.id_atendimento)}
                    >
                      Remover
                    </Button>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </PageContainer>
  );
}
