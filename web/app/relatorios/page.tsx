"use client";

import { useEffect, useState } from "react";
import { apiFetch, ApiError } from "@/lib/api";
import { PageContainer } from "@/components/PageContainer";
import { PageHeader } from "@/components/PageHeader";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Label } from "@/components/ui/label";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Alert, AlertDescription } from "@/components/ui/alert";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";

type Relatorio = {
  nome: string;
  description: string;
  tecnica: string;
  params: { name: string; label: string; type: string }[];
};

// Um INTERVAL do Postgres chega aqui como duração ISO 8601 — o Pydantic
// serializa o timedelta assim. "PT15M" é P(eríodo) T(empo) 15 M(inutos), o que
// é correto mas ilegível na tela. Acontece com "Tempo médio de espera".
const DURACAO_ISO = /^P(?:(\d+)D)?T(?:(\d+)H)?(?:(\d+)M)?(?:([\d.]+)S)?$/;

function formatarDuracao(texto: string): string | null {
  const partes = DURACAO_ISO.exec(texto);
  if (!partes) return null;

  const [, dias, horas, minutos, segundos] = partes;
  // Todos os grupos são opcionais no padrão, então a string "PT" casaria sem
  // trazer unidade nenhuma. Sem isso, um texto qualquer viraria uma duração.
  if (!dias && !horas && !minutos && !segundos) return null;

  // Componente zerado não vira texto ("1h 0min" é ruído), exceto quando é o
  // único que existe — aí "0min" é a resposta certa.
  const pedacos: string[] = [];
  if (Number(dias) > 0) pedacos.push(`${Number(dias)}d`);
  if (Number(horas) > 0) pedacos.push(`${Number(horas)}h`);
  if (Number(minutos) > 0) pedacos.push(`${Number(minutos)}min`);
  if (Number(segundos) > 0) pedacos.push(`${Number(segundos)}s`);

  return pedacos.length > 0 ? pedacos.join(" ") : "0min";
}

// As consultas devolvem os nomes de coluna do banco (snake_case), e algumas são
// ambíguas fora do contexto do SQL. O caso que motivou isto: "titulacao", no
// relatório de residentes sem supervisor, é a titulação do PRECEPTOR, não do
// residente — a view filtra por `pc.titulacao NOT IN ('DOUTOR', 'POS_DOUTOR')`.
// A view é artefato da entrega avaliada e não muda; o rótulo é de exibição.
// Chave fora do mapa aparece crua: feio, mas honesto.
const ROTULOS_COLUNA: Record<string, string> = {
  data_hora: "Data/hora",
  data_plantao: "Data do plantão",
  id_escala: "ID da escala",
  id_pessoa: "ID",
  id_preceptor: "ID do preceptor",
  id_procedimento_mais_comum: "ID do procedimento mais comum",
  id_residente: "ID do residente",
  id_unidade: "ID da unidade",
  media_duracao_minutos: "Duração média (min)",
  mes: "Mês",
  paciente: "Paciente",
  percentual_risco_alto: "% de risco alto",
  preceptor: "Preceptor",
  procedimento_mais_comum: "Procedimento mais comum",
  procedimentos: "Procedimentos",
  procedimentos_risco_alto: "Procedimentos de risco alto",
  quantidade_procedimento_mais_comum: "Qtd. do procedimento mais comum",
  residente: "Residente",
  tempo_medio_espera: "Tempo médio de espera",
  titulacao: "Titulação do preceptor",
  total_atendimentos: "Total de atendimentos",
  total_plantoes: "Total de plantões",
  total_procedimentos: "Total de procedimentos",
  turno: "Turno",
  unidade: "Unidade",
};

function rotuloDaColuna(chave: string): string {
  return ROTULOS_COLUNA[chave] ?? chave;
}

// Mostra qual item da Etapa 2 o relatório demonstra — serve à apresentação da
// disciplina: dá para ver "View" ou "Stored procedure" sem ler o código.
function EtiquetaTecnica({ tecnica }: { tecnica: string }) {
  return (
    <span className="rounded-md border bg-muted px-2 py-0.5 text-xs font-medium whitespace-nowrap">
      {tecnica}
    </span>
  );
}

