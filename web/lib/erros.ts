// Traduz o corpo de erro do FastAPI para uma frase que faça sentido na tela.
//
// O `detail` vem em dois formatos diferentes, e essa é a origem do problema:
//   - string, quando a rota levanta HTTPException — ex.: "Procedimento já
//     faturado, não pode ser removido."
//   - lista de objetos, quando o Pydantic rejeita o corpo (HTTP 422) — ex.:
//     [{ type: "int_type", loc: ["body", "id_paciente"], msg: "Input should
//     be a valid integer" }]
//
// Jogar a lista direto num `new Error(...)` a coage via Array.toString() e
// produz "[object Object],[object Object]", que não diz nada a ninguém.

/** Um item da lista de erros de validação do FastAPI. */
type ErroDeValidacao = {
  type?: string;
  loc?: (string | number)[];
  msg?: string;
};

// Nome do campo na API → rótulo como ele aparece no formulário. Cobre os três
// schemas de request existentes (atendimentos, escalas, pacientes). Campo fora
// do mapa cai no nome cru, que é feio mas continua informativo — melhor que
// esconder o erro.
const ROTULOS: Record<string, string> = {
  // CriarAtendimentoRequest
  data_hora: "Data/hora",
  duracao_minutos: "Duração (min)",
  id_paciente: "Paciente",
  id_residente: "Residente",
  id_preceptor: "Preceptor",
  id_unidade: "Unidade",
  procedimentos: "Procedimentos",
  // ProcedimentoRealizadoInput
  id_procedimento: "Procedimento",
  quantidade: "Quantidade",
  tempo_real_minutos: "Tempo real (min)",
  data_hora_inicio: "Início do procedimento",
  observacao: "Observação",
  faturado: "Faturado",
  // ReajustarEscalaRequest
  data_origem: "Data de origem",
  turno_origem: "Turno de origem",
  data_destino: "Data de destino",
  turno_destino: "Turno de destino",
  // AtualizarPacienteRequest
  campo: "Campo",
  valor: "Valor",
};

// Usa o `type` do Pydantic, não o `msg`: o type é um identificador estável,
// enquanto o msg é texto em inglês que muda entre versões da biblioteca.
const MENSAGENS: Record<string, string> = {
  missing: "campo obrigatório",
  int_type: "precisa ser um número inteiro",
  int_parsing: "precisa ser um número inteiro",
  int_from_float: "precisa ser um número inteiro, sem casas decimais",
  float_type: "precisa ser um número",
  string_type: "precisa ser um texto",
  string_too_short: "texto curto demais",
  bool_type: "precisa ser verdadeiro ou falso",
  list_type: "precisa ser uma lista",
  datetime_type: "data e hora inválidas",
  datetime_parsing: "data e hora inválidas",
  datetime_from_date_parsing: "data e hora inválidas",
  date_type: "data inválida",
  date_parsing: "data inválida",
  date_from_datetime_parsing: "data inválida",
  literal_error: "valor não permitido",
  enum: "valor não permitido",
  greater_than: "valor abaixo do mínimo",
  greater_than_equal: "valor abaixo do mínimo",
  less_than: "valor acima do máximo",
  less_than_equal: "valor acima do máximo",
};

/** Último segmento textual de `loc`, ignorando "body" e índices numéricos. */
function nomeDoCampo(loc: (string | number)[]): string | null {
  const segmentos = loc
    .slice(1) // "body" não diz nada ao usuário
    .filter((s): s is string => typeof s === "string");
  return segmentos.at(-1) ?? null;
}

function descreverErro(erro: ErroDeValidacao): string {
  const campo = nomeDoCampo(erro.loc ?? []);
  const rotulo = campo ? ROTULOS[campo] ?? campo : null;
  // Se o `type` for desconhecido, o msg do Pydantic (em inglês) ainda é melhor
  // que uma frase genérica — pelo menos diz o que houve.
  const motivo =
    (erro.type ? MENSAGENS[erro.type] : undefined) ??
    erro.msg ??
    "valor inválido";

  return rotulo ? `${rotulo}: ${motivo}` : motivo;
}

/**
 * Monta a mensagem exibida ao usuário a partir do `detail` do FastAPI.
 *
 * @param detail  o campo `detail` do corpo da resposta (string ou lista)
 * @param statusText  usado como último recurso, quando não há `detail` legível
 */
export function mensagemDoErro(detail: unknown, statusText: string): string {
  if (typeof detail === "string" && detail.trim() !== "") return detail;

  if (Array.isArray(detail)) {
    const partes = (detail as ErroDeValidacao[])
      .map(descreverErro)
      .filter((parte) => parte.trim() !== "");

    if (partes.length > 0) return partes.join("; ");
  }

  return statusText || "Erro desconhecido.";
}
