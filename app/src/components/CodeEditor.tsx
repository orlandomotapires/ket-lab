import { useEffect, useRef } from "react";
import { lineForStep } from "../lib/steps";
import { selectCurrentStep, useStore } from "../state/store";
import { useTheme } from "../theme/theme";
import { MONACO_THEME, monaco } from "./monacoSetup";

const FONT_STACK = '"IBM Plex Mono", ui-monospace, "SF Mono", Menlo, Consolas, monospace';

export function CodeEditor() {
  const container = useRef<HTMLDivElement>(null);
  const editorRef = useRef<monaco.editor.IStandaloneCodeEditor | null>(null);
  const decorations = useRef<monaco.editor.IEditorDecorationsCollection | null>(null);
  const theme = useTheme();

  const code = useStore((s) => s.code);
  const error = useStore((s) => s.error);
  const resultIsCurrent = useStore((s) => s.resultIsCurrent);
  const followCursor = useStore((s) => s.followCursor);
  const steps = useStore((s) => s.result?.steps);
  const currentStep = useStore(selectCurrentStep);

  useEffect(() => {
    const { code: initial, setCode, setCursorLine } = useStore.getState();
    const editor = monaco.editor.create(container.current!, {
      value: initial,
      language: "python",
      theme: MONACO_THEME[theme],
      fontFamily: FONT_STACK,
      fontSize: 13.5,
      lineHeight: 22,
      minimap: { enabled: false },
      scrollBeyondLastLine: false,
      automaticLayout: true,
      tabSize: 4,
      renderLineHighlight: "line",
      overviewRulerLanes: 0,
      stickyScroll: { enabled: false },
      padding: { top: 12, bottom: 12 },
      lineNumbersMinChars: 3,
      glyphMargin: false,
      folding: false,
      contextmenu: false,
      scrollbar: { verticalScrollbarSize: 10, horizontalScrollbarSize: 10 },
    });
    editorRef.current = editor;
    decorations.current = editor.createDecorationsCollection();

    const lastLine = editor.getModel()!.getLineCount();
    editor.setPosition({ lineNumber: lastLine, column: editor.getModel()!.getLineMaxColumn(lastLine) });
    editor.focus();

    const onContent = editor.onDidChangeModelContent(() => setCode(editor.getValue()));
    const onCursor = editor.onDidChangeCursorPosition((event) => {
      // Só o aluno move o foco da inspeção; mudanças programáticas não contam.
      if (event.source !== "api" && event.source !== "modelChange") setCursorLine(event.position.lineNumber);
    });
    return () => {
      onContent.dispose();
      onCursor.dispose();
      editor.dispose();
      editorRef.current = null;
    };
    // O editor é criado uma única vez; tema e código são sincronizados abaixo.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    monaco.editor.setTheme(MONACO_THEME[theme]);
  }, [theme]);

  // Mudanças de código vindas de fora (trocar de lição, restaurar o código inicial).
  useEffect(() => {
    const editor = editorRef.current;
    if (editor && editor.getValue() !== code) editor.setValue(code);
  }, [code]);

  // Erros do motor viram marcadores na linha correspondente.
  useEffect(() => {
    const model = editorRef.current?.getModel();
    if (!model) return;
    const line = error?.line;
    const show = error && !resultIsCurrent && line != null && line >= 1 && line <= model.getLineCount();
    monaco.editor.setModelMarkers(
      model,
      "qlp",
      show
        ? [{
            severity: monaco.MarkerSeverity.Error,
            message: error.message,
            startLineNumber: line,
            startColumn: model.getLineFirstNonWhitespaceColumn(line) || 1,
            endLineNumber: line,
            endColumn: model.getLineMaxColumn(line),
          }]
        : [],
    );
  }, [error, resultIsCurrent, code]);

  // Com a linha do tempo no controle, destaca a linha que gerou o passo em exibição.
  useEffect(() => {
    const line = !followCursor && steps ? lineForStep(steps, currentStep) : null;
    decorations.current?.set(
      line
        ? [{
            range: new monaco.Range(line, 1, line, 1),
            options: { isWholeLine: true, className: "qlp-step-line", linesDecorationsClassName: "qlp-step-marker" },
          }]
        : [],
    );
  }, [followCursor, steps, currentStep]);

  return <div ref={container} className="editor" />;
}
