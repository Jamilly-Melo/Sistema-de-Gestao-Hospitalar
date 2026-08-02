// web/components/Autocomplete.tsx
"use client";

import { useMemo, useState } from "react";

type Opcao = { id: number; nome: string };

type Props = {
  options: Opcao[];
  value: number | null;
  onChange: (id: number | null) => void;
  placeholder?: string;
};

export function Autocomplete({ options, value, onChange, placeholder }: Props) {
  const [filtro, setFiltro] = useState("");
  const selecionado = options.find((opcao) => opcao.id === value);

  const filtradas = useMemo(() => {
    if (!filtro) return options.slice(0, 20);
    return options
      .filter((opcao) => opcao.nome.toLowerCase().includes(filtro.toLowerCase()))
      .slice(0, 20);
  }, [filtro, options]);

  return (
    <div style={{ position: "relative" }}>
      <input
        type="text"
        value={selecionado ? selecionado.nome : filtro}
        placeholder={placeholder}
        onChange={(evento) => {
          onChange(null);
          setFiltro(evento.target.value);
        }}
      />
      {filtro && !selecionado && (
        <ul style={{ border: "1px solid #ccc", position: "absolute", background: "white", width: "100%", listStyle: "none", margin: 0, padding: 0, zIndex: 1 }}>
          {filtradas.map((opcao) => (
            <li
              key={opcao.id}
              style={{ padding: "4px 8px", cursor: "pointer" }}
              onClick={() => {
                onChange(opcao.id);
                setFiltro("");
              }}
            >
              {opcao.nome}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
