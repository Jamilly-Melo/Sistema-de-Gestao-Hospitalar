"use client";

import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import { useParams } from "next/navigation";
import { apiFetch, ApiError } from "@/lib/api";
import { PageContainer } from "@/components/PageContainer";
import { PageHeader } from "@/components/PageHeader";
import { Button, buttonVariants } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Alert, AlertDescription } from "@/components/ui/alert";

type Procedimento = {
  id_procedimento: number;
  nome: string;
  quantidade: number;
  tempo_real_minutos: number;
  faturado: boolean;
};

export default function DetalheAtendimentoPage() {
  const params = useParams<{ id: string }>();
  const [procedimentos, setProcedimentos] = useState<Procedimento[]>([]);
  const [erro, setErro] = useState<string | null>(null);

  const carregar = useCallback(async () => {
    setProcedimentos(
      await apiFetch<Procedimento[]>(`/atendimentos/${params.id}/procedimentos`)
    );
  }, [params.id]);

  useEffect(() => {
    carregar();
  }, [carregar]);

  async function remover(idProcedimento: number) {
    setErro(null);
    try {
      await apiFetch(
        `/atendimentos/${params.id}/procedimentos/${idProcedimento}`,
        { method: "DELETE" }
      );
      await carregar();
    } catch (excecao) {
      setErro(excecao instanceof ApiError ? excecao.message : "Erro inesperado.");
    }
  }

  return (
    <PageContainer>
      <PageHeader
        titulo={<>Atendimento #{params.id}</>}
        descricao="Procedimentos realizados neste atendimento."
        acao={
          <Link
            href="/atendimentos"
            className={buttonVariants({ variant: "outline" })}
          >
            Voltar
          </Link>
        }
      />

      {erro && (
        <Alert variant="destructive" className="mb-6">
          <AlertDescription>{erro}</AlertDescription>
        </Alert>
      )}

      <Card>
        <CardHeader>
          <CardTitle>Procedimentos</CardTitle>
        </CardHeader>
        <CardContent>
          {procedimentos.length === 0 ? (
            <p className="py-8 text-center text-sm text-muted-foreground">
              Nenhum procedimento neste atendimento.
            </p>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Procedimento</TableHead>
                  <TableHead>Qtd</TableHead>
                  <TableHead>Tempo real (min)</TableHead>
                  <TableHead>Situação</TableHead>
                  <TableHead></TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {procedimentos.map((procedimento) => (
                  <TableRow key={procedimento.id_procedimento}>
                    <TableCell>{procedimento.nome}</TableCell>
                    <TableCell>{procedimento.quantidade}</TableCell>
                    <TableCell>{procedimento.tempo_real_minutos}</TableCell>
                    <TableCell>
                      {procedimento.faturado ? (
                        <span className="rounded-md bg-muted px-2 py-1 text-xs font-medium">
                          Faturado
                        </span>
                      ) : (
                        <span className="text-xs text-muted-foreground">
                          Não faturado
                        </span>
                      )}
                    </TableCell>
                    <TableCell className="text-right">
                      <Button
                        variant="outline"
                        size="sm"
                        disabled={procedimento.faturado}
                        title={
                          procedimento.faturado
                            ? "Procedimentos faturados não podem ser removidos."
                            : undefined
                        }
                        onClick={() => remover(procedimento.id_procedimento)}
                      >
                        Remover
                      </Button>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>
    </PageContainer>
  );
}
