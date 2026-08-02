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

type Residente = {
  id: number;
  nome: string;
  ano_residencia: string;
  crm: string;
  tempo_medio_de_atendimentos: number | null;
};

export default async function ResidentesPage() {
  const residentes = await apiFetch<Residente[]>("/profissionais/residentes");

  return (
    <PageContainer>
      <PageHeader titulo="Residentes" descricao="Médicos em formação e seu tempo médio de atendimento." />
      <Card>
        <CardHeader>
          <CardTitle>Lista de residentes</CardTitle>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Nome</TableHead>
                <TableHead>Ano</TableHead>
                <TableHead>CRM</TableHead>
                <TableHead>Tempo médio (min)</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {residentes.map((r) => (
                <TableRow key={r.id}>
                  <TableCell>{r.nome}</TableCell>
                  <TableCell>{r.ano_residencia}</TableCell>
                  <TableCell>{r.crm}</TableCell>
                  <TableCell>{r.tempo_medio_de_atendimentos ?? "—"}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </PageContainer>
  );
}
