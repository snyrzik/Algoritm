import {isCompleted} from "../types";
import { memo, useEffect, useMemo, useRef, useState } from "react";
import {
  ArrowLeft,
  ArrowRight,
  BookOpen,
  Check,
  CheckCircle2,
  ChevronDown,
  ChevronRight,
  Code2,
  Download,
  List,
  RefreshCw,
} from "lucide-react";
import { api } from "../api";
import { type Attempt, type Task, statusNames } from "../types";
import { Markdown, headings } from "./Markdown";
import "./theory.css";

interface Section {
  id: string;
  title: string;
  markdown: string;
  chapter?: number;
  checkId?: string;
}
export interface Lecture {
  id: string;
  day: number;
  lecture: number;
  title: string;
  sourceFilename: string;
  sourceSha256: string;
  sections: Section[];
  checks: Task[];
  projects: Task[];
  localInstructions: string;
  reading: string[];
}
interface Props {
  section: string;
  anchor: string;
  attempts: Attempt[];
  go: (path: string) => Promise<void>;
  onReading?: (reading:string[]) => void;
}

export default memo(function Theory({ section, anchor, attempts, go, onReading }: Props) {
  const [lecture, setLecture] = useState<Lecture | null>(null);
  const [error, setError] = useState("");
  const [menuOpen, setMenuOpen] = useState(false);
  const [readingBusy,setReadingBusy] = useState(false);
  const [readingError,setReadingError] = useState('');
  const content = useRef<HTMLDivElement>(null);
  useEffect(() => {
    let current = true;
    api<Lecture>("theory/day-1/lecture-1")
      .then((data) => {
        if (current) setLecture(data);
      })
      .catch((e) => {
        if (current) setError(String(e));
      });
    return () => {
      current = false;
    };
  }, []);
  const selected =
    lecture?.sections.find((s) => s.id === section) || lecture?.sections[0];
  const toc = useMemo(
    () => headings(selected?.markdown || ""),
    [selected?.markdown],
  );
  useEffect(() => {
    setMenuOpen(false);
    if (!selected) return;
    const frame = requestAnimationFrame(() => {
      if (anchor) {
        let id = anchor;
        try {
          id = decodeURIComponent(anchor);
        } catch {
          /* Keep malformed anchors harmless. */
        }
        document
          .getElementById(id)
          ?.scrollIntoView({ behavior: "instant", block: "start" });
      } else window.scrollTo({ top: 0, behavior: "instant" });
    });
    return () => cancelAnimationFrame(frame);
  }, [selected?.id, anchor, lecture?.id]);
  if (error)
    return (
      <div className="error-banner" role="alert">
        {error}
        <button onClick={() => go("day/1")}>Вернуться к дню 1</button>
      </div>
    );
  if (!lecture || !selected)
    return (
      <div className="loading-state">
        <RefreshCw className="spin" />
        <p>Открываем лекцию № 1…</p>
      </div>
    );
  const latest: Record<string, Attempt> = {};
  for (const attempt of attempts)
    if (attempt.mode !== "compile" && !latest[attempt.task])
      latest[attempt.task] = attempt;
  const passed = lecture.checks.filter(
    (t) => isCompleted(latest[t.id]),
  ).length;
  const position = lecture.sections.findIndex((s) => s.id === selected.id);
  const check = lecture.checks.find((t) => t.id === selected.checkId);
  async function markReading(){
    if(!selected||!lecture)return;
    setReadingBusy(true);setReadingError('');
    try{const value=await api<{reading:string[]}>('lecture-read/'+selected.id,{completed:!lecture.reading.includes(selected.id)});setLecture({...lecture,reading:value.reading});onReading?.(value.reading);}
    catch(e){setReadingError(String(e));}finally{setReadingBusy(false);}
  }
  const title = selected.chapter
    ? `Глава ${selected.chapter}`
    : selected.id === "summary"
      ? "Итоги лекции"
      : "Начало лекции";
  function downloadOriginal() {
    const url = URL.createObjectURL(
      new Blob([lecture!.sections.map((s) => s.markdown).join("")], {
        type: "text/markdown;charset=utf-8",
      }),
    );
    const link = document.createElement("a");
    link.href = url;
    link.download = lecture!.sourceFilename;
    link.click();
    setTimeout(() => URL.revokeObjectURL(url), 1000);
  }
  return (
    <div className="theory-page">
      <div className="theory-topline">
        <button className="back-link" onClick={() => go("day/1")}>
          <ArrowLeft size={15} />
          День 1 · Перегрузка операторов
        </button>
        <button className="theory-source-button" onClick={downloadOriginal}>
          <Download size={14} />
          Исходный Markdown
        </button>
      </div>
      <div className="theory-page-header">
        <div>
          <div className="eyebrow">ЛЕКЦИЯ № 1 / ДЕНЬ 1</div>
          <h2>Теория</h2>
          <p>{lecture.title}</p>
        </div>
        <div className="theory-header-progress">
          <span>
            <Code2 size={15} />
            Закрепления
          </span>
          <strong>
            {passed}
            <small> / {lecture.checks.length}</small>
          </strong>
          <div className="progress-bar">
            <i style={{ width: `${(passed / lecture.checks.length) * 100}%` }} />
          </div>
          <small>Прочитано глав: {lecture.reading.length} / 5</small>
        </div>
      </div>
      <button
        className="theory-mobile-menu"
        aria-expanded={menuOpen}
        onClick={() => setMenuOpen(!menuOpen)}
      >
        <List size={16} />
        Содержание лекции <span>{title}</span>
        <ChevronDown size={15} />
      </button>
      <div className="theory-layout">
        <aside
          className={`theory-navigation ${menuOpen ? "is-open" : ""}`}
          aria-label="Содержание лекции № 1"
        >
          <div className="theory-nav-caption">В ЭТОЙ ЛЕКЦИИ</div>
          <nav>
            {lecture.sections.map((item) => (
              <button
                key={item.id}
                className={selected.id === item.id ? "selected" : ""}
                aria-current={selected.id === item.id ? "page" : undefined}
                onClick={() => go(`theory/1/${item.id}`)}
              >
                <span className="theory-chapter-number">
                  {item.chapter ? (
                    String(item.chapter).padStart(2, "0")
                  ) : item.id === "summary" ? (
                    <CheckCircle2 size={15} />
                  ) : (
                    <BookOpen size={15} />
                  )}
                </span>
                <span>
                  {item.chapter
                    ? item.title.replace(/^Глава \d\. /, "").replace(/`/g, "")
                    : item.title}
                </span>
                {item.checkId && isCompleted(latest[item.checkId]) ? (
                  <Check size={13} />
                ) : (
                  <ChevronRight size={12} />
                )}
              </button>
            ))}
          </nav>
          <div className="theory-nav-note">
            <Code2 size={17} />
            <p>
              После каждой главы — самостоятельное задание. Прочтение и
              выполнение учитываются отдельно.
            </p>
          </div>
          <button
            className="theory-to-practice"
            onClick={() => go("theory/1/practice")}
          >
            <ArrowRight size={15} />К трём проектам
          </button>
        </aside>
        <div className="theory-reading-column" ref={content}>
          <div className="theory-reading-label">
            <span>{title}</span>
            <span>C++17 · Лекция № 1</span>
          </div>
          {toc.length > 1 && (
            <details className="theory-section-toc">
              <summary>
                <List size={14} />
                Внутри раздела <span>{toc.length} тем</span>
              </summary>
              <nav aria-label="Темы открытой главы">
                {toc.map((item) => (
                  <button
                    key={item.id}
                    onClick={() => go(`theory/1/${selected.id}/${item.id}`)}
                  >
                    {item.title}
                    <ChevronRight size={12} />
                  </button>
                ))}
              </nav>
            </details>
          )}
          <article className="theory-article" aria-label={selected.title}>
            <div className="lecture01-example-label">Теоретический пример — учебный код в тексте главы</div>
            <Markdown source={selected.markdown} />
          </article>
          {selected.chapter&&<div className="lecture01-read-toggle"><span>Прочтение главы не засчитывает выполнение задания.</span><button disabled={readingBusy} onClick={markReading}><Check size={15}/>{lecture.reading.includes(selected.id)?'Прочитано · снять отметку':'Отметить главу прочитанной'}</button></div>}
          {readingError&&<p role="alert">{readingError}</p>}
          {check && (
            <section
              className="theory-check-card"
              aria-label={`Самостоятельное закрепление главы ${selected.chapter}`}
            >
              <div className="theory-check-icon">
                <Code2 size={23} />
              </div>
              <div>
                <div className="eyebrow">
                  САМОСТОЯТЕЛЬНОЕ ЗАДАНИЕ / ГЛАВА {selected.chapter}
                </div>
                <h3>{check.title.replace(/^Закрепление \d · /, "")}</h3>
                <p>
                  Напишите код с нуля, сравните результат с готовым main и
                  отметьте, совпал ли вывод. У этой задачи своя история отметок.
                </p>
                <div className="theory-check-meta">
                  <span
                    className={`status ${latest[check.id]?.status || "NEW"}`}
                  >
                    {latest[check.id]
                      ? statusNames[latest[check.id].status]
                      : "Ещё не проверено"}
                  </span>
                  <span>
                    {
                      attempts.filter(
                        (a) => a.task === check.id && a.mode !== "compile",
                      ).length
                    }{" "}
                    попыток
                  </span>
                  <span>{check.minutes} мин</span>
                </div>
              </div>
              <button
                className="primary"
                onClick={() => go("task/" + check.id)}
              >
                Открыть закрепление
                <ArrowRight size={15} />
              </button>
            </section>
          )}
          {selected.id === "summary" && (
            <section className="theory-practice-card">
              <BookOpen size={24} />
              <div>
                <h3>Перейдите к самостоятельным проектам</h3>
                <p>
                  Закрепления лекции: {passed} из {lecture.checks.length}.
                  Базовая проверка трёх проектов отмечается отдельно.
                </p>
              </div>
              <button className="primary" onClick={() => go("theory/1/practice")}>
                Открыть три проекта
                <ArrowRight size={15} />
              </button>
            </section>
          )}
          <nav className="theory-pagination" aria-label="Переход между главами">
            <button
              disabled={position === 0}
              onClick={() =>
                go(`theory/1/${lecture.sections[position - 1].id}`)
              }
            >
              <ArrowLeft size={15} />
              {position > 0
                ? lecture.sections[position - 1].chapter
                  ? `Глава ${lecture.sections[position - 1].chapter}`
                  : "Начало лекции"
                : "Начало лекции"}
            </button>
            <span>
              {position + 1} / {lecture.sections.length}
            </span>
            <button
              onClick={() =>
                position + 1 < lecture.sections.length
                  ? go(`theory/1/${lecture.sections[position + 1].id}`)
                  : go("theory/1/practice")
              }
            >
              {position + 1 < lecture.sections.length
                ? lecture.sections[position + 1].chapter
                  ? `К главе ${lecture.sections[position + 1].chapter}`
                  : "Итоги теории"
                : "К трём проектам"}
              <ArrowRight size={15} />
            </button>
          </nav>
        </div>
      </div>
    </div>
  );
});
