import React, {
  useState,
  useEffect,
  useRef,
  useCallback,
  lazy,
  Suspense,
} from "react";
import { createRoot } from "react-dom/client";
import {
  ArrowRight,
  ArrowLeft,
  BookOpen,
  Braces,
  ChevronRight,
  Check,
  CheckCircle2,
  Clock,
  Code2,
  Command,
  Download,
  FileCode2,
  FlaskConical,
  FolderOpen,
  GraduationCap,
  History,
  LayoutDashboard,
  Lightbulb,
  Menu,
  Moon,
  Play,
  RefreshCw,
  RotateCcw,
  Save,
  Search,
  ShieldCheck,
  Sun,
  Target,
  Terminal,
  TriangleAlert,
  X,
  Activity,
  ArrowUpRight,
  ListChecks,
  Settings2,
  Square,
} from "lucide-react";
import { api } from "./api";
import {
  Task,
  Day,
  Kind,
  Attempt,
  Detail,
  isCompleted,
  Result,
  Exam,
  labels,
  statusNames,
} from "./types";
import "./styles.css";
const Theory = lazy(() => import("./lecture01/Lecture01"));
const TheoryMarkdown = lazy(() =>
  import("./theory/Markdown").then((module) => ({ default: module.Markdown })),
);
const ManualExercise = lazy(() => import("./manual/ManualExercise"));
const Editor = lazy(() =>
  import("./Editor").then((module) => ({ default: module.Editor })),
);

type Page =
  | "home"
  | "day"
  | "task"
  | "review"
  | "report"
  | "settings"
  | "theory";
