import { backendUrl } from "./backend-url";

function getCookie(name) {
  const match = document.cookie.match(new RegExp(`(?:^|; )${name.replace(/([.$?*|{}()[\]\\/+^])/g, "\\$1")}=([^;]*)`));
  return match ? decodeURIComponent(match[1]) : "";
}

let csrfReady;

async function ensureCsrf() {
  if (!getCookie("csrftoken")) {
    csrfReady ||= fetch(backendUrl("/auth/api/react/csrf/"), { credentials: "same-origin" });
    await csrfReady;
  }
}

export async function authRequest(path, payload = {}) {
  await ensureCsrf();
  const response = await fetch(backendUrl(path), {
    method: "POST",
    credentials: "same-origin",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": getCookie("csrftoken"),
      "X-Requested-With": "XMLHttpRequest",
    },
    body: JSON.stringify(payload),
  });
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
