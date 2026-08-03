// web/components/Autocomplete.tsx
"use client";

import { useState } from "react";
import { Check, ChevronsUpDown } from "lucide-react";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import {
  Command,
  CommandEmpty,
  CommandGroup,
  CommandInput,
  CommandItem,
  CommandList,
} from "@/components/ui/command";
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover";

type Opcao = { id: number; nome: string };

type Props = {
  options: Opcao[];
  value: number | null;
  onChange: (id: number | null) => void;
  placeholder?: string;
};

export function Autocomplete({ options, value, onChange, placeholder }: Props) {
  const [open, setOpen] = useState(false);
  const selecionado = options.find((opcao) => opcao.id === value);

  return (
    <Popover open={open} onOpenChange={setOpen}>
      <PopoverTrigger
        render={
          <Button
            type="button"
            variant="outline"
            role="combobox"
            aria-expanded={open}
            className="w-full justify-between font-normal"
          />
        }
      >
        {selecionado ? selecionado.nome : placeholder ?? "Selecione..."}
        <ChevronsUpDown className="ml-2 h-4 w-4 shrink-0 opacity-50" />
      </PopoverTrigger>
      <PopoverContent className="w-[300px] p-0">
        <Command>
          <CommandInput placeholder={placeholder ?? "Buscar..."} />
          <CommandList>
            <CommandEmpty>Nenhum resultado.</CommandEmpty>
            <CommandGroup>
              {options.map((opcao) => (
                <CommandItem
                  key={opcao.id}
                  value={opcao.nome}
                  onSelect={() => {
                    onChange(opcao.id === value ? null : opcao.id);
                    setOpen(false);
                  }}
                >
                  <Check
                    className={cn(
                      "mr-2 h-4 w-4",
                      opcao.id === value ? "opacity-100" : "opacity-0"
                    )}
                  />
                  {opcao.nome}
                </CommandItem>
              ))}
            </CommandGroup>
          </CommandList>
        </Command>
      </PopoverContent>
    </Popover>
  );
}
