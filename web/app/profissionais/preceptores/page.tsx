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

type Preceptor = { id_profissional: number; nome: string; titulacao: string };

export default async function PreceptoresPage() {
  const preceptores = await apiFetch<Preceptor[]>("/profissionais/preceptores");

  return (
    <PageContainer>
      <h1 className="mb-6 text-2xl font-semibold">Preceptores</h1>
      <Card>
        <CardHeader>
          <CardTitle>Lista de preceptores</CardTitle>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Nome</TableHead>
                <TableHead>Titulação</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {preceptores.map((p) => (
                <TableRow key={p.id_profissional}>
                  <TableCell>{p.nome}</TableCell>
                  <TableCell>{p.titulacao}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </PageContainer>
  );
}
