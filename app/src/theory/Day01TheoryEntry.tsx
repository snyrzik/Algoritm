import { BookOpen, ArrowRight, Check } from "lucide-react";
import type { Attempt } from "../types";
import "./entry.css";

export function Day01TheoryEntry({
  attempts,
  go,
}: {
  attempts: Attempt[];
  go: (path: string) => Promise<void>;
}) {
  const latest: Record<string, Attempt> = {};
  for (const attempt of attempts)
    if (attempt.mode !== "compile" && !latest[attempt.task])
      latest[attempt.task] = attempt;
  const chapters = [
    "Класс, ссылки и const",
    "Перегрузка операторов",
    "Индексация и границы",
    "Потоковый ввод и вывод",
  ];
  const passed = chapters.filter(
    (_, index) =>
      latest[`d1-l1-c${String(index + 1).padStart(2, "0")}`]?.status === "PASS",
  ).length;
  return (
    <section
      className="day01-theory-entry"
      aria-label="Теория Дня 1, лекция № 1"
    >
      <div className="day01-theory-heading">
        <span className="day01-theory-book">
          <BookOpen size={24} />
        </span>
        <div>
          <div className="eyebrow">ДЕНЬ 1 / ЛЕКЦИЯ № 1</div>
          <h2>Теория: классы и перегрузка операций</h2>
          <p>
            Четыре большие главы и самостоятельное закрепление после каждой.
          </p>
        </div>
        <button className="primary" onClick={() => go("theory/1/overview")}>
          Читать лекцию
          <ArrowRight size={15} />
        </button>
      </div>
      <div className="day01-theory-chapters">
        {chapters.map((title, index) => (
          <button
            key={title}
            onClick={() => go(`theory/1/chapter-${index + 1}`)}
          >
            <span>{String(index + 1).padStart(2, "0")}</span>
            {title}
            {latest[`d1-l1-c${String(index + 1).padStart(2, "0")}`]?.status ===
            "PASS" ? (
              <Check size={13} />
            ) : (
              <ArrowRight size={12} />
            )}
          </button>
        ))}
      </div>
      <div className="day01-theory-footnote">
        <span>
          Закрепления лекции: <strong>{passed} / 4</strong>
        </span>
        <span>Полная практика A/B/C — ниже, отдельным блоком</span>
      </div>
    </section>
  );
}
