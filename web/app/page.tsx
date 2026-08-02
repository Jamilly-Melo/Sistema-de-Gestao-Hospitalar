import Link from "next/link";
import { PageContainer } from "@/components/PageContainer";
import { Card, CardHeader, CardTitle } from "@/components/ui/card";

const paginas = [
  { href: "/pacientes", titulo: "Pacientes" },
  { href: "/profissionais/residentes", titulo: "Residentes" },
  { href: "/profissionais/preceptores", titulo: "Preceptores" },
  { href: "/atendimentos", titulo: "Atendimentos" },
  { href: "/escalas", titulo: "Escalas" },
  { href: "/relatorios", titulo: "Relatórios" },
];

export default function HomePage() {
  return (
    <PageContainer>
      <h1 className="mb-6 text-2xl font-semibold">Sistema de Gestão Hospitalar</h1>
      <div className="grid grid-cols-2 gap-4 sm:grid-cols-3">
        {paginas.map((pagina) => (
          <Link key={pagina.href} href={pagina.href}>
            <Card className="transition-colors hover:bg-accent">
              <CardHeader>
                <CardTitle>{pagina.titulo}</CardTitle>
              </CardHeader>
            </Card>
          </Link>
        ))}
      </div>
    </PageContainer>
  );
}
