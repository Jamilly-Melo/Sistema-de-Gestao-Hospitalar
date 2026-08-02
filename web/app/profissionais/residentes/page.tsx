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
  tempo_medio_de_atendimentos: string | null;
};

// A API devolve o AVG do Postgres como string de Decimal ("33.5000000000000000").
function formatarMinutos(valor: string | null): string {
  if (valor === null) return "—";
  const numero = Number(valor);
  return Number.isNaN(numero) ? "—" : numero.toFixed(1);
}

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
          {residentes.length === 0 ? (
            <p className="py-8 text-center text-sm text-muted-foreground">
              Nenhum residente cadastrado.
            </p>
          ) : (
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
                    <TableCell>{formatarMinutos(r.tempo_medio_de_atendimentos)}</TableCell>
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
