import Link from "next/link";
import {
  GraduationCap,
  Stethoscope,
  UserCheck,
  Users,
} from "lucide-react";
import type { ComponentType } from "react";
import { apiFetch } from "@/lib/api";
import { PageContainer } from "@/components/PageContainer";
import { PageHeader } from "@/components/PageHeader";
import { buttonVariants } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

type LinhaAtendimento = { id_atendimento: number };

type Indicador = {
  label: string;
  valor: number;
  nota: string;
  icone: ComponentType<{ className?: string }>;
};

export default async function HomePage() {
  const [pacientes, residentes, preceptores, atendimentos] = await Promise.all([
    apiFetch<unknown[]>("/pacientes/listagem"),
    apiFetch<unknown[]>("/profissionais/residentes"),
    apiFetch<unknown[]>("/profissionais/preceptores"),
    apiFetch<LinhaAtendimento[]>("/atendimentos"),
  ]);

  // /atendimentos devolve uma linha por procedimento, não por atendimento — o
  // mesmo id_atendimento se repete entre linhas. Contar o array daria um número
  // inflado, por isso a contagem é de ids distintos.
  const totalAtendimentos = new Set(
    atendimentos.map((linha) => linha.id_atendimento)
  ).size;

  const indicadores: Indicador[] = [
    { label: "Pacientes", valor: pacientes.length, nota: "cadastrados", icone: Users },
    { label: "Residentes", valor: residentes.length, nota: "em formação", icone: GraduationCap },
    { label: "Preceptores", valor: preceptores.length, nota: "supervisores", icone: UserCheck },
    { label: "Atendimentos", valor: totalAtendimentos, nota: "registrados", icone: Stethoscope },
  ];

  return (
    <PageContainer>
      <PageHeader titulo="Visão geral" descricao="Resumo do que está cadastrado no sistema." />

      <div className="mb-8 grid grid-cols-4 gap-4">
        {indicadores.map((indicador) => {
          const Icone = indicador.icone;
          return (
            <Card key={indicador.label}>
              <CardContent className="flex flex-col gap-2">
                <div className="flex items-center gap-2 text-muted-foreground">
                  <Icone className="size-4" />
                  <span className="text-xs font-medium tracking-wide uppercase">
                    {indicador.label}
                  </span>
                </div>
                <span className="text-3xl font-semibold tabular-nums">
                  {indicador.valor}
                </span>
                <span className="text-xs text-muted-foreground">{indicador.nota}</span>
              </CardContent>
            </Card>
          );
        })}
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Ações rápidas</CardTitle>
        </CardHeader>
        <CardContent className="flex gap-3">
          <Link href="/atendimentos/novo" className={buttonVariants()}>
            Novo atendimento
          </Link>
          <Link href="/escalas/reajustar" className={buttonVariants({ variant: "outline" })}>
            Reajustar escala
          </Link>
        </CardContent>
      </Card>
    </PageContainer>
  );
}
