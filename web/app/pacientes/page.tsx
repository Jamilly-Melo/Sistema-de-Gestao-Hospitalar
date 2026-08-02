import Link from "next/link";
import { apiFetch } from "@/lib/api";

type Linha = { nome: string; data_hora: string | null };

export default async function PacientesPage() {
  const linhas = await apiFetch<Linha[]>("/pacientes");

  return (
    <main>
      <h1>Pacientes</h1>
      <table>
        <thead>
          <tr>
            <th>Nome</th>
            <th>Último atendimento</th>
          </tr>
        </thead>
        <tbody>
          {linhas.map((linha, indice) => (
            <tr key={indice}>
              <td>{linha.nome}</td>
              <td>{linha.data_hora ?? "—"}</td>
            </tr>
          ))}
        </tbody>
      </table>
      <p>
        Editar cadastro: <Link href="/pacientes/1">ir para o formulário</Link>{" "}
        (digite o id do paciente na URL — não há detalhe por id nesta tela).
      </p>
    </main>
  );
}
