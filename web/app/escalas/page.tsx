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

type Linha = { unidade: string | null; residente: string; total_plantoes: number };

export default async function EscalasPage({
  searchParams,
}: {
  searchParams: Promise<{ [chave: string]: string | string[] | undefined }>;
}) {
  const ok = (await searchParams).ok;
  const mensagem = typeof ok === "string" ? ok : null;
  const linhas = await apiFetch<Linha[]>("/escalas");

  return (
    <PageContainer>
      <PageHeader
        titulo="Plantões do mês corrente"
        descricao="Total de plantões por residente em cada unidade."
        acao={
          <Link href="/escalas/reajustar" className={buttonVariants()}>
            Reajustar escala
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
          <CardTitle>Plantões</CardTitle>
        </CardHeader>
        <CardContent>
          {linhas.length === 0 ? (
            <p className="py-8 text-center text-sm text-muted-foreground">
              Nenhum plantão no mês corrente.
            </p>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Unidade</TableHead>
                  <TableHead>Residente</TableHead>
                  <TableHead>Total de plantões</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {linhas.map((linha, indice) => (
                  <TableRow key={indice}>
                    <TableCell>{linha.unidade ?? "—"}</TableCell>
                    <TableCell>{linha.residente}</TableCell>
                    <TableCell>{linha.total_plantoes}</TableCell>
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
