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
  id_pessoa: number;
  nome: string;
  data_hora: string | null;
  residente: string | null;
  preceptor: string | null;
  procedimentos: string[];
};

function ou(valor: string | null): string {
  return valor ?? "—";
}

export default async function PacientesPage({
  searchParams,
}: {
  searchParams: Promise<{ [chave: string]: string | string[] | undefined }>;
}) {
  const ok = (await searchParams).ok;
  const mensagem = typeof ok === "string" ? ok : null;
  const linhas = await apiFetch<Linha[]>("/pacientes/listagem");

  return (
    <PageContainer>
      <PageHeader
        titulo="Pacientes"
        descricao="Pacientes cadastrados e a data do último atendimento."
      />
      {mensagem && (
        <Alert variant="success" className="mb-6">
          <AlertDescription>{mensagem}</AlertDescription>
        </Alert>
      )}
      <Card>
        <CardHeader>
          <CardTitle>Lista de pacientes</CardTitle>
        </CardHeader>
        <CardContent>
          {linhas.length === 0 ? (
            <p className="py-8 text-center text-sm text-muted-foreground">
              Nenhum paciente cadastrado.
            </p>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Nome</TableHead>
                  <TableHead>Último atendimento</TableHead>
                  <TableHead>Residente</TableHead>
                  <TableHead>Preceptor</TableHead>
                  <TableHead>Procedimentos</TableHead>
                  <TableHead></TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {linhas.map((linha) => (
                  <TableRow key={linha.id_pessoa}>
                    <TableCell>{linha.nome}</TableCell>
                    <TableCell>{ou(linha.data_hora)}</TableCell>
                    <TableCell>{ou(linha.residente)}</TableCell>
                    <TableCell>{ou(linha.preceptor)}</TableCell>
                    <TableCell>
                      {linha.procedimentos.length > 0
                        ? linha.procedimentos.join(", ")
                        : "—"}
                    </TableCell>
                    <TableCell className="text-right">
                      <Link
                        href={`/pacientes/${linha.id_pessoa}`}
                        className={buttonVariants({ variant: "outline", size: "sm" })}
                      >
                        Editar
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
