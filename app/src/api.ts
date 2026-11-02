let token = "";
export async function api<T>(
  path: string,
  body?: unknown,
  method = "POST",
): Promise<T> {
  if (body !== undefined && !token) {
    const session = await fetch("/api/session").then((r) => r.json());
    token = session.token;
  }
  const response = await fetch(
    "/api/" + path,
    body === undefined
      ? { cache: "no-store" }
      : {
          method,
          headers: {
            "Content-Type": "application/json",
            "X-Mastery-Token": token,
          },
          body: JSON.stringify(body),
        },
  );
  const data = await response.json();
  if (!response.ok)
    throw new Error(data.error || "Сервер не ответил. Проверьте соединение.");
  return data;
}
