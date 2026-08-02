import Link from "next/link";

export default function HomePage() {
  return (
    <main>
      <h1>Sistema de Gestão Hospitalar</h1>
      <ul>
        <li><Link href="/pacientes">Pacientes</Link></li>
        <li><Link href="/profissionais/residentes">Residentes</Link></li>
        <li><Link href="/profissionais/preceptores">Preceptores</Link></li>
        <li><Link href="/atendimentos">Atendimentos</Link></li>
        <li><Link href="/escalas">Escalas</Link></li>
        <li><Link href="/relatorios">Relatórios</Link></li>
      </ul>
    </main>
  );
}
