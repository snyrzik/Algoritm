export type Kind = "Q" | "S" | "P" | "D" | "C";
export interface Task {
  id: string;
  day: number;
  kind: Kind;
  title: string;
  prompt: string;
  level: string;
  minutes: number;
  tags: string[];
  required: boolean;
  order: number;
  filePath: string;
  options?: string[];
  multiple?: boolean;
  memory?: boolean;
  starter?: string;
  category?: string;
  difficulty?: string;
  section?: "lecture-theory" | "stereolab";
  version?: number;
  number?: number;
  group?: "Q" | "S" | "P" | "D" | "A" | "B" | "C";
  maxPoints?: number;
  runner?: "choice" | "prediction" | "cpp" | "console";
  code?: string;
  variant?: number;
  traceFields?: {id:string;label:string;options?:{value:string;label:string}[]}[];
  diagnosisChoices?: {id:string;label:string}[];
  dependencies?: string[];
  fixtures?: string[];
  archived?: boolean;
  lecture?: number;
  chapter?: number;
  protocol?: string;
}
export interface Day {
  id: number;
  title: string;
  subtitle: string;
  topics: string[];
  duration: string;
}
export interface TestResult {
  name: string;
  category: string;
  passed: boolean;
  output: string;
  duration: number;
  timeout: boolean;
  exitCode: number;
}
export interface Result {
  status: string;
  score: number;
  mode: string;
  message?: string;
  compiled?: boolean;
  compilation?: string;
  tests?: TestResult[];
  staticErrors?: string[];
  memory?: {
    required: boolean;
    addressSanitizer: boolean;
    undefinedSanitizer: boolean;
    leakSanitizer: boolean;
    allocationTracking: boolean;
  };
  reviewNote?: string;
  hintsUsed?: number;
  codeHash?: string;
  answer?: number[];
  pointsEarned?: number;
  maxPoints?: number;
  criticalFailures?: string[];
  signaturePassed?: boolean;
  diagnosisCorrect?: boolean;
  explanation?: string;
  rules?: string[];
  variant?: number;
  feedback?: {expectedOutput:string;explanation:string;trace:{label:string;correct:boolean}[]};
}
export interface Attempt extends Result {
  id: number;
  task: string;
  created: string;
}
export interface Detail {
  task: Task;
  files: Record<string, string>;
  revision: string;
  history: Attempt[];
  context: { before: string; after: string };
  testNames: { name: string; category: string }[];
  timerError?: string;
  syntaxDeadline?: number | null;
}
export interface Exam {
  id: number;
  started: number;
  duration: number;
  timed: boolean;
  finished: number | null;
  tasks: string[];
  serverTime: number;
}
export interface Doctor {
  available: boolean;
  compiler: string;
  path: string;
  addressSanitizer: boolean;
  undefinedSanitizer: boolean;
  leakSanitizer: boolean;
  details: string;
}
export const labels: Record<Kind, string> = {
  Q: "Теория",
  S: "Синтаксис",
  P: "Предсказание",
  D: "Отладка",
  C: "Практика",
};
export const statusNames: Record<string, string> = {
  PASS: "Пройдено",
  FAIL: "Есть ошибки",
  COMPILE_ERROR: "Ошибка компиляции",
  COMPILED: "Скомпилировано",
  BLOCKED: "Проверка недоступна",
  UNVERIFIED: "Память не проверена",
  REVIEW_REQUIRED: "Нужен разбор",
  EXPIRED: "Время истекло",
  DEPENDENCY_ERROR: "Нужны ваши компоненты",
  ANALYSIS_REQUIRED: "Сначала разбор",
  DIAGNOSIS_RECORDED: "Разбор зафиксирован",
  REPAIR_REQUIRED: "Нужно исправление",
  STATIC_ERROR: "Нарушен контракт",
};
