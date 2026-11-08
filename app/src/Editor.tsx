import { useEffect, useRef } from "react";
import { EditorState } from "@codemirror/state";
import {
  EditorView,
  keymap,
  lineNumbers,
  highlightActiveLine,
  highlightActiveLineGutter,
  drawSelection,
} from "@codemirror/view";
import {
  defaultKeymap,
  history,
  historyKeymap,
  indentWithTab,
} from "@codemirror/commands";
import { cpp } from "@codemirror/lang-cpp";
import { python } from "@codemirror/lang-python";
import { oneDark } from "@codemirror/theme-one-dark";
import {
  bracketMatching,
  indentOnInput,
  syntaxHighlighting,
  defaultHighlightStyle,
} from "@codemirror/language";

export function Editor({
  value,
  onChange,
  theme,
  filename,
  readOnly = false,
}: {
  value: string;
  onChange: (value: string) => void;
  theme: string;
  filename: string;
  readOnly?: boolean;
}) {
  const host = useRef<HTMLDivElement>(null),
    view = useRef<EditorView | null>(null),
    change = useRef(onChange);
  change.current = onChange;
  useEffect(() => {
    if (!host.current) return;
    const editor = new EditorView({
      parent: host.current,
      state: EditorState.create({
        doc: value,
        extensions: [
          lineNumbers(),
          EditorState.readOnly.of(readOnly),
          EditorView.editable.of(!readOnly),
          highlightActiveLineGutter(),
          history(),
          drawSelection(),
          indentOnInput(),
          bracketMatching(),
          highlightActiveLine(),
          keymap.of([indentWithTab, ...defaultKeymap, ...historyKeymap]),
          ...(filename.endsWith(".md") ? [] : [filename.endsWith('.py')?python():cpp()]),
          ...(theme === "dark"
            ? [oneDark]
            : [syntaxHighlighting(defaultHighlightStyle)]),
          EditorView.contentAttributes.of({
            "aria-label": `Редактор ${filename}`,
          }),
          EditorView.theme({
            "&": { height: "100%", fontSize: "13px" },
            ".cm-scroller": {
              fontFamily: 'Consolas, "Cascadia Code", monospace',
              lineHeight: "1.75",
            },
            ".cm-content": { padding: "20px 0" },
            ".cm-gutters": { border: "none", background: "transparent" },
            "&.cm-focused": { outline: "none" },
          }),
          EditorView.updateListener.of((update) => {
            if (update.docChanged) change.current(update.state.doc.toString());
          }),
        ],
      }),
    });
    view.current = editor;
    return () => {
      editor.destroy();
      view.current = null;
    };
    // File and theme changes reconstruct the view; ordinary edits preserve history.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [theme, filename, readOnly]);
  useEffect(() => {
    const v = view.current;
    if (v && v.state.doc.toString() !== value)
      v.dispatch({
        changes: { from: 0, to: v.state.doc.length, insert: value },
      });
  }, [value]);
  return <div className="editor-host" ref={host} />;
}
