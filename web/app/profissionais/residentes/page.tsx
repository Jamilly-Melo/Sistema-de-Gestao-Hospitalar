import { apiFetch } from "@/lib/api";

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
    <main>
      <h1>Residentes</h1>
      <table>
        <thead>
          <tr><th>Nome</th><th>Ano</th><th>CRM</th><th>Tempo médio (min)</th></tr>
        </thead>
        <tbody>
          {residentes.map((r) => (
            <tr key={r.id}>
              <td>{r.nome}</td>
              <td>{r.ano_residencia}</td>
              <td>{r.crm}</td>
              <td>{r.tempo_medio_de_atendimentos ?? "—"}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </main>
  );
}
