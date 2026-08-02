import { apiFetch } from "@/lib/api";
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

type Preceptor = { id_profissional: number; nome: string; titulacao: string };

export default async function PreceptoresPage() {
  const preceptores = await apiFetch<Preceptor[]>("/profissionais/preceptores");

  return (
    <PageContainer>
      <PageHeader titulo="Preceptores" descricao="Profissionais responsáveis pela supervisão dos residentes." />
      <Card>
        <CardHeader>
          <CardTitle>Lista de preceptores</CardTitle>
        </CardHeader>
        <CardContent>
          {preceptores.length === 0 ? (
            <p className="py-8 text-center text-sm text-muted-foreground">
              Nenhum preceptor cadastrado.
            </p>
          ) : (
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
          )}
        </CardContent>
      </Card>
    </PageContainer>
  );
}
