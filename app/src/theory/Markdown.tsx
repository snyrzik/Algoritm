import { memo, useMemo, useState, type ReactNode, isValidElement } from "react";
import ReactMarkdown, { type Components } from "react-markdown";
import remarkGfm from "remark-gfm";
import { cppLanguage } from "@codemirror/lang-cpp";
import { highlightTree, classHighlighter } from "@lezer/highlight";
import { Check, Copy, Code2, Layers3 } from "lucide-react";
import "./theory.css";

export function textContent(value: ReactNode): string {
  if (typeof value === "string" || typeof value === "number")
    return String(value);
  if (Array.isArray(value)) return value.map(textContent).join("");
  if (isValidElement<{ children?: ReactNode }>(value))
    return textContent(value.props.children);
  return "";
}

export function headingId(title: string) {
  return (
    "theory-" +
    title
      .normalize("NFKC")
      .replace(/`|\*\*/g, "")
      .toLowerCase()
      .replace(/[^\p{L}\p{N}]+/gu, "-")
      .replace(/^-|-$/g, "")
  );
}

export function headings(markdown: string) {
  let fenced = false;
  const result: { title: string; id: string }[] = [];
  for (const line of markdown.split(/\r?\n/)) {
    if (line.startsWith("```")) {
      fenced = !fenced;
      continue;
    }
    if (!fenced && /^## /.test(line)) {
      const title = line.slice(3).replace(/`|\*\*/g, "");
      result.push({ title, id: headingId(title) });
    }
  }
  return result;
}

const CodeBlock = memo(function CodeBlock({
  language,
  value,
}: {
  language: string;
  value: string;
}) {
  const [copied, setCopied] = useState(false);
  const [copyError, setCopyError] = useState(false);
  const cpp = ["cpp", "c++", "c"].includes(language);
  const memory = !cpp && /┌|m_data|До вызова|отдельный объект/.test(value);
  const highlighted = useMemo(() => {
    if (!cpp) return value;
    const parts: ReactNode[] = [];
    let previous = 0;
    highlightTree(
      cppLanguage.parser.parse(value),
      classHighlighter,
      (from, to, classes) => {
        if (from > previous) parts.push(value.slice(previous, from));
        parts.push(
          <span className={classes} key={`${from}-${to}`}>
            {value.slice(from, to)}
          </span>,
        );
        previous = to;
      },
    );
    if (previous < value.length) parts.push(value.slice(previous));
    return parts;
  }, [cpp, value]);
  async function copy() {
    try {
      await navigator.clipboard.writeText(value);
      setCopied(true);
      setCopyError(false);
    } catch {
      setCopyError(true);
    }
  }
  return (
    <figure className={`theory-code-block ${memory ? "theory-memory" : ""}`}>
      <div className="theory-code-toolbar">
        <span>
          {cpp ? <Code2 size={14} /> : <Layers3 size={14} />}
          {cpp
            ? "C++17"
            : memory
              ? "Логическая схема памяти"
              : "Разбор / результат"}
        </span>
        <button type="button" onClick={copy} aria-label="Скопировать пример">
          {copied ? <Check size={13} /> : <Copy size={13} />}
          {copyError
            ? "Копирование недоступно"
            : copied
              ? "Скопировано"
              : "Копировать"}
        </button>
      </div>
      <pre
        tabIndex={0}
        aria-label={cpp ? "Пример C++" : "Схема или результат из лекции"}
      >
        <code className={cpp ? "language-cpp" : "language-text"}>
          {highlighted}
        </code>
      </pre>
    </figure>
  );
});

const components: Components = {
  h1: ({ children }) => (
    <h1 id={headingId(textContent(children))}>{children}</h1>
  ),
  h2: ({ children }) => (
    <h2 id={headingId(textContent(children))}>{children}</h2>
  ),
  h3: ({ children }) => (
    <h3 id={headingId(textContent(children))}>{children}</h3>
  ),
  pre: ({ children }) => <>{children}</>,
  code: ({ className, children }) => {
    const language = /language-([^\s]+)/.exec(className || "")?.[1];
    return language ? (
      <CodeBlock language={language} value={String(children)} />
    ) : (
      <code>{children}</code>
    );
  },
  table: ({ children }) => (
    <div className="theory-table-scroll" tabIndex={0}>
      <table>{children}</table>
    </div>
  ),
};

export const Markdown = memo(function Markdown({ source }: { source: string }) {
  return (
    <div className="theory-markdown">
      <ReactMarkdown remarkPlugins={[remarkGfm]} components={components}>
        {source}
      </ReactMarkdown>
    </div>
  );
});
