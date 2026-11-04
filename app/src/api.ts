let token = "";
let session: Promise<void> | null = null;
function initializeSession() {
  session ??= fetch("/api/session", {cache:"no-store"}).then(r=>{
    if(!r.ok)throw new Error("Не удалось открыть локальную сессию");
    return r.json();
  }).then(value=>{
    token=value.token;
    for(const key of Object.keys(localStorage))
      if(/^mastery-draft-(?:d01-v2-|d1-)/.test(key))localStorage.removeItem(key);
    if(localStorage.getItem("mastery-workspace")!==value.profileId){
      for(const key of Object.keys(localStorage))
        if(key.startsWith("mastery-draft-"))localStorage.removeItem(key);
      localStorage.setItem("mastery-workspace",value.profileId);
    }
  }).catch(error=>{session=null;throw error;});
  return session;
}
export async function api<T>(
  path: string,
  body?: unknown,
  method = "POST",
): Promise<T> {
  await initializeSession();
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
