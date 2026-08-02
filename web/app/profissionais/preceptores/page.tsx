import { apiFetch } from "@/lib/api";

type Preceptor = { id_profissional: number; nome: string; titulacao: string };

export default async function PreceptoresPage() {
  const preceptores = await apiFetch<Preceptor[]>("/profissionais/preceptores");

  return (
    <main>
      <h1>Preceptores</h1>
      <table>
        <thead>
          <tr><th>Nome</th><th>Titulação</th></tr>
        </thead>
        <tbody>
          {preceptores.map((p) => (
            <tr key={p.id_profissional}>
              <td>{p.nome}</td>
              <td>{p.titulacao}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </main>
  );
}
