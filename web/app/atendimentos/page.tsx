import Link from "next/link";
import { apiFetch } from "@/lib/api";
import { PageContainer } from "@/components/PageContainer";
import { PageHeader } from "@/components/PageHeader";
import { buttonVariants } from "@/components/ui/button";
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

type Linha = {
  id_atendimento: number;
  data_hora: string;
  nome: string;
  quantidade: number;
  tempo_medio_minutos: number;
  tempo_real_minutos: number;
};

type Atendimento = {
  id_atendimento: number;
  data_hora: string;
  procedimentos: number;
};

// /atendimentos devolve uma linha por procedimento; a tela mostra um
// atendimento por linha, então agrupamos pelo id.
function agrupar(linhas: Linha[]): Atendimento[] {
  const mapa = new Map<number, Atendimento>();
  for (const linha of linhas) {
    const atual = mapa.get(linha.id_atendimento);
    if (atual) {
      atual.procedimentos += 1;
    } else {
      mapa.set(linha.id_atendimento, {
        id_atendimento: linha.id_atendimento,
        data_hora: linha.data_hora,
        procedimentos: 1,
      });
    }
  }
  return [...mapa.values()].sort((a, b) => a.id_atendimento - b.id_atendimento);
}

export default async function AtendimentosPage({
  searchParams,
}: {
  searchParams: Promise<{ [chave: string]: string | string[] | undefined }>;
}) {
  const ok = (await searchParams).ok;
  const mensagem = typeof ok === "string" ? ok : null;
  const atendimentos = agrupar(await apiFetch<Linha[]>("/atendimentos"));

  return (
    <PageContainer>
      <PageHeader
        titulo="Atendimentos"
        descricao="Atendimentos registrados e seus procedimentos."
        acao={
          <Link href="/atendimentos/novo" className={buttonVariants()}>
            Novo atendimento
          </Link>
        }
      />
      {mensagem && (
        <Alert variant="success" className="mb-6">
          <AlertDescription>{mensagem}</AlertDescription>
        </Alert>
      )}
      <Card>
        <CardHeader>
          <CardTitle>Lista de atendimentos</CardTitle>
        </CardHeader>
        <CardContent>
          {atendimentos.length === 0 ? (
            <p className="py-8 text-center text-sm text-muted-foreground">
              Nenhum atendimento registrado.
            </p>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Atendimento</TableHead>
                  <TableHead>Data</TableHead>
                  <TableHead>Procedimentos</TableHead>
                  <TableHead></TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {atendimentos.map((atendimento) => (
                  <TableRow key={atendimento.id_atendimento}>
                    <TableCell>{atendimento.id_atendimento}</TableCell>
                    <TableCell>{atendimento.data_hora}</TableCell>
                    <TableCell>{atendimento.procedimentos}</TableCell>
                    <TableCell className="text-right">
                      <Link
                        href={`/atendimentos/${atendimento.id_atendimento}`}
                        className={buttonVariants({ variant: "outline", size: "sm" })}
                      >
                        Gerenciar procedimentos
                      </Link>
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
