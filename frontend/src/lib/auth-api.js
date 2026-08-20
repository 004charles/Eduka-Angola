import { backendUrl } from "./backend-url";

function getCookie(name) {
  const match = document.cookie.match(new RegExp(`(?:^|; )${name.replace(/([.$?*|{}()[\]\\/+^])/g, "\\$1")}=([^;]*)`));
  return match ? decodeURIComponent(match[1]) : "";
}

let csrfReady;
const csrfCookieNames = ["eduka_csrftoken", "csrftoken"];

function csrfToken() {
  return csrfCookieNames.map(getCookie).find(Boolean) || "";
}

async function ensureCsrf({ refresh = false } = {}) {
  if (refresh || !csrfToken()) {
    csrfReady ||= fetch(backendUrl("/auth/api/react/csrf/"), {
      credentials: "include",
      cache: "no-store",
    }).then((response) => {
      if (!response.ok) throw new Error("Não foi possível iniciar a sessão de segurança.");
    });
    try {
      await csrfReady;
    } finally {
      csrfReady = undefined;
    }
  }
  if (!csrfToken()) throw new Error("A sessão de segurança não foi iniciada. Atualize a página e tente novamente.");
}

export async function authRequest(path, payload = {}) {
  await ensureCsrf({ refresh: true });
  const request = () => fetch(backendUrl(path), {
      method: "POST",
      credentials: "include",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": csrfToken(),
        "X-Requested-With": "XMLHttpRequest",
      },
      body: JSON.stringify(payload),
    });
  let response = await request();
  if (response.status === 403) {
    await ensureCsrf({ refresh: true });
    response = await request();
  }
  const data = await response.json().catch(() => ({
    ok: false,
    message: response.status === 403
      ? "A sessão de segurança expirou. Atualize a página e tente novamente."
      : "Não foi possível concluir esta ação. Tente novamente.",
  }));
  if (!response.ok && data.ok !== true) throw Object.assign(new Error(data.message || data.detail || "Não foi possível concluir esta ação."), { data, status: response.status });
  return data;
}

export async function logoutStudent() {
  return authRequest('/auth/api/react/logout/');
}

export async function getStudentSession() {
  const response = await fetch(backendUrl("/auth/api/react/aluno/resumo/"), {
    cache: "no-store",
    credentials: "same-origin",
    headers: { Accept: "application/json" },
  });
  if (response.status === 401 || response.status === 403) return null;
  if (!response.ok) throw new Error("Não foi possível confirmar a sessão.");
  const data = await response.json();
  return data?.ok ? data.aluno : null;
}
