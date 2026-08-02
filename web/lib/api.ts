// No servidor (Server Components, rodando dentro do container `web`), "localhost"
// aponta para o próprio container, não para o container `api` — por isso o
// fetch server-side precisa de API_URL_INTERNAL (nome do serviço no Docker).
// No navegador (Client Components), só o host consegue resolver `api`, então
// o fetch client-side precisa da URL pública NEXT_PUBLIC_API_URL.
const API_URL =
  typeof window === "undefined"
    ? process.env.API_URL_INTERNAL ?? process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000"
    : process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export class ApiError extends Error {
  status: number;

  constructor(status: number, detail: string) {
    super(detail);
    this.status = status;
  }
}

export async function apiFetch<T>(path: string, init?: RequestInit): Promise<T> {
  const resposta = await fetch(`${API_URL}${path}`, {
    ...init,
    headers: { "Content-Type": "application/json", ...init?.headers },
    cache: "no-store",
  });

  if (!resposta.ok) {
    const corpo = await resposta.json().catch(() => ({ detail: resposta.statusText }));
    throw new ApiError(resposta.status, corpo.detail ?? "Erro desconhecido.");
  }

  return resposta.json() as Promise<T>;
}
