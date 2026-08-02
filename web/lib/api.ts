const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

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
