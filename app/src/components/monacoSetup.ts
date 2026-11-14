import * as monaco from "monaco-editor/esm/vs/editor/edcore.main";
import "monaco-editor/esm/vs/basic-languages/python/python.contribution";
import EditorWorker from "monaco-editor/esm/vs/editor/editor.worker?worker";
import { t, type MessageKey } from "../strings";
import { PALETTES, type ThemeName } from "../theme/theme";

// O Monaco vem empacotado no aplicativo (nada é baixado de CDN: funciona offline).
self.MonacoEnvironment = { getWorker: () => new EditorWorker() };

// Ao descartar um editor, o Monaco rejeita promessas internas com "Canceled". É esperado.
window.addEventListener("unhandledrejection", (event) => {
  if (event.reason?.name === "Canceled") event.preventDefault();
});

export const MONACO_THEME: Record<ThemeName, string> = { light: "qlp-light", dark: "qlp-dark" };

function defineTheme(name: ThemeName, base: "vs" | "vs-dark", syntax: Record<string, string>) {
  const palette = PALETTES[name];
  monaco.editor.defineTheme(MONACO_THEME[name], {
    base,
    inherit: true,
    rules: Object.entries(syntax).map(([token, foreground]) => ({ token, foreground })),
    colors: {
      "editor.background": palette.surface,
      "editor.foreground": palette.text,
      "editorLineNumber.foreground": palette.lineStrong,
      "editorLineNumber.activeForeground": palette.text,
      "editor.lineHighlightBackground": palette.editorLine,
      "editor.lineHighlightBorder": "#00000000",
      "editorCursor.foreground": palette.accent,
      "editorIndentGuide.background1": palette.line,
      "editorWidget.border": palette.line,
      "focusBorder": "#00000000",
    },
  });
}

defineTheme("light", "vs", {
  comment: "8a909b", keyword: "9a3b6e", string: "2f7a52", number: "a15c00", identifier: "15171c",
});
defineTheme("dark", "vs-dark", {
  comment: "7d8491", keyword: "d79ccc", string: "8cc9a4", number: "e0b46c", identifier: "e6e8ec",
});

// O editor mede a largura dos caracteres ao ser criado; se a fonte do projeto
// carregar depois, as medidas precisam ser refeitas.
void document.fonts?.ready.then(() => monaco.editor.remeasureFonts());

interface GateDoc {
  name: string;
  signature: string;
}

// As descrições vêm de strings.ts (chaves gate.<nome>).
const GATES: GateDoc[] = [
  { name: "x", signature: "x(${1:qubit})" },
  { name: "y", signature: "y(${1:qubit})" },
  { name: "z", signature: "z(${1:qubit})" },
  { name: "h", signature: "h(${1:qubit})" },
  { name: "s", signature: "s(${1:qubit})" },
  { name: "sdg", signature: "sdg(${1:qubit})" },
  { name: "t", signature: "t(${1:qubit})" },
  { name: "tdg", signature: "tdg(${1:qubit})" },
  { name: "rx", signature: "rx(${1:theta}, ${2:qubit})" },
  { name: "ry", signature: "ry(${1:theta}, ${2:qubit})" },
  { name: "rz", signature: "rz(${1:theta}, ${2:qubit})" },
  { name: "p", signature: "p(${1:theta}, ${2:qubit})" },
  { name: "cx", signature: "cx(${1:control}, ${2:target})" },
  { name: "cz", signature: "cz(${1:control}, ${2:target})" },
  { name: "cp", signature: "cp(${1:theta}, ${2:control}, ${3:target})" },
  { name: "swap", signature: "swap(${1:qubit_a}, ${2:qubit_b})" },
  { name: "ccx", signature: "ccx(${1:control_a}, ${2:control_b}, ${3:target})" },
  { name: "mcx", signature: "mcx([${1:controls}], ${2:target})" },
  { name: "measure", signature: "measure(${1:qubit}, ${2:clbit})" },
  { name: "measure_all", signature: "measure_all()" },
  { name: "barrier", signature: "barrier()" },
  { name: "reset", signature: "reset(${1:qubit})" },
];

monaco.languages.registerCompletionItemProvider("python", {
  triggerCharacters: ["."],
  provideCompletionItems(model, position) {
    const prefix = model.getLineContent(position.lineNumber).slice(0, position.column - 1);
    const match = /\b[A-Za-z_]\w*\.(\w*)$/.exec(prefix);
    if (!match) return { suggestions: [] };
    const range = new monaco.Range(
      position.lineNumber, position.column - match[1].length, position.lineNumber, position.column,
    );
    return {
      suggestions: GATES.map((gate, order) => ({
        label: gate.name,
        kind: monaco.languages.CompletionItemKind.Method,
        detail: t(`gate.${gate.name}` as MessageKey),
        insertText: gate.signature,
        insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
        sortText: String(order).padStart(3, "0"),
        range,
      })),
    };
  },
});

export { monaco };
