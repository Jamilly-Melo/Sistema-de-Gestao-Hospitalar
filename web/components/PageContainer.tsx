import type { ReactNode } from "react";

export function PageContainer({ children }: { children: ReactNode }) {
  return <main className="mx-auto max-w-3xl px-4 py-12">{children}</main>;
}