function route() {
  const p = location.hash.replace(/^#\/?/, "").split("/");
  return {
    page: (p[0] || "day") as Page,
    key: p[1] || "1",
    section: p[2] || "overview",
    anchor: p[3] || "",
  };
}
function pct(tasks: Task[], latest: Record<string, Attempt>) {
  const r = tasks.filter((t) => t.required);
  return r.length
    ? Math.round(
        (r.filter((t) => isCompleted(latest[t.id])).length / r.length) *
          100,
      )
    : 0;
}
function Badge({ status }: { status?: string }) {
  return (
    <span className={"status " + (status || "NEW")}>
      {isCompleted(status ? {status} : undefined) ? <Check size={12} /> : null}
      {status ? statusNames[status] || status : "Не начато"}
    </span>
  );
}
function download(name: string, value: string) {
  const url = URL.createObjectURL(
    new Blob([value], { type: "text/plain;charset=utf-8" }),
  );
  const a = document.createElement("a");
  a.href = url;
  a.download = name;
  a.click();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}

function App() {
  const [workspaceTab, setWorkspaceTab] = useState("condition");
  const [locationState, setLocationState] = useState(route),
    [days, setDays] = useState<Day[]>([]),
    [tasks, setTasks] = useState<Task[]>([]),
    [attempts, setAttempts] = useState<Attempt[]>([]),
    [exam, setExam] = useState<Exam | null>(null);
  const [detail, setDetail] = useState<Detail | null>(null),
    [files, setFiles] = useState<Record<string, string>>({}),
    [filename, setFilename] = useState("solution.hpp"),
    [dirty, setDirty] = useState(false),
    [saveState, setSaveState] = useState("Все изменения сохранены");
  const [theme, setTheme] = useState(
      () => localStorage.getItem("mastery-theme") || "dark",
    ),
    [filter, setFilter] = useState<Kind | "all">("all"),
    [query, setQuery] = useState(""),
    [mobileMenu, setMobileMenu] = useState(false),
    [error, setError] = useState(""),
    [loading, setLoading] = useState(true),
    [busy, setBusy] = useState(false),
    [result, setResult] = useState<Result | null>(null),
    [consoleTab, setConsoleTab] = useState("tests"),
    [sideTab, setSideTab] = useState("condition");
  const [selection, setSelection] = useState<number[]>([]),
    [review, setReview] = useState<{
      answer?: number[];
      explanation?: string;
      optionExplanations?: string[];
      message?: string;
    } | null>(null),
    [hint, setHint] = useState(""),
    [hintLevel, setHintLevel] = useState(0),
    [now, setNow] = useState(Date.now()),
    [restored, setRestored] = useState(false);
  const editing = useRef<{
      id: string;
      files: Record<string, string>;
      revision: string;
      dirty: boolean;
    } | null>(null),
    saving = useRef<Promise<void> | null>(null),
    changeGeneration = useRef(0);
  const latest: Record<string, Attempt> = {};
  for (const a of attempts)
    if (!['compile','diagnosis'].includes(a.mode) && !latest[a.task]) latest[a.task] = a;
  const completed = tasks.filter(
      (t) => t.required && isCompleted(latest[t.id]),
    ).length,
    required = tasks.filter((t) => t.required).length;
  const currentDay =
    locationState.page === "task"
      ? tasks.find((t) => t.id === locationState.key)?.day || 1
      : Number(locationState.key) || 1;
  const current = days.find((d) => d.id === currentDay) || days[0];
  const refresh = useCallback(async () => {
    const p = await api<{ attempts: Attempt[]; exam: Exam | null }>("progress");
    setAttempts(p.attempts);
    setExam(p.exam);
  }, []);
  const persist = useCallback(async () => {
    if (saving.current) {
      await saving.current;
    }
    if (!editing.current?.dirty) return;
    const work = async () => {
      while (editing.current?.dirty) {
        const item = editing.current;
        const copy = { ...item.files };
        setSaveState("Сохраняется…");
        const data = await api<{ revision: string }>(
          "files/" + item.id,
          { files: copy, revision: item.revision },
          "PUT",
        );
        if (editing.current !== item) return;
        item.revision = data.revision;
        item.dirty = JSON.stringify(item.files) !== JSON.stringify(copy);
        if (!item.dirty) {
          localStorage.removeItem("mastery-draft-" + item.id);
          setDirty(false);
          setSaveState("Сохранено на диск");
        }
      }
    };
    const promise = work();
    saving.current = promise;
    try {
      await promise;
    } catch (e) {
      setSaveState("Черновик сохранён в браузере");
      throw e;
    } finally {
      if (saving.current === promise) saving.current = null;
    }
  }, []);
  const go = useCallback(
    async (path: string) => {
      try {
        await persist();
        setMobileMenu(false);
        setQuery("");
        setFilter("all");
        location.hash = "/" + path;
      } catch (e) {
        setError(String(e));
      }
    },
    [persist],
  );
  useEffect(() => {
    document.documentElement.dataset.theme = theme;
    localStorage.setItem("mastery-theme", theme);
  }, [theme]);
  useEffect(() => {
    const h = () => setLocationState(route());
    window.addEventListener("hashchange", h);
    return () => window.removeEventListener("hashchange", h);
  }, []);
  useEffect(() => {
    if (
      locationState.page === "day" &&
      locationState.key === "1" &&
      locationState.section === "practice"
    )
      setFilter("C");
  }, [locationState.page, locationState.key, locationState.section]);
  useEffect(() => {
    Promise.all([
      api<{ days: Day[]; tasks: Task[] }>("course").then((c) => {
        setDays(c.days);
        setTasks(c.tasks);
      }),
      refresh(),
    ])
      .catch((e) => setError(String(e)))
      .finally(() => setLoading(false));
  }, [refresh]);
  useEffect(() => {
    const timer = setInterval(() => setNow(Date.now()), 1000);
    return () => clearInterval(timer);
  }, []);
  useEffect(() => {
    const generation = ++changeGeneration.current;
    if (locationState.page !== "task") {
      persist().catch((e) => setError(String(e)));
      return;
    }
    setLoading(true);
    setError("");
    (async () => {
      await persist();
      const data = await api<Detail>("task/" + locationState.key);
      if (generation !== changeGeneration.current) return;
      let draft: Record<string, string> | null = null;
      try {
        const cached = localStorage.getItem("mastery-draft-" + data.task.id);
        if (cached) {
          const parsed = JSON.parse(cached);
          if (
            parsed &&
            Object.keys(parsed).sort().join() ===
              Object.keys(data.files).sort().join() &&
            Object.values(parsed).every((v) => typeof v === "string")
          )
            draft = parsed;
        }
      } catch {
        /* Malformed browser state is ignored; disk files stay authoritative. */
      }
      editing.current = {
        id: data.task.id,
        files: draft || data.files,
        revision: data.revision,
        dirty: !!draft,
      };
      setDetail(data);
      setFiles(draft || data.files);
      setDirty(!!draft);
      setRestored(!!draft);
      setSaveState(
        draft
          ? "Восстановлен несохранённый черновик"
          : "Все изменения сохранены",
      );
      setFilename(
        data.task.runner === "console" ? "main.cpp" :
        data.task.kind === "Q" || data.task.kind === "P"
          ? "notes.md"
          : "solution.hpp",
      );
      setResult(data.history[0] || null);
      setSelection([]);
      setReview(null);
      setHint("");
      setHintLevel(0);
      setSideTab("condition");
      setConsoleTab("tests");
      if (data.timerError) setError(data.timerError);
    })()
      .catch((e) => setError(String(e)))
      .finally(() => {
        if (generation === changeGeneration.current) setLoading(false);
      });
  }, [locationState.page, locationState.key, persist]);
  useEffect(() => {
    if (!dirty) return;
    const timer = setTimeout(
      () => persist().catch((e) => setError(String(e))),
      800,
    );
    return () => clearTimeout(timer);
  }, [files, dirty, persist]);
  useEffect(() => {
    const warn = (e: BeforeUnloadEvent) => {
      if (editing.current?.dirty) {
        e.preventDefault();
        e.returnValue = "";
      }
    };
    window.addEventListener("beforeunload", warn);
    return () => window.removeEventListener("beforeunload", warn);
  }, []);
  useEffect(() => {
    const focus = () => {
      if (locationState.page === "task" && !editing.current?.dirty && !busy) {
        api<Detail>("task/" + locationState.key)
          .then((data) => {
            const item = editing.current;
            if (
              item?.id === data.task.id &&
              !item.dirty &&
              item.revision !== data.revision
            ) {
              item.files = data.files;
              item.revision = data.revision;
              setFiles(data.files);
              setSaveState("Обновлено из файлов на диске");
            }
          })
          .catch((e) => setError(String(e)));
      }
    };
    window.addEventListener("focus", focus);
    return () => window.removeEventListener("focus", focus);
  }, [locationState, busy]);
  function edit(value: string, name: string = filename) {
    const item = editing.current;
    if (!item) return;
    item.files = { ...item.files, [name]: value };
    item.dirty = true;
    setFiles(item.files);
    setDirty(true);
    setSaveState("Есть изменения");
    try {
      localStorage.setItem(
        "mastery-draft-" + item.id,
        JSON.stringify(item.files),
      );
    } catch {
      setError(
        "Не удалось сохранить резервный черновик в браузере. Сохраните файл на диск.",
      );
    }
  }
  async function answer() {
    if (!detail) return;
    setBusy(true);
    try {
      const r = await api<Result>("answer/" + detail.task.id, {
        answer: selection,
      });
      setResult(r);
      setReview(await api("review/" + detail.task.id));
      await refresh();
    } catch (e) {
      setError(String(e));
    } finally {
      setBusy(false);
    }
  }
  async function askHint() {
    if (!detail || hintLevel >= 3) return;
    try {
      const h = await api<{ text: string }>("hint/" + detail.task.id, {
        level: hintLevel + 1,
      });
      setHint(h.text);
      setHintLevel((x) => x + 1);
      await refresh();
    } catch (e) {
      setError(String(e));
    }
  }
  async function startExam(timed: boolean) {
    try {
      setExam(await api<Exam>("exam/start", { timed }));
      setError("");
    } catch (e) {
      setError(String(e));
    }
  }
  async function reloadDisk() {
    if (!detail) return;
    try {
      if (editing.current?.dirty)
        download(
          detail.task.id + "-draft.json",
          JSON.stringify(editing.current.files, null, 2),
        );
      const data = await api<Detail>("task/" + detail.task.id);
      editing.current = {
        id: data.task.id,
        files: data.files,
        revision: data.revision,
        dirty: false,
      };
      localStorage.removeItem("mastery-draft-" + data.task.id);
      setFiles(data.files);
      setDetail(data);
      setDirty(false);
      setRestored(false);
      setError("");
      setSaveState("Загружено с диска");
    } catch (e) {
      setError(String(e));
    }
  }
  function nextTask() {
    if (!detail) return;
    if (detail.task.section === "lecture-theory") {
      go(
        `theory/1/${detail.task.chapter! < 5 ? "chapter-" + (detail.task.chapter! + 1) : "summary"}`,
      );
      return;
    }
    let list = tasks.filter(
      (t) => t.day === detail.task.day && t.kind === detail.task.kind,
    );
    if (
      exam &&
      !exam.finished &&
      detail.task.day === 5 &&
      detail.task.kind === "S"
    )
      list = exam.tasks
        .map((id) => tasks.find((t) => t.id === id)!)
        .filter(Boolean);
    const idx = list.findIndex((t) => t.id === detail.task.id);
    go(
      idx + 1 < list.length
        ? "task/" + list[idx + 1].id
        : "day/" + detail.task.day,
    );
  }
  const failedTasks = tasks.filter(
    (t) => latest[t.id] && !isCompleted(latest[t.id]),
  );
  const allTags = [...new Set(tasks.flatMap((t) => t.tags))];
  const weakTags = [...new Set(failedTasks.flatMap((t) => t.tags))];
  const recommendation =
    tasks.find(
      (t) => !latest[t.id] && t.tags.some((tag) => weakTags.includes(tag)),
    ) ||
    failedTasks[0] ||
    tasks.find((t) => t.required && !latest[t.id]);
  const activeExam = exam?.timed && !exam.finished;
  const timeLeft = exam
    ? Math.max(0, Math.floor(exam.started + exam.duration - now / 1000))
    : 0;
  const topicData = allTags.map((tag) => {
    const group = tasks.filter((t) => t.tags.includes(tag));
    const pass = group.filter((t) => isCompleted(latest[t.id]));
    const evidence = attempts.filter(
      (a) =>
        isCompleted(a) &&
        a.hintsUsed === 0 &&
        group.some((t) => t.id === a.task),
    );
    const dates = new Set(
      evidence.map((a) => new Date(a.created).toLocaleDateString("ru-RU")),
    );
    const independent = new Set(evidence.map((a) => a.task));
    return {
      tag,
      score: pct(group, latest),
      pass: pass.length,
      total: group.filter((t) => t.required).length,
      mastered:
        pct(group, latest) >= 95 &&
        dates.size >= 2 &&
        independent.size >= 3 &&
        !group.some((t) => latest[t.id] && !isCompleted(latest[t.id])),
    };
  });

  function taskTable(items: Task[]) {
    return (
      <div className="task-table">
        <div className="table-head">
          <span>Задание</span>
          <span>Уровень</span>
          <span>Статус</span>
          <span>Попытки</span>
          <span />
        </div>
        {items.length ? (
          items.map((t) => (
            <button
              className="task-row"
              key={t.id}
              onClick={() => go("task/" + t.id)}
            >
              <div className="task-name">
                <span className={"type-icon type-" + t.kind}>{t.kind}</span>
                <div>
                  <strong>{t.title}</strong>
                  <small>
                    {t.tags.slice(0, 2).join(" · ")}{" "}
                    <span className="task-id">{t.id}</span>
                  </small>
                </div>
              </div>
              <span className="level">
                {t.kind === "C" ? t.level : "—"}
                {!t.required ? " +" : ""}
              </span>
              <Badge status={latest[t.id]?.status} />
              <span className="attempt-count">
                {attempts.filter((a) => a.task === t.id && a.mode !== "compile")
                  .length || "—"}
              </span>
              <ChevronRight size={16} />
            </button>
          ))
        ) : (
          <div className="empty">
            <Search />
            <p>Задания не найдены. Измените запрос или выберите другой блок.</p>
          </div>
        )}
      </div>
    );
  }
  function dayCards() {
    return (
      <div className="day-cards">
        {days.map((d, i) => (
          <button
            key={d.id}
            className={"day-card " + (d.id === currentDay ? "selected" : "")}
            onClick={() => go("day/" + d.id)}
          >
            <div className="day-card-top">
              <span>ДЕНЬ 0{d.id}</span>
              {pct(
                tasks.filter((t) => t.day === d.id),
                latest,
              ) === 100 ? (
                <CheckCircle2 size={16} />
              ) : i === 4 ? (
                <GraduationCap size={17} />
              ) : (
                <span className="tiny-dot" />
              )}
            </div>
            <strong>{d.title}</strong>
            <div className="card-progress">
              <div>
                <i
                  style={{
                    width:
                      pct(
                        tasks.filter((t) => t.day === d.id),
                        latest,
                      ) + "%",
                  }}
                />
              </div>
              <small>
                {pct(
                  tasks.filter((t) => t.day === d.id),
                  latest,
                )}
                %
              </small>
            </div>
          </button>
        ))}
      </div>
    );
  }
  function Dashboard({ home = false }: { home?: boolean }) {
    const dt = home ? tasks : tasks.filter((t) => t.day === currentDay);
    if(!home&&currentDay===1)return <Suspense fallback={<div className="loading-state">Открываем лекцию № 1…</div>}><Theory section={locationState.section} anchor={locationState.anchor} attempts={attempts} go={go}/></Suspense>;
    if (currentDay === 5 && exam && !exam.finished)
      dt.sort((a, b) =>
        a.kind === "S" && b.kind === "S"
          ? exam.tasks.indexOf(a.id) - exam.tasks.indexOf(b.id)
          : a.order - b.order,
      );
    const visible = dt.filter(
      (t) =>
        (filter === "all" || t.kind === filter) &&
        `${t.title} ${t.id} ${t.tags.join(" ")}`
          .toLowerCase()
          .includes(query.toLowerCase()),
    );
    return (
      <>
        <div className="page-heading">
          <div>
            <div className="eyebrow">
              {home
                ? "ВАША УЧЕБНАЯ СРЕДА"
                : `ПЯТИДНЕВНЫЙ ИНТЕНСИВ / ДЕНЬ 0${currentDay}`}
            </div>
            <h1>
              {home ? "Меньше догадок. Больше практики." : current?.title}
            </h1>
            <p>
              {home
                ? "От знакомого синтаксиса — к самостоятельному, корректному C++17."
                : current?.subtitle +
                  ". Пишите по памяти, проверяйте, разбирайте ошибки."}
            </p>
          </div>
          <span className="course-tag">
            <span /> C++17
          </span>
        </div>
        {dayCards()}
        <section className="focus-card">
          <div>
            <div className="eyebrow">
              <span className="live-dot" />
              {home
                ? "СЛЕДУЮЩИЙ ШАГ"
                : currentDay === 5
                  ? "ПРОВЕРКА САМОСТОЯТЕЛЬНОСТИ"
                  : "СЕГОДНЯ В ФОКУСЕ"}
            </div>
            <h2>
              {home
                ? recommendation?.title || "Повторите курс без подсказок"
                : currentDay === 1
                  ? "Знать синтаксис. Чувствовать семантику."
                  : currentDay === 2
                    ? "Каждый ресурс должен иметь владельца."
                    : currentDay === 3
                      ? "Один контракт. Разные типы."
                      : currentDay === 4
                        ? "Соберите работающую архитектуру."
                        : "Напишите TSequence с чистого листа."}
            </h2>
            <p>
              {currentDay === 5 && !home
                ? "30 вопросов, 20 заданий на синтаксис, разбор кода и собственный контейнер. Критические ошибки блокируют готовность."
                : "Начните с диагностики, затем переходите к коду. Все уровни практики входят в курс; незакрытые задачи остаются видны."}
            </p>
            <div className="focus-footer">
              <button
                className="primary"
                onClick={() =>
                  go(
                    "task/" +
                      (home
                        ? recommendation?.id
                        : dt.find(
                            (t) =>
                              !latest[t.id] || !isCompleted(latest[t.id]),
                          )?.id || dt[0]?.id),
                  )
                }
              >
                {home
                  ? "Продолжить обучение"
                  : attempts.some((a) => dt.some((t) => t.id === a.task))
                    ? "Продолжить день"
                    : "Начать диагностику"}
                <ArrowRight size={16} />
              </button>
              <span>
                <Clock size={14} />
                4–6 часов <span className="dot-divider">·</span> {dt.length}{" "}
                заданий
              </span>
            </div>
          </div>
          <div className="code-art" aria-hidden="true">
            <div className="code-art-label">
              <span />
              <span />
              <span />
              <small>
                {currentDay === 5 ? "sequence.hpp" : "practice.cpp"}
              </small>
            </div>
            <div className="code-lines">
              <span className="code-comment">// От понимания к реализации</span>
              <br />
              <span className="code-purple">template</span> &lt;
              <span className="code-purple">typename</span> T&gt;
              <br />
              <span className="code-purple">class</span>{" "}
              <span className="code-blue">
                {currentDay === 5 ? "TSequence" : "YourNextStep"}
              </span>{" "}
              {"{"}
              <br />
              &nbsp;{" "}
              <span className="code-comment">// Ваш код начинается здесь.</span>
              <br />
              {"}"};
            </div>
            <div className="code-art-bottom">
              <Braces size={14} />
              <span>Практика важнее узнавания</span>
            </div>
          </div>
        </section>
        <div className="metrics">
          <div>
            <span className="metric-icon">
              <Target size={18} />
            </span>
            <div>
              <small>Прогресс {home ? "курса" : "дня"}</small>
              <strong>
                {pct(dt, latest)}
                <em>%</em>
              </strong>
            </div>
            <div className="mini-bar">
              <i style={{ width: pct(dt, latest) + "%" }} />
            </div>
          </div>
          <div>
            <span className="metric-icon">
              <CheckCircle2 size={18} />
            </span>
            <div>
              <small>Пройдено заданий</small>
              <strong>
                {
                  dt.filter(
                    (t) => t.required && isCompleted(latest[t.id]),
                  ).length
                }
                <em> / {dt.filter((t) => t.required).length}</em>
              </strong>
            </div>
          </div>
          <div>
            <span className="metric-icon">
              <RotateCcw size={18} />
            </span>
            <div>
              <small>Нужно разобрать</small>
              <strong>
                {failedTasks.filter((t) => home || t.day === currentDay).length}
                <em> заданий</em>
              </strong>
            </div>
          </div>
          <div>
            <span className="metric-icon">
              <Activity size={18} />
            </span>
            <div>
              <small>Самостоятельность</small>
              <strong>
                {attempts.length
                  ? attempts.filter(
                      (a) =>
                        a.mode !== "compile" &&
                        a.hintsUsed === 0 &&
                        isCompleted(a),
                    ).length
                  : "—"}
                <em>{attempts.length ? " без подсказок" : " нет данных"}</em>
              </strong>
            </div>
          </div>
        </div>
        {!home && currentDay === 5 && (
          <section className="exam-bar">
            <GraduationCap />
            <div>
              <strong>
                {activeExam
                  ? `Экзамен идёт · ${Math.floor(timeLeft / 3600)}:${String(Math.floor(timeLeft / 60) % 60).padStart(2, "0")}:${String(timeLeft % 60).padStart(2, "0")}`
                  : exam?.finished
                    ? "Сессия завершена"
                    : "Выберите режим экзамена"}
              </strong>
              <p>
                6 часов на сессию, по 4 минуты на синтаксис. В тренировке время
                не ограничено. Разбор ответов в экзамене — после завершения.
              </p>
            </div>
            {activeExam ? (
              <button
                onClick={async () => {
                  setExam(await api("exam/finish", {}));
                  await refresh();
                }}
              >
                Завершить сессию
              </button>
            ) : (
              <>
                <button onClick={() => startExam(false)}>Без таймера</button>
                <button className="primary" onClick={() => startExam(true)}>
                  Начать экзамен
                </button>
              </>
            )}
          </section>
        )}
        <div className="section-heading">
          <div>
            <h2>{home ? "Программа интенсива" : "Практикум дня"}</h2>
            <p>Проверьте решение с готовым main и отметьте результат.</p>
          </div>
          <label className="search">
            <Search size={15} />
            <input
              placeholder="Найти задание…"
              aria-label="Поиск заданий"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
            />
            <kbd>/</kbd>
          </label>
        </div>
        <div className="tabs">
          <button
            className={filter === "all" ? "active" : ""}
            onClick={() => setFilter("all")}
          >
            Все задания <span>{dt.length}</span>
          </button>
          {(["Q", "S", "P", "D", "C"] as Kind[]).map((k) => (
            <button
              key={k}
              className={filter === k ? "active" : ""}
              onClick={() => setFilter(k)}
            >
              <b>{k}</b>
              {labels[k]}
              <span>{dt.filter((t) => t.kind === k).length}</span>
            </button>
          ))}
        </div>
        {taskTable(visible.slice(0, home ? 12 : filter === "all" ? 12 : 100))}
        {(home || filter === "all") && visible.length > 12 && (
          <div className="table-footer">
            <span>Показаны первые 12 из {visible.length} заданий</span>
            <button onClick={() => setFilter("Q")}>
              Открыть блок теории <ArrowRight size={14} />
            </button>
          </div>
        )}
        <div className="bottom-notes">
          <div>
            <ShieldCheck size={18} />
            <p>
              <strong>Прогресс без скидок</strong>
              <br />
              Одна успешная попытка ещё не подтверждает освоение темы. Повторная
              самостоятельная проверка проводится в другой день.
            </p>
          </div>
          <button onClick={() => go("review")}>
            <RotateCcw size={16} />
            Ошибки и повторение
            <ArrowUpRight size={15} />
          </button>
        </div>
      </>
    );
  }

  function Exercise() {
    if (!detail || detail.task.id !== locationState.key)
      return <div className="empty">Загружается задание…</div>;
    const t = detail.task;
    const hs = attempts.filter((a) => a.task === t.id);
    const quiz = t.kind === "Q" || t.kind === "P";
    return (
      <>
        <div className="exercise-heading">
          <button
            className="back-link"
            onClick={() =>
              go(
                t.section === 'lecture-practice' ? 'theory/1/practice' : t.section === "lecture-theory"
                  ? `theory/1/chapter-${t.chapter}`
                  : "day/" + t.day,
              )
            }
          >
            <ArrowLeft size={15} />
            {t.section === 'lecture-practice' ? 'Лекция № 1 · Практика' : t.section === "lecture-theory"
              ? `Лекция № 1 · Глава ${t.chapter}`
              : `День 0${t.day}`}
          </button>
          <div className="exercise-title">
            <span className={"type-icon type-" + t.kind}>{t.kind}</span>
            <div>
              <div className="eyebrow">
                {t.section === "lecture-theory"
                  ? "Закрепление теории"
                  : labels[t.kind]}{" "}
                / {t.id} {t.category ? " / " + t.category : ""}
              </div>
              <h1>{t.title}</h1>
            </div>
            <Badge status={latest[t.id]?.status} />
          </div>
          <div className="exercise-meta">
            {t.tags.map((tag) => (
              <span key={tag}>{tag}</span>
            ))}
            <span>
              <Clock size={12} />
              {t.minutes} мин
            </span>
            {activeExam && t.day === 5 && (
              <span className="exam-indicator">
                {detail.syntaxDeadline
                  ? `Синтаксис: ${Math.floor(Math.max(0, detail.syntaxDeadline - now / 1000) / 60)}:${String(Math.floor(Math.max(0, detail.syntaxDeadline - now / 1000)) % 60).padStart(2, "0")}`
                  : "Экзамен · подсказки отключены"}
              </span>
            )}
          </div>
        </div>
        {quiz ? (
          <div className="quiz-layout">
            <section className="quiz-card">
              <div className="eyebrow">
                {t.multiple
                  ? "ВЫБЕРИТЕ ВСЕ ПОДХОДЯЩИЕ ОТВЕТЫ"
                  : "ОДИН ПРАВИЛЬНЫЙ ОТВЕТ"}
              </div>
              <h2>
                {t.kind === "P"
                  ? "Предскажите поведение C++17"
                  : "Проверьте понимание"}
              </h2>
              <div
                className={t.kind === "P" ? "question-code" : "question-text"}
              >
                {t.prompt}
              </div>
              <div className="options">
                {t.options?.map((o, i) => (
                  <button
                    className={
                      "option " +
                      (selection.includes(i) ? "chosen " : "") +
                      (review?.answer?.includes(i) ? "correct" : "")
                    }
                    key={i}
                    onClick={() => {
                      setSelection((old) =>
                        t.multiple
                          ? old.includes(i)
                            ? old.filter((n) => n !== i)
                            : [...old, i]
                          : [i],
                      );
                      setReview(null);
                    }}
                  >
                    <span className={t.multiple ? "check-box" : "radio"}>
                      {selection.includes(i) && <Check size={12} />}
                    </span>
                    <span>{o}</span>
                    <small>{String.fromCharCode(65 + i)}</small>
                  </button>
                ))}
              </div>
              {review && (
                <div
                  className={
                    "answer-review " +
                    (result?.status === "PASS" ? "success" : "")
                  }
                >
                  <strong>{result?.message}</strong>
                  <p>{review.explanation || review.message}</p>
                  {review.optionExplanations && (
                    <details>
                      <summary>Разобрать все варианты</summary>
                      {review.optionExplanations.map((e, i) => (
                        <p key={i}>
                          {String.fromCharCode(65 + i)}. {e}
                        </p>
                      ))}
                    </details>
                  )}
                </div>
              )}
              <div className="quiz-actions">
                <button
                  disabled={selection.length === 0 || busy}
                  className="primary"
                  onClick={answer}
                >
                  {busy ? "Проверка…" : "Проверить ответ"}
                  <ArrowRight size={16} />
                </button>
                <button onClick={nextTask}>
                  Следующее задание
                  <ChevronRight size={15} />
                </button>
              </div>
            </section>
            <aside className="quiz-aside">
              <div className="aside-card">
                <Target size={21} />
                <h3>Сначала — своя попытка</h3>
                <p>
                  Ответы и объяснения доступны после отправки. Первая попытка
                  сохраняется отдельно, даже если вы исправите ошибку.
                </p>
                <div className="aside-stat">
                  <span>Попыток</span>
                  <strong>{hs.length}</strong>
                </div>
                <div className="aside-stat">
                  <span>Последний результат</span>
                  <strong>
                    {latest[t.id] ? latest[t.id].score + "%" : "—"}
                  </strong>
                </div>
              </div>
              <div className="aside-card subtle">
                <BookOpen size={18} />
                <p>
                  Если стандарт не гарантирует результат, выбирайте
                  неопределённое поведение или ошибку компиляции, а не
                  предполагаемый вывод.
                </p>
              </div>
            </aside>
          </div>
        ) : (
          <Suspense fallback={<p className="muted">Открываем самостоятельную проверку…</p>}>
            <ManualExercise detail={detail} files={files} history={hs} edit={edit} persist={persist} refresh={refresh} onResult={setResult} theme={theme} go={go}/>
          </Suspense>
        )}
        <div className="exercise-bottom">
          <span>
            <ShieldCheck size={14} />
            Все попытки сохраняются локально
          </span>
          <button onClick={nextTask}>
            {t.section === "lecture-theory"
              ? t.chapter === 5
                ? "К итогам лекции"
                : "К следующей главе"
              : "Следующее задание"}
            <ArrowRight size={15} />
          </button>
        </div>
      </>
    );
  }

  function ReviewPage() {
    const weak = failedTasks.filter((t) => !query || t.tags.includes(query));
    const repeats = tasks.filter(
      (t) => !latest[t.id] && t.tags.some((tag) => weakTags.includes(tag)),
    );
    return (
      <>
        <div className="page-heading">
          <div>
            <div className="eyebrow">ОСОЗНАННАЯ ПРАКТИКА</div>
            <h1>Ошибки и повторение</h1>
            <p>
              Ошибка — конкретная тема для работы. История сохраняется после
              исправления.
            </p>
          </div>
          <button
            className="primary"
            disabled={!recommendation}
            onClick={() => go("task/" + recommendation?.id)}
          >
            Повторить слабые места
            <RotateCcw size={15} />
          </button>
        </div>
        <div className="topic-chips">
          <button
            className={!query ? "active" : ""}
            onClick={() => setQuery("")}
          >
            Все темы
          </button>
          {weakTags.map((tag) => (
            <button
              key={tag}
              className={query === tag ? "active" : ""}
              onClick={() => setQuery(tag)}
            >
              {tag}
              <span>
                {failedTasks.filter((t) => t.tags.includes(tag)).length}
              </span>
            </button>
          ))}
        </div>
        {weak.length ? (
          taskTable(weak)
        ) : (
          <div className="empty-state">
            <Target size={34} />
            <h2>
              {attempts.length
                ? "Незакрытых ошибок в этом разделе нет"
                : "Диагностика ещё впереди"}
            </h2>
            <p>
              После первой попытки здесь появятся темы, которые требуют
              внимания.
            </p>
            <button onClick={() => go("day/1")}>
              Перейти к первому дню
              <ArrowRight size={15} />
            </button>
          </div>
        )}
        {repeats.length > 0 && (
          <>
            <div className="section-heading">
              <div>
                <h2>Независимая проверка</h2>
                <p>
                  Новые задания по темам прошлых ошибок. Вернитесь к ним на
                  следующий день.
                </p>
              </div>
            </div>
            {taskTable(repeats.slice(0, 6))}
          </>
        )}
        <div className="section-heading">
          <div>
            <h2>История ошибочных попыток</h2>
            <p>Сохраняются даже после успешного исправления.</p>
          </div>
        </div>
        {attempts
          .filter((a) => a.mode !== "compile" && !isCompleted(a))
          .slice(0, 20)
          .map((a) => (
            <button
              key={a.id}
              className="history-row"
              onClick={() => go("task/" + a.task)}
            >
              <span>
                <History size={15} />
                {tasks.find((t) => t.id === a.task)?.title}
              </span>
              <small>{new Date(a.created).toLocaleString("ru-RU")}</small>
              <Badge status={a.status} />
            </button>
          ))}
      </>
    );
  }
  function ReportPage() {
    const remaining = tasks.filter(
      (t) => t.required && !isCompleted(latest[t.id]),
    );
    const dimensions = [
      ["Синтаксис", tasks.filter((t) => t.kind === "S")],
      [
        "Понимание поведения",
        tasks.filter((t) => t.kind === "Q" || t.kind === "P"),
      ],
      [
        "Корректность реализации",
        tasks.filter((t) => t.kind === "C" || t.kind === "D"),
      ],
      ["Работа с памятью", tasks.filter((t) => t.memory)],
      [
        "Обработка ошибок",
        tasks.filter((t) => t.tags.includes("Exception safety")),
      ],
    ] as [string, Task[]][];
    return (
      <>
        <div className="page-heading">
          <div>
            <div className="eyebrow">ВАШИ РЕЗУЛЬТАТЫ</div>
            <h1>Прогресс и готовность</h1>
            <p>
              Результат вычисляется по последней проверке каждого обязательного
              задания.
            </p>
          </div>
          <button
            onClick={() =>
              download(
                "mastery-progress.json",
                JSON.stringify({ attempts, exam }, null, 2),
              )
            }
          >
            <Download size={15} />
            Экспорт истории
          </button>
        </div>
        <div className="report-banner">
          <GraduationCap size={28} />
          <div>
            <h2>
              {remaining.length
                ? "Есть задания для самостоятельной проверки"
                : "Все обязательные задания отмечены выполненными"}
            </h2>
            <p>
              {completed} из {required} заданий пройдено. {remaining.length} ещё
              требуют работы. Самостоятельность и устойчивость подтверждаются
              повторной практикой.
            </p>
          </div>
          <strong>{pct(tasks, latest)}%</strong>
        </div>
        <div className="dimension-grid">
          {dimensions.map(([name, group]) => (
            <div key={name}>
              <span>{name}</span>
              <strong>{pct(group, latest)}%</strong>
              <div className="progress-bar">
                <i style={{ width: pct(group, latest) + "%" }} />
              </div>
            </div>
          ))}
        </div>
        <div className="section-heading">
          <div>
            <h2>Освоение тем</h2>
            <p>
              Процент показывает выполненные задания. Повторные самостоятельные
              проверки в разные дни отмечаются отдельно.
            </p>
          </div>
        </div>
        <div className="topic-report">
          {topicData.map((t) => (
            <div key={t.tag}>
              <span>{t.tag}</span>
              <div className="progress-bar">
                <i style={{ width: t.score + "%" }} />
              </div>
              <strong>{t.score}%</strong>
              <small>
                {t.mastered
                  ? "Есть повторная самостоятельная проверка"
                  : t.pass
                    ? "Нужна повторная проверка"
                    : "Нет подтверждения"}
              </small>
            </div>
          ))}
        </div>
        <div className="section-heading">
          <div>
            <h2>Незакрытые обязательства</h2>
            <p>Переход к следующему дню не скрывает эти задания.</p>
          </div>
        </div>
        {taskTable(remaining.slice(0, 15))}
        <div className="grading-scale">
          <h3>Как считается прогресс</h3>
          <p>
            Процент отражает долю выполненных заданий. В программных заданиях
            результатом служит ваша отметка после сравнения с main; в Q/P —
            проверка ответа на сайте.
          </p>
          <p>
            Смысл письменного разбора, читаемость и авторство не оцениваются
            автоматически. Отметка «Проверено мной» сохраняет результат вашей самопроверки.
          </p>
        </div>
      </>
    );
  }
  function SettingsPage() {
    return <><div className="page-heading"><div><div className="eyebrow">ВАША ПРАКТИКА</div><h1>Настройки и самостоятельная проверка</h1><p>Задания, main, ожидаемый вывод и ваши отметки о результате.</p></div></div><div className="settings-grid">
      <section className="settings-card"><CheckCircle2/><h2>Как сдавать задания</h2><p>Напишите решение в своей среде C++. В задании откройте «Показать main для проверки», проверьте перечисленные случаи и сравните вывод с ожидаемым.</p><p>Если всё совпало, нажмите «Да, всё совпало». Если нашли ошибку — «Есть расхождения». Отметку можно изменить в любой момент.</p></section>
      <section className="settings-card"><FolderOpen/><h2>Файлы и сохранение</h2><p>Черновик на сайте синхронизируется с <code>student/day-XX/ID/</code>. Можно работать напрямую в своей IDE.</p><p>Вместе с main можно скачать архив проверки: в нём ваши исходники, нужные заголовки и ожидаемый вывод. История отметок хранится в <code>progress/mastery.sqlite3</code>.</p></section>
      <section className="settings-card"><Sun/><h2>Оформление</h2><p>Тема применяется к интерфейсу и черновику кода.</p><button onClick={()=>setTheme(theme==='dark'?'light':'dark')}>{theme==='dark'?<Sun size={16}/>:<Moon size={16}/>}Включить {theme==='dark'?'светлую':'тёмную'} тему</button></section>
      <section className="settings-card"><ShieldCheck/><h2>Что означает прогресс</h2><p>«Проверено мной» — ваша отметка о совпадении результатов с примером. Сайт сохраняет её и учитывает в прогрессе.</p><p>Тесты с вариантами ответа и предсказанием вывода проверяются на сайте. Запускать ваш C++-код на сайте не требуется.</p></section>
    </div></>;
  }

  return (
    <div className="app-shell">
      <button
        className="mobile-toggle"
        aria-label="Открыть навигацию"
        onClick={() => setMobileMenu(!mobileMenu)}
      >
        <Menu size={20} />
      </button>
      {mobileMenu && (
        <div className="sidebar-overlay" onClick={() => setMobileMenu(false)} />
      )}
      <aside className={"sidebar " + (mobileMenu ? "open" : "")}>
        <button className="brand" onClick={() => go("home")}>
          <span className="brand-icon">
            C<span>++</span>
          </span>
          <span>
            C++ Mastery<small>ПРАКТИКА. ПОНИМАНИЕ. КОД.</small>
          </span>
        </button>
        <div className="course-info">
          <span className="course-info-icon">
            <GraduationCap size={19} />
          </span>
          <div>
            <strong>Интенсив C++17</strong>
            <small>5 дней · от синтаксиса к практике</small>
          </div>
        </div>
        <nav>
          <button
            className={locationState.page === "home" ? "nav-active" : ""}
            onClick={() => go("home")}
          >
            <LayoutDashboard size={18} />
            Обзор курса
          </button>
          <div className="nav-caption">ПРОГРАММА ОБУЧЕНИЯ</div>
          {days.map((d) => (
            <React.Fragment key={d.id}>
              <button
                className={
                  "day-nav " +
                  ((locationState.page === "day" ||
                    locationState.page === "task" ||
                    locationState.page === "theory") &&
                  currentDay === d.id
                    ? "nav-active"
                    : "")
                }
                key={d.id}
                onClick={() => go("day/" + d.id)}
              >
                <span className="day-number">0{d.id}</span>
                <span>
                  <small>День {d.id}</small>
                  {
                    [
                      "Операторы",
                      "Память и строки",
                      "Шаблоны функций",
                      "Классы и RTTI",
                      "Итоговый экзамен",
                    ][d.id - 1]
                  }
                </span>
                {pct(
                  tasks.filter((t) => t.day === d.id),
                  latest,
                ) === 100 ? (
                  <Check size={15} />
                ) : (
                  <ChevronRight size={14} />
                )}
              </button>
              {d.id === 1 && currentDay === 1 && (
                <button
                  className={
                    "day01-theory-nav " +
                    (locationState.page === "theory" ? "nav-active" : "")
                  }
                  onClick={() => go("theory/1/overview")}
                >
                  <BookOpen size={14} />
                  Лекция № 1 · Теория
                </button>
              )}
            </React.Fragment>
          ))}
          <div className="nav-caption">ВАШЕ ОБУЧЕНИЕ</div>
          <button
            className={locationState.page === "review" ? "nav-active" : ""}
            onClick={() => go("review")}
          >
            <RotateCcw size={18} />
            Ошибки и повторение
            {failedTasks.length > 0 && (
              <span className="nav-count">{failedTasks.length}</span>
            )}
          </button>
          <button
            className={locationState.page === "report" ? "nav-active" : ""}
            onClick={() => go("report")}
          >
            <Activity size={18} />
            Прогресс и результаты
          </button>
        </nav>
        <div className="sidebar-bottom">
          <div className="sidebar-progress">
            <div>
              <span>Весь интенсив</span>
              <strong>{pct(tasks, latest)}%</strong>
            </div>
            <div className="progress-bar">
              <i style={{ width: pct(tasks, latest) + "%" }} />
            </div>
            <small>
              {completed} из {required} заданий пройдено
            </small>
          </div>
          <button className="settings-link" onClick={() => go("settings")}>
            <Settings2 size={17} />
            Среда и настройки
          </button>
          <div className="local-badge"><span className="tiny-dot saved"/>Самостоятельная проверка<span>v1.1</span></div>
        </div>
      </aside>
      <div className="main-shell">
        <header className="topbar">
          <div className="breadcrumbs">
            <span>Рабочее пространство</span>
            <ChevronRight size={13} />
            <strong>
              {locationState.page === "day" ||
              locationState.page === "task" ||
              locationState.page === "theory"
                ? `День 0${currentDay}`
                : (
                    {
                      home: "Обзор курса",
                      review: "Повторение",
                      report: "Результаты",
                      settings: "Настройки",
                    } as Record<string, string>
                  )[locationState.page] || "Курс"}
            </strong>
            {locationState.page === "task" && (
              <>
                <ChevronRight size={13} />
                <span>{locationState.key}</span>
              </>
            )}
            {locationState.page === "theory" && (
              <>
                <ChevronRight size={13} />
                <span>Лекция № 1 · Теория</span>
              </>
            )}
          </div>
          <div className="topbar-actions">
            <span>
              <span className="tiny-dot saved" />
              Локальный режим
            </span>
            <button
              title="Сменить тему"
              aria-label="Сменить тему"
              onClick={() => setTheme(theme === "dark" ? "light" : "dark")}
            >
              {theme === "dark" ? <Sun size={17} /> : <Moon size={17} />}
            </button>
            <div className="avatar">Я</div>
          </div>
        </header>
        <main
          className={
            "main-content " +
            (locationState.page === "task" ? "task-content" : "")
          }
        >
          {error && (
            <div className="error-banner" role="alert">
              <TriangleAlert size={18} />
              <span>{error}</span>
              <button
                aria-label="Закрыть сообщение"
                onClick={() => setError("")}
              >
                <X size={16} />
              </button>
            </div>
          )}
          {loading && (!days.length || locationState.page === "task") ? (
            <div className="loading-state">
              <RefreshCw className="spin" />
              <p>Подготавливаем рабочее пространство…</p>
            </div>
          ) : locationState.page === "theory" ? (
            locationState.key === "1" ? (
              <Suspense
                fallback={
                  <div className="loading-state">
                    <RefreshCw className="spin" />
                    <p>Открываем теорию…</p>
                  </div>
                }
              >
                <Theory
                  section={locationState.section}
                  anchor={locationState.anchor}
                  attempts={attempts}
                  go={go}
                />
              </Suspense>
            ) : (
              <div className="empty">Теория этой лекции не найдена.</div>
            )
          ) : locationState.page === "task" ? (
            Exercise()
          ) : locationState.page === "review" ? (
            ReviewPage()
          ) : locationState.page === "report" ? (
            ReportPage()
          ) : locationState.page === "settings" ? (
            SettingsPage()
          ) : (
            Dashboard({ home: locationState.page === "home" })
          )}
          <footer>
            <span>Сначала понимание. Затем уверенность.</span>
            <span>
              C++ Mastery <span> / </span> C++17
            </span>
          </footer>
        </main>
      </div>
    </div>
  );
}
createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
);
