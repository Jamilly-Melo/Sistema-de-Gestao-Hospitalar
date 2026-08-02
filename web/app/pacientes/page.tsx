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

type Linha = { nome: string; data_hora: string | null };

export default async function PacientesPage() {
  const linhas = await apiFetch<Linha[]>("/pacientes");

  return (
    <PageContainer>
      <h1 className="mb-6 text-2xl font-semibold">Pacientes</h1>
      <Card>
        <CardHeader>
          <CardTitle>Lista de pacientes</CardTitle>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Nome</TableHead>
                <TableHead>Último atendimento</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {linhas.map((linha, indice) => (
                <TableRow key={indice}>
                  <TableCell>{linha.nome}</TableCell>
                  <TableCell>{linha.data_hora ?? "—"}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
      <p className="mt-4 text-sm text-muted-foreground">
        Editar cadastro:{" "}
        <Link className="underline" href="/pacientes/1">
          ir para o formulário
        </Link>{" "}
        (digite o id do paciente na URL — não há detalhe por id nesta tela).
      </p>
    </PageContainer>
  );
}
