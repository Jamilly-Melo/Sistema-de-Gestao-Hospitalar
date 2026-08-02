// web/app/escalas/page.tsx
import Link from "next/link";
import { apiFetch } from "@/lib/api";
import { PageContainer } from "@/components/PageContainer";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";

type Linha = { unidade: string | null; residente: string; total_plantoes: number };

export default async function EscalasPage() {
  const linhas = await apiFetch<Linha[]>("/escalas");

  return (
    <PageContainer>
      <h1 className="mb-6 text-2xl font-semibold">Plantões do mês corrente</h1>
      <p className="mb-4">
        <Link className="underline" href="/escalas/reajustar">
          Reajustar escala
        </Link>
      </p>
      <Card>
        <CardHeader>
          <CardTitle>Plantões</CardTitle>
        </CardHeader>
        <CardContent>
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
        </CardContent>
      </Card>
    </PageContainer>
  );
}
