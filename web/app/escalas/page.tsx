// web/app/escalas/page.tsx
import Link from "next/link";
import { apiFetch } from "@/lib/api";

type Linha = { unidade: string | null; residente: string; total_plantoes: number };

export default async function EscalasPage() {
  const linhas = await apiFetch<Linha[]>("/escalas");

  return (
    <main>
      <h1>Plantões do mês corrente</h1>
      <p><Link href="/escalas/reajustar">Reajustar escala</Link></p>
      <table>
        <thead><tr><th>Unidade</th><th>Residente</th><th>Total de plantões</th></tr></thead>
        <tbody>
          {linhas.map((linha, indice) => (
            <tr key={indice}>
              <td>{linha.unidade ?? "—"}</td>
              <td>{linha.residente}</td>
              <td>{linha.total_plantoes}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </main>
  );
}