// O resultado de um relatório é uma lista de objetos com formato desconhecido em
// tempo de compilação — o catálogo é dinâmico. Esta função é a única que decide
// como cada valor vira texto.
function celula(valor: unknown): string {
  if (valor === null || valor === undefined) return "—";
  // "Último atendimento por paciente" traz `procedimentos` como array.
  if (Array.isArray(valor)) return valor.length > 0 ? valor.join(", ") : "—";
  if (typeof valor === "object") return JSON.stringify(valor);

  if (typeof valor === "string") {
    const duracao = formatarDuracao(valor);
    if (duracao !== null) return duracao;
  }

  return String(valor);
}

export default function RelatoriosPage() {
  const [relatorios, setRelatorios] = useState<Relatorio[]>([]);
  const [selecionado, setSelecionado] = useState<string | null>(null);
  const [parametros, setParametros] = useState<Record<string, string>>({});
  const [resultado, setResultado] = useState<Record<string, unknown>[] | null>(null);
  const [erro, setErro] = useState<string | null>(null);

  useEffect(() => {
    apiFetch<Relatorio[]>("/relatorios").then(setRelatorios);
  }, []);

  const atual = relatorios.find((r) => r.nome === selecionado);

  async function executar() {
    if (!selecionado) return;
    setErro(null);
    setResultado(null);
    try {
      const dados = await apiFetch<Record<string, unknown>[]>(
        `/relatorios/${encodeURIComponent(selecionado)}`,
        { method: "POST", body: JSON.stringify(parametros) }
      );
      setResultado(dados);
    } catch (excecao) {
      setErro(excecao instanceof ApiError ? excecao.message : "Erro inesperado.");
    }
  }

  return (
    <PageContainer>
      <PageHeader titulo="Relatórios" descricao="Consultas analíticas sobre atendimentos, escalas e pacientes." />
      <Card className="max-w-5xl">
        <CardHeader>
          <CardTitle>Executar relatório</CardTitle>
        </CardHeader>
        <CardContent className="flex flex-col gap-4">
          <div className="flex flex-col gap-2">
            <Label>Relatório</Label>
            <Select
              items={relatorios.map((r) => ({ value: r.nome, label: r.nome }))}
              value={selecionado ?? undefined}
              onValueChange={(v) => {
                setSelecionado(v);
                setParametros({});
                setResultado(null);
              }}
            >
              <SelectTrigger className="w-full">
                <SelectValue placeholder="Selecione um relatório" />
              </SelectTrigger>
              <SelectContent>
                {relatorios.map((r) => (
                  <SelectItem key={r.nome} value={r.nome}>
                    <span className="flex items-center gap-2">
                      {r.nome}
                      <EtiquetaTecnica tecnica={r.tecnica} />
                    </span>
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          {atual && (
            <>
              <div className="flex items-start gap-2">
                <EtiquetaTecnica tecnica={atual.tecnica} />
                <p className="text-sm text-muted-foreground">{atual.description}</p>
              </div>
              {atual.params.map((param) => (
                <div key={param.name} className="flex flex-col gap-2">
                  <Label htmlFor={param.name}>{param.label}</Label>
                  <Input
                    id={param.name}
                    value={parametros[param.name] ?? ""}
                    onChange={(e) =>
                      setParametros({ ...parametros, [param.name]: e.target.value })
                    }
                  />
                </div>
              ))}
              <Button onClick={executar} className="w-fit">
                Executar
              </Button>
            </>
          )}

          {erro && (
            <Alert variant="destructive">
              <AlertDescription>{erro}</AlertDescription>
            </Alert>
          )}

          {resultado &&
            (resultado.length === 0 ? (
              <p className="py-8 text-center text-sm text-muted-foreground">
                A consulta não retornou nenhuma linha.
              </p>
            ) : (
              <Table>
                <TableHeader>
                  <TableRow>
                    {Object.keys(resultado[0]).map((coluna) => (
                      <TableHead key={coluna}>{rotuloDaColuna(coluna)}</TableHead>
                    ))}
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {resultado.map((linha, indice) => (
                    <TableRow key={indice}>
                      {Object.keys(resultado[0]).map((coluna) => (
                        <TableCell key={coluna}>{celula(linha[coluna])}</TableCell>
                      ))}
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            ))}
        </CardContent>
      </Card>
    </PageContainer>
  );
}
