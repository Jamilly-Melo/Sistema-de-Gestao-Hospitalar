"use client";

import type { ComponentType, ReactNode } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  BarChart3,
  CalendarDays,
  GraduationCap,
  Stethoscope,
  UserCheck,
  Users,
} from "lucide-react";
import { cn } from "@/lib/utils";

type Item = {
  href: string;
  label: string;
  icone: ComponentType<{ className?: string }>;
};

const GRUPOS: { titulo: string; itens: Item[] }[] = [
  {
    titulo: "Cadastros",
    itens: [
      { href: "/pacientes", label: "Pacientes", icone: Users },
      { href: "/profissionais/residentes", label: "Residentes", icone: GraduationCap },
      { href: "/profissionais/preceptores", label: "Preceptores", icone: UserCheck },
    ],
  },
  {
    titulo: "Operação",
    itens: [
      { href: "/atendimentos", label: "Atendimentos", icone: Stethoscope },
      { href: "/escalas", label: "Escalas", icone: CalendarDays },
    ],
  },
  {
    titulo: "Análise",
    itens: [{ href: "/relatorios", label: "Relatórios", icone: BarChart3 }],
  },
];

export function AppShell({ children }: { children: ReactNode }) {
  const pathname = usePathname();

  return (
    <div className="flex min-h-screen">
      <aside className="w-60 shrink-0 border-r bg-card">
        <Link href="/" className="flex h-16 flex-col justify-center px-5">
          <span className="text-sm font-semibold tracking-tight">SGH</span>
          <span className="text-xs text-muted-foreground">Gestão Hospitalar</span>
        </Link>
        <nav className="flex flex-col gap-6 px-3 py-2">
          {GRUPOS.map((grupo) => (
            <div key={grupo.titulo} className="flex flex-col gap-1">
              <span className="px-3 pb-1 text-xs font-medium tracking-wide text-muted-foreground uppercase">
                {grupo.titulo}
              </span>
              {grupo.itens.map((item) => {
                const ativo =
                  pathname === item.href || pathname.startsWith(`${item.href}/`);
                const Icone = item.icone;
                return (
                  <Link
                    key={item.href}
                    href={item.href}
                    className={cn(
                      "flex items-center gap-3 rounded-md px-3 py-2 text-sm transition-colors",
                      ativo
                        ? "bg-primary font-medium text-primary-foreground"
                        : "text-foreground hover:bg-muted"
                    )}
                  >
                    <Icone className="size-4 shrink-0" />
                    {item.label}
                  </Link>
                );
              })}
            </div>
          ))}
        </nav>
      </aside>
      <div className="flex-1">{children}</div>
    </div>
  );
}
