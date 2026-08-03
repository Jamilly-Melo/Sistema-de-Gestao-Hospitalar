import type { ReactNode } from "react";

export function PageHeader({
  titulo,
  descricao,
  acao,
}: {
  titulo: ReactNode;
  descricao: string;
  acao?: ReactNode;
}) {
  return (
    <div className="mb-8 flex items-start justify-between gap-4 border-b pb-5">
      <div className="flex flex-col gap-1">
        <h1 className="text-2xl font-semibold tracking-tight">{titulo}</h1>
        <p className="text-sm text-muted-foreground">{descricao}</p>
      </div>
      {acao}
    </div>
  );
}
